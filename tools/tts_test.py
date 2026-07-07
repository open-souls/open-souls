"""
试跑：从 epub 提取前2章，用三个声线各生成一段 mp3，输出到 tools/tts_out/
用法：python tools/tts_test.py
"""
import asyncio
import re
import sys
import os

# Windows UTF-8 fix
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import edge_tts

EPUB = "docs/镇狱之渊.epub"
OUT_DIR = "tools/tts_out"
VOICES = [
    "zh-CN-XiaoxiaoNeural",   # 女，温柔
    "zh-CN-YunxiNeural",      # 男，沉稳
    "zh-CN-YunjianNeural",    # 男，磁性
]
# 每章只取前 300 字做测试
PREVIEW_CHARS = 300


def extract_chapters(epub_path, max_chapters=2):
    book = epub.read_epub(epub_path)
    chapters = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), "html.parser")
            # 跳过目录、版权页等极短片段
            text = soup.get_text(separator="\n").strip()
            text = re.sub(r"\n{3,}", "\n\n", text)
            if len(text) > 100:
                chapters.append(text)
        if len(chapters) >= max_chapters:
            break
    return chapters


async def tts(text, voice, out_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(out_path)
    print(f"  ✓ {out_path}")


async def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    chapters = extract_chapters(EPUB)
    if not chapters:
        print("未能从 epub 提取到章节，检查路径或 epub 结构")
        return

    print(f"提取到 {len(chapters)} 章，各取前 {PREVIEW_CHARS} 字\n")

    tasks = []
    for i, ch in enumerate(chapters, 1):
        snippet = ch[:PREVIEW_CHARS]
        for voice in VOICES:
            short = voice.split("-")[2].replace("Neural", "")
            out = f"{OUT_DIR}/ch{i:02d}_{short}.mp3"
            tasks.append(tts(snippet, voice, out))

    await asyncio.gather(*tasks)
    print(f"\n完成！文件在 {OUT_DIR}/")
    print("对比听：ch01_Xiaoxiao / ch01_Yunxi / ch01_Yunjian")


asyncio.run(main())
