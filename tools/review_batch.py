# -*- coding: utf-8 -*-
"""Batch review tool for subagent outputs.

对一批章节跑硬线检查 + 机器腔检查 + 改动幅度检查 + 锚点去重检查。
主编用：agent 返回后 → python tools/review_batch.py ch001-ch020
"""
import os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))
import prose_lint as PL
import safety_lint as SL
import village as V

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

# Keep batch review on the same deterministic hardline implementation as the
# generation hot path.
HARDLINE_PATTERNS = SL.HARDLINE_PATTERNS


def parse_chapter_range(spec):
    """Parse 'ch001-ch020' or 'ch005,ch007-ch010' or 'ch420-428' into list of chapter numbers."""
    nums = []
    for part in spec.split(","):
        s = part.strip()
        # accept ch420-ch428, ch420-428, 420-428
        m = re.match(r"^(?:ch)?(\d+)(?:[-](?:ch)?(\d+))?$", s)
        if m and m.group(2):
            a, b = int(m.group(1)), int(m.group(2))
            nums.extend(range(a, b + 1))
        elif m and m.group(1):
            nums.append(int(m.group(1)))
    return sorted(set(nums))


def _candidate_rank(path, strict_editorial=False):
    """Prefer a branch that actually passes the requested review gate."""
    try:
        raw = open(path, encoding="utf-8").read()
        meta = V.read_frontmatter(raw)
        errors, _, metrics = PL.lint_file(path, strict=strict_editorial)
        hardline = SL.check(PL.body_of(raw))
        base_ok = not V.validate_frontmatter(meta)
        editorial_ok = not V.validate_editorial_metadata(meta)
        length_ok = metrics.get("chars", 0) >= PL.MIN_CHAPTER_CHARS
        lint_ok = not errors and not hardline
        publishable = lint_ok and base_ok and (editorial_ok and length_ok if strict_editorial else True)
        return (
            int(publishable),
            int(lint_ok and base_ok),
            int(editorial_ok),
            int(length_ok),
            metrics.get("chars", 0),
            os.path.getsize(path),
            -len(os.path.basename(path)),
            os.path.basename(path),
        )
    except (OSError, UnicodeError):
        return (0, 0, 0, 0, 0, 0, -len(os.path.basename(path)), os.path.basename(path))


def find_files(nums, strict_editorial=False):
    """Find chapter files, preferring a passing duplicate branch over size."""
    files = []
    for n in nums:
        candidates = [
            f for f in os.listdir(CHRONICLE)
            if re.match(rf"^(?:ch)?{n:03d}-", f, re.I)
        ]
        # Among duplicate same-number branches, a passing branch is canonical;
        # file size is only a fallback for equally healthy branches.
        # Skip files with extra markers like "-扩写" / "-alt"
        canonical = [f for f in candidates if not re.search(r"-(?:扩写|alt|draft|副本)", f)]
        chosen = (canonical or candidates)
        chosen.sort(
            key=lambda x: _candidate_rank(
                os.path.join(CHRONICLE, x), strict_editorial=strict_editorial
            ),
            reverse=True,
        )
        if chosen:
            files.append((n, os.path.join(CHRONICLE, chosen[0])))
    return files


def check_hardline(path):
    """Check hardline violations (露骨/自伤/未成年暧昧)."""
    text = open(path, encoding="utf-8").read()
    body = PL.body_of(text)
    return [f"硬线警告: {issue}" for issue in SL.check(body)]


