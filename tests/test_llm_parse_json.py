# -*- coding: utf-8 -*-
import pytest
import urllib.error

from engine import llm


def test_parse_json_accepts_nested_object_and_fenced_response():
    raw = '前置说明\n```json\n{"frontmatter": {"ships": {"林夙×苏挽": "桌沿"}}, "items": [1, {"ok": true}]}\n```\n'

    assert llm.parse_json(raw) == {
        "frontmatter": {"ships": {"林夙×苏挽": "桌沿"}},
        "items": [1, {"ok": True}],
    }


def test_parse_json_handles_braces_inside_string():
    assert llm.parse_json('{"hook":"她说过 {别回头}", "ok": true}') == {
        "hook": "她说过 {别回头}",
        "ok": True,
    }


def test_parse_json_rejects_missing_or_truncated_object():
    with pytest.raises(ValueError, match="JSON"):
        llm.parse_json("没有结构化结果")
    with pytest.raises(ValueError, match="完整"):
        llm.parse_json('{"hook": "未完')


def test_parse_json_rejects_non_object_json():
    with pytest.raises(ValueError, match="对象"):
        llm.parse_json('[{"hook": "不接受数组顶层"}]')


def test_complete_retries_bad_provider_json_and_bad_retry_config(monkeypatch):
    class Response:
        def __init__(self, payload):
            self.payload = payload

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return self.payload

    responses = iter([Response(b"not json"), Response(b'{"content":[{"text":"{}"}]}')])
    calls = []

    def fake_urlopen(request, timeout):
        calls.append(timeout)
        return next(responses)

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("LLM_RETRIES", "not-an-int")
    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(llm.time, "sleep", lambda seconds: None)

    assert llm.complete("system", "user") == "{}"
    assert calls == [120, 120]
