# -*- coding: utf-8 -*-
"""Unit tests for tools/jinjiang_chapter_distance.py.

Locks the dual-track scoring contract:
  * Engineering 5 dimensions are deterministic for the same body text.
  * R-track returns None when no L2 evidence exists, regardless of L1 files.
  * The publish / blowup / addictive gates all key off min(E, R) and refuse
    to clear when R-track is missing.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "jinjiang_chapter_distance.py"


def _load():
    spec = importlib.util.spec_from_file_location("jinjiang_chapter_distance", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def module_loaded():
    return _load()


def _body_with(action_count, has_resistance, decision_count, named, hook_signal):
    body_lines = ["开场。"]
    verbs = ["走", "拿", "放", "递", "收", "拆", "开", "关", "挡", "写"]
    for i in range(action_count):
        body_lines.append(f"第{i}段。人物{verbs[i % len(verbs)]}了某物。")
    if has_resistance:
        body_lines[-1] = body_lines[-1].replace("某物", "某物，但他不肯接")
    decision_words = ["决定", "主动", "不再", "签下"]
    for i in range(decision_count):
        body_lines.append(f"中段{decision_words[i % len(decision_words)]}了一件事。")
    # 末段必须触发 E6 钩子枚举,否则 strong 的 E6 会被压回 4。
    body_lines.append("末段。她递出那封信，等一句回答。")
    body = "\n\n".join(body_lines)
    for c in named:
        body = body.replace("人物", c)
    return body


def test_e_score_exposes_hook_type_and_pov_initiator(module_loaded):
    body = (
        "林夙看见林彻。林夙决定亲自去问。\n\n"
        "林夙签下那卷旧账。\n\n"
        "林彻把旧账递来，林夙没有接。\n\n"
        "她没有回答。"
    )
    scores = module_loaded.e_score(body, {"hook_signal": True}, pov_name="林夙")

    assert scores["E5_pov_initiator"] == 10.0
    assert scores["E6_hook_label"] == "creepy"
    assert scores["E6_hook_type"] == 8


def test_e_score_does_not_mix_diagnostic_pov_ratio_into_engineering_min(module_loaded):
    body = "林夙看见林彻。\n\n林彻把旧账放下。\n\n屋里很静。"
    scores = module_loaded.e_score(body, {}, pov_name="林夙")
    numeric_engineering = {
        key: value
        for key, value in scores.items()
        if isinstance(value, (int, float)) and key != "E5_pov_initiator"
    }

    assert min(numeric_engineering.values()) >= 4
    assert scores["E5_pov_initiator"] == 0.0


def test_e_score_recognizes_concrete_agency_without_magic_keywords(module_loaded):
    body = "\n\n".join([
        "东堂外门。",
        "林彻把笔尖压在见证人一栏旁，先封住东堂东架。",
        "他按下旧印，给周平两条路：进去取册，或关门登记。",
        "林彻站在门槛边。",
    ])
    scores = module_loaded.e_score(body, {"hook_signal": True})
    assert scores["E4_agency"] >= 7
    assert scores["E5_relationship_cost"] >= 6


def test_e_score_deterministic(module_loaded):
    body = _body_with(8, True, 4, ["苏挽", "林夙"], True)
    e1 = module_loaded.e_score(body, {"hook_signal": True})
    e2 = module_loaded.e_score(body, {"hook_signal": True})
    assert e1 == e2
    assert all(0 <= v <= 10 for v in e1.values() if isinstance(v, (int, float)))


def test_e_score_rewards_action_and_decision(module_loaded):
    weak = module_loaded.e_score(_body_with(0, False, 0, [], False), {"hook_signal": False})
    strong = module_loaded.e_score(_body_with(8, True, 4, ["苏挽", "林夙", "阿湄"], True), {"hook_signal": True})
    weak_numeric = {
        key: value
        for key, value in weak.items()
        if isinstance(value, (int, float)) and key != "E5_pov_initiator"
    }
    strong_numeric = {
        key: value
        for key, value in strong.items()
        if isinstance(value, (int, float)) and key != "E5_pov_initiator"
    }
    assert min(strong_numeric.values()) > min(weak_numeric.values())
    assert strong["E3_hook_stop"] == 10
    assert weak["E3_hook_stop"] == 4


def test_r_score_missing_when_no_panel(module_loaded):
    r, reason = module_loaded.r_score(9999, {})
    assert r is None
    assert "no reader" in reason


def test_r_score_present_when_l2_signal(module_loaded):
    # Three personas, each clearing one R dimension the others miss.
    panel = {42: {"l1": [], "l2": [
        {"persona_id": "3", "stay_to_50": True, "love_relation": None,
         "next_chapter_focus": {"chapter": "99"}, "pattern_flags": {}},
        {"persona_id": "4", "stay_to_50": True, "love_relation": "A×B",
         "next_chapter_focus": {"chapter": "42"}, "pattern_flags": {}},
    ]}}
    r, reason = module_loaded.r_score(42, panel)
    assert r is not None
    assert reason == "ok"
    # R1 = 7.5 (persona 3 stays), R2 = 7.5 (persona 4 points at 42),
    # R3 = 7.5 (persona 4 names a relationship), R4 = 7.5 (persona 4 stays),
    # R5 = 7.5 (no smart_drop / passive_chain).
    assert all(v >= 7.5 for v in r.values())


def test_gates_refuse_without_r_track(module_loaded):
    g = module_loaded.gates(9.5, None)
    assert g["r_track_present"] is False
    assert g["publish"] is False
    assert g["blowup_chapter"] is False
    assert g["addictive_chapter"] is False


def test_gates_pass_when_combined_high(module_loaded):
    g = module_loaded.gates(9.0, 8.5)
    assert g["publish"] is True
    assert g["blowup_chapter"] is True
    assert g["addictive_chapter"] is True


def test_gates_addictive_requires_high_R(module_loaded):
    # Combined >= blowup floor but R just under the addictive R floor.
    # R = 7.4, E = 9.0 -> combined = 7.4, < blowup floor (8.5). So neither gate clears.
    g_low_r = module_loaded.gates(9.0, 7.4)
    assert g_low_r["blowup_chapter"] is False
    assert g_low_r["addictive_chapter"] is False
    # R = 7.6 (above ADDICT_R_FLOOR), E = 9.5 -> combined = 7.6, still < 8.5
    g_mid_r = module_loaded.gates(9.5, 7.6)
    assert g_mid_r["blowup_chapter"] is False
    # R = 9.0, E = 9.5 -> combined 9.0 >= 8.5 AND R >= 7.5 -> addictive passes
    g_high = module_loaded.gates(9.5, 9.0)
    assert g_high["blowup_chapter"] is True
    assert g_high["addictive_chapter"] is True


def test_read_chapter_strips_all_frontmatter_blocks(module_loaded, tmp_path):
    """A chronicle with two consecutive --- ... --- blocks must drop both.

    Old regex only matched the first block, so review metadata leaked into
    body and inflated DECISION counts (E4/E5 false positives).
    """
    p = tmp_path / "ch.md"
    p.write_text(
        "---\n"
        "season: 5\n"
        "chapter: 777\n"
        "title: test\n"
        "pov: 苏挽\n"
        "---\n"
        "review: >-\n"
        "  旧稿 139 把「改成」计进正文，导致 E4 假阳性。本改砍掉这段。\n"
        "  末段「阿湄昨夜那张油纸」同步改成「阿湄昨夜那四个字的小纸」。\n"
        "---\n"
        "\n"
        "# 第七百七十七回 · 测试\n"
        "\n"
        "她开窗。院门那辆车没动。\n",
        encoding="utf-8",
    )
    n, pov, body = module_loaded.read_chapter(p)
    assert n == 777
    assert pov == "苏挽"
    # body must NOT contain review YAML metadata
    assert "review" not in body
    assert "改成" not in body
    assert "小纸" not in body
    # body must contain the actual opening
    assert "她开窗" in body


def test_read_chapter_strips_review_block_decisions(module_loaded, tmp_path):
    """End-to-end: read_chapter must drop review-block DECISION hits.

    Locks the ch504 bug where review metadata such as
    「改成」「主动」「签下」 were counted as 正文 agency in E4 and E5.
    """
    audit = {"hook_signal": True}
    p1 = tmp_path / "ch_decision.md"
    p1.write_text(
        "---" + chr(10) +
        "chapter: 888" + chr(10) +
        "pov: 苏挽" + chr(10) +
        "---" + chr(10) + chr(10) +
        "开场。她走出门。他接了她。" + chr(10) + chr(10) +
        "review: >-" + chr(10) +
        "  本改把「改成」「主动」「签下」从 review 块里清掉。" + chr(10) + chr(10) +
        "末段。她递出最后那封信。" + chr(10),
        encoding="utf-8",
    )
    _, _, body1 = module_loaded.read_chapter(p1)
    e_real = module_loaded.e_score(body1, audit)

    p2 = tmp_path / "ch_clean.md"
    p2.write_text(
        "---" + chr(10) +
        "chapter: 889" + chr(10) +
        "pov: 苏挽" + chr(10) +
        "---" + chr(10) + chr(10) +
        "开场。她走出门。他接了她。" + chr(10) + chr(10) +
        "末段。她递出最后那封信。" + chr(10),
        encoding="utf-8",
    )
    _, _, body2 = module_loaded.read_chapter(p2)
    e_clean = module_loaded.e_score(body2, audit)

    assert e_real["E4_agency"] == e_clean["E4_agency"]
    assert e_real["E5_relationship_cost"] == e_clean["E5_relationship_cost"]

def test_strip_post_review_no_op_when_review_inside_paragraph(module_loaded):
    """_strip_post_review must not eat a review mention that lives in prose."""
    raw = (
        "开场。她走出门。\n"
        "\n"
        "末段。她在 review 会上递出那封信。\n"
    )
    out = module_loaded._strip_post_review(raw)
    assert out == raw

