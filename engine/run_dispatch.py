# -*- coding: utf-8 -*-
"""Run bounded Claude Code chapter jobs and independently verify the files.

This is deliberately a thin outer loop: Claude writes one target chapter, while
the local gates decide whether the result is publishable.  A Claude summary can
never turn a failed lint or editorial review into PASS.

Usage:
  python engine/run_dispatch.py --chapters ch897 --dry-run
  python engine/run_dispatch.py --workers 2 --max-budget-usd 12.0 --effort high
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine import batch_rewrite as BR  # noqa: E402
from engine import prose_lint as PL  # noqa: E402
from engine import season as SE  # noqa: E402
from engine import story_state as SS  # noqa: E402


DISPATCH_DIR = ROOT / "prompts" / "dispatch"
RESULTS_DIR = ROOT / "prompts" / ".results"
DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_BUDGET = 12.0
DEFAULT_WORKERS = 2
# A generation that needs longer than seven minutes is usually looping over
# context or repeatedly reopening the target. The outer validator must regain
# control before a bounded job can consume its entire budget on rereads.
DEFAULT_TIMEOUT = 420
FORMULA_PATTERNS = (
    "方向朝着",
    "方向朝向",
    "方向落在",
    "方向落下",
    "方向不必替",
    "不必替上一世",
    "不必替前世",
    "不必替谁",
    "他自己守",
    "她自己守",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _protected_paths(chapter, target: Path, prompt_path: Path):
    """List files Claude is not allowed to mutate for this one job.

    The target chapter is intentionally included so the caller can exempt it
    from the diff. We also watch the job's prompt/receipt, root-level files,
    and agent/tool/test code. Watching only the target is not enough: a model
    can otherwise manufacture a convincing receipt or leave a sidecar draft.
    """
    paths = {target.resolve(), prompt_path.resolve()}
    paths.add((RESULTS_DIR / f"ch{chapter:03d}.md").resolve())
    # Claude may leave an alternate draft beside the target (for example
    # ``ch537-new.md``).  Snapshot the target directory so a newly created
    # sibling is reported as a side effect instead of silently surviving the
    # job.  This stays scoped to one chapter directory rather than hashing the
    # whole chronicle tree for every worker.
    if target.parent.exists():
        paths.update(path.resolve() for path in target.parent.iterdir() if path.is_file())
    for path in ROOT.iterdir():
        if path.is_file():
            paths.add(path.resolve())
    for dirname in ("engine", "tools", "tests"):
        directory = ROOT / dirname
        if directory.exists():
            paths.update(path.resolve() for path in directory.rglob("*") if path.is_file())
    return paths


def _snapshot_protected(chapter, target: Path, prompt_path: Path):
    snapshot = {}
    for path in _protected_paths(chapter, target, prompt_path):
        snapshot[str(path)] = _sha256(path) if path.exists() else None
    return snapshot


def _protected_changes(before, chapter, target: Path, prompt_path: Path, allowed_paths=None):
    after = _snapshot_protected(chapter, target, prompt_path)
    allowed = {str(target.resolve())}
    for path in allowed_paths or ():
        allowed.add(str(Path(path).resolve()))
    changed = []
    for path in sorted(set(before) | set(after)):
        if path in allowed:
            continue
        if before.get(path) != after.get(path):
            changed.append(path)
    return changed


def _chapter_from_prompt(path: Path) -> int | None:
    match = re.fullmatch(r"ch(\d+)\.txt", path.name, re.I)
    return int(match.group(1)) if match else None


def _target_from_prompt(path: Path):
    """Read the exact target marker emitted by batch_rewrite.

    The chapter number is not a sufficient selector when a canonical file and
    an unhealthy same-number branch coexist.  Older prompts have no marker and
    intentionally fall back to the legacy chapter resolver.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None
    match = re.search(r"^TARGET_FILE:\s*(.+?)\s*$", text, re.M)
    if not match:
        return None
    candidate = Path(match.group(1).strip().strip("`"))
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    try:
        candidate = candidate.resolve()
        candidate.relative_to(Path(BR.CHRONICLE).resolve())
    except (OSError, ValueError):
        return None
    return str(candidate) if candidate.is_file() else None


