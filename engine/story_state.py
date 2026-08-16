"""Deterministic story-state and decision gates for the novel workflow.

The prose model may propose scenes, but it does not own the season contract or
the canonical plot state.  This module keeps those two things in small,
reviewable files and exposes the same checks to the writer, the verifier, and
the command line.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.S)
CHAPTER_RE = re.compile(r"^(?P<prefix>ch)?(?P<number>\d+)-.+\.md$", re.I)
REQUIRED_CONTRACT_FIELDS = ("pressure", "choice", "cost", "state_change", "next_pressure")
DEFAULT_MIN_BODY_CHARS = 1200
REQUIRED_MANIFEST_FIELDS = (
    "primary_reader",
    "platform_assumption",
    "opening_promise",
    "core_question",
)
REQUIRED_REWARD_FIELDS = ("power", "relationship", "faction")
REQUIRED_FACTION_FIELDS = (
    "public_goal",
    "hidden_goal",
    "resources",
    "red_lines",
    "current_move",
    "stance",
)
REQUIRED_PLOT_FIELDS = (
    "current_pressure",
    "open_threads",
    "character_goals",
    "faction_moves",
    "state_updates",
    "knowledge",
    "last_accepted_chapter",
)
REQUIRED_DECISION_FIELDS = (
    "label",
    "primary_reader",
    "opening",
    "winner",
    "loser",
    "cost",
    "next_pressure",
    "risk",
)
REQUIRED_FACTION_MOVE_FIELDS = ("faction", "move", "consequence", "stance_change", "evidence")


class StoryStateError(ValueError):
    """Raised when a story-state file is malformed or unsafe to use."""


def _path(sdir: str | os.PathLike[str], *parts: str) -> Path:
    return Path(sdir, *parts)


def _read_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return copy.deepcopy(default)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StoryStateError(f"invalid JSON: {path}: {exc}") from exc


def _read_yaml(path: Path, default: Any) -> Any:
    if not path.is_file():
        return copy.deepcopy(default)
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise StoryStateError(f"invalid YAML: {path}: {exc}") from exc
    return copy.deepcopy(default) if value is None else value


def _atomic_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() in {".yaml", ".yml"}:
        payload = yaml.safe_dump(value, allow_unicode=True, sort_keys=False)
    else:
        payload = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def load_manifest(sdir: str | os.PathLike[str]) -> dict[str, Any]:
    """Load the machine-readable season contract, with a safe legacy default."""
    path = _path(sdir, "season_manifest.yaml")
    value = _read_yaml(path, {})
    if not isinstance(value, dict):
        raise StoryStateError(f"season manifest must be an object: {path}")
    return value


def strict_mode(manifest: dict[str, Any]) -> bool:
    """Only new/pilot seasons are strict; the existing corpus remains auditable."""
    return bool(manifest.get("human_decision_required", False)) and not bool(manifest.get("legacy_mode", False))


def load_factions(sdir: str | os.PathLike[str]) -> list[dict[str, Any]]:
    value = _read_yaml(_path(sdir, "factions.yaml"), [])
    if isinstance(value, dict):
        value = value.get("factions", [])
    if not isinstance(value, list):
        raise StoryStateError("factions.yaml must contain a list or a factions list")
    if any(not isinstance(item, dict) for item in value):
        raise StoryStateError("factions.yaml factions must be objects")
    return value


def load_plot_state(sdir: str | os.PathLike[str]) -> dict[str, Any]:
    value = _read_json(
        _path(sdir, "plot_state.json"),
        {
            "version": 1,
            "open_threads": [],
            "character_goals": {},
            "faction_moves": [],
            "state_updates": [],
            "knowledge": {},
            "last_accepted_chapter": 0,
        },
    )
    if not isinstance(value, dict):
        raise StoryStateError("plot_state.json must contain an object")
    return value


def decision_options_path(sdir: str | os.PathLike[str]) -> Path:
    return _path(sdir, "decisions", "next.json")


def approved_decision_path(sdir: str | os.PathLike[str]) -> Path:
    return _path(sdir, "decisions", "approved.json")


def load_decision_options(sdir: str | os.PathLike[str]) -> dict[str, Any]:
    value = _read_json(decision_options_path(sdir), {"version": 1, "options": []})
    if not isinstance(value, dict):
        raise StoryStateError("decisions/next.json must contain an object")
    options = value.get("options", [])
    if not isinstance(options, list):
        raise StoryStateError("decisions/next.json options must be a list")
    return value


def load_approved_decision(sdir: str | os.PathLike[str]) -> dict[str, Any] | None:
    value = _read_json(approved_decision_path(sdir), None)
    if value is None:
        return None
    if (
        not isinstance(value, dict)
        or not str(value.get("id", "")).strip()
        or value.get("approved") is not True
    ):
        raise StoryStateError("decisions/approved.json needs approved=true and a non-empty id")
    if "base_chapter" in value and (
        not isinstance(value.get("base_chapter"), int)
        or isinstance(value.get("base_chapter"), bool)
        or value.get("base_chapter") < 0
    ):
        raise StoryStateError("decisions/approved.json base_chapter must be a non-negative integer")
    return value


def require_approved_decision(sdir: str | os.PathLike[str]) -> dict[str, Any] | None:
    """Return the human-approved option or fail before any model call/state write."""
    manifest = load_manifest(sdir)
    if not strict_mode(manifest):
        return load_approved_decision(sdir)
    schema_errors = []
    schema_errors.extend(validate_manifest(manifest, strict=True))
    factions = load_factions(sdir)
    plot = load_plot_state(sdir)
    options_file = load_decision_options(sdir)
    schema_errors.extend(validate_factions(factions, strict=True))
    schema_errors.extend(validate_plot_state(plot, strict=True))
    schema_errors.extend(validate_decision_options(options_file, strict=True))
    if schema_errors:
        raise StoryStateError("strict season contract invalid: " + ", ".join(dict.fromkeys(schema_errors)))
    decision = load_approved_decision(sdir)
    if not decision:
        raise StoryStateError(
            "human decision required: create decisions/next.json and approve one option "
            "with `python engine/story_state.py approve --season ... --id ...`"
        )
    if decision.get("consumed") is True:
        raise StoryStateError("approved decision is stale or already consumed; approve a decision for the next chapter")
    options = load_decision_options(sdir).get("options", [])
    ids = {str(item.get("id", "")).strip() for item in options if isinstance(item, dict)}
    if str(decision.get("id", "")).strip() not in ids:
        raise StoryStateError("approved decision is not present in decisions/next.json")
    plot = load_plot_state(sdir)
    current_chapter = plot.get("last_accepted_chapter", 0)
    base_chapter = decision.get("base_chapter")
    if not isinstance(base_chapter, int) or isinstance(base_chapter, bool):
        raise StoryStateError(
            "approved decision has no base_chapter; approve it again for exactly one next chapter"
        )
    if base_chapter != current_chapter:
        raise StoryStateError(
            "approved decision is stale or already consumed; approve a decision for the next chapter"
        )
    return decision


def approve_decision(sdir: str | os.PathLike[str], decision_id: str, rationale: str = "") -> dict[str, Any]:
    manifest = load_manifest(sdir)
    options_file = load_decision_options(sdir)
    if strict_mode(manifest):
        schema_errors = validate_decision_options(options_file, strict=True)
        if schema_errors:
            raise StoryStateError("invalid decision options: " + ", ".join(schema_errors))
    options = options_file.get("options", [])
    wanted = str(decision_id).strip()
    selected = next((item for item in options if isinstance(item, dict) and str(item.get("id", "")).strip() == wanted), None)
    if selected is None:
        raise StoryStateError(f"decision id not found in next.json: {wanted}")
    plot = load_plot_state(sdir)
    base_chapter = plot.get("last_accepted_chapter", 0)
    if not isinstance(base_chapter, int) or isinstance(base_chapter, bool) or base_chapter < 0:
        raise StoryStateError("plot_state.json last_accepted_chapter must be a non-negative integer")
    result = {
        "version": 1,
        "id": wanted,
        "approved": True,
        "base_chapter": base_chapter,
        "rationale": str(rationale).strip(),
        "option": selected,
    }
    _atomic_write(approved_decision_path(sdir), result)
    return result


def chapter_number(path: str | os.PathLike[str]) -> int | None:
    match = CHAPTER_RE.match(Path(path).name)
    return int(match.group("number")) if match else None


def chapter_candidates(sdir: str | os.PathLike[str]) -> dict[int, list[Path]]:
    root = _path(sdir, "chronicle")
    grouped: dict[int, list[Path]] = {}
    if not root.is_dir():
        return grouped
    for path in root.glob("*.md"):
        number = chapter_number(path)
        if number is not None:
            grouped.setdefault(number, []).append(path)
    for paths in grouped.values():
        paths.sort(key=lambda item: item.name.lower())
    return grouped


def _chapter_meta(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(raw)
    if not match:
        return {}
    try:
        value = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}
    return value if isinstance(value, dict) else {}


def _canonical_rank(path: Path) -> tuple[int, int, str]:
    meta = _chapter_meta(path)
    explicit = meta.get("canonical") is True or str(meta.get("status", "")).lower() == "canonical"
    prefix = path.name[:2].lower() == "ch"
    return (2 if explicit else 0, 1 if prefix else 0, path.name.lower())


def canonical_chapter_files(sdir: str | os.PathLike[str]) -> list[tuple[int, Path]]:
    """Return one deterministic candidate per chapter number, newest first.

    Duplicate numbers remain visible through :func:`chapter_candidates` and
    the validator.  They are never allowed to silently multiply prompt context.
    """
    selected = []
    for number, paths in chapter_candidates(sdir).items():
        selected.append((number, max(paths, key=_canonical_rank)))
    return sorted(selected, key=lambda item: item[0], reverse=True)


def body_of(text: str) -> str:
    match = FRONTMATTER_RE.match(text)
    return text[match.end():] if match else text


def parse_chapter(path: str | os.PathLike[str]) -> tuple[dict[str, Any], str]:
    raw = Path(path).read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(raw)
    if not match:
        return {}, raw.strip()
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        meta = {}
    return (meta if isinstance(meta, dict) else {}), body_of(raw).strip()


def _nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return value is not None


def _body_evidence(value: Any, body: str, minimum: int = 3) -> bool:
    if not isinstance(value, str):
        return False
    evidence = value.strip()
    return len(evidence) >= minimum and evidence in body


def validate_chapter_contract(
    meta: dict[str, Any],
    body: str,
    manifest: dict[str, Any] | None = None,
    *,
    strict: bool | None = None,
    faction_ids: set[str] | None = None,
    decision_ids: set[str] | None = None,
    approved_decision_id: str | None = None,
) -> list[str]:
    """Validate causal evidence, independent of any model-authored booleans."""
    if manifest is None and strict is None:
        raise StoryStateError("season manifest is required for chapter contract validation")
    manifest = manifest or {}
    if strict is None:
        strict = strict_mode(manifest)
    if not strict:
        return []
    errors: list[str] = []
    min_chars = int(manifest.get("rules", {}).get("min_body_chars", DEFAULT_MIN_BODY_CHARS))
    if len(body.strip()) < min_chars:
        errors.append(f"body<{min_chars}")
    if meta.get("canonical") is not True and str(meta.get("status", "")).lower() != "canonical":
        errors.append("canonical")
    if not str(meta.get("decision_id", "")).strip():
        errors.append("decision_id")
    elif decision_ids is not None and str(meta.get("decision_id")).strip() not in decision_ids:
        errors.append("decision_id.unknown")
    if approved_decision_id is not None and str(meta.get("decision_id", "")).strip() != str(approved_decision_id).strip():
        errors.append("decision_id.not_approved")
    causal = meta.get("causal")
    if not isinstance(causal, dict):
        errors.append("causal")
    else:
        for field in REQUIRED_CONTRACT_FIELDS:
            if not _nonempty(causal.get(field)):
                errors.append(f"causal.{field}")
    evidence = str(meta.get("hook_evidence", "")).strip()
    if not evidence:
        errors.append("hook_evidence")
    elif not _body_evidence(evidence, body):
        errors.append("hook_evidence not in body")
    state_updates = meta.get("state_updates")
    faction_moves = meta.get("faction_moves")
    if not isinstance(state_updates, list) or not state_updates:
        errors.append("state_updates")
    elif any(
        not isinstance(item, dict)
        or not _nonempty(item.get("entity"))
        or not _nonempty(item.get("change"))
        or not _body_evidence(item.get("evidence"), body)
        for item in state_updates
    ):
        errors.append("state_updates.fields_or_evidence")
    if not isinstance(faction_moves, list) or not faction_moves:
        errors.append("faction_moves")
    elif any(
        not isinstance(item, dict)
        or any(not _nonempty(item.get(field)) for field in REQUIRED_FACTION_MOVE_FIELDS[:-1])
        or not _body_evidence(item.get("evidence"), body)
        or (faction_ids is not None and str(item.get("faction")).strip() not in faction_ids)
        for item in faction_moves
    ):
        errors.append("faction_moves.fields_or_evidence_or_unknown_faction")
    return list(dict.fromkeys(errors))


def validate_manifest(manifest: dict[str, Any], *, strict: bool) -> list[str]:
    """Validate the reader contract before a new season can claim strict mode."""
    if not strict:
        return []
    errors: list[str] = []
    if not isinstance(manifest.get("season"), int) or isinstance(manifest.get("season"), bool):
        errors.append("manifest.season")
    contract = manifest.get("contract")
    if not isinstance(contract, dict):
        errors.append("manifest.contract")
    else:
        for field in REQUIRED_MANIFEST_FIELDS:
            if not _nonempty(contract.get(field)):
                errors.append(f"manifest.contract.{field}")
        rewards = contract.get("reward_mix")
        if not isinstance(rewards, dict):
            errors.append("manifest.contract.reward_mix")
        else:
            for field in REQUIRED_REWARD_FIELDS:
                value = rewards.get(field)
                if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1:
                    errors.append(f"manifest.contract.reward_mix.{field}")
    rules = manifest.get("rules")
    if not isinstance(rules, dict):
        errors.append("manifest.rules")
    else:
        minimum = rules.get("min_body_chars")
        if not isinstance(minimum, int) or isinstance(minimum, bool) or minimum <= 0:
            errors.append("manifest.rules.min_body_chars")
        for field in ("require_causal_transition", "require_hook_evidence"):
            if rules.get(field) is not True:
                errors.append(f"manifest.rules.{field}")
    return errors


def validate_factions(factions: list[dict[str, Any]], *, strict: bool) -> list[str]:
    if not strict:
        return []
    errors: list[str] = []
    if not factions:
        return ["factions.yaml has no factions"]
    ids: set[str] = set()
    for index, faction in enumerate(factions):
        prefix = f"factions.yaml faction[{index}]"
        faction_id = str(faction.get("id", "")).strip()
        if not faction_id:
            errors.append(f"{prefix}.id")
        elif faction_id in ids:
            errors.append(f"{prefix}.duplicate_id")
        ids.add(faction_id)
        for field in REQUIRED_FACTION_FIELDS:
            value = faction.get(field)
            if field in {"resources", "red_lines"}:
                if not isinstance(value, list) or not value or any(not _nonempty(item) for item in value):
                    errors.append(f"{prefix}.{field}")
            elif not _nonempty(value):
                errors.append(f"{prefix}.{field}")
    return errors


def validate_plot_state(plot: dict[str, Any], *, strict: bool) -> list[str]:
    if not strict:
        return []
    errors: list[str] = []
    for field in REQUIRED_PLOT_FIELDS:
        if field not in plot:
            errors.append(f"plot_state.{field}")
    if not _nonempty(plot.get("current_pressure")):
        errors.append("plot_state.current_pressure")
    if not isinstance(plot.get("open_threads"), list) or not plot.get("open_threads"):
        errors.append("plot_state.open_threads")
    if not isinstance(plot.get("character_goals"), dict) or not plot.get("character_goals"):
        errors.append("plot_state.character_goals")
    for field in ("faction_moves", "state_updates"):
        if not isinstance(plot.get(field), list):
            errors.append(f"plot_state.{field}")
    if not isinstance(plot.get("knowledge"), dict):
        errors.append("plot_state.knowledge")
    chapter = plot.get("last_accepted_chapter")
    if not isinstance(chapter, int) or isinstance(chapter, bool) or chapter < 0:
        errors.append("plot_state.last_accepted_chapter")
    return list(dict.fromkeys(errors))


def validate_decision_options(value: dict[str, Any], *, strict: bool) -> list[str]:
    if not strict:
        return []
    errors: list[str] = []
    options = value.get("options") if isinstance(value, dict) else None
    if not isinstance(options, list) or not options:
        return ["decisions/next.json has no options"]
    if len(options) < 2:
        errors.append("decisions/next.json requires at least 2 options")
    ids: set[str] = set()
    for index, option in enumerate(options):
        prefix = f"decisions/next.json option[{index}]"
        if not isinstance(option, dict):
            errors.append(prefix)
            continue
        option_id = str(option.get("id", "")).strip()
        if not option_id:
            errors.append(f"{prefix}.id")
        elif option_id in ids:
            errors.append(f"{prefix}.duplicate_id")
        ids.add(option_id)
        for field in REQUIRED_DECISION_FIELDS:
            if not _nonempty(option.get(field)):
                errors.append(f"{prefix}.{field}")
        if (
            _nonempty(option.get("winner"))
            and _nonempty(option.get("loser"))
            and str(option.get("winner")).strip() == str(option.get("loser")).strip()
        ):
            errors.append(f"{prefix}.winner_equals_loser")
        rewards = option.get("reward_mix")
        if not isinstance(rewards, dict) or any(
            not isinstance(rewards.get(field), (int, float))
            or isinstance(rewards.get(field), bool)
            or not 0 <= rewards.get(field) <= 1
            for field in REQUIRED_REWARD_FIELDS
        ):
            errors.append(f"{prefix}.reward_mix")
    return list(dict.fromkeys(errors))


def validate_season(sdir: str | os.PathLike[str]) -> dict[str, Any]:
    """Return a machine-readable audit; non-legacy errors are publication blockers."""
    manifest = load_manifest(sdir)
    strict = strict_mode(manifest)
    errors: list[str] = []
    warnings: list[str] = []
    candidates = chapter_candidates(sdir)
    factions = load_factions(sdir)
    faction_ids = {str(item.get("id")).strip() for item in factions if str(item.get("id", "")).strip()}
    plot = load_plot_state(sdir)
    decision_options = load_decision_options(sdir)
    errors.extend(validate_manifest(manifest, strict=strict))
    errors.extend(validate_factions(factions, strict=strict))
    errors.extend(validate_plot_state(plot, strict=strict))
    errors.extend(validate_decision_options(decision_options, strict=strict))
    if strict:
        for required in ("factions.yaml", "plot_state.json", "decisions/next.json"):
            if not _path(sdir, required).is_file():
                errors.append(f"missing {required}")
    decision_ids = {
        str(item.get("id", "")).strip()
        for item in decision_options.get("options", [])
        if isinstance(item, dict) and str(item.get("id", "")).strip()
    }
    duplicates = {number: [path.name for path in paths] for number, paths in candidates.items() if len(paths) > 1}
    if duplicates:
        message = f"duplicate chapter numbers: {len(duplicates)}"
        (errors if strict else warnings).append(message)
    checked = 0
    stubs = 0
    for number, path in canonical_chapter_files(sdir):
        checked += 1
        try:
            meta, body = parse_chapter(path)
        except OSError as exc:
            errors.append(f"{path}: {exc}")
            continue
        if len(body) < int(manifest.get("rules", {}).get("min_body_chars", DEFAULT_MIN_BODY_CHARS)):
            stubs += 1
            (errors if strict else warnings).append(f"chapter {number} stub: {path.name}")
        errors.extend(
            f"chapter {number} {path.name}: {item}"
            for item in validate_chapter_contract(
                meta,
                body,
                manifest,
                strict=strict,
                faction_ids=faction_ids,
                decision_ids=decision_ids,
            )
        )
    if strict:
        last_accepted = plot.get("last_accepted_chapter")
        highest_chapter = max((number for number, _ in canonical_chapter_files(sdir)), default=0)
        if isinstance(last_accepted, int) and last_accepted != highest_chapter:
            errors.append(
                f"plot_state.last_accepted_chapter={last_accepted} does not match latest chapter={highest_chapter}"
            )
    return {
        "season": manifest.get("season"),
        "strict": strict,
        "legacy_mode": bool(manifest.get("legacy_mode", False)),
        "checked": checked,
        "duplicates": duplicates,
        "stubs": stubs,
        "errors": list(dict.fromkeys(errors)),
        "warnings": list(dict.fromkeys(warnings)),
        "ok": not errors,
    }


def prompt_context(sdir: str | os.PathLike[str]) -> str:
    """Bounded context for the model: contract, factions, goals, and state."""
    manifest = load_manifest(sdir)
    plot = load_plot_state(sdir)
    factions = load_factions(sdir)
    decision = load_approved_decision(sdir)
    parts = []
    contract = manifest.get("contract") or {}
    if contract:
        parts.append("SEASON CONTRACT:\n" + yaml.safe_dump(contract, allow_unicode=True, sort_keys=False)[:2400])
    if factions:
        parts.append("FACTION STANCES:\n" + yaml.safe_dump(factions, allow_unicode=True, sort_keys=False)[:3000])
    state = {
        "current_pressure": plot.get("current_pressure", ""),
        "open_threads": plot.get("open_threads", [])[-8:],
        "character_goals": plot.get("character_goals", {}),
        "faction_moves": plot.get("faction_moves", [])[-8:],
        "state_updates": plot.get("state_updates", [])[-8:],
        "knowledge": plot.get("knowledge", {}),
    }
    parts.append("CANONICAL PLOT STATE:\n" + yaml.safe_dump(state, allow_unicode=True, sort_keys=False)[:4200])
    if decision:
        decision_view = dict(decision)
        decision_view["rationale"] = str(decision_view.get("rationale") or "")[:500]
        parts.append("HUMAN-APPROVED DECISION:\n" + yaml.safe_dump(decision_view, allow_unicode=True, sort_keys=False)[:2400])
    return "\n\n".join(parts)


def apply_chapter_state(sdir: str | os.PathLike[str], meta: dict[str, Any], number: int) -> dict[str, Any]:
    """Advance plot_state only after the chapter has been written successfully."""
    state = load_plot_state(sdir)
    manifest = load_manifest(sdir)
    strict = strict_mode(manifest)
    current_chapter = state.get("last_accepted_chapter", 0)
    if strict:
        if not isinstance(current_chapter, int) or number != current_chapter + 1:
            raise StoryStateError(
                f"strict chapter commit must advance from {current_chapter} to {current_chapter + 1}, not {number}"
            )
        decision = load_approved_decision(sdir)
        decision_id = str(meta.get("decision_id") or "").strip()
        if (
            not decision
            or decision.get("consumed") is True
            or str(decision.get("id") or "").strip() != decision_id
            or decision.get("base_chapter") != current_chapter
        ):
            raise StoryStateError("strict chapter commit does not match the current human approval")
    causal = meta.get("causal") if isinstance(meta.get("causal"), dict) else {}
    if causal.get("next_pressure"):
        state["current_pressure"] = causal["next_pressure"]
    for field in ("open_threads", "character_goals", "knowledge"):
        if field in meta and isinstance(meta[field], (list, dict)):
            state[field] = meta[field]
    moves = meta.get("faction_moves")
    if isinstance(moves, list) and moves:
        state.setdefault("faction_moves", []).extend(moves)
        state["faction_moves"] = state["faction_moves"][-40:]
    updates = meta.get("state_updates")
    if isinstance(updates, list) and updates:
        state.setdefault("state_updates", []).extend(updates)
        state["state_updates"] = state["state_updates"][-40:]
    state["last_accepted_chapter"] = number
    state["last_transition"] = {
        "chapter": number,
        "decision_id": meta.get("decision_id"),
        "choice": causal.get("choice"),
        "cost": causal.get("cost"),
        "state_change": causal.get("state_change"),
    }
    _atomic_write(_path(sdir, "plot_state.json"), state)
    if strict:
        consumed = dict(decision)
        consumed["consumed"] = True
        consumed["consumed_chapter"] = number
        _atomic_write(approved_decision_path(sdir), consumed)
    return state


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Inspect and approve Open Souls story state")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("status", "validate"):
        item = sub.add_parser(command)
        item.add_argument("--season", required=True)
    approve = sub.add_parser("approve")
    approve.add_argument("--season", required=True)
    approve.add_argument("--id", required=True)
    approve.add_argument("--rationale", default="")
    args = parser.parse_args()
    if args.command == "status":
        manifest = load_manifest(args.season)
        result = {
            "manifest": manifest,
            "plot_state": load_plot_state(args.season),
            "approved_decision": load_approved_decision(args.season),
            "decision_required": strict_mode(manifest),
        }
    elif args.command == "validate":
        result = validate_season(args.season)
    else:
        result = approve_decision(args.season, args.id, args.rationale)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.command == "validate" and not result["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
