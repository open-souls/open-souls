# -*- coding: utf-8 -*-
"""Batch rewrite dispatcher for Open Souls.

Spawns subagents in parallel to rewrite chapters that fail lint (mostly §七.1
disease章 + stub占位章). Uses the治本范文章 ch512-不接 as the gold reference.

Usage:
    python engine/batch_rewrite.py --pick 12           # pick 12 chapters automatically
    python engine/batch_rewrite.py --chapters ch531,ch532,ch857
    python engine/batch_rewrite.py --stubs-only --pick 20
    python engine/batch_rewrite.py --dry-run --pick 5
"""
import argparse
import hashlib
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
LINT_CACHE_NAME = "batch_lint_cache.json"
_LAST_LINT_ERRORS = {}
sys.path.insert(0, str(ROOT / "engine"))
import village as V
import prose_lint as PL
import safety_lint as SL
import season as SE
import story_state as SS

REFERENCE_CHAPTER = "ch512-不接.md"  # 治本范文章


EXCLUDED_BRANCHES = frozenset({"alternate", "parallel", "archive"})


def _chapter_number_from_path(path_or_name):
    """Extract a chapter number from ``857-title.md`` or ``ch857-title.md``."""
    name = Path(str(path_or_name)).name
    match = re.match(r"(?:ch)?(\d{3,4})-", name, re.I)
    return int(match.group(1)) if match else None


def _resolve_reported_path(reported_path):
    """Resolve the relative Windows path printed by prose_lint."""
    raw = str(reported_path).strip().strip("`")
    if os.sep != "\\":
        raw = raw.replace("\\", os.sep)
    path = Path(raw)
    if not path.is_absolute():
        path = ROOT / path
    return path if path.exists() and path.is_file() else None


def _parse_lint_error_targets(output):
    """Return exact ``(chapter, path)`` pairs for every lint ERROR file."""
    targets = []
    seen = set()
    for line in output.splitlines():
        stripped = line.lstrip()
        if not stripped.startswith("\u2717"):
            continue
        match = re.match(r"^\u2717\s+(.+\.md)\s*$", stripped)
        if not match:
            continue
        path = _resolve_reported_path(match.group(1))
        chapter = _chapter_number_from_path(path or match.group(1))
        if chapter is None or path is None:
            continue
        key = str(path.resolve())
        if key in seen:
            continue
        seen.add(key)
        targets.append((chapter, str(path)))
    return sorted(targets, key=lambda item: (item[0], item[1]))


def _lint_cache_path():
    """Return the local-only cache path used by status/picker scans."""
    return ROOT / ".audit_tmp" / LINT_CACHE_NAME


def _sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _lint_cache_version():
    """Invalidate cached verdicts when the lint rules or stub manifest change."""
    digest = hashlib.sha256()
    for path in (Path(PL.__file__), STUB_MANIFEST):
        if not path.exists():
            digest.update(str(path).encode("utf-8"))
            continue
        digest.update(str(path).encode("utf-8"))
        digest.update(_sha256_file(path).encode("ascii"))
    return digest.hexdigest()


def _load_lint_cache():
    path = _lint_cache_path()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {"version": _lint_cache_version(), "files": {}}
    if payload.get("version") != _lint_cache_version():
        return {"version": _lint_cache_version(), "files": {}}
    return {"version": payload["version"], "files": payload.get("files", {})}


def _save_lint_cache(cache):
    path = _lint_cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    temporary.replace(path)


def _chapter_files_for_lint():
    """Return the same numbered chapter universe as prose_lint's CLI."""
    stub_set = PL.load_stub_set()
    paths = []
    for path in sorted((CHRONICLE).glob("*.md")):
        if not re.match(r"^(?:\d|ch\d)", path.name, re.I):
            continue
        if path.name in stub_set:
            continue
        paths.append(path)
    return paths


