import json, statistics
d = json.load(open("prompts/.notes/2026-09-04-quality-grades-v3.json", encoding="utf-8"))
gs = d["grades"]
# Filter out test/index files
gs = [g for g in gs if "test" not in g["file"] and "INDEX" not in g["file"]]
print(f"Real chapters: {len(gs)}")
print("total_52 avg:", round(statistics.mean(g["total_52"] for g in gs), 2))
print("total_52 median:", statistics.median(g["total_52"] for g in gs))
print("total_52 stdev:", round(statistics.stdev(g["total_52"] for g in gs), 2))

# distribution by max=52, normalize to 33 for comparison with v2
norm = [(g["total_52"]/52)*33 for g in gs]
print("normalized to /33:", round(statistics.mean(norm), 2), "median:", round(statistics.median(norm), 2))

# show top 30 S tier
top = sorted(gs, key=lambda g: -g["total_52"])[:30]
print("\n=== TOP 30 (S tier ≥42/52 = ~80%) ===")
for g in top:
    print(f"  {g['file']:35s} total={g['total_52']:>2}/52 (norm {round(g['total_52']/52*33, 1):>4}) d7={g['d7_sum']:>2} rubric={g['rubric_sum']:>2} pub={g['pub_sum']:>2} sh={g['sh_sum']:>2}")

print("\n=== BOTTOM 30 (C/D tier ≤27/52) ===")
bot = sorted(gs, key=lambda g: g["total_52"])[:30]
for g in bot:
    print(f"  {g['file']:35s} total={g['total_52']:>2}/52 (norm {round(g['total_52']/52*33, 1):>4}) chars={g['body_chars']:>5} d7={g['d7_sum']:>2} rubric={g['rubric_sum']:>2} pub={g['pub_sum']:>2} sh={g['sh_sum']:>2}")
