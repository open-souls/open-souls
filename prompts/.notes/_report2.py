import json
from collections import Counter
d = json.load(open('prompts/.notes/2026-09-04-corpus-map.json', encoding='utf-8'))
chs = d['chapters']

# 真正的样板（手写30分）vs 模板（24-26分）
handwritten_candidates = []
for r in chs:
    if r.get('error'):
        continue
    if r['chapter'] <= 499 and r['metrics']['body_chars'] >= 1500 and r['metrics']['cv_sentence_len']>=0.5:
        handwritten_candidates.append(r)
print('Hand-written candidates:', len(handwritten_candidates))

# 看 ch712 真稿评分
for r in chs:
    if r['file'].startswith('ch712-'):
        print('ch712 sample: title=', r['title'], 'chars=', r['metrics']['body_chars'],
              'cv=', r['metrics']['cv_sentence_len'], 'micro=', r['metrics']['micro'],
              'verb_div=', r['metrics']['verb_diversity'])

# 模板题头分布
titles = Counter(r['title'] for r in chs if not r.get('error'))
print('Top 10 标题模板:')
total = len(chs)
for t, c in titles.most_common(10):
    pct = c/total*100
    print('  %s: %d 章 (%.1f%%)' % (t, c, pct))

# 长度质量分桶 by 标题模板
title_chars = {}
for r in chs:
    if r.get('error'): continue
    title_chars.setdefault(r['title'], []).append(r['metrics']['body_chars'])
print('\n标题模板与字数中位数:')
for t in [t for t,_ in titles.most_common(15)]:
    cs = title_chars.get(t, [])
    if cs:
        med = sorted(cs)[len(cs)//2]
        print('  %s: n=%d med=%d short=%d' % (t, len(cs), med, sum(1 for c in cs if c<1500)))
