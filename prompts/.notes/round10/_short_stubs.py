import json
d = json.load(open("prompts/.notes/2026-09-04-quality-grades-v2.json", encoding="utf-8"))
gs = d["grades"]
short = [c for c in gs if c["body_chars"] < 500]
print(f"Chapters <500 chars: {len(short)}")
for c in short[:30]:
    print(f"  {c['file']:35s} {c['body_chars']} chars grader={c['total_27']}")
