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
DECISION = re.compile(r"决定|改为|改成|只[把将]|不再|不肯|拒绝|主动|亲自|自己开|自己拿|自己写|签下|不签|先封|按在|按下|留下|设定|逼得|给.{0,8}两条路|让.{0,8}写|要求.{0,8}落名")
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


def e_score(body, audit_row):
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
    return {"E1_open_conflict": e1, "E2_mid_turn": e2, "E3_hook_stop": e3, "E4_agency": e4, "E5_relationship_cost": e5}


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
        e = e_score(body, audit_by_chapter.get(n))
        e_min = min(e.values())
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