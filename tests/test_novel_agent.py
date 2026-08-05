# -*- coding: utf-8 -*-
import json

import pytest
import yaml

from engine import prose_lint, safety_lint, village, writer


def test_full_prose_gate_catches_filler_and_generated_length():
    filler = ("\u5c4b\u91cc\u5f88\u5b89\u9759\u3002" * 20)

    errors, _, metrics = prose_lint.lint_text(filler)

    assert metrics["filler"] == 20
    assert any("\u586b\u5145" in error for error in errors)
    assert "\u586b\u5145" in writer._prose_note(filler)
    assert prose_lint.lint_text("short", min_chars=1500)[0]


def test_prose_gate_catches_repeated_direction_formula():
    text = ("\u4ed6\u7684\u65b9\u5411\u671d\u7740\u95e8\u53e3\u3002" * 7)

    errors, _, metrics = prose_lint.lint_text(text)

    assert metrics["direction_formula"] == 7
    assert any("\u53e5\u5f0f\u56de\u73af" in error for error in errors)


def test_prose_gate_catches_direction_variants_and_self_repair_loop():
    text = (
        "他的方向落在门口。"
        "她的方向不必替上一世守。"
        "他自己守。"
    ) * 4

    errors, _, metrics = prose_lint.lint_text(text)

    assert metrics["direction_formula"] == 8
    assert metrics["self_repair_formula"] == 8
    assert any("自我修复回环" in error for error in errors)


def test_prose_gate_catches_self_referential_way_formula():
    text = (
        "他站着的方式，是他自己那一路。"
        "她问的方式，是那种不肯明说的问。"
    ) * 2

    errors, _, metrics = prose_lint.lint_text(text)

    assert metrics["wall_formula"] >= 4
    assert any("自指解释回环" in error for error in errors)


def test_strict_prose_gate_catches_high_frequency_machine_echo():
    text = ("他把那一寸纸压在案角。" * 30) + ("我自己承担这一笔。" * 18)

    ordinary_errors, _, _ = prose_lint.lint_text(text)
    strict_errors, _, metrics = prose_lint.lint_text(text, strict=True)

    assert not any("物象位置回环" in error for error in ordinary_errors)
    assert metrics["motif_slot"] == 30
    assert metrics["self_claim"] == 18
    assert any("物象位置回环" in error for error in strict_errors)
    assert any("自我承担回环" in error for error in strict_errors)


def test_hardline_lint_catches_explicit_self_harm_and_minor_intimacy():
    text = (
        "\u4ed6\u63d2\u5165\u4e86\u4e00\u53e5\u8bdd\u3002"
        "\u6797\u7a88\u7684\u624b\u8155\u88ab\u4ed6\u63e1\u4f4f\u3002"
        "阿湄亲吻了他。"
        "\u5979\u5272\u8155\u4e86\u3002"
    )

    issues = safety_lint.check(text)

    assert "\u53ef\u80fd\u9732\u9aa8" in issues
    assert "\u53ef\u80fd\u81ea\u4f24" in issues
    assert any("\u6797\u7a88" in issue for issue in issues)
    assert any("阿湄" in issue for issue in issues)


def test_chapter_count_uses_highest_numeric_filename(tmp_path):
    chronicle = tmp_path / "chronicle"
    chronicle.mkdir()
    (chronicle / "001-old.md").write_text("old", encoding="utf-8")
    (chronicle / "ch1000-new.md").write_text("new", encoding="utf-8")
    (chronicle / "INDEX.md").write_text("index", encoding="utf-8")

    assert village.chap_count(str(tmp_path)) == 1000


