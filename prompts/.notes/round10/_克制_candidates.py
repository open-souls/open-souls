import json
d = json.load(open("prompts/.notes/2026-09-04-quality-grades-v2.json", encoding="utf-8"))
gs = d["grades"]
# Find chapters where d7[6] (克制) is 1 and grader is 30-32 (high potential to lift to 33+)
print("B/C tier chapters where 克制=1 (author summarized at end):")
count = 0
for c in gs:
    if c["d7"][6] == 1 and 27 <= c["total_27"] <= 32:
        count += 1
print(f"Total: {count}")
