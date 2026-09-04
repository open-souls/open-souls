# -*- coding: utf-8 -*-
"""P0 stub 归档 + P1 line 标签重打 · plan 阶段。

只读 scan 后给出执行计划；不在 plan 阶段改任何文件。
执行阶段另外跑（见 prompts/.notes/_apply_p0_p1.py）。
"""
from __future__ import annotations
import os, re, json, shutil, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHRON = ROOT / "seasons" / "01-xianxia" / "chronicle"
ARCHIVE = CHRON / "_stub_archive"
STUB_MANIFEST = CHRON / "_STUB_MANIFEST.json"

ALWAYS_KEEP = {"_STUB_MANIFEST.json", "INDEX.md", "test_write.md"}


def scan():
    files = []
    for p in sorted(CHRON.glob("*.md")):
        if p.name in ALWAYS_KEEP:
            continue
        if p.name.startswith("test_"):
            continue
        text = p.read_text(encoding="utf-8")
        m = re.match(r"^---\n.*?\n---\n", text, re.DOTALL)
        body = text[m.end():] if m else text
        body = re.sub(r"^#[^\n]*\n", "", body, count=1).strip()
        files.append({"path": p, "name": p.name, "body_chars": len(body), "text": text})
    return files


def plan_stub_archive(files):
    per_chap = defaultdict(list)
    for f in files:
        m = re.match(r"^(?:ch)?(\d+)-", f["name"])
        if m:
            per_chap[int(m.group(1))].append(f)
        else:
            per_chap[0].append(f)
    to_archive = []
    for cnum, fs in per_chap.items():
        if len(fs) <= 1:
            continue
        fs_sorted = sorted(fs, key=lambda f: -f["body_chars"])
        for f in fs_sorted[1:]:
            if f["body_chars"] < 1500:
                to_archive.append(f)
    return to_archive


def plan_line_retag(files):
    to_retag = []
    for f in files:
        if "line: 男频" in f["text"] or "line: 混合" in f["text"]:
            to_retag.append(f)
    return to_retag


def main():
    files = scan()
    print("scan files:", len(files), file=sys.stderr)

    to_archive = plan_stub_archive(files)
    to_retag = plan_line_retag(files)

    print()
    print("P0 plan: archive", len(to_archive), "stubs to", ARCHIVE)
    for f in to_archive[:8]:
        print("  ", f["name"], "body_chars=", f["body_chars"])
    if len(to_archive) > 8:
        print("  ... and", len(to_archive) - 8, "more")

    print()
    print("P1 plan: retag", len(to_retag), "line fields")
    line_counts = defaultdict(int)
    for f in to_retag:
        if "line: 男频" in f["text"]:
            line_counts["nanpin"] += 1
        if "line: 混合" in f["text"]:
            line_counts["hunhe"] += 1
    print("  distribution:", dict(line_counts))

    out = {
        "archive": [f["name"] for f in to_archive],
        "retag": [f["name"] for f in to_retag],
    }
    (ROOT / "prompts" / ".notes" / "_p0_p1_plan.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print()
    print("plan written to prompts/.notes/_p0_p1_plan.json")


if __name__ == "__main__":
    main()
