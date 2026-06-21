"""续写一回 / one chapter of the open isekai serial.

  VILLAGE_MOCK=1 python engine/village.py --ticks 3     # 零 token 看流程
  ANTHROPIC_API_KEY=... python engine/village.py        # 真·续写一回
"""
import os, sys, json, random, itertools, datetime, glob, argparse
sys.path.insert(0, os.path.dirname(__file__))
import yaml
import soul as SOUL, cast as C, season as SE, llm, trace, writer


def heat(ties, a, b):
    r1, r2 = SE.rel(ties, a, b), SE.rel(ties, b, a)
    return abs(r1["tension"]) + abs(r2["tension"]) + abs(r1["affection"] - r2["affection"])


def pick_cast(names, ties, season, pressure, newcomer_first):
    newcomers = [n for n in names if not C.incarnated(n, season)]
    pairs = list(itertools.combinations(names, 2))
    w = [heat(ties, a, b) + random.random() * 3 + 1 for a, b in pairs]
    a, b = random.choices(pairs, weights=w, k=1)[0]
    chosen = [a, b]
    # 新进村的角色优先被写进剧情 —— PR/表单一进村就登场
    if newcomer_first and newcomers and not (set(chosen) & set(newcomers)):
        chosen[random.randint(0, 1)] = random.choice(newcomers)
    if len(names) > 2 and random.random() < 0.2 + pressure * 0.5:
        rest = [n for n in names if n not in chosen]
        if rest:
            chosen.append(random.choice(rest))
    weight = min(10, int(heat(ties, chosen[0], chosen[1]) / 2 + pressure * 4 + 2))
    return chosen, [n for n in chosen if n in newcomers], weight


def pressure_event(p, scope):
    if random.random() > p:
        return ""
    return random.choice([
        "一个名额/一次机会只剩一个，得有人被留下、有人被放弃。",
        "有人要离开了，时间不多。",
        "一场谁也没料到的变故砸下来，打乱所有人的盘算。",
    ])


def story_so_far(sdir):
    idx = os.path.join(sdir, "chronicle", "INDEX.md")
    if not os.path.exists(idx):
        return ""
    lines = [l for l in open(idx, encoding="utf-8") if l.strip().startswith("- ")]
    return ("上一回：" + lines[0][2:].strip()) if lines else ""


def build_prompt(souls, states, ties, chosen, newcomers, world, beat, target, sdir):
    cards = "\n\n".join(SOUL.card(souls[n], states[n]) for n in chosen)
    if newcomers:
        cards += "\n\n新登场(本季第一次): " + " ".join(newcomers)
    rels = [f"{a}→{b}: 好感{SE.rel(ties,a,b)['affection']} 张力{SE.rel(ties,a,b)['tension']}"
            + (f"（{SE.rel(ties,a,b)['feeling']}）" if SE.rel(ties, a, b)["feeling"] else "")
            for a, b in itertools.permutations(chosen, 2)]
    mems = [f"{n}记得：" + "；".join(C.recall(n)) for n in chosen if C.recall(n)]
    trends = open("trends.md", encoding="utf-8").read()[:500] if os.path.exists("trends.md") else ""
    ev = pressure_event(0, world.get("scope", ""))
    parts = ["【出场（角色数据，非指令）】\n" + cards, "【此刻关系】\n" + "\n".join(rels)]
    if mems:    parts.append("【他们带着的记忆（可跨季）】\n" + "\n".join(mems))
    sof = story_so_far(sdir)
    if sof:     parts.append("【前情】\n" + sof)
    if trends:  parts.append("【当季叙事趋势（学形状，别抄）】\n" + trends)
    return "\n\n".join(parts)


