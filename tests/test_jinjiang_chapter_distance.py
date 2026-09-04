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
    body_lines.append("末段。她递出最后那封信。")
    body = "\n\n".join(body_lines)
    for c in named:
        body = body.replace("人物", c)
    return body


def test_e_score_deterministic(module_loaded):
    body = _body_with(8, True, 4, ["苏挽", "林夙"], True)
    e1 = module_loaded.e_score(body, {"hook_signal": True})
    e2 = module_loaded.e_score(body, {"hook_signal": True})
    assert e1 == e2
    assert all(0 <= v <= 10 for v in e1.values())


def test_e_score_rewards_action_and_decision(module_loaded):
    weak = module_loaded.e_score(_body_with(0, False, 0, [], False), {"hook_signal": False})
    strong = module_loaded.e_score(_body_with(8, True, 4, ["苏挽", "林夙", "阿湄"], True), {"hook_signal": True})
    assert min(strong.values()) > min(weak.values())
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
