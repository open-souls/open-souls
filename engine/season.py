"""Season = a world the souls are dropped into: world.md + ties.json + arc.json (beats)."""
import os, json, glob, re
import yaml

DEFAULT_ARC = ["起：人物落定", "承：关系与心结积累", "转：一场变故打乱所有人", "合：直面与收束"]


def current_dir():
    dirs = sorted(glob.glob("seasons/*/"))
    return dirs[-1].rstrip("/") if dirs else None


def load_world(sdir):
    raw = open(os.path.join(sdir, "world.md"), encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", raw, re.S)
    meta = (yaml.safe_load(m.group(1)) if m else {}) or {}
    meta["_body"] = ((m.group(2) if m else raw) or "").strip()[:300]
    return meta


def _p(sdir, f): return os.path.join(sdir, f)


def load_ties(sdir):
    p = _p(sdir, "ties.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def rel(ties, a, b):
    return ties.setdefault(a, {}).setdefault(b, {"affection": 0, "trust": 0, "tension": 0, "feeling": ""})


def apply_update(ties, u):
    r = rel(ties, u["from"], u["to"])
    for k in ("affection", "trust", "tension"):
        r[k] = max(-10, min(10, r[k] + int(u.get(k + "_delta", 0))))
    if u.get("feeling"):
        r["feeling"] = u["feeling"]


def save_ties(sdir, ties):
    json.dump(ties, open(_p(sdir, "ties.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def load_arc(sdir, world):
    p = _p(sdir, "arc.json")
    if os.path.exists(p):
        return json.load(open(p, encoding="utf-8"))
    return {"beats": world.get("arc") or DEFAULT_ARC, "beat": 0, "in_beat": 0}


def advance_arc(sdir, arc, per_beat):
    arc["in_beat"] += 1
    if arc["in_beat"] >= per_beat and arc["beat"] < len(arc["beats"]) - 1:
        arc["beat"] += 1
        arc["in_beat"] = 0
    json.dump(arc, open(_p(sdir, "arc.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return arc


def beat_line(arc):
    return arc["beats"][arc["beat"]]
