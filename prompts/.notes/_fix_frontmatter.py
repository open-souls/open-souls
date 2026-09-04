# -*- coding: utf-8 -*-
"""修补缺失 --- 起头的章节文件（只在开头加 ---）。"""
import os, re

CHRON = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "seasons", "01-xianxia", "chronicle"))

fixed = []
for fn in sorted(os.listdir(CHRON)):
    if not fn.endswith(".md") or fn.startswith("test_") or fn in ("INDEX.md", "_STUB_MANIFEST.json"):
        continue
    p = os.path.join(CHRON, fn)
    text = open(p, encoding="utf-8").read()
    if text.startswith("---\n") or text.startswith("---\r\n"):
        continue
    first_30 = "\n".join(text.split("\n")[:30])
    if "season:" in first_30 and "chapter:" in first_30 and "title:" in first_30:
        # 检查文件末段是否已有 --- 收尾
        last_30 = "\n".join(text.split("\n")[-30:])
        if "---" in last_30:
            # 仅在前置 ---，不动文件末尾
            new_text = "---\n" + text
            open(p, "w", encoding="utf-8").write(new_text)
            fixed.append((fn, "prepended"))
        else:
            # 都没有：前后都加（找标题行位置）
            m = re.search(r"^#\s+第\S+回", text, re.M)
            if m:
                title_pos = m.start()
                # 找标题前的最近空行
                pre = text[:title_pos]
                lines = pre.split("\n")
                # 移除尾部空行
                while lines and lines[-1].strip() == "":
                    lines.pop()
                post = text[title_pos:]
                new_text = "---\n" + "\n".join(lines) + "\n---\n\n" + post
                open(p, "w", encoding="utf-8").write(new_text)
                fixed.append((fn, "wrapped"))
print("Fixed missing leading ---:", len(fixed))
for fn, mode in fixed:
    print(" ", fn, mode)
