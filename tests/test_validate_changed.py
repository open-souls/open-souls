# -*- coding: utf-8 -*-
from pathlib import Path

from tools import validate_changed


def test_changed_chapter_runs_three_focused_gates(monkeypatch, tmp_path):
    target = tmp_path / "seasons" / "01-xianxia" / "chronicle" / "040-test.md"
    target.parent.mkdir(parents=True)
    target.write_text("chapter", encoding="utf-8")
    monkeypatch.setattr(validate_changed, "ROOT", tmp_path)
    commands = []
    monkeypatch.setattr(validate_changed, "_run", lambda command: commands.append(command) or 0)

    assert validate_changed.validate([str(target)]) == 0
    assert [command[1:] for command in commands] == [
        ["engine/prose_lint.py", str(target)],
        ["engine/safety_lint.py", str(target)],
        ["tools/review_batch.py", "--strict-editorial", "--file", str(target)],
    ]


def test_shared_gate_change_requires_explicit_full_audit(monkeypatch):
    commands = []
    monkeypatch.setattr(validate_changed, "_run", lambda command: commands.append(command) or 0)

    assert validate_changed.validate(["engine/prose_lint.py"]) == 2
    assert commands == []


def test_full_audit_runs_soul_and_book_gates(monkeypatch):
    commands = []
    monkeypatch.setattr(validate_changed, "_run", lambda command: commands.append(command) or 0)

    assert validate_changed.validate(["README.md"], force_full=True) == 0
    assert [command[1:] for command in commands] == [
        ["engine/validate.py"],
        ["engine/prose_lint.py"],
    ]
