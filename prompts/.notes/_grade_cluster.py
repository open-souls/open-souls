import json
from collections import defaultdict
d = json.load(open('prompts/.notes/2026-09-04-quality-grades.json', encoding='utf-8'))
grades = d['grades']

per_bucket = defaultdict(list)
for g in grades:
    per_bucket[g['chapter'] // 100].append(g)

print('%-9s %4s %6s %7s %7s %7s %7s' % ('range', 'n', 'avg_ch', 'avg_d7', 'avg_rub', 'avg_pub', 'avg_total'))
for b in sorted(per_bucket.keys()):
    rs = per_bucket[b]
    n = len(rs)
    avg_ch = sum(r['body_chars'] for r in rs) / n
    avg_d7 = sum(r['d7_sum'] for r in rs) / n
    avg_rub = sum(r['rubric_sum'] for r in rs) / n
    avg_pub = sum(r['pub_sum'] for r in rs) / n
    avg_total = sum(r['total_27'] for r in rs) / n
    print('%3d-%3d %4d %6.0f %7.2f %7.2f %7.2f %7.2f' % (
        b*100, b*100+99, n, avg_ch, avg_d7, avg_rub, avg_pub, avg_total))
