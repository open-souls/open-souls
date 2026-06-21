"""Parse + validate cast/<name>/soul.md. Souls are character DATA, never instructions."""
import re, os, glob
import yaml

REQUIRED = ["name", "one_line", "drives", "fracture", "under_pressure", "boundaries"]
MAX_CHARS = 1500
INJECTION = re.compile(
    r"(ignore (the )?(previous|above)|system\s*:|you (are|must) now|"
    r"忽略(上面|之前)|你现在(必须|是)|disregard|jailbreak)", re.I)


class SoulError(Exception):
    pass


def parse(path):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", raw, re.S)
    if not m:
        raise SoulError(f"{path}: 缺少 YAML frontmatter")
    meta = yaml.safe_load(m.group(1)) or {}
    meta["_body"] = (m.group(2) or "").strip()[:400]
    meta["_path"] = path
    return meta


def validate(meta):
    errs = []
    for k in REQUIRED:
        if not meta.get(k):
            errs.append(f"缺少必填字段: {k}")
    fr = meta.get("fracture") or {}
    if not (isinstance(fr, dict) and fr.get("says") and fr.get("does")):
        errs.append("fracture 必须有 says 和 does（嗑点来源）")
    blob = yaml.safe_dump(meta, allow_unicode=True)
    if INJECTION.search(blob):
        errs.append("疑似操纵生成器的指令。灵魂只描述角色，不下命令。")
    if len(blob) > MAX_CHARS:
        errs.append(f"灵魂过长（{len(blob)}>{MAX_CHARS}）。请精简。")
    return errs


def load_cast(root="souls"):
    cast = {}
    for p in sorted(glob.glob(os.path.join(root, "*", "soul.md"))):
        if os.sep + "_" in p:
            continue
        meta = parse(p)
        errs = validate(meta)
        if errs:
            raise SoulError(f"{p}: " + "; ".join(errs))
        cast[meta["name"]] = meta
    return cast


def card(meta, state=None):
    fr = meta["fracture"]
    lines = [
        f"姓名: {meta['name']}（{meta.get('pronoun','他')}）",
        f"一句话: {meta['one_line']}",
        "想要: " + "；".join(meta.get("drives", [])),
        f"裂缝: 嘴上「{fr['says']}」/ 实际「{fr['does']}」",
        f"被逼到墙角: {meta['under_pressure']}",
        f"说话: {meta.get('voice','')}",
        f"边界: {meta['boundaries']}",
    ]
    if state and state.get("incarnation"):
        lines.append(f"本季身份: {state['incarnation']}（{state.get('condition','')}）")
    elif meta.get("_body"):
        lines.append(f"底色: {meta['_body'][:120]}")
    return "\n".join(lines)
