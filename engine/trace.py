"""有迹可循: every character gets a dossier — their incarnations, ties, appearances, key memories.
Plus a global CAST.md so any reader can follow any thread."""
import os, json, glob
import cast as C, season as SE


def appearances():
    feed = json.load(open("docs/chronicle.json", encoding="utf-8")) if os.path.exists("docs/chronicle.json") else []
    by = {}
    for ch in feed:
        for n in ch.get("cast", []):
            by.setdefault(n, []).append(ch)
    return by


def dossier(name, meta, ties, apps):
    st = C.load_state(name)
    fr = meta["fracture"]
    L = [f"# {name}", f"> {meta['one_line']}", "",
         f"**裂缝** 嘴上「{fr['says']}」/ 实际「{fr['does']}」  ",
         f"**逼到墙角** {meta['under_pressure']}", ""]
    if st.get("incarnation"):
        L.append(f"**本季身份** {st['incarnation']}（{st.get('condition','') or '在场'}）\n")
    rels = ties.get(name, {})
    if rels:
        L.append("## 关系")
        for o, r in rels.items():
            L.append(f"- 对 **{o}**：好感{r['affection']} 信任{r['trust']} 张力{r['tension']}"
                     + (f" — {r['feeling']}" if r["feeling"] else ""))
        L.append("")
    mem = C.recall(name, k=5)
    if mem:
        L.append("## 记得的事")
        L += [f"- {m}" for m in mem]
        L.append("")
    if apps:
        L.append("## 出场")
        L += [f"- 第{a['n']}回《{a['title']}》（S{a.get('season','?')}·{a['date']}）" for a in apps]
        L.append("")
    return "\n".join(L)


def rebuild(souls):
    sdir = SE.current_dir()
    ties = SE.load_ties(sdir) if sdir else {}
    apps = appearances()
    rows = []
    for name, meta in souls.items():
        a = apps.get(name, [])
        open(os.path.join("souls", _slugdir(name), "dossier.md"), "w", encoding="utf-8").write(
            dossier(name, meta, ties, a))
        rows.append((name, meta["one_line"], len(a)))
    rows.sort(key=lambda r: r[2], reverse=True)
    idx = ["# 众魂名册 · Open Souls", "", "谁都有迹可循。点开任一个看 ta 的整条线。", ""]
    idx += [f"- **{n}** — {ol} · 出场 {c} 回" for n, ol, c in rows]
    os.makedirs("docs", exist_ok=True)
    open("CAST.md", "w", encoding="utf-8").write("\n".join(idx) + "\n")


def _slugdir(name):
    # map a soul name back to its cast/ folder
    for p in glob.glob("souls/*/soul.md"):
        import soul as SOUL
        if SOUL.parse(p)["name"] == name:
            return os.path.basename(os.path.dirname(p))
    return name


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    import soul as SOUL
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    rebuild(SOUL.load_cast())
    print("dossiers + CAST.md rebuilt")
