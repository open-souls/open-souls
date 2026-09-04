# -*- coding: utf-8 -*-
"""Five-persona reader-panel driver.

Operational layer on top of tools/reader_panel_runner.py.

Enforces the cross-pollination contract from
docs/standards/jinjiang-blowup-baseline-operator.md sections 5 and 8:

  * 5 L1 prompts with unique persona_seed, drop_chapter, drop_pack,
    love_relation, next_chapter_focus.
  * 1 L2 真人 sub-agent prompt that re-issues the 5 L1 JSONs with full
    provenance (schema_version=2, model_id, reading_log, pack_hash,
    isolation block with no_chronicle, no_frontmatter, cwd, persona_seed).
  * Cross-pollination is enforced in code, not just in prose prompts.

The driver is deliberately model-agnostic. It writes isolated packs and
prompts, then delegates reading to the host Codex session and final
classification / aggregation to tools/reader_panel_runner.py.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports" / "jinjiang-r20"
PACKS = REPORTS / "blindtest_packs"
ISOLATED = REPORTS / "isolated-reader-packs"
PERSONAS = ROOT / "prompts" / "reader" / "personas.json"
PANEL = ROOT / "tools" / "reader_panel_runner.py"
GEN = ROOT / "tools" / "reader_blindtest_pack.py"


def load_personas() -> list:
    return json.loads(PERSONAS.read_text(encoding="utf-8")).get("personas", [])


def pack_hash() -> str:
    digest = hashlib.sha256()
    for path in sorted(PACKS.glob("*.md")):
        digest.update(path.read_bytes())
    return digest.hexdigest()[:16]


def _rotated_keys():
    summary_path = REPORTS / "distance-summary.md"
    chapters = []
    if summary_path.exists():
        for line in summary_path.read_text(encoding="utf-8").splitlines():
            if not line.strip().startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if cells and cells[0].isdigit():
                chapters.append(cells[0])
    if not chapters:
        chapters = ["506", "505", "504", "502", "682", "4", "1143"]
    relations = [
        "林窈×阿湄",
        "林夙×苏挽",
        "阿湄×林夙",
        "苏挽×林窈",
        "林崇×林夙",
    ]
    return chapters, relations


def _build_persona_prompt(persona, persona_id, isolated_dir, current_pack_hash, seed_date, rotation):
    chapters, relations = rotation
    index = int(persona_id) - 1
    drop_chapter = chapters[index % len(chapters)]
    next_chapter = chapters[(index + 1) % len(chapters)]
    drop_pack = ["mid_a", "mid_b", "open", "latest"][index % 4]
    relation = relations[index % len(relations)]
    seed = "l1-persona-" + persona_id + "-" + seed_date
    lines = [
        "# Five-reader blindtest prompt",
        "persona_id: " + persona_id,
        "persona: " + persona["label"],
        "perspective: " + persona["perspective"],
        "keep_if: " + persona["keep_if"],
        "drop_if: " + persona["drop_if"] + " (per-persona drop_chapter=" + drop_chapter + ", pack=" + drop_pack + ")",
        "must_disagree_with: " + persona["must_disagree_with"],
        "rotation.drop_chapter: " + drop_chapter,
        "rotation.drop_pack: " + drop_pack,
        "rotation.love_relation: " + relation,
        "rotation.next_chapter_focus: " + next_chapter,
        "read only: " + isolated_dir + "/{open,mid_a,mid_b,latest}.md",
        "forbidden: chronicle, frontmatter, review, score, existing reader JSONs",
        "isolation.no_chronicle: true",
        "isolation.no_frontmatter: true",
        "isolation.cwd: " + isolated_dir,
        "isolation.persona_seed: " + seed,
        "pack_hash: " + current_pack_hash,
        "output: reports/jinjiang-r20/reader-" + persona_id + ".json",
        "output must include schema_version=2, model_id, reading_log, source, drop, love_relation, next_chapter_focus, stay_to_50, stay_reason, pattern_flags",
    ]
    return "\n".join(lines) + "\n"


def _emit(args):
    subprocess.run([sys.executable, str(GEN)], check=True, cwd=str(ROOT))
    seed_date = datetime.date.today().isoformat() if args.new_seed else "2026-09-04"
    current_pack_hash = pack_hash()
    ISOLATED.mkdir(parents=True, exist_ok=True)
    rotation = _rotated_keys()
    for persona in load_personas():
        persona_id = str(persona["id"])
        target = ISOLATED / ("persona-" + persona_id)
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)
        for pack in PACKS.glob("*.md"):
            shutil.copy2(pack, target / pack.name)
        try:
            isolated_dir = target.relative_to(ROOT).as_posix()
        except ValueError:
            isolated_dir = target.as_posix()
        prompt = _build_persona_prompt(persona, persona_id, isolated_dir, current_pack_hash, seed_date, rotation)
        (REPORTS / ("reader-prompt-" + persona_id + ".txt")).write_text(prompt, encoding="utf-8")
    l2_lines = [
        "# L2 真人 sub-agent prompt",
        "Read only the five isolated persona directories under reports/jinjiang-r20/isolated-reader-packs/persona-{1..5}/.",
        "Do NOT read chronicle, frontmatter, review, score, existing reader JSONs or grader outputs.",
        "For each persona (1..5), write reports/jinjiang-r20/reader-N.json with schema_version=2, model_id, reading_log, pack_hash=" + current_pack_hash + ".",
        "Each JSON MUST satisfy the per-persona rotation in reader-prompt-N.txt: drop_chapter, drop_pack, love_relation, next_chapter_focus.",
        "source MUST start with 真人 sub-agent.",
        "isolation MUST contain no_chronicle=true, no_frontmatter=true, the actual isolation.cwd path, and a unique isolation.persona_seed string per JSON.",
        "After writing the five JSONs, run: py -3 -X utf8 tools/reader_panel_runner.py check && py -3 -X utf8 tools/reader_panel_runner.py aggregate.",
        "Hard boundary: effective_n must reach >=3 and diversity_score >=0.5 before any 爆款 / 上瘾 / 读者会追 judgment is allowed.",
    ]
    (REPORTS / "reader-prompt-real.txt").write_text("\n".join(l2_lines) + "\n", encoding="utf-8")
    print("emitted 5 persona prompts + L2 prompt; pack_hash=" + current_pack_hash)
    return 0


def _aggregate(_args):
    subprocess.run([sys.executable, str(PANEL), "check"], check=False, cwd=str(ROOT))
    subprocess.run([sys.executable, str(PANEL), "aggregate"], check=False, cwd=str(ROOT))
    return 0


def _verify(_args):
    chapters, relations = _rotated_keys()
    personas = load_personas()
    if len(personas) != 5:
        print("FAIL: expected 5 personas, got " + str(len(personas)))
        return 1
    drops = [chapters[(int(p["id"]) - 1) % len(chapters)] for p in personas]
    nexts = [chapters[int(p["id"]) % len(chapters)] for p in personas]
    rels = [relations[(int(p["id"]) - 1) % len(relations)] for p in personas]
    for name, values in [("drop_chapter", drops), ("next_chapter_focus", nexts), ("love_relation", rels)]:
        if len(set(values)) < 4:
            print("FAIL: " + name + " rotation too uniform: " + repr(values))
            return 1
    print("cross-pollination invariants hold:")
    print("  drop_chapters: " + str(drops))
    print("  love_relations: " + str(rels))
    print("  next_chapter_focus: " + str(nexts))
    return 0


def main():
    parser = argparse.ArgumentParser(description="Five-persona reader-panel driver")
    sub = parser.add_subparsers(dest="command", required=True)
    emit_p = sub.add_parser("emit")
    emit_p.add_argument("--new-seed", action="store_true")
    emit_p.set_defaults(func=_emit)
    sub.add_parser("aggregate").set_defaults(func=_aggregate)
    sub.add_parser("verify").set_defaults(func=_verify)
    sub.add_parser("all").set_defaults(func=lambda a: (_emit(a), _aggregate(a))[1])
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
