# -*- coding: utf-8 -*-
"""Categorize hook-evidence failures by pattern."""
import json, re
d = json.load(open('prompts/.notes/2026-09-04-corpus-map.json', encoding='utf-8'))
chs = d['chapters']
fail = [r for r in chs if not r.get('error') and not r['hook']['evidence']]

# 看看 first8 在正文里出现的位置（如果出现）
import os, sys
sys.path.insert(0, 'engine')
import prose_lint as PL
chron = 'seasons/01-xianxia/chronicle'

categories = {
    'first8_in_body_partial': 0,  # 前8字不在文里但文中类似
    'first8_in_body_no_match': 0,
    'first8_empty': 0,
    'first8_with_punct': 0,
}
samples = []
for r in fail:
    h = r['hook']
    if not h['first8']:
        categories['first8_empty'] += 1
        continue
    p = os.path.join(chron, r['file'])
    if not os.path.exists(p):
        continue
    text = open(p, encoding='utf-8').read()
    body = PL.body_of(text)
    if h['first8'] in body:
        categories['first8_in_body_partial'] += 1  # shouldn't happen, evidence was false
    else:
        categories['first8_in_body_no_match'] += 1
        if len(samples) < 5:
            samples.append((r['file'], h['first8'], h['hook_text'][:60]))

print('Categories:')
for k, v in categories.items():
    print(' ', k, ':', v)
print()
print('Sample failures (first 5):')
for fn, f8, ht in samples:
    print('  ', fn)
    print('    first8:', repr(f8))
    print('    hook:', ht)
