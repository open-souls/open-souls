import json
d = json.load(open("prompts/.notes/2026-09-04-quality-grades-v2.json", encoding="utf-8"))
gs = d["grades"]
# Show author score distribution
af_counts = {}
for c in gs:
    af = c.get("score_field", "0/14")
    af_counts[af] = af_counts.get(af, 0) + 1
print("Author score distribution (out of 1191):")
for k in sorted(af_counts.keys(), reverse=True):
    print(f"  {k}: {af_counts[k]}")

# What grader total does each author-score bucket get?
print("\nGrader avg by author score:")
author_buckets = {}
for c in gs:
    af = c.get("score_field", "0/14")
    author_buckets.setdefault(af, []).append(c["total_27"])
for k in sorted(author_buckets.keys(), reverse=True):
    lst = author_buckets[k]
    print(f"  {k}: count={len(lst)}, avg_grader={sum(lst)/len(lst):.2f}, min={min(lst)}, max={max(lst)}")
