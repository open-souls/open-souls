# -*- coding: utf-8 -*-
"""Batch rewrite dispatcher for Open Souls.

Spawns subagents in parallel to rewrite chapters that fail lint (mostly §七.1
disease章 + stub占位章). Uses the治本范文章 ch512-不接 as the gold reference.

Usage:
    python engine/batch_rewrite.py --pick 12           # pick 12 chapters automatically
    python engine/batch_rewrite.py --pick 12 --parallel 6
    python engine/batch_rewrite.py --chapters ch531,ch532,ch857
    python engine/batch_rewrite.py --stubs-only --pick 20
    python engine/batch_rewrite.py --dry-run --pick 5
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHRONICLE = ROOT / "seasons" / "01-xianxia" / "chronicle"
STUB_MANIFEST = CHRONICLE / "_STUB_MANIFEST.json"
RESULTS_DIR = ROOT / "prompts" / ".results"
RESULTS_DIR.mkdir(exist_ok=True)

REFERENCE_CHAPTER = "ch512-不接.md"  # 治本范文章


def load_state():
    """Load progress and target queues."""
    with open(STUB_MANIFEST) as f:
        stub_data = json.load(f)
    stub_set = {e["filename"] for e in stub_data["files"]}
    stub_by_chapter = {e["chapter"]: e["filename"] for e in stub_data["files"]}

    # Find disease chapters via lint
    result = subprocess.run(
        ["python", "engine/prose_lint.py"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    error_chs = set()
    for line in result.stdout.splitlines():
        m = re.match(r"^✗\s+(.+\.md)", line)
        if m:
            f = m.group(1)
            mm = re.search(r"ch?(\d{3,4})", f)
            if mm:
                error_chs.add(int(mm.group(1)))

    return stub_set, stub_by_chapter, sorted(error_chs)


def pick_targets(n, stubs_only=False, disease_only=False, skip_done=True):
    """Pick n chapters to rewrite. Order: stub ch857-997 first (no real chapter
    on disk), then disease chapters by chapter number."""
    stub_set, stub_by_chapter, error_chs = load_state()
    targets = []
    if not disease_only:
        # Stub chapters in gap range (ch858-997) are highest priority
        for ch in sorted(stub_by_chapter.keys()):
            if 858 <= ch <= 997:
                if skip_done and _already_done(ch):
                    continue
                targets.append(("stub", ch, stub_by_chapter[ch]))
                if len(targets) >= n:
                    return targets
    if not stubs_only:
        for ch in error_chs:
            if skip_done and _already_done(ch):
                continue
            targets.append(("disease", ch, _chapter_file(ch)))
            if len(targets) >= n:
                return targets
    return targets


def _chapter_file(ch):
    """Resolve a chapter number to a real chapter file on disk."""
    candidates = list(CHRONICLE.glob(f"ch{ch:03d}-*.md")) + list(CHRONICLE.glob(f"ch{ch}-*.md"))
    candidates = [c for c in candidates if not c.stem.startswith("_")]
    if not candidates:
        return None
    # Pick the largest non-stub file
    candidates.sort(key=lambda c: c.stat().st_size, reverse=True)
    return str(candidates[0])


def _already_done(ch):
    """Check if chapter is already gold (PASSed lint)."""
    f = _chapter_file(ch)
    if not f or not os.path.exists(f):
        return False
    if os.path.getsize(f) < 1500:
        return False  # stub
    r = subprocess.run(
        ["python", "engine/prose_lint.py", f],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    return "0 章退回" in r.stdout and "文笔过线" in r.stdout


def build_prompt(target_ch, target_file):
    """Build the subagent prompt with the治本范文 ch512 as reference."""
    reference_path = CHRONICLE / REFERENCE_CHAPTER
    reference_text = reference_path.read_text(encoding="utf-8")

    # Read pre/post hooks for continuity
    pre_hook = ""
    post_hook = ""
    for delta in (-1, +1):
        adj_ch = target_ch + delta
        if adj_ch < 1 or adj_ch > 1000:
            continue
        adj_files = list(CHRONICLE.glob(f"ch{adj_ch:03d}-*.md")) + list(CHRONICLE.glob(f"ch{adj_ch}-*.md"))
        adj_files = [c for c in adj_files if not c.stem.startswith("_") and c.stat().st_size > 1000]
        if not adj_files:
            continue
        adj_files.sort(key=lambda c: c.stat().st_size, reverse=True)
        text = adj_files[0].read_text(encoding="utf-8")
        # Extract hook field
        m = re.search(r"hook:\s*\|\s*\n((?:  .+\n)+)", text)
        hook = m.group(1).strip() if m else "(无)"
        if delta == -1:
            pre_hook = f"ch{adj_ch} hook:\n{hook}"
        else:
            post_hook = f"ch{adj_ch} hook:\n{hook}"

    return f"""你是《镇狱之渊》重写工坊的一名写手 sub-agent。本轮 TARGET=ch{target_ch:03d}。

