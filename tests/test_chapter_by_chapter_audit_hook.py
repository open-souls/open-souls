# -*- coding: utf-8 -*-
"""Lock the hook-signal detection rules in tools/chapter_by_chapter_audit.py.

Phase-1 detector used a last-line keyword regex and missed closing beats like:
  - question marks ("林夙在哪儿？")
  - future-intent verbs ("明日还要再去一次")
  - action + noun-object phrases ("刀柄方向拉长了一寸")

This regression test pins the new detection rules so the audit does not
silently regress to the under-counting keyword regex.

Run: py -3 -X utf8 -m pytest tests/test_chapter_by_chapter_audit_hook.py -q
"""
from __future__ import annotations

import importlib.util
import pathlib
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "chapter_by_chapter_audit.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("audit", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_chapter(tmp_path: pathlib.Path, body_tail: str) -> pathlib.Path:
    chapter = tmp_path / "001-test.md"
    chapter.write_text(
        "---\nseason: 1\nchapter: 1\ntitle: test\ncast: [a, b]\npov: a\nline: x\nthread: x\nbeat: x\nships: {}\nhook: |\n  ---\n\n# 测试\n\n第一段。\n\n第二段。\n\n" + body_tail + "\n",
        encoding="utf-8",
    )
    return chapter


def _audit_with(module, path):
    original_root = module.ROOT
    module.ROOT = path.parent
    try:
        return module.audit(path)
    finally:
        module.ROOT = original_root
def test_question_mark_closes_a_hook():
    module_loaded = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        chapter = _write_chapter(pathlib.Path(tmp), "她要先问门房：\n\n\u201c林夙在哪儿？\u201d")
        row = _audit_with(module_loaded, chapter)
    assert row["hook_signal"] is True


def test_future_intent_closes_a_hook():
    module_loaded = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        chapter = _write_chapter(pathlib.Path(tmp), "她隔着药包按住那片碎纸。\n\n明日，她还要再去一次。")
        row = _audit_with(module_loaded, chapter)
    assert row["hook_signal"] is True


def test_action_with_object_closes_a_hook():
    module_loaded = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        chapter = _write_chapter(pathlib.Path(tmp), "脚前那块地上，影子落在月光那一寸里。\n\n月光底下，他自己脚前这一截影子，被刀柄的方向拉长了一寸。")
        row = _audit_with(module_loaded, chapter)
    assert row["hook_signal"] is True


def test_pure_mood_ending_is_not_a_hook():
    module_loaded = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        chapter = _write_chapter(pathlib.Path(tmp), "屋里很安静。\n\n夜很静。")
        row = _audit_with(module_loaded, chapter)
    assert row["hook_signal"] is False
