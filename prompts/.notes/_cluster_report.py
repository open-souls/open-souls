import json
from collections import Counter
d = json.load(open('prompts/.notes/2026-09-04-corpus-map.json', encoding='utf-8'))
chs = sorted(d['chapters'], key=lambda r: r['chapter'])
buckets = {}
for r in chs:
    if r.get('error'):
        continue
    b = r['chapter'] // 100
    buckets.setdefault(b, []).append(r)
print('%-9s %4s %9s %8s %11s %7s %8s %8s %s' % ('range', 'n', 'avg_ch', '%short', '%hook_fail', '%loop', '%hunhe', '%nanpin', 'top_title'))
for b in sorted(buckets):
    rs = buckets[b]
    n = len(rs)
    avg = sum(r['metrics']['body_chars'] for r in rs)/n
    short = sum(1 for r in rs if r['metrics']['body_chars']<1500)/n*100
    hfail = sum(1 for r in rs if not r['hook']['evidence'])/n*100
    loop = sum(1 for r in rs if r['template_loop'])/n*100
    hunhe = sum(1 for r in rs if r['line']=='混合')/n*100
    nanpin = sum(1 for r in rs if '男频' in r['line'])/n*100
    ttop = Counter(r['title'] for r in rs).most_common(1)[0]
    print('%3d-%3d %4d %9.0f %7.1f%% %6.1f%% %5.1f%% %6.1f%% %6.1f%% %s(%d)' % (
        b*100, b*100+99, n, avg, short, hfail, loop, hunhe, nanpin, ttop[0], ttop[1]))