def _cached_lint_error_targets():
    """Lint chapters with a content/rule cache, preserving exact error paths."""
    global _LAST_LINT_ERRORS
    cache = _load_lint_cache()
    records = cache["files"]
    current = set()
    lint_errors = {}
    error_targets = []
    for path in _chapter_files_for_lint():
        key = str(path.resolve())
        current.add(key)
        stat = path.stat()
        fingerprint = {
            "size": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
            "sha256": None,
        }
        record = records.get(key)
        if record and all(record.get(field) == fingerprint[field] for field in ("size", "mtime_ns")):
            fingerprint["sha256"] = record.get("sha256")
        if not fingerprint["sha256"]:
            fingerprint["sha256"] = _sha256_file(path)
        if record and all(record.get(field) == fingerprint[field] for field in ("size", "mtime_ns", "sha256")):
            errors = record.get("errors", [])
        else:
            errors, _, _ = PL.lint_file(str(path))
            records[key] = {**fingerprint, "errors": list(errors)}
        lint_errors[key] = list(errors)
        if errors:
            chapter = _chapter_number_from_path(path)
            if chapter is not None:
                error_targets.append((chapter, str(path)))
    cache["files"] = {key: value for key, value in records.items() if key in current}
    _save_lint_cache(cache)
    _LAST_LINT_ERRORS = lint_errors
    return sorted(error_targets, key=lambda item: (item[0], item[1]))


def load_state():
    """Load progress and target queues."""
    if not STUB_MANIFEST.exists():
        stub_data = {"files": []}
    else:
        with open(STUB_MANIFEST, encoding="utf-8") as f:
            stub_data = json.load(f)
    entries = stub_data.get("files") or []
    if entries:
        stub_set = {e["filename"] for e in entries}
        stub_by_chapter = {e["chapter"]: e["filename"] for e in entries}
    else:
        chapter_numbers = {int(number) for number in stub_data.get("chapter_numbers", [])}
        stub_set = {str(number) for number in chapter_numbers}
        stub_by_chapter = {number: None for number in chapter_numbers}

    # Find disease chapters via a content/rule-keyed local cache. Delete
    # .audit_tmp/batch_lint_cache.json to force a full refresh.
    error_targets = _cached_lint_error_targets()

    return stub_set, stub_by_chapter, error_targets


def parse_chapter_spec(spec):
    """Parse ch999, 999, ch999-ch1000, or comma-separated combinations."""
    numbers = []
    for part in spec.split(","):
        match = re.fullmatch(r"(?:ch)?(\d+)(?:-(?:ch)?(\d+))?", part.strip(), re.I)
        if not match:
            raise ValueError(f"invalid chapter selector: {part}")
        start = int(match.group(1))
        end = int(match.group(2) or start)
        if end < start:
            raise ValueError(f"chapter range is reversed: {part}")
        numbers.extend(range(start, end + 1))
    return sorted(set(numbers))


def _stub_target_file(chapter, manifest_file=None):
    """Resolve a manifest entry to an existing chapter file, if any."""
    if manifest_file:
        candidate = Path(manifest_file)
        candidates = [candidate] if candidate.is_absolute() else [CHRONICLE / candidate, ROOT / candidate]
        for path in candidates:
            if path.exists() and path.is_file():
                return str(path)
    return _chapter_file(chapter)


def pick_targets(n, stubs_only=False, disease_only=False, skip_done=True):
    """Pick n chapters to rewrite.

    Manifest stubs are always considered before lint-failing disease chapters.
    The manifest is the source of truth for stub coverage; do not assume a
    fixed chapter-number range because older stub chapters can sit below the
    current rewrite frontier.
    """
    stub_set, stub_by_chapter, error_targets = load_state()
    targets = []
    selected_chapters = set()
    if not disease_only:
        # Every manifest stub is highest priority, including older chapters
        # outside the former ch858-997 rewrite window.
        for ch in sorted(stub_by_chapter.keys()):
            target_file = _stub_target_file(ch, stub_by_chapter[ch])
            if not target_file:
                continue
            if ch in selected_chapters:
                continue
            if skip_done and _already_done(ch, target_file=target_file):
                continue
            targets.append(("stub", ch, target_file))
            selected_chapters.add(ch)
            if len(targets) >= n:
                return targets
    if not stubs_only:
        for item in error_targets:
            if isinstance(item, (tuple, list)):
                ch, target_file = int(item[0]), item[1]
            else:  # Backward-compatible with callers that supply chapter numbers.
                ch, target_file = int(item), _chapter_file(int(item))
            if not target_file or _branch_name(target_file) in EXCLUDED_BRANCHES:
                continue
            if ch in selected_chapters:
                continue
            if skip_done and _already_done(ch, target_file=target_file):
                continue
            targets.append(("disease", ch, target_file))
            selected_chapters.add(ch)
            if len(targets) >= n:
                return targets
    return targets


