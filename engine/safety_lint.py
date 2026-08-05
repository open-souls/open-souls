# -*- coding: utf-8 -*-
"""Deterministic hardline checks for generated chapter bodies."""
import re


HARDLINE_PATTERNS = (
    (re.compile(r"(?:他|她)\s*插入"), "可能露骨"),
    (re.compile(r"(?:射精|阴茎|阴道|口交|自慰)"), "可能露骨"),
    (re.compile(r"(?:割腕|割脉|吞药|上吊|跳楼|自杀|自残)"), "可能自伤"),
)
MINOR_INTIMACY = re.compile(
    r"(?:耳根|颈侧|指节|手腕|亲吻|吻|拥抱|抚摸|贴近|暧昧)"
)


def check(text, minor_names=("林窈", "阿湄")):
    """Return hardline violations; empty means no deterministic hit."""
    issues = []
    for pattern, description in HARDLINE_PATTERNS:
        if pattern.search(text):
            issues.append(description)
    for name in minor_names or ():
        if name and re.search(
            re.escape(name) + r"[^。！？\n]{0,60}" + MINOR_INTIMACY.pattern,
            text,
        ):
            issues.append(f"{name} 未成年角色不得出现暧昧身体描写")
    return list(dict.fromkeys(issues))