def test_frontmatter_round_trip_and_chapter_write(tmp_path, monkeypatch):
    out = {
        "chapter_title": "\u95e8\u5f00",
        "chapter": "A chapter body.",
        "frontmatter": {
            "pov": "A",
            "line": "mixed",
            "thread": "the door",
            "beat": "turn",
            "ships": {"AxB": "a mark on the table"},
            "hook": "someone is outside",
        },
    }
    meta = village.build_frontmatter(out, 1001, 1, ["A", "B"], "turn")
    assert village.validate_frontmatter(meta) == []
    assert yaml.safe_load(village.serialize_frontmatter(meta).split("---\n", 2)[1])["chapter"] == 1001

    monkeypatch.chdir(tmp_path)
    sdir = tmp_path / "season"
    village.write_chapter(str(sdir), 1001, out, ["A", "B"], 1, frontmatter=meta)
    written = list((sdir / "chronicle").glob("1001-*.md"))
    assert len(written) == 1
    assert village.read_frontmatter(written[0].read_text(encoding="utf-8"))["hook"] == "someone is outside"
    feed = json.loads((tmp_path / "docs" / "chronicle.json").read_text(encoding="utf-8"))
    assert feed[0]["hook"] == "someone is outside"


def test_frontmatter_rejects_placeholder_title():
    meta = village.build_frontmatter(
        {"chapter": "body", "frontmatter": {"hook": "hook"}},
        1001, 1, ["A", "B"], "turn",
    )

    assert "title" in village.validate_frontmatter(meta)


def test_frontmatter_rejects_self_ship():
    meta = village.build_frontmatter(
        {
            "chapter_title": "门开",
            "chapter": "body",
            "frontmatter": {"hook": "hook", "ships": {"A×A": "self"}},
        },
        1001, 1, ["A", "B"], "turn",
    )

    assert any(error.startswith("ships.A×A") for error in village.validate_frontmatter(meta))


def test_editorial_metadata_requires_evidence_and_publish_score():
    meta = village.build_frontmatter(
        {"chapter_title": "门开", "chapter": "body", "frontmatter": {"hook": "hook"}},
        1001, 1, ["A", "B"], "turn",
    )

    assert village.validate_editorial_metadata(meta) == ["review", "score"]
    meta["review"] = "这是一段包含正文引句、范文对照、人物行动证据、节奏判断和明确修复方向的审稿证据。"
    meta["score"] = "11/14"
    assert village.validate_editorial_metadata(meta) == ["score<12"]
    meta["score"] = "12/14"
    assert village.validate_editorial_metadata(meta) == []


def test_editorial_metadata_quote_must_exist_in_body():
    meta = {
        "review": "正文证据：「门外的雪停了」；人物行动和钩子成立，节奏有停顿，关系有变化，后续需兑现门外来人。",
        "score": "12/14",
    }
    assert village.validate_editorial_metadata(meta, body="门外的雪停了，门闩没有动。") == []
    assert village.validate_editorial_metadata(meta, body="屋里只剩一盏灯。") == ["review evidence"]


def test_write_chapter_rejects_invalid_frontmatter_before_side_effects(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="frontmatter"):
        village.write_chapter(
            str(tmp_path / "season"), 1,
            {"chapter_title": "无题", "chapter": "body"},
            ["A", "B"], 1,
        )

    assert not (tmp_path / "season").exists()
    assert not (tmp_path / "docs").exists()


def test_recent_context_prefers_newest_hooks(tmp_path):
    chronicle = tmp_path / "chronicle"
    chronicle.mkdir()
    for number, title, hook in ((1000, "old", "old hook"), (1001, "new", "new hook")):
        meta = {
            "season": 1, "chapter": number, "title": title,
            "cast": ["A"], "pov": "A", "line": "mixed",
            "thread": title, "beat": "turn", "ships": {}, "hook": hook,
        }
        (chronicle / f"ch{number}-{title}.md").write_text(
            village.serialize_frontmatter(meta) + "\nbody\n", encoding="utf-8"
        )

    context = village.recent_chapter_context(str(tmp_path), limit=2)

    assert context.index("new hook") < context.index("old hook")
    assert village.recent_hooks(str(tmp_path), limit=2) == ["new hook", "old hook"]


def test_prose_review_failure_is_not_a_pass(monkeypatch):
    def fail(*args, **kwargs):
        raise RuntimeError("offline")

    monkeypatch.setattr(writer.llm, "complete", fail)

    result = writer.prose_review("body")

    assert result["verdict"] == "fail"
    assert result["problems"]


