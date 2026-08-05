# -*- coding: utf-8 -*-
from pathlib import Path
import subprocess
import sys

from engine import batch_rewrite, village
from tools import review_batch


def _chapter(number, title, body, *, editorial=False):
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
    context = prompt.split("【你要做的】", 1)[0]
    assert "的方式不是" not in context
    assert "方向朝着" not in context
    assert len(prompt) < 16000
