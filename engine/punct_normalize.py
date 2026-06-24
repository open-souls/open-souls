# -*- coding: utf-8 -*-
"""把 chronicle/*.md 正文里的半角标点改全角。

JJWXC 标准：中文正文里所有标点都应是全角。`,`→`，`、`?`→`？`、`!`→`！`、
`(`→`（`、`)`→`）`、`:`→`：`(行内)、`;`→`；`、ASCII `"`/`'` → 中文「」/''成对、
`...`→`……`、文字之间的 `--` → `——`。

跳过：
  - frontmatter (---...--- YAML 块，里面的半角符号是 YAML 语法)
  - 单独成行的 `---` (Markdown 分场线)
  - 标题行（如果里面有半角标点也保留为 YAML-like 安全）

Usage:
    python engine/punct_normalize.py                 # 改全部
    python engine/punct_normalize.py path/to/ch.md   # 只改指定文件
    python engine/punct_normalize.py --dry-run       # 只列改了什么
"""
import os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 半角 → 全角（顺序敏感：长的先）
SIMPLE_MAP = [
    ("...", "……"),
    (",", "，"),
    (";", "；"),
    (":", "："),
    ("!", "！"),
    ("?", "？"),
    ("(", "（"),
    (")", "）"),
]

# 行内 `--` → `——`（但跳过单独成行的 `---`）
LINE_BREAK = re.compile(r"(?m)^[ \t]*---[ \t]*$")  # 单独成行的 ---
INLINE_DOUBLE_DASH = re.compile(r"(?<![—])(--)(?![—])")  # 行内 `--`，前后无 `—`


def normalize_body(body):
    """body 已经是去掉了 frontmatter 的纯正文。"""
    # 1. 把单独成行的 `---` 替换成占位符（避免被 `--` 转换误伤），最后再换回
    placeholders = []
    def stash(m):
        placeholders.append(m.group(0))
        return f"\x00LINBREAK{len(placeholders)-1}\x00"
    body = LINE_BREAK.sub(stash, body)

    # 2. 行内 `--` → `——`（先做，避免被后面的步骤拆开）
    body = INLINE_DOUBLE_DASH.sub("——", body)

    # 3. 简单半角 → 全角
    for src, dst in SIMPLE_MAP:
        body = body.replace(src, dst)

    # 4. ASCII `"` 成对 → `「」`。按行处理——每行内独立配对。
    new_lines = []
    for line in body.split("\n"):
        if '"' in line:
            parts = line.split('"')
            # 奇数索引是引号外（保留），偶数索引是引号内（也保留）
            # 重新组装：引号位置 1,3,5... 替换为 「 」 「 」...
            rebuilt = parts[0]
            for i, seg in enumerate(parts[1:], start=1):
                if i % 2 == 1:
                    rebuilt += "「" + seg
                else:
                    rebuilt += "」" + seg
            new_lines.append(rebuilt)
        else:
            new_lines.append(line)
    body = "\n".join(new_lines)

    # 5. ASCII `'` → 中文 `''` 成对。每行独立成对；跳过明显是英文缩写的撇号
    #    (前后都是 ASCII 字母，如 don't / it's / 林's 这种)。
    new_lines = []
    for line in body.split("\n"):
        if "'" not in line:
            new_lines.append(line); continue
        out = []
        in_quote = False
        for i, ch in enumerate(line):
            if ch != "'":
                out.append(ch); continue
            # 检查前后字符：判定是不是英文缩写撇号
            prev_ch = line[i-1] if i > 0 else ""
            next_ch = line[i+1] if i+1 < len(line) else ""
            prev_is_ascii_alpha = prev_ch.isascii() and prev_ch.isalpha()
            next_is_ascii_alpha = next_ch.isascii() and next_ch.isalpha()
            # 是英文缩写（前后都是 ASCII 字母）→ 保留
            if prev_is_ascii_alpha or next_is_ascii_alpha:
                out.append("'")
                continue
            # 当成中文引号成对翻
            out.append("‘" if not in_quote else "’")
            in_quote = not in_quote
        new_lines.append("".join(out))
    body = "\n".join(new_lines)

    # 6. 还原占位符
    for i, orig in enumerate(placeholders):
        body = body.replace(f"\x00LINBREAK{i}\x00", orig)

    return body


FM_RE = re.compile(r"^---\s*\n.*?\n---\s*\n?", re.S)


def normalize_file(path, dry_run=False):
    text = open(path, encoding="utf-8").read()
    m = FM_RE.match(text)
    if m:
        fm = m.group(0)
        body = text[m.end():]
    else:
        fm = ""
        body = text

    new_body = normalize_body(body)
    new_text = fm + new_body

    if new_text == text:
        return 0
    if not dry_run:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_text)

    # 统计 diff 字符数
    return sum(1 for a, b in zip(text, new_text) if a != b) + abs(len(new_text) - len(text))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    dry_run = "--dry-run" in sys.argv
    targets = args or sorted(glob.glob(
        os.path.join(ROOT, "seasons", "*", "chronicle", "[0-9]*.md")))
    total = 0
    n_changed = 0
    for p in targets:
        diff = normalize_file(p, dry_run=dry_run)
        if diff:
            n_changed += 1
            total += diff
            rel = os.path.relpath(p, ROOT)
            mode = "[dry]" if dry_run else "[fixed]"
            print(f"  {mode} {rel}  ({diff} 处标点改动)")
    print(f"\n扫了 {len(targets)} 章；{n_changed} 章有改动；共改 {total} 处标点。")
    if dry_run:
        print("(dry-run，没写盘。去掉 --dry-run 真正写盘。)")


if __name__ == "__main__":
    main()