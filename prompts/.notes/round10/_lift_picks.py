import json
d = json.load(open("prompts/.notes/2026-09-04-quality-grades-v2.json", encoding="utf-8"))
gs = d["grades"]
candidates = []
for c in gs:
    if c["total_27"] < 30 or c["total_27"] > 32: continue
    easy_room = 0
    if c["rubric"][2] < 2: easy_room += (2 - c["rubric"][2])
    if c["pub"][3] < 2: easy_room += (2 - c["pub"][3])
    if c["d7"][6] < 2: easy_room += (2 - c["d7"][6])
    if c["rubric"][3] < 2: easy_room += (2 - c["rubric"][3])
    if c["d7"][2] < 2: easy_room += (2 - c["d7"][2])
    candidates.append((c["file"], c["total_27"], easy_room, c["d7_sum"], c["rubric_sum"], c["pub_sum"]))

candidates.sort(key=lambda x: -x[2])
print(f"B-tier (30-32) chapters ranked by easy-lift room (top 30):")
for c in candidates[:30]:
    print(f"  {c[0]:35s} total={c[1]} room={c[2]:.1f}  d7={c[3]} rubric={c[4]} pub={c[5]}")
