# -*- coding: utf-8 -*-
"""List current S/A tier chapters as爆款 candidates for真读者 试读."""
import json
from collections import defaultdict
d = json.load(open('prompts/.notes/2026-09-04-quality-grades.json', encoding='utf-8'))
grades = d['grades']

top = sorted([g for g in grades if g['total_27'] >= 33], key=lambda g: -g['total_27'])

print('Total S/A chapters (>=33):', len(top))
print()
print('TOP TIER爆款 candidates (按总评分):')
print('%-5s %-30s %4s %4s %4s %4s %4s %s' % ('ch', 'file', 'chars', 'd7', 'rub', 'pub', 'tot', 'title'))
for g in top:
    print('%-5d %-30s %4d %4d %4d %4d %4d %s' % (
        g['chapter'], g['file'][:30], g['body_chars'],
        g['d7_sum'], g['rubric_sum'], g['pub_sum'], g['total_27'], g['title']))
