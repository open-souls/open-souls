import json
d = json.load(open("prompts/.notes/2026-09-04-quality-grades-v2.json", encoding="utf-8"))
gs = d["grades"]
top = [c for c in gs if c["total_27"] >= 33]
top.sort(key=lambda c: -c["total_27"])
print(f"total S+A candidates: {len(top)}")
for c in top:
    print(f"{c['file']:35s} {c['total_27']:>2}/27  d7={c['d7_sum']:>2}  rubric={c['rubric_sum']:>2}  pub={c['pub_sum']:>2}")
