import json
d = json.load(open("prompts/.notes/2026-09-04-quality-grades-v2.json", encoding="utf-8"))
gs = d["grades"]
# Per-tier dim analysis
def bucket(c):
    t = c["total_27"]
    if t >= 35: return "S"
    elif t >= 33: return "A"
    elif t >= 30: return "B"
    elif t >= 27: return "C"
    elif t >= 24: return "D"
    else: return "E"

tiers = {}
for c in gs:
    t = bucket(c)
    tiers.setdefault(t, []).append(c)

d7_names = ["节奏", "用词", "潜台", "感官", "对话", "视角", "克制"]
rubric_names = ["钩子", "爽痛", "反差", "拉扯", "记忆", "代入", "新"]
pub_names = ["画面", "截图", "独立", "cast3-5", "开场", "收尾"]

print("=== Per-tier dim averages (out of 2) ===\n")
header = f"{'Tier':<5} {'N':<5}"
for n in d7_names: header += f" {n:<6}"
for n in rubric_names: header += f" {n:<6}"
for n in pub_names: header += f" {n:<6}"
print(header)
print("-" * len(header))
for t in "SABCDE":
    lst = tiers.get(t, [])
    if not lst: continue
    n = len(lst)
    line = f"{t:<5} {n:<5}"
    for i in range(7):
        line += f" {sum(c['d7'][i] for c in lst)/n:<6.2f}"
    for i in range(7):
        line += f" {sum(c['rubric'][i] for c in lst)/n:<6.2f}"
    for i in range(6):
        line += f" {sum(c['pub'][i] for c in lst)/n:<6.2f}"
    print(line)

# Per-dim across ALL chapters
print("\n=== ALL CHAPTERS per-dim average ===")
n = len(gs)
print(f"N = {n}")
for i, name in enumerate(d7_names):
    avg = sum(c['d7'][i] for c in gs) / n
    pct_below = sum(1 for c in gs if c['d7'][i] < 1.5) / n * 100
    print(f"  d7.{i+1} {name:<6} avg={avg:.2f}/2  pct<1.5={pct_below:.0f}%")
print()
for i, name in enumerate(rubric_names):
    avg = sum(c['rubric'][i] for c in gs) / n
    pct_below = sum(1 for c in gs if c['rubric'][i] < 1.5) / n * 100
    print(f"  rubric.{i+1} {name:<6} avg={avg:.2f}/2  pct<1.5={pct_below:.0f}%")
print()
for i, name in enumerate(pub_names):
    avg = sum(c['pub'][i] for c in gs) / n
    pct_below = sum(1 for c in gs if c['pub'][i] < 1.5) / n * 100
    print(f"  pub.{i+1} {name:<6} avg={avg:.2f}/2  pct<1.5={pct_below:.0f}%")
