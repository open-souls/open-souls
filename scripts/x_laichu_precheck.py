"""X_LAI_CHU formula pre-check.

The prose_lint §七.1 第二道墙 regex (engine/prose_lint.py:X_LAI_CHU) is more
aggressive than the prose rule comment suggests. It matches any of:

    [1-4 CJK chars] 的 (来处|方式|方向|位|位是|路径|路) (不是|是他|是她|是我|是自己)

That means even "[1-4 chars]的方向不是灶" (right side is just a noun) trips
the formula — NOT only "[1-4 chars]的方向是他自己" as the comment example
implies. ch875 first draft hit 16 ERROR sites because every "亮的方向不是灶"
/ "搁的方向不是窈儿" / "坐的方向不是窈儿那一边" was caught.

Use this script as a **pre-write** check on your own draft **before** running
prose_lint. Threshold = 0 hits to PASS; >0 means you leaked the formula and
must rewrite the offending sentences with concrete actions.

The SKILL.md (P-08) carries the rewrite patterns; this script only counts.

Usage:
    python scripts/x_laichu_precheck.py path/to/draft.md
    python scripts/x_laichu_precheck.py path/to/draft.md --verbose
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Mirror engine/prose_lint.py:X_LAI_CHU exactly. If the lint regex changes,
# this script MUST be updated in lockstep — keep them as siblings.
X_LAI_CHU = re.compile(
    r"(?:[\u4e00-\u9fff]{1,4})的"
    r"(?:来处|方式|方向|位|位是|路径|路)"
    r"(?:不是|是他|是她|是我|是自己)"
)


def body_of(text: str) -> str:
    """Strip frontmatter / heading / scene-dash lines, return body only.

    Mirrors engine/prose_lint.body_of so the count matches what prose_lint sees.
    """
    text = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    m = re.match(r"^---\s*\n.*?\n---\s*\n?(.*)$", text, re.S)
    b = m.group(1) if m else text
    b = re.sub(r"^#.*$", "", b, flags=re.M)
    b = re.sub(r"^\s*\*.*?\*\s*$", "", b, flags=re.M)
    b = b.replace("---", "")
    return b


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", type=Path, help="draft .md to scan")
    ap.add_argument(
        "--verbose", "-v", action="store_true", help="print every match with context"
    )
    args = ap.parse_args()

    if not args.path.is_file():
        print(f"ERROR: file not found: {args.path}", file=sys.stderr)
        return 2

    text = args.path.read_text(encoding="utf-8")
    body = body_of(text)
    matches = list(X_LAI_CHU.finditer(body))
    count = len(matches)

    print(f"file: {args.path}")
    print(f"X_LAI_CHU hits in body: {count}")
    print(f"verdict: {'PASS' if count == 0 else 'FAIL (must rewrite)'}")

    if args.verbose and matches:
        print("\nmatches:")
        for m in matches:
            s = max(0, m.start() - 8)
            e = min(len(body), m.end() + 8)
            ctx = body[s:e].replace("\n", " ")
            print(f"  [{m.start():>5}] ...{ctx}...")

    return 0 if count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
