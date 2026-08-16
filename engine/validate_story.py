"""CLI for the deterministic Open Souls season audit."""

from __future__ import annotations

import argparse
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

sys.path.insert(0, os.path.dirname(__file__))
import story_state


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a season's canonical story state")
    parser.add_argument("--season", default=None, help="season directory; defaults to the active season")
    args = parser.parse_args()
    sdir = args.season
    if not sdir:
        import season

        sdir = season.current_dir()
    if not sdir:
        print(json.dumps({"ok": False, "errors": ["no season directory"]}, ensure_ascii=False, indent=2))
        return 1
    result = story_state.validate_season(sdir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