def test_critique_recomputes_total_and_fails_mismatch(monkeypatch):
    monkeypatch.setattr(
        writer,
        "_json_call",
        lambda *args, **kwargs: {
            "scores": {field: 0 for field in writer.SCORE_FIELDS},
            "total": 14,
            "safe": True,
            "review": "正文证据足够长的一段审校说明，包含动作、钩子和下一步修复方向。",
        },
    )

    result = writer.critique("正文", {}, "暧昧")

    assert result["total"] == 0
    assert result["_failed"] is True
    assert result["safe"] is False


def test_structured_call_retries_malformed_json(monkeypatch):
    responses = iter(["not json", '{"ok": true}'])
    monkeypatch.setattr(writer.llm, "complete", lambda *args, **kwargs: next(responses))

    assert writer._json_call("request", scene_weight=3) == {"ok": True}


def test_best_opening_ignores_malformed_candidates(monkeypatch):
    monkeypatch.setattr(
        writer,
        "_json_call",
        lambda *args, **kwargs: {"candidates": [None, {"opening": "hook", "intensity": 8}]},
    )

    assert writer.best_opening("context", {}, "暧昧")["opening"] == "hook"


def test_tick_provider_failure_is_a_clean_noop(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(village.C, "load_state", lambda name: {})
    monkeypatch.setattr(village, "pick_cast", lambda *args: (["A", "B"], [], 3))
    monkeypatch.setattr(village, "build_prompt", lambda *args: "context")
    monkeypatch.setattr(village.SE, "beat_line", lambda arc: "beat")

    def fail(*args, **kwargs):
        raise RuntimeError("provider down")

    monkeypatch.setattr(village.writer, "compose", fail)
    village.tick(
        {"target_chapter_chars": 1500, "newcomer_priority": True},
        {"A": {}, "B": {}}, str(tmp_path),
        {"season": 1, "rating": "暧昧"}, {}, {}, 0.2,
    )

    assert "generation rejected" in capsys.readouterr().out
    assert not (tmp_path / "chronicle").exists()
    assert not (tmp_path / "docs").exists()


def test_tick_mock_writes_numbered_frontmatter(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VILLAGE_MOCK", "1")
    monkeypatch.setattr(writer, "_log_hit", lambda *args, **kwargs: None)
    monkeypatch.setattr(village.C, "load_state", lambda name: {})
    monkeypatch.setattr(village.C, "save_state", lambda name, state: None)
    monkeypatch.setattr(village.C, "add_memory", lambda *args, **kwargs: None)
    monkeypatch.setattr(village, "pick_cast", lambda *args: (["A", "B"], [], 3))
    monkeypatch.setattr(
        village, "build_prompt", lambda *args: "姓名: A（他）\n姓名: B（她）"
    )
    monkeypatch.setattr(village.SE, "beat_line", lambda arc: "turn")
    monkeypatch.setattr(village.SE, "apply_update", lambda ties, update: None)
    monkeypatch.setattr(village.SE, "save_ties", lambda sdir, ties: None)
    monkeypatch.setattr(village.SE, "advance_arc", lambda sdir, arc, step: None)

    sdir = tmp_path / "season"
    village.tick(
        {"target_chapter_chars": 10, "newcomer_priority": True, "chapters_per_beat": 3},
        {"A": {}, "B": {}}, str(sdir),
        {"season": 1, "title": "test", "genre": "x", "rating": "暧昧"},
        {}, {"beats": [], "beat": 0}, 0.2,
    )

    written = list((sdir / "chronicle").glob("0001-*.md"))
    assert len(written) == 1
    meta = village.read_frontmatter(written[0].read_text(encoding="utf-8"))
    assert village.validate_frontmatter(meta) == []
    assert village.validate_editorial_metadata(meta) == []
    assert meta["score"] == "12/14"


def test_mock_draft_contains_frontmatter(monkeypatch):
    monkeypatch.setenv("VILLAGE_MOCK", "1")
    ctx = "\u59d3\u540d: \u7532(\u4ed6)\n\u59d3\u540d: \u4e59(\u5979)"

    out = writer.draft(ctx, {}, {}, 10, "\u66a7\u6627")

    assert set((out.get("frontmatter") or {})) >= {
        "pov", "line", "thread", "beat", "ships", "hook"
    }
