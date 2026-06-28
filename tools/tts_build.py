"""
两阶段有声书生成流程。

Phase 1 — 生成播音稿（SSML）：
  python tools/tts_build.py --prepare
  输出: tools/tts_scripts/ch001.ssml … ch502.ssml

Phase 2 — 从播音稿生成 mp3：
  python tools/tts_build.py --tts
  python tools/tts_build.py --tts --voice Yunjian
  输出: tools/tts_out/Xiaoxiao/ Yunxi/ Yunjian/

其他选项：
  --chapters 1-10   只处理指定范围
  --voice NAME      只跑某一声线（Phase 2）
  --force           覆盖已存在文件
"""
import asyncio
import argparse
import re
import sys
import os

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import edge_tts
import edge_tts.communicate as _et_comm
from tts_preprocess import preprocess

# ── SSML 直通补丁 ─────────────────────────────────────────────
# edge-tts 7.x 会把用户文本 xml.escape()，导致 <speak> 标签被朗读。
# 在此 monkey-patch mkssml：若文本本身已是完整 SSML，直接返回，不再套壳。
_orig_mkssml = _et_comm.mkssml

def _ssml_passthrough(tc, escaped_text):
    txt = escaped_text.decode('utf-8') if isinstance(escaped_text, bytes) else escaped_text
    if txt.lstrip().startswith('<speak'):
        return txt
    return _orig_mkssml(tc, escaped_text)

_et_comm.mkssml = _ssml_passthrough



class SSMLCommunicate(edge_tts.Communicate):
    """接收完整 SSML 字符串，绕过 edge-tts 内部的 xml.escape()。
    自动注入 <voice> 元素和命名空间声明，符合 Microsoft TTS 服务要求。"""
    def __init__(self, ssml: str, voice: str):
        super().__init__('.', voice)
        inner = re.sub(r'^<speak[^>]*>', '', ssml.strip())
        inner = re.sub(r'</speak>\s*$', '', inner)
        # Strip inner <voice> tags — edge-tts only supports one voice per request
        inner = re.sub(r'<voice\b[^>]*>', '', inner)
        inner = re.sub(r'</voice>', '', inner)
        # Strip <mstts:*> tags (Azure Cognitive Services only, not supported by Edge TTS)
        # but keep their inner content so breaks/emphasis inside still apply
        inner = re.sub(r'<mstts:[^/][^>]*>', '', inner)
        inner = re.sub(r'</mstts:[^>]+>', '', inner)
        full = (
            "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' "
            "xmlns:mstts='http://www.w3.org/2001/mstts' xml:lang='en-US'>"
            f"<voice name='{voice}'>"
            + inner +
            "</voice></speak>"
        )
        self.texts = [full.encode('utf-8')]

EPUB       = "docs/镇狱之渊.epub"
SCRIPT_DIR = "tools/tts_scripts"
OUT_DIR    = "tools/tts_out"

VOICES = {
    "Xiaoxiao": "zh-CN-XiaoxiaoNeural",
    "Yunxi":    "zh-CN-YunxiNeural",
    "Yunjian":  "zh-CN-YunjianNeural",
}

CONCURRENCY = 5


# ── epub 解析 ─────────────────────────────────────────────────

def extract_chapters(epub_path):
    book = epub.read_epub(epub_path)
    chapters = []
    for item in sorted(book.get_items(), key=lambda x: x.get_name()):
        if item.get_type() != ebooklib.ITEM_DOCUMENT:
            continue
        name = item.get_name()
        if not re.match(r"chap\d+\.xhtml", name):
            continue
        soup = BeautifulSoup(item.get_content(), "html.parser")
        text = soup.get_text(separator="\n").strip()
        text = re.sub(r"\n{3,}", "\n\n", text)
        chapters.append((name, text))
    return chapters


# ── Phase 1：生成播音稿 ───────────────────────────────────────

def phase_prepare(chapters, force=False):
    os.makedirs(SCRIPT_DIR, exist_ok=True)
    done = skipped = 0
    for name, text in chapters:
        ch_num = re.search(r"\d+", name).group()
        out = f"{SCRIPT_DIR}/ch{ch_num}.ssml"
        if os.path.exists(out) and not force:
            skipped += 1
            continue
        ssml = preprocess(text)
        with open(out, "w", encoding="utf-8") as f:
            f.write(ssml)
        print(f"  ✓ ch{ch_num}.ssml")
        done += 1
    print(f"\n播音稿完成：{done} 新建，{skipped} 跳过")
    print(f"文件在 {SCRIPT_DIR}/，可打开任意 .ssml 文件检查内容。")
    print(f"确认无误后运行：python tools/tts_build.py --tts")


# ── Phase 2：从播音稿生成 mp3 ─────────────────────────────────