def _chapter_candidates(ch):
    """Return every non-private file that claims the chapter number."""
    candidates = list(dict.fromkeys(
        list(CHRONICLE.glob(f"ch{ch:03d}-*.md"))
        + list(CHRONICLE.glob(f"ch{ch}-*.md"))
        + list(CHRONICLE.glob(f"{ch:03d}-*.md"))
        + list(CHRONICLE.glob(f"{ch}-*.md"))
    ))
    return [c for c in candidates if not c.stem.startswith("_")]


def _branch_name(path):
    """Return a normalized branch marker without treating missing metadata as a branch."""
    try:
        raw = Path(path).read_text(encoding="utf-8")
        return str(V.read_frontmatter(raw).get("branch") or "").strip().lower()
    except (OSError, UnicodeError):
        return ""


def _chapter_file(ch):
    """Resolve a chapter number to the best canonical file on disk."""
    candidates = _chapter_candidates(ch)
    if not candidates:
        return None
    if len(candidates) == 1:
        return str(candidates[0])

    def candidate_rank(path):
        try:
            raw = path.read_text(encoding="utf-8")
            meta = V.read_frontmatter(raw)
            canonical = _branch_name(path) not in EXCLUDED_BRANCHES
            errors, _, metrics = PL.lint_file(str(path))
            publishable = (
                not errors
                and not SL.check(PL.body_of(raw))
                and not V.validate_frontmatter(meta)
                and not V.validate_editorial_metadata(meta)
                and metrics.get("chars", 0) >= PL.MIN_CHAPTER_CHARS
            )
            lint_clean = not errors and not SL.check(PL.body_of(raw))
            return (
                int(canonical),
                int(publishable),
                int(lint_clean),
                metrics.get("chars", 0),
                path.stat().st_size,
                -len(path.name),
                path.name,
            )
        except (OSError, UnicodeError):
            return (0, 0, 0, 0, 0, -len(path.name), path.name)

    # Keep canonical branches as the edit target. Within that branch, a
    # passing candidate beats a larger broken one.
    candidates.sort(key=candidate_rank, reverse=True)
    return str(candidates[0])


def _cast_names(path):
    if not path or not os.path.exists(path):
        return []
    text = Path(path).read_text(encoding="utf-8")
    match = re.search(r"^cast:\s*\[(.*?)\]\s*$", text, re.M)
    if not match:
        return []
    return [name.strip().strip("'\"") for name in match.group(1).split(",") if name.strip()]


def _already_done(ch, target_file=None):
    """Check if chapter is already gold (PASSed lint)."""
    f = target_file or _chapter_file(ch)
    if not f or not os.path.exists(f):
        return False
    if os.path.getsize(f) < 1500:
        return False  # stub
    raw = Path(f).read_text(encoding="utf-8")
    metadata = V.read_frontmatter(raw)
    if V.validate_frontmatter(metadata) or V.validate_editorial_metadata(metadata, body=PL.body_of(raw)):
        return False
    errors = _LAST_LINT_ERRORS.get(str(Path(f).resolve()))
    if errors is None:
        errors, _, metrics = PL.lint_file(f)
    else:
        metrics = PL.measure(PL.body_of(raw))
    return not errors and metrics.get("chars", 0) >= PL.MIN_CHAPTER_CHARS


def _error_target(item):
    """Normalize a loaded error record for status and compatibility callers."""
    if isinstance(item, (tuple, list)):
        return int(item[0]), item[1]
    chapter = int(item)
    return chapter, _chapter_file(chapter)


def _duplicate_error_counts(error_targets):
    """Count failed files hidden behind another same-number candidate."""
    hidden = 0
    alternate = 0
    for item in error_targets:
        chapter, target_file = _error_target(item)
        if not target_file:
            continue
        if _branch_name(target_file) in EXCLUDED_BRANCHES:
            alternate += 1
            continue
        preferred = _chapter_file(chapter)
        if preferred and Path(preferred).resolve() != Path(target_file).resolve():
            hidden += 1
    return hidden, alternate


