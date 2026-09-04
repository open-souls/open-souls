import json
from collections import Counter, defaultdict
d = json.load(open('prompts/.notes/2026-09-04-corpus-map.json', encoding='utf-8'))
chs = d['chapters']

# 同 chapter 号取最长
files_per_chap = defaultdict(list)
for r in chs:
    if r.get('error'):
        continue
    files_per_chap[r['chapter']].append(r)

# 看 chapter 800 三篇对比
print('chapter 800 全文件:')
for r in sorted(files_per_chap[800], key=lambda r: -r['metrics']['body_chars']):
    print('  %-30s chars=%-5d cv=%.3f micro=%.3f title=%s' % (
        r['file'], r['metrics']['body_chars'], r['metrics']['cv_sentence_len'],
        r['metrics']['micro'], r['title']))

# 同 chapter 多文件的具体场景数
print('\n共有文件 = 2 个:')
n2 = sum(1 for c, rs in files_per_chap.items() if len(rs)==2)
print('  共 %d 个 chapter 号有 2 个文件' % n2)
print('共有文件 = 3 个:')
n3 = sum(1 for c, rs in files_per_chap.items() if len(rs)==3)
print('  共 %d 个 chapter 号有 3 个文件' % n3)

# 多文件中"短的那篇"是否总是模板稿
short_stubs = 0
real_short = 0
for cnum, rs in files_per_chap.items():
    rs_sorted = sorted(rs, key=lambda r: -r['metrics']['body_chars'])
    for r in rs_sorted[1:]:  # 非最长篇
        if r['metrics']['body_chars'] < 1500:
            short_stubs += 1
        else:
            real_short += 1
print('\n非最长篇中: %d 短stub, %d 长篇' % (short_stubs, real_short))

# 全部文件的字数分布
all_chars = [r['metrics']['body_chars'] for r in chs if not r.get('error')]
buckets = Counter()
for c in all_chars:
    if c < 200: buckets['<200'] += 1
    elif c < 500: buckets['200-500'] += 1
    elif c < 1000: buckets['500-1000'] += 1
    elif c < 1500: buckets['1000-1500'] += 1
    elif c < 2500: buckets['1500-2500'] += 1
    elif c < 4000: buckets['2500-4000'] += 1
    else: buckets['>=4000'] += 1
print('\n全部 %d 文件字数分布:' % len(all_chars))
for k in ['<200','200-500','500-1000','1000-1500','1500-2500','2500-4000','>=4000']:
    print('  %s: %d (%.1f%%)' % (k, buckets[k], buckets[k]/len(all_chars)*100))
