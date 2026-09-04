# -*- coding: utf-8 -*-
"""Find liftable chapters: long body but low d7/rubric/pub."""
import json
d = json.load(open('prompts/.notes/2026-09-04-quality-grades.json', encoding='utf-8'))
grades = d['grades']

# Chapters with body >= 1500 chars but d7_sum < 11 (rubric avg)
liftable_d7 = sorted(
    [g for g in grades if g['body_chars'] >= 1500 and g['d7_sum'] < 11],
    key=lambda g: -g['body_chars']
)[:30]

print('Liftable chapters (long body, d7 < 11):')
print('%-5s %-30s %5s %4s %4s %4s %4s' % ('ch', 'file', 'chars', 'd7', 'rub', 'pub', 'tot'))
for g in liftable_d7:
    print('%-5d %-30s %5d %4d %4d %4d %4d' % (
        g['chapter'], g['file'][:30], g['body_chars'],
        g['d7_sum'], g['rubric_sum'], g['pub_sum'], g['total_27']))
