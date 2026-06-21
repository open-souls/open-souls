"""cast/<name>/ : state.json (engine, per-season) + memory.md (chronicler, append, portable)."""
import os, json, re, datetime


def cdir(name):  return os.path.join("souls", name)
def spath(name): return os.path.join(cdir(name), "state.json")
def mpath(name): return os.path.join(cdir(name), "memory.md")


def load_state(name):
    if os.path.exists(spath(name)):
        return json.load(open(spath(name), encoding="utf-8"))
    return {"season": None, "incarnation": "", "location": "", "condition": ""}


def save_state(name, st):
    os.makedirs(cdir(name), exist_ok=True)
    json.dump(st, open(spath(name), "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def incarnated(name, season):
    return load_state(name).get("season") == season


def add_memory(name, text, weight, season, kind=""):
    os.makedirs(cdir(name), exist_ok=True)
    new = not os.path.exists(mpath(name))
    with open(mpath(name), "a", encoding="utf-8") as f:
        if new:
            f.write(f"# {name} · 忆\n")
        tag = f"[w{weight}]" + (f" {kind}" if kind else "")
        f.write(f"\n## S{season} {datetime.date.today().isoformat()}  {tag}\n{text}\n")


_ENTRY = re.compile(r"^## S(\d+) (\S+)\s+\[w(\d+)\]")


def recall(name, k=4):
    """Top-k by weight, latest first. Cheap retrieval, carries across seasons."""
    if not os.path.exists(mpath(name)):
        return []
    parts = re.split(r"(?=^## S\d+ )", open(mpath(name), encoding="utf-8").read(), flags=re.M)
    out = []
    for i, part in enumerate(parts):
        m = _ENTRY.match(part.strip())
        if not m:
            continue
        body = part.split("\n", 1)[1].strip() if "\n" in part.strip() else ""
        out.append({"w": int(m.group(3)), "i": i, "text": body})
    out.sort(key=lambda e: (e["w"] + e["i"] * 0.05), reverse=True)
    return [e["text"] for e in out[:k] if e["text"]]
