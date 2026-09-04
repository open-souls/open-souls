import json, os, re
d = json.load(open("prompts/.notes/2026-09-04-quality-grades-v2.json", encoding="utf-8"))
gs = d["grades"]
# Author self-rubric parse from frontmatter
def author_score(c):
    return c.get("score_field", "")
# 14/14 vs grader
for c in gs[:30]:
    print(c["file"], "author=", author_score(c), "grader=", c["total_27"], "d7=", c["d7_sum"], "rubric=", c["rubric_sum"], "pub=", c["pub_sum"])