def _compact_role_snapshot(name, limit=900):
    """Inline only the role signals a writer needs; do not make Claude read a huge dossier."""
    path = ROOT / "souls" / name / "soul.md"
    if not path.exists():
        return f"{name}: （无角色卡，严格按目标章 frontmatter）"
    raw = path.read_text(encoding="utf-8")
    front = raw.split("---", 2)[1] if raw.startswith("---") and "---" in raw[3:] else raw
    lines = front.splitlines()
    wanted = ("name:", "one_line:", "drives:", "fracture:", "under_pressure:", "voice:", "seed_relations:")
    selected = []
    for index, line in enumerate(lines):
        if line.lstrip().startswith(wanted):
            selected.extend(lines[index:index + 3])
    compact = "\n".join(dict.fromkeys(line for line in selected if line.strip()))
    return (compact or f"name: {name}")[:limit]


def _reference_snapshot(limit=1800):
    """Use a bounded beginning/end excerpt instead of a full reference read."""
    path = CHRONICLE / REFERENCE_CHAPTER
    if not path.exists():
        return "（范章缺失；按下列写法约束执行）"
    body = PL.body_of(path.read_text(encoding="utf-8"))
    bad_markers = (
        "方向朝着", "方向朝向", "方向落在", "方向不必替", "不必替上一世",
        "不必替前世", "他自己守", "她自己守", "的方式不是", "的方式，是",
        "是……的那种",
    )
    body = "\n".join(
        line for line in body.splitlines()
        if not any(marker in line for marker in bad_markers)
    )
    if len(body) <= limit:
        return body
    head = limit * 2 // 3
    tail = limit - head
    return body[:head] + "\n……（范章中段省略）……\n" + body[-tail:]


def build_prompt(target_ch, target_file):
    """Build a bounded subagent prompt with compact, target-relevant context."""
    cast_names = _cast_names(target_file)
    cast_snapshot = "\n\n".join(
        f"【{name}】\n{_compact_role_snapshot(name)}" for name in cast_names
    )
    cast_snapshot = f"TARGET_FILE: {Path(target_file).resolve()}\n\n{cast_snapshot}"
    reference_snapshot = _reference_snapshot()

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

【只读这些上下文，禁止扫描全仓库】
- 目标章：{target_file}
- 治本范章的有界片段（仅作节奏参照，不要再打开其他章节）：
{reference_snapshot}
- 本章 cast 的有界角色快照（禁止再打开整张 soul.md）：
{cast_snapshot or '- （未解析到 cast，严格以目标章 frontmatter 为准）'}
- 机器标准：engine/prose_lint.py、tools/review_batch.py

【ch{target_ch} 当前状态】
目标文件路径: {target_file}
文件大小: {os.path.getsize(target_file) if os.path.exists(target_file) else 0} bytes

【前后章钩子（必须承接）】
{pre_hook if pre_hook else '(无前一章)'}

{post_hook if post_hook else '(无后一章)'}

【你要做的】
1. 只使用上面的角色快照，特别注意 voice / fracture / under_pressure / seed_relations
2. 把 ch{target_ch} **整章重写**——不是改改，而是按范文章 ch512 的写法重写：删 §七.1 第二道墙（不写"X 的来处是 Y"/"X 的方式不是 X"/动词+朝+自反代词/"就第一刹让"/"是...的那种..."，也不写"方向朝着/方向落在/方向不必替"或"不必替上一世/自己守"的后置回环）；用物象（每个角色一套专属物象）+ 留白（单字收尾）+ 行为先于意识。**同一个物象位置（那一寸/那一道/那一截等）和“我/他/她自己”不能高频换名复述；把回声改成新动作、关系压力或信息。**
3. 范文章 ch512 的核心写法：
   - 每个角色有自己的专属物象（秤/粥/包子/茶渍/糖玉）
   - 段落短句切镜，不堆砌长释义
   - **每个动作只写一次，不要"是...的那种..."的同义复述**
   - 章末用单字/单句/动作收尾
   - 余伯声线 = 极短（嗯/我看见了），苏挽声线 = 否决句+嗅觉，林崇声线 = 把字掂一掂再说，赤渊 = 编号排比，裴无咎 = 自嘲+嚼包子，牛阿大 = 全沉默+动作，阿湄 = 计算+备用笑，叶观澜 = 极轻+压字+抹旧痕
