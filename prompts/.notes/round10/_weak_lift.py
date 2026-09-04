import json
d = json.load(open("prompts/.notes/2026-09-04-quality-grades-v2.json", encoding="utf-8"))
gs = d["grades"]
# Author-weak B/C chapters (author < 13 AND grader < 31)
weak = []
for c in gs:
    af = c.get("score_field", "0/14")
    try:
        a = int(af.split("/")[0])
    except: a = 14
    if a <= 12 and c["total_27"] <= 30:
        weak.append((c["file"], c["total_27"], a, c["d7_sum"], c["rubric_sum"], c["pub_sum"], c["body_chars"]))
weak.sort(key=lambda x: x[1])  # lowest total first
print(f"Chapters where author AND grader both flag weak: {len(weak)}")
print("Bottom 30:")
for c in weak[:30]:
    print(f"  {c[0]:35s} grader={c[1]} author={c[2]}/14 d7={c[3]} rubric={c[4]} pub={c[5]} chars={c[6]}")
print()
print("Distribution:")
buckets = {12: 0, 11: 0, 10: 0, 9: 0}
for c in weak:
    buckets[c[2]] = buckets.get(c[2], 0) + 1
for k in sorted(buckets.keys(), reverse=True):
    print(f"  author {k}/14: {buckets[k]}")
