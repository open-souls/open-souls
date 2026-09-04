import json
from collections import Counter, defaultdict
d = json.load(open('prompts/.notes/2026-09-04-corpus-map.json', encoding='utf-8'))
chs = d['chapters']

# 每个 chapter 号的最长篇代表
files_per_chap = defaultdict(list)
for r in chs:
    if r.get('error'):
        continue
    files_per_chap[r['chapter']].append(r)

heroes = []
for cnum, rs in files_per_chap.items():
    rs_sorted = sorted(rs, key=lambda r: -r['metrics']['body_chars'])
    heroes.append((cnum, rs_sorted[0]))

# 按百桶统计
buckets = defaultdict(list)
for cnum, h in heroes:
    buckets[cnum // 100].append(h)

print('英雄代表篇（每章号最长篇）按 100 桶:')
print('%-9s %4s %8s %7s %8s %8s %s' % ('range', 'n', 'avg_ch', '%short', 'cv_avg', 'micro_avg', 'top_title'))
for b in sorted(buckets):
    rs = buckets[b]
    n = len(rs)
    avg = sum(r['metrics']['body_chars'] for r in rs) / n
    short = sum(1 for r in rs if r['metrics']['body_chars']<1500) / n * 100
    cv_avg = sum(r['metrics']['cv_sentence_len'] for r in rs) / n
    micro_avg = sum(r['metrics']['micro'] for r in rs) / n
    title = Counter(r['title'] for r in rs).most_common(1)[0]
    print('%3d-%3d %4d %8.0f %6.1f%% %8.3f %8.3f %s(%d)' % (
        b*100, b*100+99, n, avg, short, cv_avg, micro_avg, title[0], title[1]))

# 总览
print('\n总览:')
all_heroes = [h for _, h in heroes]
print('英雄代表数:', len(all_heroes))
print('短<1500:', sum(1 for h in all_heroes if h['metrics']['body_chars']<1500))
print('CV<0.4:', sum(1 for h in all_heroes if h['metrics']['cv_sentence_len']<0.4))
print('micro>0.4:', sum(1 for h in all_heroes if h['metrics']['micro']>0.4))
print('平均字数:', sum(h['metrics']['body_chars'] for h in all_heroes)/len(all_heroes))
print('平均 CV:', sum(h['metrics']['cv_sentence_len'] for h in all_heroes)/len(all_heroes))
print('平均 micro:', sum(h['metrics']['micro'] for h in all_heroes)/len(all_heroes))