def _target_for_prompt(path: Path, chapter: int | None = None):
    """Resolve a prompt to its exact file, with a safe legacy fallback."""
    return _target_from_prompt(path) or (
        BR._chapter_file(chapter) if chapter is not None else None
    )


def _prompt_paths(chapters=None):
    paths = sorted(DISPATCH_DIR.glob("ch*.txt"))
    if chapters is None:
        return paths
    wanted = set(chapters)
    return [path for path in paths if _chapter_from_prompt(path) in wanted]


def _terminate_process_tree(process):
    """Terminate a bounded child and any wrapper it spawned.

    On Windows, invoking ``claude.cmd`` creates a command-wrapper process and
    the actual Claude/Node child can survive ``Popen.kill()``.  That was the
    source of orphan Claude jobs after a timeout.  ``taskkill /T`` is scoped to
    this Popen PID, so it cannot touch unrelated long-running Claude sessions.
    """
    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
                check=False,
            )
            return
        except (OSError, subprocess.TimeoutExpired):
            pass
    try:
        process.kill()
    except OSError:
        pass


def _run_process(command, *, input_text=None, timeout=DEFAULT_TIMEOUT):
    creationflags = 0
    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    try:
        process = subprocess.Popen(
            command,
            cwd=str(ROOT),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=creationflags,
        )
        try:
            stdout, stderr = process.communicate(input=input_text, timeout=timeout)
            return {
                "returncode": process.returncode,
                "stdout": stdout or "",
                "stderr": stderr or "",
                "timed_out": False,
            }
        except subprocess.TimeoutExpired as exc:
            _terminate_process_tree(process)
            try:
                stdout, stderr = process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                # A wrapper that ignores termination must not hold the outer
                # batch open indefinitely.  This is a last-resort local kill.
                try:
                    process.kill()
                except OSError:
                    pass
                stdout, stderr = process.communicate()

            def _text(value):
                if isinstance(value, bytes):
                    return value.decode("utf-8", errors="replace")
                return value or ""

            return {
                "returncode": 124,
                "stdout": _text(stdout) or _text(exc.stdout),
                "stderr": "timeout; process tree terminated\n" + _text(stderr),
                "timed_out": True,
            }
    except OSError as exc:
        return {"returncode": 127, "stdout": "", "stderr": str(exc), "timed_out": False}


def _claude(prompt, *, budget, model, effort, timeout, claude_cmd):
    command = [
        claude_cmd,
        "-p",
        "--bare",
        "--no-session-persistence",
        "--model",
        model,
        "--max-budget-usd",
        str(budget),
        "--effort",
        effort,
        "--allowed-tools",
        "Read,Edit",
        "--permission-mode",
        "acceptEdits",
        "--output-format",
        "json",
    ]
    raw = _run_process(command, input_text=prompt, timeout=timeout)
    payload = None
    try:
        payload = json.loads(raw["stdout"].strip())
    except (TypeError, json.JSONDecodeError):
        pass
    success = (
        raw["returncode"] == 0
        and isinstance(payload, dict)
        and payload.get("is_error") is not True
        and payload.get("subtype") not in {"error_max_budget_usd", "error"}
    )
    return {
        "ok": success,
        "returncode": raw["returncode"],
        "payload": payload,
        "stdout_tail": raw["stdout"][-2000:],
        "stderr_tail": raw["stderr"][-1000:],
        "timed_out": raw["timed_out"],
    }


def _gate(command, *, timeout):
    result = _run_process(command, timeout=timeout)
    return {
        "ok": result["returncode"] == 0 and not result["timed_out"],
        "returncode": result["returncode"],
        "output": (result["stdout"] + result["stderr"])[-2500:],
        "timed_out": result["timed_out"],
    }


