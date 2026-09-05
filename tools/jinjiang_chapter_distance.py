# -*- coding: utf-8 -*-
"""Distance-to-Jinjiang-blowup per chapter.

Implements docs/standards/晋江爆款基线.md section 1 to 6:
  * Engineering 5 dimensions (E1 to E5), fully deterministic.
  * Reader 5 dimensions (R1 to R5), looked up against reports/jinjiang-r20/reader-*.json.

Output is one record per chapter with three gates:
  publish  - min(E_min, R_min) >= 7.0
  blowup   - min(E_min, R_min) >= 8.5 sustained for 3+ chapters
  addictive - min(E_min, R_min) >= 8.5 for 5+ chapters AND all R >= 7.5

When no L2 reader evidence exists, R-track returns None and the report
prints explicit warnings. This is the same boundary the rubric section 0
enforces.

Usage:
    py -3 -X utf8 tools/jinjiang_chapter_distance.py path/to/ch.md
    py -3 -X utf8 tools/jinjiang_chapter_distance.py
    py -3 -X utf8 tools/jinjiang_chapter_distance.py --range 504 506
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
CHRONICLE = ROOT / "seasons" / "01-xianxia" / "chronicle"
REPORTS = ROOT / "reports" / "jinjiang-r20"
AUDIT_PATH = REPORTS / "chapter-by-chapter-audit.json"

FRONTMATTER = re.compile(r"\A---\s*\n([\s\S]*?)\n---\s*(?:\n|\Z)", re.M)
POST_FRONT = re.compile(r"^[ \t]*review:\s*>-?\s*\n((?:[ \t]+[^\n]*\n|[ \t]*\n)*)", re.M)
HAN = re.compile(r"[一-鿿]")
ACTION = re.compile(r"走|来|去|问|答|拿|放|递|收|拆|开|关|挡|写|烧|抬|转身|停|进|出|抓|握|听|闻|落|动|转|挪|按|拂|盯|擦|撕|换|验|翻|压|推|扶")
RESISTANCE = re.compile(r"却|但|不肯|不能|没有|未|拦|拒绝|停住|不让|来不及|门外|追")
DECISION = re.compile(r"决定|改为|改成|只[把将]|不再|不肯|拒绝|主动|亲自|自己开|自己拿|自己写|签下|不签|先封|按下旧印|设定|逼得|给.{0,8}两条路|要求.{0,8}落名|先写下|把.{0,12}推到.{0,12}面前|说是我让你|现在去")

# 末 6 行作为章尾钩分析窗
TAIL_WINDOW = 6

# E6 章末钩子类型枚举（batch 14 焊入）。每个枚举都给一个或多个特征词；
# 分类顺序固定,先匹配先赢;不可判 fallback。
HOOK_REVERSAL = re.compile(r"原来|不料|谁知|岂料|竟|然而|却[是为]?" r"|没想到|反转|翻供|认错")
HOOK_CHOICE = re.compile(r"两条路|二择|二选|要不要|留.{0,4}还是|去.{0,4}还是|留.{0,4}或去")
HOOK_BURST = re.compile(r"一刀|一剑|一掌|一拳|拔刀|拔剑|一刀落|一刀下|血溅|血落|血从|摔了|砸了|碎了|断了|爆了|炸了|炸开|撕了|撕开|劈了|撞开")
HOOK_UNFINISHED = re.compile(r"等.{0,4}(?:他|她|它|谁)" r"|再.{0,3}不来|还没.{0,3}|还没来|还没回|等一根|等一柄|等一句|等一个|还差|尚未")
HOOK_QUESTION = re.compile(r"[^。！？\n]{2,80}[\uff1f\?]$", re.M)
HOOK_CREEPY = re.compile(r"那.{0,3}(?:不?动|不?响|没?有)|没有.{0,3}(?:回|答|应|声|响)|不.{0,3}(?:回答|应答)|不回|不答|不应|不答话|不作声|不接话|装.{0,3}死|装.{0,3}没听见|装.{0,3}不在")
HOOK_RELATION = re.compile(r"手|指|肩|发|眼|泪|笑|沉默|没.{0,3}接|没.{0,3}应|没.{0,3}答|没.{0,3}看|没.{0,3}说话|没.{0,3}问|没.{0,3}动|没.{0,3}回|没.{0,3}递|没.{0,3}挡|没.{0,3}替")
HOOK_VAGUE = re.compile(r"夜.{0,3}(?:很|深|长)|风.{0,3}(?:很|起)|屋里.{0,3}(?:很|空|暗)|月.{0,3}(?:很|淡)|心里.{0,3}(?:很|咯)|不知.{0,3}(?:为|怎)")
HOOK_ENUM = (
    ("reversal", HOOK_REVERSAL),
    ("choice", HOOK_CHOICE),
    ("burst", HOOK_BURST),
    ("unfinished", HOOK_UNFINISHED),
    ("question", HOOK_QUESTION),
    ("creepy", HOOK_CREEPY),
    ("relation", HOOK_RELATION),
    ("vague", HOOK_VAGUE),
)

# E5 POV 主动发起方识别:POV 名字在中段选择动词主语位置出现占比
POV_AGENCY_VERB = re.compile(r"(?:^|[。！？\n])" r"([^。！？\n]{1,30}?)" r"(?:决定|改为|改成|主动|亲自|签下|不签|不再|拒绝|逼得|先封|按下旧印|设定|先写下|把.{0,8}推到|说是我让你)")

POV_NAME_TO_CHAR = {
    "苏挽": "苏挽", "林夙": "林夙", "阿湄": "阿湄",
    "林崇": "林崇", "林彻": "林彻", "林窈": "林窈",
    "林叙": "林叙", "叶观澜": "叶观澜", "余伯": "余伯",
    "凌朔": "凌朔", "裴无咎": "裴无咎", "牛阿大": "牛阿大",
}
NAMED = ("苏挽", "林夙", "阿湄", "林崇", "林彻", "林窈", "林叙", "叶观澜", "余伯", "凌朔", "裴无咎", "牛阿大")

PUBLISH_FLOOR = 7.0
BLOWUP_FLOOR = 8.5
ADDICT_R_FLOOR = 7.5


def _strip_all_frontmatter(raw):
    """Strip every YAML frontmatter block.

    Some chronicles embed a second frontmatter block (review / score / hook)
    after the first. We drop both before counting DECISION hits; otherwise
    review metadata inflates E4 agency.
    """
    cursor = 0
    while True:
        m = FRONTMATTER.search(raw, cursor)
        if not m:
            return raw[cursor:]
        cursor = m.end()


def _strip_post_review(raw):
    """Drop a trailing review: >- block if it lives outside the YAML fence.

    Defensive belt-and-suspenders for chronicles whose second frontmatter
    block is malformed enough that FRONTMATTER misses it.
    """
    m = POST_FRONT.search(raw)
    if not m:
        return raw
    head = raw[: m.start()]
    if "\n\n" in head.strip():
        return raw
    return raw.replace(m.group(0), "")


def read_chapter(path):
    raw = path.read_text(encoding="utf-8")
    n_match = re.search(r"^chapter:\s*(\d+)", raw, re.M)
    pov = re.search(r"^pov:\s*(.+)$", raw, re.M)
    n = int(n_match.group(1)) if n_match else int(path.name.split("-", 1)[0])
    pov_name = pov.group(1).strip() if pov else ""
    body = _strip_all_frontmatter(raw)
    body = _strip_post_review(body)
    return n, pov_name, body.strip()


def _opening_paragraph(body):
    """Return the first real prose paragraph, skipping H1 / H2 titles."""
    for p in body.split("\n\n"):
        p = p.strip()
        if not p:
            continue
        if p.startswith("#"):
            continue
        return p
    return ""


def e_score(body, audit_row, pov_name=""):
    paras = [p.strip() for p in body.split("\n\n") if p.strip() and not p.strip().startswith("#")]
    first = _opening_paragraph(body)
    mid = "\n\n".join(paras[1:-1])
    # E1 reads the first 180 chars of the chapter body so the action+resistance
    # signal can come from the first few real paragraphs, not only the opening line.
    head180 = body[:180]
    open_actions = len(ACTION.findall(head180))
    e1 = 10 if open_actions >= 2 and RESISTANCE.search(head180) else 7 if open_actions else 4
    e2 = 10 if DECISION.search(mid) else 6 if ACTION.search(mid) else 4
    e3 = 10 if (audit_row or {}).get("hook_signal") else 4
    e4 = min(10, 4 + len(DECISION.findall(body)))
    named = len({c for c in NAMED if c in body})
    e5 = min(10, 4 + max(0, named - 2) // 2 + (2 if DECISION.search(body) else 0))
    pov_name, pov_ratio, pov_sample = _pov_initiator_score(body, pov_name)
    hook_type = _hook_type(body)
    e5_sub_init = (pov_ratio or 0) * 10 if pov_ratio is not None else 4
    if pov_ratio is not None and pov_ratio < 0.5:
        e5 = max(4, e5 - 1)  # POV 不主动 -> E5 降一档
    # E6:枚举钩类型。vague / undetermined 不算有效钩,分 4;其他按枚举分
    if hook_type in {"vague", "undetermined"}:
        e6 = 4
    elif hook_type == "reversal":
        e6 = 10
    elif hook_type in {"choice", "burst"}:
        e6 = 9
    elif hook_type in {"unfinished", "question", "creepy"}:
        e6 = 8
    elif hook_type == "relation":
        e6 = 7
    else:
        e6 = 5
    return {"E1_open_conflict": e1, "E2_mid_turn": e2, "E3_hook_stop": e3, "E4_agency": e4, "E5_relationship_cost": e5, "E5_pov_initiator": round(e5_sub_init, 2), "E6_hook_type": e6, "E6_hook_label": hook_type, "E6_pov_sample": pov_sample}

def _pov_initiator_score(body, pov_name):
    """Return (pov_name, ratio, sample) tuple.

    ratio = occurrences where POV character appears in the clause preceding
    a mid-turn verb / total mid-turn verb clauses. If POV character is not
    in POV_NAME_TO_CHAR, return (pov_name, None, "").

    S2 工程启发式:不假装这是「晋江标准」,只是机器代理「POV 主动发起」信号。
    """
    if not pov_name or pov_name not in POV_NAME_TO_CHAR:
        return pov_name, None, ""
    char = POV_NAME_TO_CHAR[pov_name]
    clauses = POV_AGENCY_VERB.findall(body)
    if not clauses:
        return pov_name, 0.0, ""
    hits = sum(1 for clause in clauses if char in clause)
    ratio = round(hits / len(clauses), 2)
    sample = next((c.strip() for c in clauses if char in c), "")[:40]
    return pov_name, ratio, sample


def _hook_type(body):
    """Classify the tail window into one HOOK_ENUM category or 'undetermined'.

    S2 工程启发式:每个枚举有显式触发词,顺序固定,先匹配先赢。
    「vague」被记录但不算有效钩(等同于原 E3 不触发)。
    """
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    tail = "\n".join(lines[-TAIL_WINDOW:]) if lines else ""
    normalized_tail = "\n".join(
        line.strip('“”「」『』\" ') for line in lines[-TAIL_WINDOW:]
    ) if lines else ""
    for name, regex in HOOK_ENUM:
        if regex.search(normalized_tail):
            return name
    return "undetermined"




def r_score(chapter_number, panel):
    if chapter_number not in panel:
        return None, "no reader blindtest evidence for this chapter"
    info = panel[chapter_number]
    l1 = info.get("l1") or []
    l2 = info.get("l2") or []
    if not l1 and not l2:
        return None, "panel row exists but empty"
    r1 = 7.5 if any(p.get("persona_id") == "3" and p.get("stay_to_50") for p in l1 + l2) else 5.0
    n_match = lambda p: p.get("next_chapter_focus", {}).get("chapter") == str(chapter_number)
    r2 = 7.5 if any(n_match(p) for p in l1 + l2) else 5.0
    r3 = 7.5 if any(p.get("love_relation") for p in l1 + l2) else 5.0
    r4 = 7.5 if any(p.get("persona_id") == "4" and p.get("stay_to_50") for p in l1 + l2) else 5.0
    bad_smart = any((p.get("pattern_flags") or {}).get("smart_drop") for p in l1 + l2)
    bad_chain = any((p.get("pattern_flags") or {}).get("passive_chain") for p in l1 + l2)
    r5 = 7.5 if not (bad_smart or bad_chain) else 4.0
    return {"R1_cross_genre": r1, "R2_hook_carry": r2, "R3_relationship": r3, "R4_agency": r4, "R5_no_forbidden": r5}, "ok"


def gates(e_min, r_min):
    combined = min(e_min, r_min) if r_min is not None else e_min
    return {
        "publish": combined >= PUBLISH_FLOOR if r_min is not None else False,
        "blowup_chapter": combined >= BLOWUP_FLOOR if r_min is not None else False,
        "addictive_chapter": combined >= BLOWUP_FLOOR and r_min is not None and r_min >= ADDICT_R_FLOOR,
        "combined_when_R_missing": e_min,
        "r_track_present": r_min is not None,
    }


def build_panel(reader_dir):
    panel = defaultdict(lambda: {"l1": [], "l2": []})
    summary = {"files": 0, "l1": 0, "l2": 0, "downgraded": 0}
    if not reader_dir.exists():
        return panel, summary
    for path in sorted(reader_dir.glob("reader-*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        summary["files"] += 1
        source = (data.get("source") or "").strip()
        isolation = data.get("isolation") or {}
        modern = data.get("schema_version") == 2
        isolated = modern and isolation.get("no_chronicle") and isolation.get("no_frontmatter")
        kind = "L2" if (source.startswith("真人读者") or source.startswith("真人 sub-agent")) and isolated else "L1"
        if kind == "L2" and not isolated:
            kind = "L1"
            summary["downgraded"] += 1
        if kind == "L2":
            summary["l2"] += 1
        else:
            summary["l1"] += 1
        chapters = set()
        d = data.get("drop") or {}
        if isinstance(d, dict) and d.get("chapter"):
            try:
                chapters.add(int(d["chapter"]))
            except Exception:
                pass
        nx = data.get("next_chapter_focus") or {}
        if isinstance(nx, dict) and nx.get("chapter"):
            try:
                chapters.add(int(nx["chapter"]))
            except Exception:
                pass
        if not chapters:
            continue
        persona_id = str(data.get("id") or "")
        for ch in chapters:
            entry = {
                "persona_id": persona_id,
                "pattern_flags": data.get("pattern_flags") or {},
                "stay_to_50": bool(data.get("stay_to_50")),
                "love_relation": (data.get("love_relation") or {}).get("name"),
                "next_chapter_focus": nx,
            }
            panel[ch][kind.lower()].append(entry)
    return panel, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("path", nargs="?", help="single chapter md file")
    parser.add_argument("--range", nargs=2, type=int, metavar=("LOW", "HIGH"))
    parser.add_argument("--out", help="write JSON to this path")
    args = parser.parse_args()

    audit_rows = json.loads(AUDIT_PATH.read_text(encoding="utf-8")).get("chapters", [])
    audit_by_chapter = {row["chapter"]: row for row in audit_rows}
    panel, panel_summary = build_panel(REPORTS)

    targets = []
    if args.path:
        targets = [Path(args.path)]
    else:
        lo, hi = (None, None)
        if args.range:
            lo, hi = args.range
        for path in sorted(CHRONICLE.glob("*.md")):
            if path.name in {"INDEX.md", "test_write.md"}:
                continue
            if not path.name[:1].isdigit():
                continue
            n = int(path.name.split("-", 1)[0])
            if lo is not None and (n < lo or n > hi):
                continue
            targets.append(path)

    records = []
    for path in targets:
        n, pov, body = read_chapter(path)
        if not HAN.search(body):
            continue
        e = e_score(body, audit_by_chapter.get(n), pov_name=pov)
        # Only numeric keys count toward e_min.
        _e_num = {k: v for k, v in e.items() if isinstance(v, (int, float)) and k != "E5_pov_initiator"}
        e_min = min(_e_num.values())
        r, reason = r_score(n, panel)
        r_min = min(r.values()) if r else None
        g = gates(e_min, r_min)
        records.append({
            "chapter": n,
            "file": str(path.relative_to(ROOT)),
            "pov": pov,
            "engineering": e,
            "engineering_min": e_min,
            "reader": r,
            "reader_min": r_min,
            "reader_reason": reason if r is None else "ok",
            "gates": g,
        })

    payload = {
        "summary": {
            "chapters_scored": len(records),
            "panel_files": panel_summary,
            "publish_floor": PUBLISH_FLOOR,
            "blowup_floor": BLOWUP_FLOOR,
            "addict_R_floor": ADDICT_R_FLOOR,
            "distance_definition": "combined = min(engineering_min, reader_min). distance = max(0, 7.0 - combined). blowup needs 3 consecutive chapters with combined >= 8.5; addictive needs 5 consecutive chapters with combined >= 8.5 and all R >= 7.5.",
        },
        "records": records,
        "boundary": "Engineering score is deterministic. Reader score is null until L2 sub-agent evidence arrives. Any chapter with reader_min == null cannot clear the publish / blowup / addictive gates. This is by design (晋江爆款基线 section 0, 6).",
    }

    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote {args.out} ({len(records)} records, panel={panel_summary})")
        return 0

    print(f"chapters scored: {len(records)}  panel files: {panel_summary}")
    print(f"publish floor: {PUBLISH_FLOOR}  blowup floor: {BLOWUP_FLOOR}  addictive R floor: {ADDICT_R_FLOOR}")
    n_with_r = sum(1 for r in records if r["reader_min"] is not None)
    print(f"chapters with reader track: {n_with_r} / {len(records)}")
    print()
    print(f"{'chapter':>6}  {'E_min':>6}  {'R_min':>6}  {'pub':>4}  {'blow':>5}  {'add':>4}  file")
    for r in records[:50]:
        e = r["engineering_min"]
        m = r["reader_min"]
        m_str = f"{m:.1f}" if m is not None else "--"
        g = r["gates"]
        print(f"{r['chapter']:>6}  {e:>6.2f}  {m_str:>6}  {('Y' if g['publish'] else 'n'):>4}  {('Y' if g['blowup_chapter'] else 'n'):>5}  {('Y' if g['addictive_chapter'] else 'n'):>4}  {r['file']}")
    if len(records) > 50:
        print(f"... ({len(records) - 50} more)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
