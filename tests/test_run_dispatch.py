# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path

from engine import run_dispatch


def _chapter_file(tmp_path, body="他把信压在案角，门外的雪又落了一层。"):
    path = tmp_path / "ch901-测试.md"
    path.write_text(
        "---\nchapter: 901\ntitle: 测试\n---\n\n# 第901回 · 测试\n\n"
        + body
        + "\n",
        encoding="utf-8",
    )
    return path


def test_run_one_never_trusts_claude_pass_without_local_gates(tmp_path, monkeypatch):
    target = _chapter_file(tmp_path)
    prompt = tmp_path / "ch901.txt"
    prompt.write_text("只改目标章", encoding="utf-8")
    results = tmp_path / "results"
    monkeypatch.setattr(run_dispatch.BR, "_chapter_file", lambda chapter: str(target))
    monkeypatch.setattr(run_dispatch, "RESULTS_DIR", results)

    def fake_claude(*args, **kwargs):
        target.write_text(target.read_text(encoding="utf-8") + "\n新动作。", encoding="utf-8")
        return {"ok": True, "payload": {"result": "PASS"}, "stdout_tail": "", "stderr_tail": ""}

    monkeypatch.setattr(run_dispatch, "_claude", fake_claude)
    gate_calls = iter([
        {"ok": True, "returncode": 0, "output": "lint ok"},
        {"ok": False, "returncode": 1, "output": "review rejected"},
    ])
    monkeypatch.setattr(run_dispatch, "_gate", lambda *args, **kwargs: next(gate_calls))

    result = run_dispatch.run_one(prompt, timeout=1)

    assert result["changed"] is True
    assert result["claude"]["ok"] is True
    assert result["pass"] is False
    assert "status: BLOCKED" in (results / "ch901.md").read_text(encoding="utf-8")


def test_run_one_pass_requires_formula_scan_to_be_clean(tmp_path, monkeypatch):
    target = _chapter_file(tmp_path)
    prompt = tmp_path / "ch901.txt"
    prompt.write_text("只改目标章", encoding="utf-8")
    results = tmp_path / "results"
    monkeypatch.setattr(run_dispatch.BR, "_chapter_file", lambda chapter: str(target))
    monkeypatch.setattr(run_dispatch, "RESULTS_DIR", results)

    def fake_claude(*args, **kwargs):
        target.write_text(
            target.read_text(encoding="utf-8") + "\n他的方向落在门口。",
            encoding="utf-8",
        )
        return {"ok": True, "payload": {"result": "PASS"}, "stdout_tail": "", "stderr_tail": ""}

    monkeypatch.setattr(run_dispatch, "_claude", fake_claude)
    monkeypatch.setattr(
        run_dispatch,
        "_gate",
        lambda *args, **kwargs: {"ok": True, "returncode": 0, "output": "ok"},
    )

    result = run_dispatch.run_one(prompt, timeout=1)

    assert result["pass"] is False
    assert result["formula_hits"]["方向落在"] == 1


def test_claude_command_is_bounded_and_uses_explicit_model(monkeypatch):
    captured = {}

    def fake_process(command, **kwargs):
        captured["command"] = command
        return {
            "returncode": 0,
            "stdout": json.dumps({"type": "result", "subtype": "success", "is_error": False}),
            "stderr": "",
            "timed_out": False,
        }

    monkeypatch.setattr(run_dispatch, "_run_process", fake_process)
    result = run_dispatch._claude(
        "prompt", budget=4.0, model="claude-sonnet-4-6", effort="medium",
        timeout=10, claude_cmd="claude.cmd",
    )

    assert result["ok"] is True
    assert captured["command"][0] == "claude.cmd"
    assert "--bare" in captured["command"]
    assert "--no-session-persistence" in captured["command"]
    assert "--max-budget-usd" in captured["command"]
    assert "4.0" in captured["command"]
    assert "--model" in captured["command"]
    assert "claude-sonnet-4-6" in captured["command"]
    assert "--allowed-tools" in captured["command"]
    assert "Read,Edit" in captured["command"]
    assert "--permission-mode" in captured["command"]
    assert "acceptEdits" in captured["command"]


def test_run_process_timeout_terminates_the_child_tree():
    result = run_dispatch._run_process(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        timeout=0.05,
    )

    assert result["timed_out"] is True
    assert result["returncode"] == 124
    assert "process tree terminated" in result["stderr"]