def check_metadata(path, strict_editorial=False):
    """Apply the same frontmatter schema gate used before publication."""
    text = open(path, encoding="utf-8").read()
    body = PL.body_of(text)
    errors = V.validate_frontmatter(V.read_frontmatter(text))
    if strict_editorial:
        errors.extend(V.validate_editorial_metadata(V.read_frontmatter(text), body=body))
    current_hook = V.read_frontmatter(text).get("hook")
    current_hook = str(current_hook or "").strip()
    season_dir = os.path.dirname(os.path.dirname(path))
    current_number = V.chapter_number(path)
    previous_hooks = []
    for number, candidate in V.chapter_files(season_dir):
        if os.path.abspath(candidate) == os.path.abspath(path) or number >= current_number:
            continue
        candidate_meta = V.read_frontmatter(open(candidate, encoding="utf-8").read())
        hook = str(candidate_meta.get("hook") or "").strip()
        if hook:
            previous_hooks.append(hook)
        if len(previous_hooks) >= 3:
            break
    if current_hook and current_hook in previous_hooks:
        errors.append("hook重复")
    return [f"元数据: {error}" for error in errors]


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
        print("用法: python tools/review_batch.py [--strict-editorial] ch001-ch020")
        print("或: python tools/review_batch.py --strict-editorial --file path/to/ch.md")
        print("示例: python tools/review_batch.py ch001-005,ch010")
        sys.exit(1)

    strict_editorial = "--strict-editorial" in sys.argv[1:]
    raw_args = [arg for arg in sys.argv[1:] if arg != "--strict-editorial"]
    args = []
    exact_paths = []
    index = 0
    while index < len(raw_args):
        arg = raw_args[index]
        if arg == "--file":
            if index + 1 >= len(raw_args):
                print("--file 需要一个路径")
                sys.exit(1)
            exact_paths.append(raw_args[index + 1])
            index += 2
            continue
        if arg.startswith("--file="):
            exact_paths.append(arg.split("=", 1)[1])
            index += 1
            continue
        args.append(arg)
        index += 1

    if exact_paths:
        files = []
        for raw_path in exact_paths:
            path = os.path.abspath(raw_path)
            number = V.chapter_number(path)
            if number is None or not os.path.isfile(path):
                print(f"未找到有效章节文件: {raw_path}")
                sys.exit(1)
            files.append((number, path))
    else:
        all_nums = []
        for spec in args:
            all_nums.extend(parse_chapter_range(spec))

        files = find_files(all_nums, strict_editorial=strict_editorial)
    if not files:
        print("未找到章节文件")
        sys.exit(1)

    print(f"审查 {len(files)} 章 · 范围 ch{min(n for n,_ in files):03d}-ch{max(n for n,_ in files):03d}\n")

    pass_count = fail_count = 0
    for n, path in files:
        rel = os.path.relpath(path, ROOT)
        errors, warns, m = PL.lint_file(path, strict=strict_editorial)
        if strict_editorial and m.get("chars", 0) < PL.MIN_CHAPTER_CHARS:
            errors.append(
                f"章节字数不足：{m.get('chars', 0)} < {PL.MIN_CHAPTER_CHARS}"
            )
        hl = check_hardline(path)
        metadata = check_metadata(path, strict_editorial=strict_editorial)
        dup = check_anchor_dup(path)

        if hl or errors or metadata:
            fail_count += 1
            print(f"✗ ch{n:03d} ({rel})")
            for h in hl:
                print(f"   HARDLINE  {h}")
            for e in errors:
                print(f"   ERROR     {e}")
            for item in metadata:
                print(f"   METADATA  {item}")
            for w in warns[:3]:
                print(f"   warn      {w}")
        else:
            pass_count += 1
            tag = "✓"
            if warns:
                tag = "⚠"
                for w in warns[:3]:
                    print(f"   warn      {w}")
            if m.get('exempt'):
                print(f"{tag} ch{n:03d} | EXEMPT (prose_lint_exempt)")
            else:
                print(f"{tag} ch{n:03d} | chars={m['chars']} micro={m['micro']*100:.0f}% avg={m['avg']:.1f}")
        if m.get('exempt'):
            print(f"   EXEMPT   prose_lint_exempt — 跳过文笔门")

        if dup:
            for d in dup:
                print(f"   DUP       {d}")

    print(f"\n总结: {pass_count} 章过 / {fail_count} 章拒")
    sys.exit(0 if fail_count == 0 else 1)


if __name__ == "__main__":
    main()
