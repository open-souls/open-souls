# -*- coding: utf-8 -*-
"""Sample hook-evidence failures to see patterns."""
import json, re
from pathlib import Path
d = json.load(open('prompts/.notes/2026-09-04-corpus-map.json', encoding='utf-8'))
chs = d['chapters']

fail = [r for r in chs if not r.get('error') and not r['hook']['evidence']]
print('Hook evidence fail count:', len(fail))
print()
print('Sample (first 15):')
for r in fail[:15]:
    h = r['hook']['hook_text']
    first8 = r['hook']['first8']
    print('  %-30s first8=%-12s hook=%s' % (r['file'][:30], repr(first8)[:14], repr(h)[:50]))
