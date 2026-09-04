import json
from collections import Counter
d = json.load(open('prompts/.notes/2026-09-04-corpus-map.json', encoding='utf-8'))
chs = d['chapters']

# 每个标题的 H/T 分布
title_stats = {}
for r in chs:
    t = r['title']
    if not t:
        continue
    title_stats.setdefault(t, {'hand': 0, 'template': 0, 'empty': 0, 'files': []})
    if r['metrics']['body_chars'] < 1500:
        title_stats[t]['template'] += 1
    else:
        title_stats[t]['hand'] += 1
    if r['metrics']['body_chars'] == 0:
        title_stats[t]['empty'] += 1
    title_stats[t]['files'].append(r['file'])

# 标题排序
print('%-15s %5s %8s %9s' % ('title', 'hand', 'template', 'empty'))
totals = {'hand': 0, 'template': 0, 'empty': 0}
for t in sorted(title_stats.keys(), key=lambda t: -title_stats[t]['template']):
    s = title_stats[t]
    print('%-15s %5d %8d %9d' % (t, s['hand'], s['template'], s['empty']))
    totals['hand'] += s['hand']
    totals['template'] += s['template']
    totals['empty'] += s['empty']
print('%-15s %5d %8d %9d' % ('TOTAL', totals['hand'], totals['template'], totals['empty']))

# 多少 chapter 有模板版
n_total_files = sum(1 for r in chs if not r.get('error'))
print('\n总文件:', n_total_files)
print('手写 (<1500 短不算):', sum(1 for r in chs if not r.get('error') and r['metrics']['body_chars'] >= 1500))
print('模板短 (<1500):', sum(1 for r in chs if not r.get('error') and r['metrics']['body_chars'] < 1500))
