# -*- coding: utf-8 -*-
"""Cast size audit."""
import json, re
from collections import Counter
d = json.load(open('prompts/.notes/2026-09-04-quality-grades.json', encoding='utf-8'))
grades = d['grades']

cast_dist = Counter()
for g in grades:
    fm_text = open('seasons/01-xianxia/chronicle/' + g['file'], encoding='utf-8').read()
    m = re.match(r'^---\n.*?cast:\s*\[([^\]]*)\]', fm_text, re.S)
    cast_str = m.group(1) if m else ''
    n = cast_str.count(',') + 1 if cast_str else 0
    cast_dist[n] += 1

print('Cast size distribution:')
for n in sorted(cast_dist.keys()):
    print(' ', n, 'chars:', cast_dist[n])

# per chapter
print()
print('Cast=1 chapters:', sum(1 for c in cast_dist.values() if c))
print('Cast=2 chapters:', sum(1 for c in [cast_dist[2]]))
print('Cast=3-5 chapters:', sum(cast_dist[n] for n in [3,4,5]))
print('Cast=6+ chapters:', sum(cast_dist[n] for n in cast_dist if n >= 6))
