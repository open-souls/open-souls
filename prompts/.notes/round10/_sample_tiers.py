import json, os
d = json.load(open("prompts/.notes/2026-09-04-quality-grades-v2.json", encoding="utf-8"))
gs = d["grades"]
# Sample: 5 from each tier (S, A, B, C, D)
buckets = {"S": [], "A": [], "B": [], "C": [], "D": []}
for c in gs:
    t = c["total_27"]
    if t >= 35: buckets["S"].append(c)
    elif t >= 33: buckets["A"].append(c)
    elif t >= 30: buckets["B"].append(c)
    elif t >= 27: buckets["C"].append(c)
    else: buckets["D"].append(c)
print("S:", len(buckets["S"]), "A:", len(buckets["A"]), "B:", len(buckets["B"]), "C:", len(buckets["C"]), "D:", len(buckets["D"]))
# Pick chapter number ranges from each tier
import random
random.seed(11)
def pick_spread(b, n=5):
    if len(b) <= n: return b
    # pick spread across the chapter range
    b_sorted = sorted(b, key=lambda c: c.get("chapter", 999))
    step = max(1, len(b_sorted)//n)
    return [b_sorted[i*step] for i in range(n)]
for tier, lst in buckets.items():
    print(f"\n--- TIER {tier} samples (5) ---")
    for c in pick_spread(lst, 5):
        print(f"  {c['file']:35s} {c['total_27']:>2}/27  d7={c['d7_sum']:>2} rubric={c['rubric_sum']:>2} pub={c['pub_sum']:>2} chars={c['body_chars']:>5}")