4. **先做内容设计，再落句子**：先确定一个可观察的现场冲突、一个角色选择和一个不可逆的新信息；每个段落至少推进其中一项。范章只提供节奏，不提供可复制的句法；禁止整章变成“某物在某处—某人按一下—再解释一次”的动作回声。一个物象只在首次出现和关键回收处出现，重复出现必须改变信息或关系。
5. **反模板硬门**：正文不要使用“方向/位置/那一寸/那一截/那一道”解释人物心理；用门、纸、碗、秤、脚步、气味等具体变化承载选择。不要把动作拆成连续的单字短句堆满整章；短句之间必须有对白、阻力、具体新事实或中段叙述。目标正文 1800–2600 个汉字，宁可写清一场完整交接，也不要用回环凑字数。
6. 保留 frontmatter 的 cast / pov / line / thread / beat / ships 字段（**改 ships 为 ≤60 字一条，不堆叠章号链**），其他字段可以重写；`hook` 必须是本章正文中真实出现的独特动作或对白，禁止写“下一章切下批头一章”一类占位句。
7. 字数 ≥ 1500 字（实际正文汉字数）
8. 只做一次有限编辑回合：读目标章，完成整章写入，然后停下。不要反复重读目标章、不要扫描全仓库、不要启动子代理；外层 runner 会独立执行 lint、strict editorial、硬线和公式/回声扫描。
9. 不要写 prompts/.results 或任何其他文件；只修改 TARGET。不要把命令结果或自报 PASS 写进正文，外层 runner 会独立写 receipt，不能用自报结果放行。

【绝对硬禁】
- ❌ 不写「X 的来处是 Y」「X 的方式不是 X」「是...的那种...」「按完按完」「就第一刹让」「走朝他自己走的」「擦朝苏挽自己擦的」「方向落在」「方向不必替」「不必替上一世」「他自己守」这类公式
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
    p.add_argument("--status", action="store_true", help="Refresh and print current rewrite counts")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--no-dry-run", dest="dry_run", action="store_false")
    p.add_argument("--no-skip-done", action="store_true")
    args = p.parse_args()

    active_season = SE.current_dir()
    if active_season and SS.strict_mode(SS.load_manifest(active_season)):
        print(
            "BLOCKED: engine/batch_rewrite.py is a legacy prose-rewrite dispatcher "
            "and cannot write prompts for a strict season. Use engine/village.py."
        )
        return 2

    if args.status:
        stub_set, stub_by_chapter, error_targets = load_state()
        stub_files = {
            ch: _stub_target_file(ch, stub_by_chapter[ch])
            for ch in stub_by_chapter
        }
        stub_missing = sum(1 for path in stub_files.values() if not path)
        stub_remaining = sum(
            1 for ch, path in stub_files.items()
            if path and not _already_done(ch, target_file=path)
        )
        error_chapters = {_error_target(item)[0] for item in error_targets}
        unfinished = sum(
            1
            for item in error_targets
            if not _already_done(*_error_target(item))
        )
        hidden_duplicates, alternate_errors = _duplicate_error_counts(error_targets)
        print(
            f"stubs_total={len(stub_set)} stubs_remaining={stub_remaining} "
            f"stubs_missing={stub_missing} disease_or_lint_errors={len(error_chapters)} "
            f"error_files={len(error_targets)} unfinished_lint={unfinished} "
            f"hidden_duplicate_errors={hidden_duplicates} "
            f"alternate_error_files={alternate_errors}"
        )
        return

    if args.chapters:
        targets = []
        for ch in parse_chapter_spec(args.chapters):
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
    print("  python engine/run_dispatch.py --workers 2  (one-shot)  or")
    print("  /loop  with cron  (autonomous batch)")


if __name__ == "__main__":
    raise SystemExit(main() or 0)
