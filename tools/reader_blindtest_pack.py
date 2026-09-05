# -*- coding: utf-8 -*-
"""Generate blinded reader packs without changing chapter source files."""
from __future__ import annotations

import csv
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHRONICLE = ROOT / "seasons" / "01-xianxia" / "chronicle"
REPORTS = ROOT / "reports" / "jinjiang-r20"
PACK_DIR = REPORTS / "blindtest_packs"
PACKS = {
    "open": (1, 10),
    "mid_a": (501, 510),
    "mid_b": (681, 690),
    "latest": (1136, 1145),
}


def chapter_files(low: int, high: int) -> list[tuple[int, Path]]:
    selected = []
    for path in CHRONICLE.glob("*.md"):
        prefix = path.name.split("-", 1)[0]
        if prefix.isdigit() and low <= int(prefix) <= high:
            selected.append((int(prefix), path))
    return sorted(selected)


def body_without_frontmatter(path: Path) -> str:
    source = path.read_text(encoding="utf-8")
    if source.startswith("---"):
        parts = source.split("---", 2)
        return parts[-1].strip()
    return source.strip()


def main() -> None:
    PACK_DIR.mkdir(parents=True, exist_ok=True)
    index_rows = []
    randomizer = random.Random(42)
    for pack_name, (low, high) in PACKS.items():
        entries = chapter_files(low, high)
        randomizer.shuffle(entries)
        pack_path = PACK_DIR / f"{pack_name}.md"
        with pack_path.open("w", encoding="utf-8") as handle:
            handle.write(f"# 盲读包 {pack_name}（第 {low} 至 {high} 回，随机化）\n\n")
            handle.write("只读正文。读者不看章节标签、frontmatter、review 或工程分。\n\n")
            for chapter_number, chapter_path in entries:
                handle.write(f"## {chapter_number}\n\n")
                handle.write(body_without_frontmatter(chapter_path) + "\n\n---\n\n")
                index_rows.append({
                    "pack": pack_name,
                    "chapter": chapter_number,
                    "source": str(chapter_path.relative_to(ROOT)),
                })
    index_path = REPORTS / "blindtest-index.csv"
    with index_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["pack", "chapter", "source"])
        writer.writeheader()
        writer.writerows(index_rows)
    print({"packs": list(PACKS), "index": str(index_path.relative_to(ROOT))})


if __name__ == "__main__":
    main()
