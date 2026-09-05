# -*- coding: utf-8 -*-
"""JJ-LINT batch 14 regression tests."""
import sys
sys.path.insert(0, '.')
from engine.prose_lint import lint_text


def _wrap(body):
    return "---\ntitle: t\n---\n\n" + body + "\n"


def test_nayix_warn_at_6():
    body = "".join("那一" + char for char in "一二三四五六") + ("她在门外站着。" * 8)
    errs, warns, m = lint_text(_wrap(body))
    assert m["jj_nayix"] == 6
    assert any("JJ-LINT-01" in w and "临界" in w for w in warns), warns


def test_nayix_error_at_10():
    motifs = ["那一" + c for c in "一二三四五六七八九十"]
    body = "".join(motifs) + ("她从车里下来。" * 8)
    errs, warns, m = lint_text(_wrap(body))
    # ERROR threshold now 20; 10 hits = WARN
    assert m["jj_nayix"] == 10
    assert not any("JJ-LINT-01" in e for e in errs), errs
    assert any("JJ-LINT-01" in w and "临界" in w for w in warns), warns


def test_nayix_error_at_20():
    # batch 14 修订：JJ-LINT-01 默认 WARN-only（不拦 push）。
    # 阈值常量 JJ_LINT_NAYIX_ERROR = 40 仍保留为研究分层参考；测试只验证计数与常量一致。
    motifs = ["那一" + c for c in "甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申亥"]
    body = "".join(motifs) + ("她从车里下来。" * 8)
    errs, warns, m = lint_text(_wrap(body))
    assert m["jj_nayix"] == 20
    assert not any("JJ-LINT-01" in e for e in errs), errs
    assert any("JJ-LINT-01" in w for w in warns), warns
def test_ziji_warn_at_quarter():
    body = "\n".join(["自己" + "雨声在外头不停下来。" * 2] * 5)  # 5 lines
    errs, warns, m = lint_text(_wrap(body))
    # WARN-only：极端比例不再升级 ERROR
    assert not any("JJ-LINT-02" in e for e in errs), errs
    assert any("JJ-LINT-02" in w and "临界" in w for w in warns), warns


def test_ziji_warn_low_threshold():
    # 8 lines, 3 ziji -> 3 * 4 = 12 > 8 -> WARN, 3 * 2 = 6 < 8 -> not ERROR
    body = "\n".join(["他信不哭，雨声在外头。", "她眼泪止不住，雨声在外头。"] + ["自己" + "雨声在外头不停。" * 2] * 3 + ["外面下雨不停。" * 2] * 3)
    errs, warns, m = lint_text(_wrap(body))
    assert m["jj_ziji"] == 3
    # Should be WARN but not ERROR
    assert any("JJ-LINT-02" in w and "临界" in w for w in warns), warns
    assert not any("JJ-LINT-02" in e for e in errs), errs


def test_taily_han_warn():
    body = "她走到门口那扇木门前，雨声不停。" * 3 + "\n她在外头站了一会儿，雨声不停。\n她。"
    errs, warns, m = lint_text(_wrap(body))
    assert m["jj_tail"] is True
    assert any("JJ-LINT-07" in w for w in warns), warns


def test_normal_chapter_clean():
    body = "她抬起脚，迈到门外那扇木门前。她心里惦着孩子，抬脚往外走。\n外面下雨不停。"
    errs, warns, m = lint_text(_wrap(body))
    assert not any("JJ-LINT-01" in e for e in errs)
    assert not any("JJ-LINT-02" in e for e in errs)
    assert not any("JJ-LINT-07" in w for w in warns)


def test_jj_lint_03_short_tail_density():
    # 末 6 行里 >= 4 行 <= 6 字 -> WARN
    body = (
        "林彻看见她，林彻没有说话。林彻只是把那碗糖水端走。\n" * 30
        + "夜里。\n火很静。\n雪没响。\n夜深。\n她停。\n她等。"
    )
    errs, warns, m = lint_text(_wrap(body))
    assert m["jj_tail_short_count"] >= 4
    assert any("JJ-LINT-03" in w for w in warns), warns


def test_jj_lint_05_dialog_without_agency():
    # dialog >= 8 && agency < 2 -> WARN
    body = ("「你来了？」「坐。」「喝。」「吃。」「等。」「说。」「走。」「停。」\n") * 30
    errs, warns, m = lint_text(_wrap(body))
    assert m["jj_dialog_count"] >= 8
    assert m["jj_agency_count"] < 2
    assert any("JJ-LINT-05" in w for w in warns), warns


def test_jj_lint_06_tail_atmosphere():
    # 末 3 行命中 (屋里|夜|风|雪|火|雨|街上) + (很静|没停|没熄|没响) -> WARN
    body = (
        "林彻看见她，林彻没有说话。林彻只是把那碗糖水端走。\n" * 30
        + "屋里很静。\n火没有熄。\n夜没有停。"
    )
    errs, warns, m = lint_text(_wrap(body))
    assert m["jj_tail_atmosphere"] is True
    assert any("JJ-LINT-06" in w for w in warns), warns


def test_jj_lint_03_promoted_above_error_gate():
    # 即使 ERROR 已触发,JJ-LINT-03 仍应出现
    body = (
        "她。" * 200
        + "\n"
        + ("她看向他。" * 1 + "\n") * 30
        + "夜里。\n火很静。\n雪没响。\n夜深。\n她停。\n她等。"
    )
    errs, warns, m = lint_text(_wrap(body))
    # JJ-LINT-03 must fire even when errors list is non-empty.
    assert any("JJ-LINT-03" in w for w in warns), warns


if __name__ == "__main__":
    test_nayix_warn_at_6()
    test_nayix_error_at_10()
    test_ziji_warn_at_quarter()
    test_ziji_warn_low_threshold()
    test_taily_han_warn()
    test_normal_chapter_clean()
    print("6/6 JJ-LINT tests pass")
