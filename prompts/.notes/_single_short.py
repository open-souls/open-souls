import json, os, re
from collections import defaultdict
d = json.load(open('prompts/.notes/2026-09-04-corpus-map.json', encoding='utf-8'))
chs = d['chapters']

per_chap = defaultdict(list)
for r in chs:
    if r.get('error'):
        continue
    per_chap[r['chapter']].append(r)

single_short = []
for c, rs in per_chap.items():
    if len(rs) == 1:
        r = rs[0]
        if r['metrics']['body_chars'] < 1500:
            single_short.append((c, r))
print('Single-file short chapters:', len(single_short))
for c, r in sorted(single_short):
    print('  ch%d %s chars=%d cv=%.2f title=%s' % (
        c, r['file'], r['metrics']['body_chars'],
        r['metrics']['cv_sentence_len'], r['title']))
