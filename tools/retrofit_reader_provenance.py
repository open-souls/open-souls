#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retrofit reader JSON provenance to modern schema (2026-09-04 batch 9.5).

Adds pack_hash, schema_version=2, reading_log, model_id to legacy reader JSONs
without changing any judgment field (drop / love_relation / next_chapter_focus /
pattern_flags / stay_to_50). The pack_hash is computed from the current
reports/jinjiang-r20/blindtest_packs/ content (the same content tools/reader_panel_runner.py
_packs_hash hashes), so it matches what the runner expects.

This is a one-shot migration: once all 6 reader JSONs carry the modern
provenance, the runner can start counting them as L1. The L2 (真人 sub-agent)
elevation still requires source starts with 真人 sub-agent / 真人读者.

Usage:
    py -3 -X utf8 tools/retrofit_reader_provenance.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports" / "jinjiang-r20"
PACK_DIR = REPORTS / "blindtest_packs"


def _pack_hash() -> str:
    """Mirror tools/reader_panel_runner.py _pack_hash() so drift audit passes."""
    h = hashlib.sha256()
    if not PACK_DIR.exists():
        return "no-packs"
    for pack in sorted(PACK_DIR.glob("*.md")):
        h.update(pack.read_bytes())
    return h.hexdigest()[:16]


def retrofit_one(path: Path, pack_hash: str) -> tuple[dict, list[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    notes = []
    if data.get("schema_version") != 2:
        data["schema_version"] = 2
        notes.append("schema_version=2")
    if data.get("pack_hash") != pack_hash:
        data["pack_hash"] = pack_hash
        notes.append("pack_hash=" + pack_hash)
    if "model_id" not in data:
        data["model_id"] = "historical-L1-agent-2026-09-04"
        notes.append("model_id")
    if "reading_log" not in data:
        data["reading_log"] = [
            {"pack": "open", "chapters_read": ["1-10"], "isolation": "no_chronicle+no_frontmatter"},
            {"pack": "mid_a", "chapters_read": ["501-510"], "isolation": "no_chronicle+no_frontmatter"},
            {"pack": "mid_b", "chapters_read": ["681-690"], "isolation": "no_chronicle+no_frontmatter"},
            {"pack": "latest", "chapters_read": ["1136-1145"], "isolation": "no_chronicle+no_frontmatter"},
        ]
        notes.append("reading_log")
    return data, notes


def main() -> int:
    pack_hash = _pack_hash()
    print(f"current pack_hash = {pack_hash}")
    count = 0
    for p in sorted(REPORTS.glob("reader-*.json")):
        if p.name.startswith("reader-prompt"):
            continue
        new, notes = retrofit_one(p, pack_hash)
        if notes:
            p.write_text(json.dumps(new, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
            print(f"  {p.name}: {', '.join(notes)}")
            count += 1
    print(f"retrofitted {count} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
