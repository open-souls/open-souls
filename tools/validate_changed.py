# -*- coding: utf-8 -*-
"""Run publication gates only for files changed in a Git push.

The repository-wide prose lint remains available through the full audit path.
This command is the fast, evidence-preserving gate for ordinary chapter work:
changed chapters still run prose, safety, and strict editorial checks; a full
scan is required explicitly when lint rules or shared schemas change.

Examples::

    python tools/validate_changed.py --base origin/main --head HEAD
    python tools/validate_changed.py --paths seasons/01-xianxia/chronicle/040-另一封.md
    OPEN_SOULS_FULL_PUSH=1 python tools/validate_changed.py --base origin/main --head HEAD
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


ROOT = Path(__file__).resolve().parent.parent
CHAPTER_PREFIX = "seasons/"
SHARED_GATE_FILES = {
    "config.yaml",
    "engine/prose_lint.py",
    "engine/safety_lint.py",
    "tools/review_batch.py",
    "engine/village.py",
}


def _run(command: list[str]) -> int:
    print("$ " + " ".join(command))
    completed = subprocess.run(command, cwd=ROOT, check=False)
    return completed.returncode


def _changed_paths(base: str, head: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMRTUXB", base, head, "--"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode:
        print(result.stderr.strip() or "git diff failed", file=sys.stderr)
        return []
    return sorted({line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()})


def _normalise_paths(paths: list[str]) -> list[str]:
    output = []
    for value in paths:
        path = Path(value)
        if not path.is_absolute():
            path = ROOT / path
        try:
            relative = path.resolve().relative_to(ROOT.resolve()).as_posix()
        except ValueError:
            continue
        output.append(relative)
    return sorted(set(output))


def _chapter_paths(paths: list[str]) -> list[str]:
    return [
        path for path in paths
        if path.startswith(CHAPTER_PREFIX)
        and "/chronicle/" in path
        and path.lower().endswith(".md")
        and Path(ROOT / path).is_file()
    ]


def validate(paths: list[str], *, force_full: bool = False) -> int:
    paths = _normalise_paths(paths)
    if force_full or os.environ.get("OPEN_SOULS_FULL_PUSH") == "1":
        print("Full publication audit requested.")
        for command in (
            [sys.executable, "engine/validate.py"],
            [sys.executable, "engine/prose_lint.py"],
        ):
            if _run(command):
                return 1
        return 0

    if any(path in SHARED_GATE_FILES for path in paths):
        print("Shared gate code changed; run the full audit explicitly.", file=sys.stderr)
        print("Set OPEN_SOULS_FULL_PUSH=1 or pass --full.", file=sys.stderr)
        return 2

    chapters = _chapter_paths(paths)
    if chapters:
        print(f"Changed-chapter publication gate: {len(chapters)} file(s)")
        for chapter in chapters:
            absolute = str(ROOT / chapter)
            for command in (
                [sys.executable, "engine/prose_lint.py", absolute],
                [sys.executable, "engine/safety_lint.py", absolute],
                [sys.executable, "tools/review_batch.py", "--strict-editorial", "--file", absolute],
            ):
                if _run(command):
                    return 1
    else:
        print("No chapter files changed; chapter publication gates skipped.")

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="Git base ref")
    parser.add_argument("--head", default="HEAD", help="Git head ref")
    parser.add_argument("--paths", nargs="*", help="Explicit changed paths")
    parser.add_argument("--full", action="store_true", help="Run the full audit")
    args = parser.parse_args(argv)
    if args.paths is not None:
        paths = args.paths
    elif args.base:
        paths = _changed_paths(args.base, args.head)
    else:
        parser.error("provide --base/--head or --paths")
    return validate(paths, force_full=args.full)


if __name__ == "__main__":
    raise SystemExit(main())