def _formula_hits(target: Path):
    body = PL.body_of(target.read_text(encoding="utf-8"))
    hits = {pattern: body.count(pattern) for pattern in FORMULA_PATTERNS if pattern in body}
    metrics = PL.measure(body)
    if metrics.get("wall_formula", 0) >= PL.WALL_FORMULA_ERROR:
        hits["wall_formula"] = metrics["wall_formula"]
    hits.update(PL.machine_echo_hits(body))
    return hits


def _write_result(chapter, target, result):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    claude_payload = result["claude"].get("payload") or {}
    claude_note = claude_payload.get("result") if isinstance(claude_payload, dict) else ""
    if not isinstance(claude_note, str):
        claude_note = json.dumps(claude_note, ensure_ascii=False)
    lines = [
        f"status: {'PASS' if result['pass'] else 'BLOCKED'}",
        f"chapter: {chapter}",
        f"target: {target}",
        f"claude: {'ok' if result['claude']['ok'] else 'fail'}",
        f"changed: {'yes' if result['changed'] else 'no'}",
        f"lint: {'ok' if result['lint']['ok'] else 'fail'}",
        f"strict_editorial: {'ok' if result['strict']['ok'] else 'fail'}",
        f"formula_scan: {'ok' if not result['formula_hits'] else 'fail'}",
        f"elapsed_seconds: {result['elapsed_seconds']:.1f}",
        "claude_subtype: " + str((claude_payload or {}).get("subtype", "")),
        "claude_stop_reason: " + str((claude_payload or {}).get("stop_reason", "")),
        "claude_cost_usd: " + str((claude_payload or {}).get("total_cost_usd", "")),
        "claude_errors: " + json.dumps((claude_payload or {}).get("errors", []), ensure_ascii=False),
        "formula_hits: " + (json.dumps(result["formula_hits"], ensure_ascii=False) if result["formula_hits"] else "{}"),
        "side_effects: " + (json.dumps(result.get("side_effects", []), ensure_ascii=False) if result.get("side_effects") else "[]"),
        "note: " + " ".join(claude_note.strip().split())[:1200],
    ]
    (RESULTS_DIR / f"ch{chapter:03d}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_one(prompt_path: Path, *, budget=DEFAULT_BUDGET, model=DEFAULT_MODEL,
            effort="medium", timeout=DEFAULT_TIMEOUT, claude_cmd="claude.cmd",
            allowed_targets=None):
    chapter = _chapter_from_prompt(prompt_path)
    if chapter is None:
        raise ValueError(f"invalid dispatch prompt name: {prompt_path.name}")
    target_value = _target_for_prompt(prompt_path, chapter)
    if not target_value:
        target = ROOT / "__missing_target__"
        result = {
            "pass": False,
            "chapter": chapter,
            "target": str(target),
            "changed": False,
            "claude": {"ok": False, "payload": None},
            "lint": {"ok": False, "returncode": 2, "output": "missing target"},
            "strict": {"ok": False, "returncode": 2, "output": "missing target"},
            "formula_hits": {},
            "side_effects": [],
            "elapsed_seconds": 0.0,
        }
        _write_result(chapter, target, result)
        return result

    target = Path(target_value)
    before = _sha256(target) if target.exists() else ""
    protected_before = _snapshot_protected(chapter, target, prompt_path)
    started = time.monotonic()
    prompt = prompt_path.read_text(encoding="utf-8")
    claude_result = _claude(
        prompt,
        budget=budget,
        model=model,
        effort=effort,
        timeout=timeout,
        claude_cmd=claude_cmd,
    )
    after = _sha256(target) if target.exists() else ""
    changed = bool(before and after and before != after)
    side_effects = _protected_changes(
        protected_before,
        chapter,
        target,
        prompt_path,
        allowed_paths=allowed_targets,
    )
    lint = _gate(
        [sys.executable, "engine/prose_lint.py", str(target)], timeout=timeout
    ) if target.exists() else {"ok": False, "returncode": 2, "output": "missing target"}
    strict = _gate(
        [
            sys.executable,
            "tools/review_batch.py",
            "--strict-editorial",
            "--file",
            str(target),
        ],
        timeout=timeout,
    ) if target.exists() else {"ok": False, "returncode": 2, "output": "missing target"}
    formula_hits = _formula_hits(target) if target.exists() else {"target": 1}
    result = {
        "pass": bool(
            claude_result["ok"]
            and changed
            and lint["ok"]
            and strict["ok"]
            and not formula_hits
            and not side_effects
        ),
        "chapter": chapter,
        "target": str(target),
        "changed": changed,
        "claude": claude_result,
        "lint": lint,
        "strict": strict,
        "formula_hits": formula_hits,
        "side_effects": side_effects,
        "elapsed_seconds": time.monotonic() - started,
    }
    _write_result(chapter, target, result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chapters", help="Only dispatch ch numbers, e.g. ch897,ch900-902")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--max-budget-usd", type=float, default=DEFAULT_BUDGET)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--effort", choices=("low", "medium", "high", "xhigh", "max"), default="medium")
    parser.add_argument("--timeout-sec", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--claude-cmd", default=os.environ.get("CLAUDE_CMD", "claude.cmd"))
    parser.add_argument("--force", action="store_true", help="Dispatch chapters that already pass local gates")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    active_season = SE.current_dir()
    if active_season and SS.strict_mode(SS.load_manifest(active_season)):
        print(
            "BLOCKED: engine/run_dispatch.py is the legacy prose-rewrite path and "
            "does not atomically consume a human decision or advance plot state. "
            "Use engine/village.py for a strict season."
        )
        return 2

    chapters = BR.parse_chapter_spec(args.chapters) if args.chapters else None
    paths = _prompt_paths(chapters)
    selected = []
    skipped = []
    for path in paths:
        chapter = _chapter_from_prompt(path)
        if chapter is None:
            continue
        target_value = _target_for_prompt(path, chapter)
        if not args.force and BR._already_done(chapter, target_file=target_value):
            skipped.append(chapter)
            continue
        selected.append(path)

    print(f"dispatch_targets={len(selected)} skipped_done={len(skipped)} workers={max(1, args.workers)}")
    for path in selected:
        print(f"  ch{_chapter_from_prompt(path):03d} <- {path}")
    if args.dry_run or not selected:
        return 0

    allowed_targets = set()
    for path in selected:
        chapter = _chapter_from_prompt(path)
        target_value = _target_for_prompt(path, chapter)
        if target_value:
            allowed_targets.add(str(Path(target_value).resolve()))

    outcomes = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {
            pool.submit(
                run_one,
                path,
                budget=args.max_budget_usd,
                model=args.model,
                effort=args.effort,
                timeout=args.timeout_sec,
                claude_cmd=args.claude_cmd,
                allowed_targets=allowed_targets,
            ): path
            for path in selected
        }
        for future in concurrent.futures.as_completed(futures):
            path = futures[future]
            try:
                result = future.result()
            except Exception as exc:  # keep the batch moving; the result is blocked
                result = {
                    "pass": False,
                    "chapter": _chapter_from_prompt(path),
                    "target": str(path),
                    "changed": False,
                    "claude": {"ok": False, "payload": None, "stderr_tail": str(exc)},
                    "lint": {"ok": False},
                    "strict": {"ok": False},
                    "formula_hits": {},
                    "side_effects": [],
                    "elapsed_seconds": 0.0,
                }
                _write_result(result["chapter"], Path(result["target"]), result)
            outcomes.append(result)
            state = "PASS" if result["pass"] else "BLOCKED"
            print(f"ch{result['chapter']:03d}: {state}")

    return 0 if all(item["pass"] for item in outcomes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
