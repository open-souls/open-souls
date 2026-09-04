import json
d = json.load(open("prompts/.notes/2026-09-04-quality-grades-v2.json", encoding="utf-8"))
gs = d["grades"]
author_pts = []
grader_pts = []
mismatch = []
for c in gs:
    af = c.get("score_field", "0/14")
    try:
        a = int(af.split("/")[0])
    except Exception:
        a = 0
    g = c["total_27"]
    author_pts.append(a)
    grader_pts.append(g)
    diff = a - (g * 14 / 27)  # rescale grader to 14
    if abs(diff) > 2:
        mismatch.append((c["file"], a, g, round(diff, 2)))

print(f"avg author: {sum(author_pts)/len(author_pts):.2f}/14")
print(f"avg grader: {sum(grader_pts)/len(grader_pts):.2f}/27 = {sum(grader_pts)*14/27/len(grader_pts):.2f}/14")
print(f"big-mismatch chapters (>2 diff): {len(mismatch)}")
print("First 30 biggest mismatches (author high, grader low):")
mismatch.sort(key=lambda x: -x[3])
for m in mismatch[:30]:
    print(f"  {m[0]:35s}  author={m[1]:>2}/14  grader={m[2]:>2}/27  diff={m[3]:+.2f}")
print("\nFirst 10 biggest reverse (grader high, author low):")
mismatch.sort(key=lambda x: x[3])
for m in mismatch[:10]:
    print(f"  {m[0]:35s}  author={m[1]:>2}/14  grader={m[2]:>2}/27  diff={m[3]:+.2f}")
