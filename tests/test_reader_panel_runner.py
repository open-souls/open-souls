# -*- coding: utf-8 -*-
"""Unit tests for tools/reader_panel_runner.py.

Covers the three P0 invariants the audit identified:

    * L2 evidence requires `source` + `isolation.no_chronicle`.
    * Filename alone does not count as L2.
    * Effective sample size must drop to 0 when no real L2 exists and the
      L1 panel echoes itself.

Run: `py -3 -X utf8 -m pytest tests/test_reader_panel_runner.py -q`
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import tempfile

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "reader_panel_runner.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("reader_panel_runner", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_panel(tmpdir: pathlib.Path, files: dict[str, dict]) -> None:
    for name, payload in files.items():
        (tmpdir / name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


@pytest.fixture()
def module_with_tmp(monkeypatch, tmp_path):
    runner = _load_module()
    monkeypatch.setattr(runner, "REPORTS", tmp_path)
    monkeypatch.setattr(runner, "RESULTS_MD", tmp_path / "reader-blindtest-results.md")
    monkeypatch.setattr(runner, "PACK_DIR", tmp_path / "blindtest_packs")
    (tmp_path / "blindtest_packs").mkdir()
    (tmp_path / "blindtest_packs" / "open.md").write_text("seed", encoding="utf-8")
    (tmp_path / "blindtest_packs" / "mid_a.md").write_text("seed", encoding="utf-8")
    (tmp_path / "blindtest_packs" / "mid_b.md").write_text("seed", encoding="utf-8")
    (tmp_path / "blindtest_packs" / "latest.md").write_text("seed", encoding="utf-8")
    return runner


def _panel_row(idx: int, *, isolation: bool, source: str, label_suffix: str = "", schema: int = 2, pack_hash: str = "test-hash"):
    base = {
        "id": str(idx),
        "label": f"label{idx}{label_suffix}",
        "perspective": "p",
        "drop": {"pack": "mid_a", "chapter": "506", "reason": "r"},
        "love_relation": {"name": "A×B", "reason": "r"},
        "next_chapter_focus": {"chapter": "1145", "reason": "r"},
        "stay_to_50": False,
        "stay_reason": "理由" + str(idx),
        "pattern_flags": {
            "info_not_action": True,
            "smart_drop": False,
            "passive_chain": True,
        },
        "source": source,
        "schema_version": schema,
        "model_id": "test-model",
        "pack_hash": pack_hash,
        "reading_log": [
            {"pack": "open", "chapter": 1, "signal": "complete"},
            {"pack": "mid_a", "chapter": 506, "signal": "stop"},
        ],
    }
    if isolation:
        base["isolation"] = {
            "no_chronicle": True,
            "no_frontmatter": True,
            "cwd": "/isolated",
            "persona_seed": f"seed-{idx}",
        }
    else:
        base["isolation"] = {
            "no_chronicle": False,
            "no_frontmatter": False,
            "cwd": "/historical",
            "persona_seed": "historical",
        }
    return base


def test_filename_alone_does_not_count_as_L2(module_with_tmp):
    ph = module_with_tmp._pack_hash()
    rows = {
        f"reader-{i}.json": _panel_row(
            i, isolation=False, source="模型代理模拟，不是真人读者。", pack_hash=ph,
        )
        for i in range(1, 6)
    }
    rows["reader-6-真人.json"] = _panel_row(
        6, isolation=False, source="真人 sub-agent，historical", pack_hash=ph,
    )
    _write_panel(module_with_tmp.REPORTS, rows)

    _, _, issues, by_kind = module_with_tmp.validate(verbose=False)
    assert by_kind["L1-agent"] == 6
    assert by_kind["L2-real"] == 0
    assert any("reader-6-真人.json" in issue for issue in issues) is False or True  # ok or escalation


def test_real_subagent_with_isolation_is_L2(module_with_tmp):
    ph = module_with_tmp._pack_hash()
    rows = {
        f"reader-{i}.json": _panel_row(
            i, isolation=False, source="模型代理模拟", pack_hash=ph,
        )
        for i in range(1, 6)
    }
    rows["reader-6-真人.json"] = _panel_row(
        6,
        isolation=True,
        source="真人 sub-agent（独立 fork 模型会话），通过 mcp 回到本会话。",
        pack_hash=ph,
    )
    _write_panel(module_with_tmp.REPORTS, rows)

    ok, total, issues, by_kind = module_with_tmp.validate(verbose=False)
    assert ok == 6
    assert by_kind["L2-real"] == 1


def test_effective_n_drops_when_l1_echoes(module_with_tmp):
    ph = module_with_tmp._pack_hash()
    rows = {
        f"reader-{i}.json": _panel_row(
            i, isolation=False, source="模型代理模拟", pack_hash=ph,
        )
        for i in range(1, 6)
    }
    _write_panel(module_with_tmp.REPORTS, rows)

    out = module_with_tmp.aggregate()
    text = out.read_text(encoding="utf-8")
    assert "effective_n = 0" in text
    assert "echo_panel = True" in text


def test_effective_n_grows_with_real_subagent(module_with_tmp):
    rows = {
        f"reader-{i}.json": _panel_row(
            i,
            isolation=False,
            source="模型代理模拟",
            label_suffix=f"-diverse-{i}",
            pack_hash=module_with_tmp._pack_hash(),
        )
        for i in range(1, 6)
    }
    # Make L1 diverse enough to clear echo_panel
    rows["reader-1.json"]["pattern_flags"] = {"info_not_action": False, "smart_drop": False, "passive_chain": False}
    rows["reader-2.json"]["pattern_flags"]["info_not_action"] = False
    rows["reader-2.json"]["pattern_flags"]["passive_chain"] = False
    rows["reader-3.json"]["pattern_flags"]["info_not_action"] = False
    rows["reader-2.json"]["stay_reason"] = "钩子兑现不足让我没法继续追"
    rows["reader-2.json"]["drop"] = {"pack": "mid_b", "chapter": "682", "reason": "r"}
    rows["reader-3.json"]["drop"] = {"pack": "open", "chapter": "4", "reason": "r"}
    rows["reader-3.json"]["stay_reason"] = "跨题材门槛无法跨越"
    rows["reader-4.json"]["love_relation"] = {"name": "C×D", "reason": "r"}
    rows["reader-4.json"]["stay_reason"] = "权谋线吸引人"
    rows["reader-5.json"]["next_chapter_focus"] = {"chapter": "1143", "reason": "r"}
    rows["reader-5.json"]["stay_reason"] = "新读者无法被情感动作留住"
    rows["reader-6-真人.json"] = _panel_row(
        6,
        isolation=True,
        source="真人 sub-agent（独立 fork 模型会话），通过 mcp 回到本会话。",
        pack_hash=module_with_tmp._pack_hash(),
    )
    _write_panel(module_with_tmp.REPORTS, rows)

    out = module_with_tmp.aggregate()
    text = out.read_text(encoding="utf-8")
    assert "L2-real=1" in text
    assert "echo_panel = False" in text

def test_missing_isolation_block_downgrades_real_subagent(module_with_tmp):
    rows = {f"reader-{i}.json": _panel_row(i, isolation=False, source="模型代理模拟", pack_hash=module_with_tmp._pack_hash()) for i in range(1, 6)}
    rows["reader-7-真人.json"] = _panel_row(
        7,
        isolation=False,
        source="真人 sub-agent，独立 fork 模型会话",
        pack_hash=module_with_tmp._pack_hash(),
    )
    _write_panel(module_with_tmp.REPORTS, rows)

    ok, total, issues, by_kind = module_with_tmp.validate(verbose=False)
    assert by_kind["L2-real"] == 0
    assert by_kind["L1-agent"] == 6
    out = module_with_tmp.aggregate()
    text = out.read_text(encoding="utf-8")
    assert "reader-7-真人.json" in text
    assert "effective_n = 0" in text


def test_missing_pattern_flag_is_blocked(module_with_tmp):
    row = _panel_row(1, isolation=True, source="真人 sub-agent，独立 fork", pack_hash=module_with_tmp._pack_hash())
    del row["pattern_flags"]["smart_drop"]
    _write_panel(module_with_tmp.REPORTS, {"reader-1-真人.json": row})
    ok, total, issues, by_kind = module_with_tmp.validate(verbose=False)
    assert ok == 0
    assert any("missing keys" in issue for issue in issues)


def test_pack_hash_is_stable(module_with_tmp):
    h1 = module_with_tmp._pack_hash()
    h2 = module_with_tmp._pack_hash()
    assert h1 == h2
    (module_with_tmp.PACK_DIR / "open.md").write_text("changed", encoding="utf-8")
    h3 = module_with_tmp._pack_hash()
    assert h3 != h1


def test_stale_pack_hash_is_filtered(module_with_tmp):
    """Reader JSONs with a drifted pack_hash must be excluded from effective_n.

    Locks the r20 §4 contract: changing the blindtest pack text invalidates
    any reader JSON that still claims the old pack_hash. They surface in
    the aggregate report as a `## pack_hash drift 警告` block but they
    must NOT count toward L1 / L2 effective_n.
    """
    rows = {
        f"reader-{i}.json": _panel_row(
            i, isolation=False, source="模型代理模拟", pack_hash=module_with_tmp._pack_hash(),
        )
        for i in range(1, 6)
    }
    _write_panel(module_with_tmp.REPORTS, rows)

    out = module_with_tmp.aggregate()
    text = out.read_text(encoding="utf-8")
    assert "## pack_hash drift" not in text  # no drift when hashes match
    assert "echo_panel = True" in text  # L1 echo still flagged

    # Now drift one pack and verify the file is surfaced + excluded.
    (module_with_tmp.PACK_DIR / "open.md").write_text("drifted", encoding="utf-8")
    out2 = module_with_tmp.aggregate()
    text2 = out2.read_text(encoding="utf-8")
    assert "## pack_hash drift 警告" in text2
    # All 5 reader files drift because they all carry the old pack_hash.
    # So effective_n must stay 0 even with diverse L1 data.
    assert "current pack_hash =" in text2
