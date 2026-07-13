#!/usr/bin/env python3
"""
engine/_extract_ships.py

Decouple the ships field of a chapter's frontmatter into a separate
`docs/anchors/chNNN-锚点.md` file. The chapter's frontmatter ships field
is then replaced with a short pointer.

Usage:
    python engine/_extract_ships.py <chapter_file> [--write]

Without --write: dry-run, prints what would change.
With --write: rewrites the chapter's ships field as pointer and creates
              docs/anchors/chNNN-锚点.md with the detailed content.

This is the production tool that supports Task 3 of docs/TODO.md.
"""
import argparse
import os
import re
import sys

CHAPTER_DIR = r'c:\Users\stanc\github\open-souls\seasons\01-xianxia\chronicle'
ANCHOR_DIR = r'c:\Users\stanc\github\open-souls\docs\anchors'


def extract_chapter_number(filepath):
    """Extract chapter number from filename like 'ch584-叶先生的车.md'."""
    m = re.match(r'ch(\d+)-', os.path.basename(filepath))
    if m:
        return int(m.group(1))
    return None


def parse_frontmatter(content):
    """Parse YAML frontmatter."""
    if not content.startswith('---'):
        return None, content
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None, content
    fm = parts[1].strip()
    body = parts[2]
    return fm, body


def extract_ships_lines(fm):
    """Extract just the ships section from the frontmatter."""
    lines = fm.split('\n')
    in_ships = False
    ships_lines = []
    indent = ''
    for line in lines:
        if line.startswith('ships:'):
            in_ships = True
            indent = ''
            ships_lines.append(line)
            continue
        if in_ships:
            # Continue if line is part of ships block (indented)
            if line.startswith(' ') or line.startswith('\t') or not line.strip():
                if line.strip():
                    ships_lines.append(line)
                continue
            else:
                # End of ships block
                break
    return ships_lines


def extract_chapter_title(fm):
    """Get the title from frontmatter."""
    m = re.search(r'title:\s*(.+)', fm)
    if m:
        return m.group(1).strip()
    return '未命名'


def generate_anchor_doc(chapter_num, title, ships_lines):
    """Generate the anchor document content."""
    ships_content = '\n'.join(ships_lines)
    return f"""---
ch: {chapter_num}
title: {title}
status: 已落盘
---

# ch{chapter_num} · {title} · 锚点说明

> **本文件由 `engine/_extract_ships.py` 自动生成**：从 chapters/ch{chapter_num}-{title}.md 的 frontmatter ships 字段解耦出来的详细锚点说明。
> 
> **写章时 frontmatter 引用方式**：用 `ships: "见 docs/anchors/ch{chapter_num}-锚点.md"` 替代冗长内嵌文本，ships 字段 ≤ 200 字符。

---

## 一、原始 ships 字段（已落盘时的内容）

```yaml
{ships_content}
```

---

## 二、详细锚点说明（待续）

本文件由脚本自动生成，仅迁移原始 ships 字段。如需更详细的锚点说明（动作链 / 心理戏 / 位 / 远景 POV / 写章必落画面），请主编手动补完。

---

## 三、出处

本文件由 `docs/TODO.md` 任务 3 调度生成。配套基础设施：
- `docs/anchors/README.md`（索引）
- `engine/_extract_ships.py`（本脚本）
- `prompts/rewrite-one.txt` §硬门（写手读此文件）
"""


def replace_ships_with_pointer(fm, chapter_num):
    """Replace the ships block with a short pointer."""
    lines = fm.split('\n')
    new_lines = []
    in_ships = False
    for line in lines:
        if line.startswith('ships:'):
            new_lines.append(f'ships: "见 docs/anchors/ch{chapter_num}-锚点.md"')
            in_ships = True
            continue
        if in_ships:
            # Skip lines that are part of the ships block
            if line.startswith(' ') or line.startswith('\t'):
                continue
            else:
                in_ships = False
                new_lines.append(line)
        else:
            new_lines.append(line)
    return '\n'.join(new_lines)


def process_chapter(filepath, write=False):
    chapter_num = extract_chapter_number(filepath)
    if chapter_num is None:
        print(f"  ERROR: Cannot extract chapter number from {filepath}")
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    fm, body = parse_frontmatter(content)
    if fm is None:
        print(f"  ERROR: No frontmatter in {filepath}")
        return False

    title = extract_chapter_title(fm)
    ships_lines = extract_ships_lines(fm)

    if not ships_lines or len(ships_lines) <= 1:
        print(f"  SKIP: No detailed ships block in {filepath}")
        return False

    # Check if any line is > 200 chars (the "bloat" indicator)
    has_bloat = any(len(l) > 200 for l in ships_lines)

    if not has_bloat:
        print(f"  OK: ships already short in {filepath}")
        return False

    print(f"  Found bloat in ch{chapter_num} ({title}):")
    print(f"    Lines: {len(ships_lines)}, Max length: {max(len(l) for l in ships_lines)}")

    if write:
        # Generate anchor doc
        anchor_path = os.path.join(ANCHOR_DIR, f'ch{chapter_num}-锚点.md')
        anchor_content = generate_anchor_doc(chapter_num, title, ships_lines)
        with open(anchor_path, 'w', encoding='utf-8') as f:
            f.write(anchor_content)
        print(f"    Created: {anchor_path}")

        # Replace ships in frontmatter
        new_fm = replace_ships_with_pointer(fm, chapter_num)
        new_content = '---\n' + new_fm + '\n---' + body
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"    Updated: {filepath}")

    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('chapter_file', help='Chapter file path (relative or absolute)')
    parser.add_argument('--write', action='store_true', help='Actually write changes (default: dry-run)')
    args = parser.parse_args()

    filepath = args.chapter_file
    if not os.path.isabs(filepath):
        # Try relative to chapter dir
        test_path = os.path.join(CHAPTER_DIR, filepath)
        if os.path.exists(test_path):
            filepath = test_path

    if not os.path.exists(filepath):
        print(f"  ERROR: File not found: {filepath}")
        return 1

    print(f"Processing: {filepath}")
    print(f"Mode: {'WRITE' if args.write else 'DRY-RUN'}\n")

    process_chapter(filepath, write=args.write)

    return 0


if __name__ == '__main__':
    sys.exit(main())