import json
from collections import Counter
d = json.load(open('prompts/.notes/2026-09-04-quality-grades.json', encoding='utf-8'))
grades = d['grades']

print('Tier distribution:')
tiers = {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
for g in grades:
    t = g['total_27']
    if t >= 35: tiers['S'] += 1
    elif t >= 33: tiers['A'] += 1
    elif t >= 30: tiers['B'] += 1
    elif t >= 27: tiers['C'] += 1
    elif t >= 24: tiers['D'] += 1
    else: tiers['E'] += 1
for k, v in tiers.items():
    print('  Tier', k, ':', v)

print()
print('Top 10 by total:')
top = sorted(grades, key=lambda g: -g['total_27'])[:10]
for g in top:
    print('  ch%4d %-30s title=%-12s d7=%2d rubric=%2d pub=%2d total=%2d' % (
        g['chapter'], g['file'][:30], g['title'], g['d7_sum'], g['rubric_sum'], g['pub_sum'], g['total_27']))

print()
print('Sub-bottom (under 27):')
bot = sorted([g for g in grades if g['total_27'] < 27], key=lambda g: g['total_27'])
print('  total sub-bottom:', len(bot))
for g in bot[:15]:
    print('  ch%4d %-30s chars=%5d total=%2d d7=%2d rubric=%2d pub=%2d' % (
        g['chapter'], g['file'][:30], g['body_chars'], g['total_27'], g['d7_sum'], g['rubric_sum'], g['pub_sum']))

print()
print('7维文笔分布:')
d7c = Counter(g['d7_sum'] for g in grades)
for k in sorted(d7c.keys()):
    print(' ', k, ':', d7c[k], '(>=12 是精品)')

print()
print('rubric 分布:')
rc = Counter(g['rubric_sum'] for g in grades)
for k in sorted(rc.keys()):
    print(' ', k, ':', rc[k])

print()
print('出片 分布:')
pc = Counter(g['pub_sum'] for g in grades)
for k in sorted(pc.keys()):
    print(' ', k, ':', pc[k], '(>=9 是出片)')
