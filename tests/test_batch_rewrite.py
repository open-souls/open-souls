# -*- coding: utf-8 -*-
from pathlib import Path
import subprocess
import sys

from engine import batch_rewrite, village
from tools import review_batch


def _chapter(number, title, body, *, editorial=False, branch=None):
    meta = {
        "season": 1,
        "chapter": number,
        "title": title,
        "cast": ["A", "B"],
        "pov": "A",
        "line": "混合",
        "thread": title,
        "beat": "转·本回",
        "ships": {"A×B": "账页边沿的一道新痕"},
        "hook": f"{title} 的门外有声音",
    }
    if editorial:
        meta["review"] = (
            "正文证据：账页边沿的新痕；对照范文的动作留白；"
            "人物主动把信压回案角；节奏通过；下一步落实门外来人。"
        )
        meta["score"] = "12/14"
    if branch:
        meta["branch"] = branch
    return village.serialize_frontmatter(meta) + f"\n# 第{number}回 · {title}\n\n{body}\n"


def test_duplicate_selection_prefers_passing_branch_over_larger_broken_branch(tmp_path, monkeypatch):
    chronicle = tmp_path / "chronicle"
    chronicle.mkdir()
    good_body = "他把账页压在案角，门外的雪又落了一层。\n\n" * 90
    bad_body = "他的方向朝着门口。\n\n" * 100
    good = chronicle / "ch999-通过.md"
    bad = chronicle / "ch999-更大但坏.md"
    good.write_text(_chapter(999, "通过", good_body, editorial=True), encoding="utf-8")
    bad.write_text(_chapter(999, "更大但坏", bad_body), encoding="utf-8")

    monkeypatch.setattr(review_batch, "CHRONICLE", str(chronicle))
    monkeypatch.setattr(batch_rewrite, "CHRONICLE", chronicle)

    selected = review_batch.find_files([999], strict_editorial=True)
    assert Path(selected[0][1]).name == good.name
    assert Path(batch_rewrite._chapter_file(999)).name == good.name


def test_duplicate_selection_keeps_canonical_branch_as_edit_target(tmp_path, monkeypatch):
    chronicle = tmp_path / "chronicle"
    chronicle.mkdir()
    canonical_body = "他把账页压在案角，门外的雪又落了一层。\n\n" * 40
    alternate_body = "他把旧信收进袖中，门外的灯没有灭。\n\n" * 100
    canonical = chronicle / "ch998-主线.md"
    alternate = chronicle / "ch998-支线.md"
    canonical.write_text(
        _chapter(998, "主线", canonical_body, editorial=True), encoding="utf-8"
    )
    alternate.write_text(
        _chapter(998, "支线", alternate_body, editorial=True, branch="alternate"),
        encoding="utf-8",
    )

    monkeypatch.setattr(batch_rewrite, "CHRONICLE", chronicle)

    assert Path(batch_rewrite._chapter_file(998)).name == canonical.name


def test_picker_reaches_manifest_stubs_outside_legacy_range(monkeypatch):
    monkeypatch.setattr(
        batch_rewrite,
        "load_state",
        lambda: (
            {"251", "858"},
            {251: None, 858: None},
            [],
        ),
    )
    monkeypatch.setattr(
        batch_rewrite,
        "_chapter_file",
        lambda chapter: {251: "old.md", 858: "new.md"}.get(chapter),
    )
    monkeypatch.setattr(batch_rewrite, "_already_done", lambda _chapter, target_file=None: False)

    selected = batch_rewrite.pick_targets(1, stubs_only=True)

    assert selected == [("stub", 251, "old.md")]


def test_picker_skips_manifest_only_stub_without_file(monkeypatch):
    monkeypatch.setattr(
        batch_rewrite,
        "load_state",
        lambda: ({"251", "858"}, {251: None, 858: None}, []),
    )
    monkeypatch.setattr(
        batch_rewrite,
        "_chapter_file",
        lambda chapter: {251: None, 858: "new.md"}.get(chapter),
    )
    monkeypatch.setattr(batch_rewrite, "_already_done", lambda _chapter, target_file=None: False)

    selected = batch_rewrite.pick_targets(1, stubs_only=True)

    assert selected == [("stub", 858, "new.md")]


def test_tick_score_is_derived_from_critique_not_payload():
    out = {
        "chapter_title": "门开",
        "chapter": "正文",
        "frontmatter": {
            "hook": "门外有声音",
            "ships": {"A×B": "门槛上的灰"},
            "score": "14/14",
            "review": "模型自己写的高分说明，不能作为独立审校证据。",
        },
    }
    crit = {
        "total": 11,
        "review": "独立审校证据：引用正文‘门槛上的灰’，对照范文动作留白，人物行动成立，但建议压低解释句。",
    }

    meta = village.build_frontmatter(out, 1001, 1, ["A", "B"], "转·本回", crit=crit)

    assert meta["score"] == "11/14"
    assert meta["review"] == crit["review"]
    assert village.validate_editorial_metadata(meta) == ["score<12"]


