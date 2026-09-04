import json, statistics
d = json.load(open("prompts/.notes/2026-09-04-quality-grades-v3.json", encoding="utf-8"))
gs = d["grades"]
print("total_33 avg:", statistics.mean(g["total_33"] for g in gs))
print("total_33 median:", statistics.median(g["total_33"] for g in gs))
print("total_33 stdev:", statistics.stdev(g["total_33"] for g in gs))
top = sorted(gs, key=lambda g: -g["total_33"])[:5]
for g in top:
    print(f"  {g['file']:35s} total={g['total_33']}/33 d7={g['d7']} rubric={g['rubric']} pub={g['pub']} sh={g['sh']}")
bot = sorted(gs, key=lambda g: g["total_33"])[:10]
for g in bot:
    print(f"  {g['file']:35s} total={g['total_33']}/33 chars={g['body_chars']}")
