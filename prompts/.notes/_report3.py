import json, os
from collections import Counter, defaultdict
d = json.load(open('prompts/.notes/2026-09-04-corpus-map.json', encoding='utf-8'))
chs = d['chapters']

# 看每个 chapter 号有多少文件
files_per_chap = defaultdict(list)
for r in chs:
    if r.get('error'):
        continue
    files_per_chap[r['chapter']].append(r)

dup_dist = Counter(len(v) for v in files_per_chap.values())
print('每个 chapter 号的文件数分布:')
for n, c in sorted(dup_dist.items()):
    print('  %d 文件/chapter: %d 个 chapter 号' % (n, c))

# 看 chapter 号 vs 文件
print('\n例: chapter 641 的所有文件:')
for r in files_per_chap[641]:
    print('  %s  title=%s  chars=%d' % (r['file'], r['title'], r['metrics']['body_chars']))

print('\nchapter 541 的所有文件:')
for r in files_per_chap[541]:
    print('  %s  title=%s  chars=%d' % (r['file'], r['title'], r['metrics']['body_chars']))

print('\nchapter 800 的所有文件:')
for r in files_per_chap[800]:
    print('  %s  title=%s  chars=%d' % (r['file'], r['title'], r['metrics']['body_chars']))

print('\nchapter 509 的所有文件:')
for r in files_per_chap[509]:
    print('  %s  title=%s  chars=%d' % (r['file'], r['title'], r['metrics']['body_chars']))

# 每章号选最长篇为代表作
hero_by_chap = {}
for cnum, rs in files_per_chap.items():
    rs_sorted = sorted(rs, key=lambda r: -r['metrics']['body_chars'])
    hero_by_chap[cnum] = rs_sorted[0]
hero_chars = [r['metrics']['body_chars'] for r in hero_by_chap.values()]
hero_short = sum(1 for c in hero_chars if c < 1500)
print('\n每章号最长篇代表: 总=%d 短于1500=%d' % (len(hero_chars), hero_short))
# 看 999 的所有
print('\nchapter 999 的所有文件:')
for r in files_per_chap[999]:
    print('  %s  title=%s  chars=%d' % (r['file'], r['title'], r['metrics']['body_chars']))
print('\nchapter 990 的所有文件:')
for r in files_per_chap[990]:
    print('  %s  title=%s  chars=%d' % (r['file'], r['title'], r['metrics']['body_chars']))
print('\nchapter 900 的所有文件:')
for r in files_per_chap[900]:
    print('  %s  title=%s  chars=%d' % (r['file'], r['title'], r['metrics']['body_chars']))