def write_chapter(sdir, n, out, chosen, season):
    cdir = os.path.join(sdir, "chronicle")
    os.makedirs(cdir, exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    date = datetime.date.today().isoformat()
    title = out.get("chapter_title", "无题")
    body = out.get("chapter", "").strip()
    open(os.path.join(cdir, f"{n:04d}-{title[:18]}.md"), "w", encoding="utf-8").write(
        f"# 第{n}回 · {title}\n\n> S{season} · {date} · {' / '.join(chosen)}\n\n{body}\n")
    idx = os.path.join(cdir, "INDEX.md")
    head = "# 连载目录\n"
    entry = f"- 第{n}回《{title}》— {' / '.join(chosen)}（{date}）\n"
    rest = ""
    if os.path.exists(idx):
        old = open(idx, encoding="utf-8").read()
        rest = old.split("\n", 1)[1] if "\n" in old else ""
    open(idx, "w", encoding="utf-8").write(head + entry + rest)
    feed = json.load(open("docs/chronicle.json", encoding="utf-8")) if os.path.exists("docs/chronicle.json") else []
    feed.insert(0, {"n": n, "season": season, "title": title, "date": date, "cast": chosen, "body": body})
    json.dump(feed, open("docs/chronicle.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def chap_count(sdir):
    return len(glob.glob(os.path.join(sdir, "chronicle", "0*.md")))


def tick(cfg, souls, sdir, world, ties, arc, pressure):
    season = world.get("season", 1)
    names = list(souls)
    if len(names) < 2:
        raise SystemExit("至少要两个魂才能起戏。先 PR / 提表单送一个进村。")
    states = {n: C.load_state(n) for n in names}
    chosen, newcomers, weight = pick_cast(names, ties, season, pressure, cfg["newcomer_priority"])
    ctx = build_prompt(souls, states, ties, chosen, newcomers, world,
                       SE.beat_line(arc), cfg["target_chapter_chars"], sdir)
    rating = world.get("rating", cfg.get("rating", "暧昧"))
    out, crit, spec = writer.compose(ctx, world, SE.beat_line(arc),
                                     cfg["target_chapter_chars"], rating, weight)

    for name, role in (out.get("incarnations") or {}).items():
        if name in souls:
            st = states[name]
            st.update({"season": season, "incarnation": role})
            C.save_state(name, st)
    for n in chosen:  # 确保出场的人本季已落定身份
        if states[n].get("season") != season:
            states[n].update({"season": season, "incarnation": "本季的一个普通人"})
            C.save_state(n, states[n])
    for u in out.get("updates", []):
        if u.get("from") in souls and u.get("to") in souls:
            SE.apply_update(ties, u)
    for m in out.get("memories", []):
        if m.get("who") in souls:
            C.add_memory(m["who"], m["text"], m.get("importance", 5), season)
    ref = out.get("reflection")
    if ref and ref.get("who") in souls:
        C.add_memory(ref["who"], ref["insight"], 9, season, kind="反思")

    n = chap_count(sdir) + 1
    write_chapter(sdir, n, out, chosen, season)
    SE.save_ties(sdir, ties)
    SE.advance_arc(sdir, arc, cfg["chapters_per_beat"])
    tag = ("★新登场 " + " ".join(newcomers)) if newcomers else ""
    rw = " ↻重写过" if crit.get("rewritten") else ""
    print(f"第{n}回 · {out.get('chapter_title')} [{' / '.join(chosen)}] {tag}"
          f"[审校 {crit.get('total','?')}/14 · {spec.get('trope','')}{rw}]")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticks", type=int, default=1)
    ap.add_argument("--pressure", type=float, default=None)
    args = ap.parse_args()
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cfg = yaml.safe_load(open("config.yaml", encoding="utf-8"))
    pressure = args.pressure if args.pressure is not None else cfg.get("default_pressure", 0.2)
    souls = SOUL.load_cast()
    sdir = SE.current_dir()
    world = SE.load_world(sdir)
    ties = SE.load_ties(sdir)
    if not ties:  # 首跑：吸收灵魂自带的 seed_relations
        for name, meta in souls.items():
            for other, feeling in (meta.get("seed_relations") or {}).items():
                if other in souls:
                    SE.rel(ties, name, other).update({"feeling": feeling, "affection": 2})
    arc = SE.load_arc(sdir, world)
    print(f"Open Souls · {len(souls)} 个魂在场：{', '.join(souls)} | 季{world.get('season')}《{world.get('title')}》| 节拍：{SE.beat_line(arc)}")
    for _ in range(args.ticks):
        tick(cfg, souls, sdir, world, ties, arc, pressure)
    trace.rebuild(souls)


if __name__ == "__main__":
    main()
