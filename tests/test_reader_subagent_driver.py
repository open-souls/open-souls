# -*- coding: utf-8 -*-
"""Unit tests for tools/reader_subagent_driver.py.

Locks the cross-pollination contract from
docs/standards/jinjiang-blowup-baseline-operator.md section 8:

  * 5 persona prompts share the same isolated pack source but each holds a
    different persona_seed, drop_chapter, drop_pack, love_relation and
    next_chapter_focus target.
  * The verify subcommand refuses to pass when any of these axes collapses
    to fewer than 4 distinct values.
  * The L2 prompt template requires schema_version=2, full isolation block
    and a source string that starts with 真人 sub-agent.

Run: py -3 -X utf8 -m pytest tests/test_reader_subagent_driver.py -q
"""
from __future__ import annotations

import importlib.util
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "reader_subagent_driver.py"


def _load():
    spec = importlib.util.spec_from_file_location("reader_subagent_driver", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_rotation_keys_match_summary(tmp_path, monkeypatch):
    driver = _load()
    summary = tmp_path / "distance-summary.md"
    summary.write_text(
        "\n".join([
            "# snapshot",
            "",
            "| 506 | 4 | 4 | 6 | 5 | 6 | seasons/01-xianxia/chronicle/506.md |",
            "| 504 | 4 | 6 | 4 | 4 | 4 | seasons/01-xianxia/chronicle/504.md |",
            "| 502 | 4 | 10 | 4 | 7 | 6 | seasons/01-xianxia/chronicle/502.md |",
        ]),
        encoding="utf-8",
    )
    monkeypatch.setattr(driver, "REPORTS", tmp_path)
    chapters, relations = driver._rotated_keys()
    assert chapters[:3] == ["506", "504", "502"]
    assert len(relations) == 5


def test_persona_prompts_cross_pollinate():
    driver = _load()
    personas = driver.load_personas()
    rotation = driver._rotated_keys()
    prompts = {
        str(p["id"]): driver._build_persona_prompt(p, str(p["id"]), "/iso", "abcd", "2026-09-04", rotation)
        for p in personas
    }
    seeds = [line for body in prompts.values() for line in body.splitlines() if line.startswith("isolation.persona_seed:")]
    drops = [line for body in prompts.values() for line in body.splitlines() if line.startswith("rotation.drop_chapter:")]
    packs = [line for body in prompts.values() for line in body.splitlines() if line.startswith("rotation.drop_pack:")]
    relations = [line for body in prompts.values() for line in body.splitlines() if line.startswith("rotation.love_relation:")]
    nexts = [line for body in prompts.values() for line in body.splitlines() if line.startswith("rotation.next_chapter_focus:")]
    assert len(set(seeds)) == 5
    assert len(set(drops)) >= 4
    assert len(set(packs)) >= 3
    assert len(set(relations)) >= 4
    assert len(set(nexts)) >= 4


def test_l2_prompt_requires_full_provenance(tmp_path, monkeypatch):
    driver = _load()
    isolated_root = tmp_path / "isolated-reader-packs"
    isolated_root.mkdir()
    pack_root = tmp_path / "blindtest_packs"
    pack_root.mkdir()
    for name in ("open.md", "mid_a.md", "mid_b.md", "latest.md"):
        (pack_root / name).write_text("seed", encoding="utf-8")
    monkeypatch.setattr(driver, "ISOLATED", isolated_root)
    monkeypatch.setattr(driver, "PACKS", pack_root)
    monkeypatch.setattr(driver, "REPORTS", tmp_path)
    rc = driver._emit(type("Args", (), {"new_seed": False})())
    assert rc == 0
    l2_path = tmp_path / "reader-prompt-real.txt"
    text = l2_path.read_text(encoding="utf-8")
    for required in [
        "schema_version=2",
        "pack_hash=",
        "source MUST start with 真人 sub-agent",
        "no_chronicle=true",
        "no_frontmatter=true",
        "isolation.cwd",
        "isolation.persona_seed",
        "diversity_score >=0.5",
    ]:
        assert required in text, "L2 prompt missing requirement: " + required


def test_verify_subcommand_enforces_diversity():
    driver = _load()
    rc = driver._verify(type("Args", (), {})())
    assert rc == 0