def test_review_batch_range_argument_advances_and_exits():
    result = subprocess.run(
        [
            sys.executable,
            "tools/review_batch.py",
            "--strict-editorial",
            "ch999",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "ch999" in result.stdout


def test_dispatch_prompt_uses_bounded_inline_context():
    target = str(Path("seasons/01-xianxia/chronicle/ch898-林彻站.md"))

    prompt = batch_rewrite.build_prompt(898, target)

    assert "有界角色快照" in prompt
    assert "有界片段" in prompt
    assert "prompts/.results" in prompt
    assert "不要再打开其他章节" in prompt
    assert "先做内容设计，再落句子" in prompt
    assert "禁止写“下一章切下批头一章”" in prompt
    context = prompt.split("【你要做的】", 1)[0]
    assert "的方式不是" not in context
    assert "方向朝着" not in context
    assert "TARGET_FILE:" in prompt
    assert len(prompt) < 16000


def test_lint_error_parser_keeps_exact_duplicate_path(tmp_path, monkeypatch):
    chronicle = tmp_path / "chronicle"
    chronicle.mkdir()
    target = chronicle / "ch857-灶边雪.md"
    target.write_text("正文", encoding="utf-8")
    monkeypatch.setattr(batch_rewrite, "ROOT", tmp_path)

    records = batch_rewrite._parse_lint_error_targets(f"✗ {target}\n   ERROR  broken")

    assert records == [(857, str(target))]


def test_cached_lint_error_targets_reuses_unchanged_file(tmp_path, monkeypatch):
    chronicle = tmp_path / "chronicle"
    chronicle.mkdir()
    target = chronicle / "ch857-坏.md"
    target.write_text("---\nchapter: 857\n---\n\n他的方向落在门口。\n", encoding="utf-8")
    monkeypatch.setattr(batch_rewrite, "ROOT", tmp_path)
    monkeypatch.setattr(batch_rewrite, "CHRONICLE", chronicle)
    monkeypatch.setattr(batch_rewrite, "STUB_MANIFEST", chronicle / "_STUB_MANIFEST.json")
    calls = []

    def fake_lint(path):
        calls.append(path)
        return (["broken"], [], {"chars": 10})

    monkeypatch.setattr(batch_rewrite.PL, "lint_file", fake_lint)
    first = batch_rewrite._cached_lint_error_targets()
    second = batch_rewrite._cached_lint_error_targets()

    assert first == [(857, str(target))]
    assert second == first
    assert calls == [str(target)]


def test_cached_lint_error_targets_invalidates_on_content_change(tmp_path, monkeypatch):
    chronicle = tmp_path / "chronicle"
    chronicle.mkdir()
    target = chronicle / "ch857-坏.md"
    target.write_text("---\nchapter: 857\n---\n\n旧内容。\n", encoding="utf-8")
    monkeypatch.setattr(batch_rewrite, "ROOT", tmp_path)
    monkeypatch.setattr(batch_rewrite, "CHRONICLE", chronicle)
    monkeypatch.setattr(batch_rewrite, "STUB_MANIFEST", chronicle / "_STUB_MANIFEST.json")
    calls = []

    def fake_lint(path):
        calls.append(path)
        return (["broken"], [], {"chars": 10})

    monkeypatch.setattr(batch_rewrite.PL, "lint_file", fake_lint)
    batch_rewrite._cached_lint_error_targets()
    target.write_text(target.read_text(encoding="utf-8") + "新内容。\n", encoding="utf-8")
    batch_rewrite._cached_lint_error_targets()

    assert calls == [str(target), str(target)]


def test_picker_surfaces_failing_duplicate_even_when_canonical_passes(tmp_path, monkeypatch):
    chronicle = tmp_path / "chronicle"
    chronicle.mkdir()
    good_body = "他把账页压在案角，门外的雪又落了一层。\n\n" * 90
    bad_body = "他的方向朝着门口。\n\n" * 100
    good = chronicle / "ch857-不收回.md"
    bad = chronicle / "ch857-灶边雪.md"
    good.write_text(_chapter(857, "不收回", good_body, editorial=True), encoding="utf-8")
    bad.write_text(_chapter(857, "灶边雪", bad_body), encoding="utf-8")

    monkeypatch.setattr(batch_rewrite, "CHRONICLE", chronicle)
    monkeypatch.setattr(
        batch_rewrite,
        "load_state",
        lambda: (set(), {}, [(857, str(bad))]),
    )

    selected = batch_rewrite.pick_targets(1, disease_only=True)

    assert selected == [("disease", 857, str(bad))]
    assert batch_rewrite._duplicate_error_counts([(857, str(bad))]) == (1, 0)
