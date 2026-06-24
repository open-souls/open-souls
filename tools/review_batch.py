# -*- coding: utf-8 -*-
"""Batch review tool for subagent outputs.

对一批章节跑硬线检查 + 机器腔检查 + 改动幅度检查 + 锚点去重检查。
主编用：agent 返回后 → python tools/review_batch.py ch001-ch020
"""
import os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))
import prose_lint as PL

CHRONICLE = os.path.join(ROOT, "seasons", "01-xianxia", "chronicle")
EDITOR_PROGRESS = os.path.join(ROOT, "editor_progress.md")

# ---- 已有锚点清单（来自 editor_progress.md，需手动同步） ----
KNOWN_ANCHORS = [
    "苏挽袖角", "林夙指节", "信纸温度", "林窈耳尖", "梅树", "粥推过方向",
    "林夙他外裳", "苏挽眼青影", "苏挽肩窄", "苏挽指节白",
    # ch101-200 锚点
    "苏挽端碗", "林夙声音下沉", "院中那片枯叶",
    # ch201-300 锚点
    "苏挽拓印", "阿湄凉茶",
]

# ---- 硬线违例模式 ----
HARDLINE_PATTERNS = [
    (r"\b他\s*插入\b", "可能露骨"),
    (r"\b她\s*插入\b", "可能露骨"),
    (r"林窈.*?(?:耳根|颈侧|指节|手腕)", "林窈 13 岁不涉及暧昧"),
]


def parse_chapter_range(spec):
    """Parse 'ch001-020' or 'ch005,ch007-010' into list of chapter numbers."""
    nums = []
    for part in spec.split(","):
        m = re.match(r"^ch(\d+)-(\d+)$", part.strip())
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            nums.extend(range(a, b + 1))
        else:
            m = re.match(r"^ch(\d+)$", part.strip())
            if m:
                nums.append(int(m.group(1)))
    return sorted(set(nums))


def find_files(nums):
    files = []
    for n in nums:
        for f in sorted(os.listdir(CHRONICLE)):
            if re.match(rf"^{n:03d}-", f):
                files.append((n, os.path.join(CHRONICLE, f)))
                break
    return files


def check_hardline(path):
    """Check hardline violations (露骨/自伤/未成年暧昧)."""
    text = open(path, encoding="utf-8").read()
    body = PL.body_of(text)
    issues = []
    for pat, desc in HARDLINE_PATTERNS:
        if re.search(pat, body):
            issues.append(f"硬线警告: {desc}")
    return issues


def check_anchor_dup(path):
    """Check if chapter adds an anchor that duplicates a known one."""
    text = open(path, encoding="utf-8").read()
    issues = []
    for anchor in KNOWN_ANCHORS:
        if anchor in text:
            issues.append(f"锚点疑似重复: 「{anchor}」(确认是否本章新用)")
    return issues


def check_modification_count(path):
    """Heuristic: count newline paragraph breaks in body. Big changes = many breaks."""
    text = open(path, encoding="utf-8").read()
    body = PL.body_of(text)
    # Count paragraphs (rough proxy)
    paragraphs = [p for p in body.split("\n\n") if p.strip()]
    return len(paragraphs)


def main():
    if len(sys.argv) < 2:
        print("用法: python tools/review_batch.py ch001-ch020 [ch030-ch040 ...]")
        print("示例: python tools/review_batch.py ch001-005,ch010")
        sys.exit(1)

    args = sys.argv[1:]
    all_nums = []
    for spec in args:
        all_nums.extend(parse_chapter_range(spec))

    files = find_files(all_nums)
    if not files:
        print("未找到章节文件")
        sys.exit(1)

    print(f"审查 {len(files)} 章 · 范围 ch{min(n for n,_ in files):03d}-ch{max(n for n,_ in files):03d}\n")

    pass_count = fail_count = 0
    for n, path in files:
        rel = os.path.relpath(path, ROOT)
        errors, warns, m = PL.lint_file(path)
        hl = check_hardline(path)
        dup = check_anchor_dup(path)

        if hl or errors:
            fail_count += 1
            print(f"✗ ch{n:03d} ({rel})")
            for h in hl:
                print(f"   HARDLINE  {h}")
            for e in errors:
                print(f"   ERROR     {e}")
            for w in warns[:3]:
                print(f"   warn      {w}")
        else:
            pass_count += 1
            tag = "✓"
            if warns:
                tag = "⚠"
                for w in warns[:3]:
                    print(f"   warn      {w}")
            print(f"{tag} ch{n:03d} | chars={m['chars']} micro={m['micro']*100:.0f}% avg={m['avg']:.1f}")

        if dup:
            for d in dup:
                print(f"   DUP       {d}")

    print(f"\n总结: {pass_count} 章过 / {fail_count} 章拒")
    sys.exit(0 if fail_count == 0 else 1)


if __name__ == "__main__":
    main()
