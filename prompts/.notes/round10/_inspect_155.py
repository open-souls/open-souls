import json
d = json.load(open("prompts/.notes/2026-09-04-quality-grades-v2.json", encoding="utf-8"))
gs = d["grades"]
for c in gs:
    if c["file"] == "155-共同展开.md":
        print(json.dumps(c, ensure_ascii=False, indent=2))