async def render_one(sem, ssml_path, voice_name, voice_id, out_path, label, force=False):
    async with sem:
        if os.path.exists(out_path) and not force:
            print(f"  skip {label} (已存在)")
            return
        try:
            with open(ssml_path, encoding="utf-8") as f:
                ssml = f.read()
            communicate = SSMLCommunicate(ssml, voice_id)
            await communicate.save(out_path)
            print(f"  ✓ {label}")
        except Exception as e:
            print(f"  ✗ {label} — {e}")


def get_chapter_title(ssml_path: str) -> str:
    """从 SSML 中提取中文章节标题，例如 '第一回，退婚书。' → '退婚书'"""
    try:
        with open(ssml_path, encoding="utf-8") as f:
            content = f.read()
        # Chapter number may be Chinese (第一回) or Arabic (第1回)
        m = re.search(r'第[\d一二三四五六七八九十零百千万亿]+回[，,](.+?)[。．\n<]', content)
        if m:
            return m.group(1).strip()
    except Exception:
        pass
    return ""


def find_ssml(ch_num: str) -> str | None:
    """Find the SSML file for a chapter number — matches ch-NNN-*.ssml or ch NNN.ssml."""
    padded = ch_num.zfill(3)
    for f in os.listdir(SCRIPT_DIR):
        if re.match(rf"^ch-{padded}-.*\.ssml$", f) or f == f"ch{padded}.ssml":
            return os.path.join(SCRIPT_DIR, f)
    return None


def make_out_path(out_dir: str, v_name: str, ch_num: str, ssml_path: str) -> str:
    """生成输出路径：ch-{number}-{中文标题}.mp3"""
    title = get_chapter_title(ssml_path)
    padded = ch_num.zfill(3)
    if title:
        return f"{out_dir}/{v_name}/ch-{padded}-{title}.mp3"
    return f"{out_dir}/{v_name}/ch{padded}.mp3"


async def phase_tts(chapters, voices, force=False):
    # 检查播音稿是否存在
    missing = []
    for name, _ in chapters:
        ch_num = re.search(r"\d+", name).group()
        if not find_ssml(ch_num):
            missing.append(ch_num)
    if missing:
        print(f"缺少播音稿（共 {len(missing)} 章），请先运行 --prepare")
        print(f"  缺: {', '.join(missing[:10])}{'…' if len(missing)>10 else ''}")
        return

    for v in voices:
        os.makedirs(f"{OUT_DIR}/{v}", exist_ok=True)

    sem = asyncio.Semaphore(CONCURRENCY)
    tasks = []
    for name, _ in chapters:
        ch_num = re.search(r"\d+", name).group()
        ssml_path = find_ssml(ch_num)
        for v_name, v_id in voices.items():
            out = make_out_path(OUT_DIR, v_name, ch_num, ssml_path)
            label = f"{v_name}/ch{ch_num.zfill(3)}"
            tasks.append(render_one(sem, ssml_path, v_name, v_id, out, label, force=force))

    print(f"\n开始 TTS（{len(tasks)} 个文件，{CONCURRENCY} 并发）…\n")
    await asyncio.gather(*tasks)
    print(f"\n全部完成！输出目录: {OUT_DIR}/")
    for v in voices:
        mp3s = [f for f in os.listdir(f"{OUT_DIR}/{v}") if f.endswith(".mp3")]
        print(f"  {v}: {len(mp3s)} 个文件")


# ── 入口 ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true", help="Phase 1：生成播音稿 SSML")
    parser.add_argument("--tts",     action="store_true", help="Phase 2：从播音稿生成 mp3")
    parser.add_argument("--chapters", default=None, help="章节范围，如 1-10")
    parser.add_argument("--voice",    default=None, help="Xiaoxiao / Yunxi / Yunjian")
    parser.add_argument("--force",    action="store_true", help="覆盖已存在文件")
    args = parser.parse_args()

    if not args.prepare and not args.tts:
        parser.print_help()
        return

    # 章节范围
    print("读取 epub …")
    chapters = extract_chapters(EPUB)
    print(f"共 {len(chapters)} 章")

    if args.chapters:
        parts = args.chapters.split("-")
        lo, hi = int(parts[0]), int(parts[-1])
        chapters = chapters[lo-1:hi]
        print(f"过滤后: 第{lo}章 ~ 第{hi}章，共 {len(chapters)} 章")

    # 声线
    voices = VOICES
    if args.voice:
        if args.voice not in VOICES:
            print(f"声线必须是: {list(VOICES.keys())}")
            return
        voices = {args.voice: VOICES[args.voice]}

    if args.prepare:
        phase_prepare(chapters, force=args.force)

    if args.tts:
        asyncio.run(phase_tts(chapters, voices, force=args.force))


main()