【治本范文章 · 必须先读后写】
下面是 ch512-不接.md 的全文（这是我亲写的治本章，把 §七.1 第二道墙在 POV 写法层面破掉）。**先精读这章的每个字，然后再开始写 ch{target_ch}**：

========= 范文章 ch512-不接.md =========
{reference_text}
========= 范文章结束 =========

【ch{target_ch} 当前状态】
目标文件路径: {target_file}
文件大小: {os.path.getsize(target_file) if os.path.exists(target_file) else 0} bytes

【前后章钩子（必须承接）】
{pre_hook if pre_hook else '(无前一章)'}

{post_hook if post_hook else '(无后一章)'}

【你要做的】
1. 读 souls/ 里所有 cast 角色的 soul.md（每个角色都读，特别注意 voice / fracture / under_pressure / seed_relations）
2. 把 ch{target_ch} **整章重写**——不是改改，而是按范文章 ch512 的写法重写：删 §七.1 第二道墙（不写"X 的来处是 Y"/"X 的方式不是 X"/动词+朝+自反代词/"就第一刹让"/"是...的那种..."）；用物象（每个角色一套专属物象）+ 留白（单字收尾）+ 行为先于意识
3. 范文章 ch512 的核心写法：
   - 每个角色有自己的专属物象（秤/粥/包子/茶渍/糖玉）
   - 段落短句切镜，不堆砌长释义
   - **每个动作只写一次，不要"是...的那种..."的同义复述**
   - 章末用单字/单句/动作收尾
   - 余伯声线 = 极短（嗯/我看见了），苏挽声线 = 否决句+嗅觉，林崇声线 = 把字掂一掂再说，赤渊 = 编号排比，裴无咎 = 自嘲+嚼包子，牛阿大 = 全沉默+动作，阿湄 = 计算+备用笑，叶观澜 = 极轻+压字+抹旧痕
4. 保留 frontmatter 的 cast / pov / line / thread / beat / ships 字段（**改 ships 为 ≤60 字一条，不堆叠章号链**），其他字段可以重写
5. 字数 ≥ 1500 字（实际正文汉字数）
6. 写完跑 `python engine/prose_lint.py "{target_file}"`，必须 0 ERROR
7. 写完结果到 `prompts/.results/ch{target_ch:03d}.md`：
   - status: PASS | BLOCKED
   - lint: ok|fail
   - score: 14/14（如果你能稳定打 14）
   - gates: G1✓ G2✓ G3✓ G4✓ G5✓
   - souls_read: 列出本章 cast 角色名
   - note: 一句话（改了什么 / 治本了什么）

【绝对硬禁】
- ❌ 不写「X 的来处是 Y」「X 的方式不是 X」「是...的那种...」「按完按完」「就第一刹让」「走朝他自己走的」「擦朝苏挽自己擦的」这类公式
- ❌ 不写「反派」「眸」「缓缓」「方才」「未曾」「须臾」「踱」「坐于」「置于」
- ❌ 不写男主姓名「反派」标签
- ❌ 不堆叠 ch-编号交叉引用到 ships 字段
- ❌ 跨章改写——只改 TARGET 一章

完成后停。
"""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pick", type=int, default=0, help="Auto-pick N chapters")
    p.add_argument("--chapters", type=str, help="Comma-separated chapter numbers")
    p.add_argument("--stubs-only", action="store_true")
    p.add_argument("--disease-only", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--no-skip-done", action="store_true")
    args = p.parse_args()

    if args.chapters:
        targets = []
        for s in args.chapters.split(","):
            ch = int(s.strip())
            targets.append(("manual", ch, _chapter_file(ch)))
    else:
        skip = not args.no_skip_done
        targets = pick_targets(args.pick or 12, args.stubs_only, args.disease_only, skip_done=skip)

    print(f"Picked {len(targets)} target chapter(s):")
    for kind, ch, f in targets:
        sz = os.path.getsize(f) if f and os.path.exists(f) else 0
        print(f"  ch{ch:4d}  [{kind}]  {sz:5d}B  {f}")

    if args.dry_run:
        print("\n[DRY RUN] No subagents spawned.")
        return

    # Write prompts to disk for dispatch
    dispatch_dir = ROOT / "prompts" / "dispatch"
    dispatch_dir.mkdir(exist_ok=True)
    for kind, ch, f in targets:
        if not f:
            print(f"  WARN: ch{ch} has no file on disk, skipping")
            continue
        prompt = build_prompt(ch, f)
        out = dispatch_dir / f"ch{ch:03d}.txt"
        out.write_text(prompt, encoding="utf-8")
        print(f"  wrote {out}")

    print(f"\nDispatch prompts ready in {dispatch_dir}/")
    print("To execute, run subagents with:")
    print("  python engine/run_dispatch.py  (one-shot)  or")
    print("  /loop  with cron  (autonomous batch)")


if __name__ == "__main__":
    main()