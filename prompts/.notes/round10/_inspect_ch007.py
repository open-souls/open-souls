import json
d = json.load(open("prompts/.notes/2026-09-04-quality-grades-v2.json", encoding="utf-8"))
for c in d["grades"]:
    if c["file"] == "007-林崇称量.md":
        print(json.dumps(c, ensure_ascii=False, indent=2))
