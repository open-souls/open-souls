import json
d = json.load(open("prompts/.notes/2026-09-04-quality-grades-v2.json", encoding="utf-8"))
gs = d["grades"]
# D-tier chapters (grader 24-26) - author agrees if <13
print("=== D-tier (grader 24-26) chapters with author score ===")
for c in gs:
    if 24 <= c["total_27"] <= 26:
        af = c.get("score_field", "0/14")
        try: a = int(af.split("/")[0])
        except: a = 14
        print(f"  {c['file']:35s} grader={c['total_27']} author={a}/14 d7={c['d7_sum']} rubric={c['rubric_sum']} pub={c['pub_sum']} chars={c['body_chars']}")
