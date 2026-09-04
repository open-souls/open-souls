# -*- coding: utf-8 -*-
"""Delete isolated filler sentences flagged by chapter_by_chapter_audit.

A line is "isolated filler" iff it:

  * matches one of the known atmosphere-only patterns; AND
  * is shorter than 25 characters; AND
  * is the ONLY content line in its paragraph (surrounded by blank lines).

This is deliberately conservative: it never edits lines that carry a
sensory anchor (e.g. "屋外很静, 但屋里风灯在抖"). Run only after
manually sampling a few chapters to confirm the pattern.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path("seasons/01-xianxia/chronicle")

# Strict atmosphere-only patterns. Multi-word verbs/clauses (e.g. "夜更深时")
# are NOT matched here; those still carry a time cue and need human review.
PATTERNS = (
    re.compile(r"^屋里又?安静(?:下来|了一阵|了)?[。\.．]?$"),
    re.compile(r"^院里又?安静(?:下来|了一阵|了)?[。\.．]?$"),
    re.compile(r"^门[外里]?重新?安静下来[。\.．]?$"),
    re.compile(r"^屋里(?:一下|忽然)?安静[。\.．]?$"),
    re.compile(r"^外头夜渐深[。\.．]?$"),
    re.compile(r"^外[出门]夜渐深[。\.．]?$"),
    re.compile(r"^[屋内院里]很静[。\.．]?$"),
    re.compile(r"^夜[，,]\s*深了[。\.．]?$"),
    re.compile(r"^夜[，,]\s*宗门[，,].*$"),  # protect chapter-opening time stamp
)


def is_isolated_filler(line: str) -> bool:
    s = line.strip()
    if not s or len(s) > 25:
        return False
    if "夜，宗门" in s:
        return False  # protect chapter-opening time stamp
    return any(p.match(s) for p in PATTERNS)


def delete_in_file(path: Path, dry_run: bool) -> int:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        return 0
    head, body = parts[0] + "---\n" + parts[1] + "---\n", parts[2]
    lines = body.split("\n")
    out = []
    deleted = 0
    for i, ln in enumerate(lines):
        prev_blank = i == 0 or not lines[i - 1].strip()
        next_blank = i == len(lines) - 1 or not lines[i + 1].strip()
        if is_isolated_filler(ln) and prev_blank and next_blank:
            deleted += 1
            continue
        out.append(ln)
    if deleted == 0:
        return 0
    new_body = "\n".join(out)
    new_text = head + new_body
    if not dry_run:
        path.write_text(new_text, encoding="utf-8")
    return deleted


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--chapters", nargs="*", type=int, help="specific chapter numbers; default = all flagged in audit")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--all", action="store_true", help="scan every chapter; default = audit-flagged only")
    args = parser.parse_args()

    total = 0
    if args.chapters:
        targets = []
        for ch in args.chapters:
            targets.extend(sorted(ROOT.glob(f"{ch:03d}-*.md")))
            targets.extend(sorted(ROOT.glob(f"{ch}-*.md")))
    elif args.all:
        targets = sorted(ROOT.glob("*.md"))
    else:
        import json
        data = json.loads(Path("reports/jinjiang-r20/chapter-by-chapter-audit.json").read_text(encoding="utf-8"))
        targets = [ROOT / Path(r["file"]).name for r in data["chapters"] if "填充描写" in r["issue_tags"]]

    for path in targets:
        n = delete_in_file(path, args.dry_run)
        if n:
            verb = "would delete" if args.dry_run else "deleted"
            print(f"{verb} {n} line(s) in {path.name}")
            total += n
    print(f"total {total} line(s) {'flagged' if args.dry_run else 'deleted'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
