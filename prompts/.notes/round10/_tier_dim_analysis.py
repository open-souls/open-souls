import json
d = json.load(open("prompts/.notes/2026-09-04-quality-grades-v2.json", encoding="utf-8"))
gs = d["grades"]
# Per-tier dim analysis
dims_d7 = ["节奏", "用词", "潜台词", "感官", "对话", "视角", "克制"]
dims_rubric = ["钩子", "爽痛", "反差", "拉扯", "记忆点", "代入", "新"]
dims_pub = ["画面钩", "截图句", "独立可读", "cast3-5", "强开场", "强收尾"]

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

print("=== Per-tier dim averages (out of 2) ===")
print(f"{'Tier':<5} {'N':<5} {'d7节奏':<7} {'d7用词':<7} {'d7潜台':<7} {'d7感官':<7} {'d7对话':<7} {'d7视角':<7} {'d7克制':<7} {'钩子':<6} {'爽痛':<6} {'反差':<6} {'拉扯':<6} {'记忆':<6} {'代入':<6} {'新':<4} {'画面':<6} {'截图':<6} {'独立':<6} {'cast3-5':<8} {'开场':<6} {'收尾':<6}")
for t in "SABCDE":
    lst = tiers.get(t, [])
    if not lst: continue
    n = len(lst)
    avg = lambda dim, arr: sum(c[dim][i] for c in lst for i in range(len(c[dim]))) / (n * len(lst[0][dim]))
    print(f"{t:<5} {n:<5} {avg('d7', lst):<7.2f} {sum(sum(c['d7']) for c in lst)/(n*7):<7.2f}".replace("0.00", "0.00"), end="")
    parts = [f"{sum(c['d7'][i] for c in lst)/n:<7.2f}" for i in range(7)]
    parts += [f"{sum(c['rubric'][i] for c in lst)/n:<6.2f}" for i in range(7)]
    parts += [f"{sum(c['pub'][i] for c in lst)/n:<6.2f}" for i in range(6)]
    print("".join(parts))