def test_formula_scan_catches_machine_echo_loop(tmp_path):
    target = tmp_path / "ch901-测试.md"
    target.write_text(
        "---\nchapter: 901\ntitle: 测试\n---\n\n"
        + ("他把那一寸纸压在案角。" * 30),
        encoding="utf-8",
    )

    assert run_dispatch._formula_hits(target)["motif_slot"] == 30


def test_run_one_blocks_non_target_side_effects(tmp_path, monkeypatch):
    target = _chapter_file(tmp_path)
    prompt = tmp_path / "ch901.txt"
    prompt.write_text("只改目标章", encoding="utf-8")
    results = tmp_path / "results"
    monkeypatch.setattr(run_dispatch, "ROOT", tmp_path)
    monkeypatch.setattr(run_dispatch, "RESULTS_DIR", results)
    monkeypatch.setattr(run_dispatch.BR, "_chapter_file", lambda chapter: str(target))

    def fake_claude(*args, **kwargs):
        target.write_text(target.read_text(encoding="utf-8") + "\n新动作。", encoding="utf-8")
        (tmp_path / "rogue-sidecar.md").write_text("不应写入", encoding="utf-8")
        return {"ok": True, "payload": {"result": "PASS"}, "stdout_tail": "", "stderr_tail": ""}

    monkeypatch.setattr(run_dispatch, "_claude", fake_claude)
    monkeypatch.setattr(
        run_dispatch,
        "_gate",
        lambda *args, **kwargs: {"ok": True, "returncode": 0, "output": "ok"},
    )

    result = run_dispatch.run_one(prompt, timeout=1)

    assert result["pass"] is False
    assert any(path.endswith("rogue-sidecar.md") for path in result["side_effects"])


def test_run_one_blocks_chapter_sibling_side_effects(tmp_path, monkeypatch):
    chronicle = tmp_path / "chronicle"
    chronicle.mkdir()
    target = _chapter_file(chronicle)
    prompt = tmp_path / "ch901.txt"
    prompt.write_text("只改目标章", encoding="utf-8")
    results = tmp_path / "results"
    monkeypatch.setattr(run_dispatch, "ROOT", tmp_path)
    monkeypatch.setattr(run_dispatch, "RESULTS_DIR", results)
    monkeypatch.setattr(run_dispatch.BR, "_chapter_file", lambda chapter: str(target))

    def fake_claude(*args, **kwargs):
        target.write_text(target.read_text(encoding="utf-8") + "\n新动作。", encoding="utf-8")
        (chronicle / "ch901-new.md").write_text("旁支草稿", encoding="utf-8")
        return {"ok": True, "payload": {"result": "PASS"}, "stdout_tail": "", "stderr_tail": ""}

    monkeypatch.setattr(run_dispatch, "_claude", fake_claude)
    monkeypatch.setattr(
        run_dispatch,
        "_gate",
        lambda *args, **kwargs: {"ok": True, "returncode": 0, "output": "ok"},
    )

    result = run_dispatch.run_one(prompt, timeout=1)

    assert result["pass"] is False
    assert any(path.endswith("ch901-new.md") for path in result["side_effects"])


def test_run_one_allows_another_selected_target_in_same_directory(tmp_path, monkeypatch):
    chronicle = tmp_path / "chronicle"
    chronicle.mkdir()
    target = _chapter_file(chronicle)
    sibling = chronicle / "ch902-另一个目标.md"
    sibling.write_text("原始目标", encoding="utf-8")
    prompt = tmp_path / "ch901.txt"
    prompt.write_text("只改目标章", encoding="utf-8")
    results = tmp_path / "results"
    monkeypatch.setattr(run_dispatch, "ROOT", tmp_path)
    monkeypatch.setattr(run_dispatch, "RESULTS_DIR", results)
    monkeypatch.setattr(run_dispatch.BR, "_chapter_file", lambda chapter: str(target))

    def fake_claude(*args, **kwargs):
        target.write_text(target.read_text(encoding="utf-8") + "\n新动作。", encoding="utf-8")
        sibling.write_text("合法的另一批次目标", encoding="utf-8")
        return {"ok": True, "payload": {"result": "PASS"}, "stdout_tail": "", "stderr_tail": ""}

    monkeypatch.setattr(run_dispatch, "_claude", fake_claude)
    monkeypatch.setattr(
        run_dispatch,
        "_gate",
        lambda *args, **kwargs: {"ok": True, "returncode": 0, "output": "ok"},
    )

    result = run_dispatch.run_one(
        prompt,
        timeout=1,
        allowed_targets={target.resolve(), sibling.resolve()},
    )

    assert result["pass"] is True
    assert result["side_effects"] == []
