# -*- coding: utf-8 -*-
"""P0+ P1 apply 阶段：执行计划。

P0:
  1. 把 _STUB_MANIFEST.json 里 599 个 chapter_numbers 转成对应文件名清单(如果存在)，
     并补加 78 个单文件短章的文件名，使 lint 自动豁免。
  2. 把 194 个多余 stub 文件移到 _stub_archive/，并把它们加入 manifest 的 files 列表。

P1:
  把 line: 男频 / line: 混合 全部刷为 line: 古言仙侠。

执行完跑 prose_lint.py 验证。
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


def chapter_num_from_filename(name):
    m = re.match(r"^(?:ch)?(\d+)-", name)
    return int(m.group(1)) if m else None


def main():
    plan = json.loads((ROOT / "prompts" / ".notes" / "_p0_p1_plan.json").read_text(encoding="utf-8"))
    to_archive = plan["archive"]
    to_retag = plan["retag"]

    manifest = json.loads(STUB_MANIFEST.read_text(encoding="utf-8"))
    chapter_numbers_set = set(manifest.get("chapter_numbers", []))
    files_set = set(manifest.get("files", []))

    all_files = []
    for p in sorted(CHRON.glob("*.md")):
        if p.name in ALWAYS_KEEP or p.name.startswith("test_"):
            continue
        all_files.append(p.name)

    for fname in all_files:
        cnum = chapter_num_from_filename(fname)
        if cnum is not None and cnum in chapter_numbers_set:
            files_set.add(fname)

    per_chap = defaultdict(list)
    for fname in all_files:
        cnum = chapter_num_from_filename(fname)
        if cnum is not None:
            per_chap[cnum].append(fname)
    for cnum, fs in per_chap.items():
        if len(fs) == 1:
            f = fs[0]
            text = (CHRON / f).read_text(encoding="utf-8")
            m2 = re.match(r"^---\n.*?\n---\n", text, re.DOTALL)
            body = text[m2.end():] if m2 else text
            body = re.sub(r"^#[^\n]*\n", "", body, count=1).strip()
            if len(body) < 1500:
                files_set.add(f)

    for fname in to_archive:
        files_set.add(fname)
    manifest["files"] = sorted(files_set)
    manifest["chapter_numbers"] = sorted(chapter_numbers_set)
    manifest["rule"] = (manifest.get("rule", "") + " | filenames added 2026-09-04").strip()

    ARCHIVE.mkdir(exist_ok=True)
    moved = 0
    for fname in to_archive:
        src = CHRON / fname
        if not src.exists():
            continue
        dst = ARCHIVE / fname
        shutil.move(str(src), str(dst))
        moved += 1

    STUB_MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("P0 done: archived", moved, "stubs to", ARCHIVE, ", manifest files=", len(files_set))

    n_retag = 0
    for fname in to_retag:
        p = CHRON / fname
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        new = text
        new = new.replace("line: 男频", "line: 古言仙侠")
        new = new.replace("line: 混合", "line: 古言仙侠")
        if new != text:
            p.write_text(new, encoding="utf-8")
            n_retag += 1
    print("P1 done: retagged", n_retag, "line fields")


if __name__ == "__main__":
    main()
