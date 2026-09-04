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

heroes = []
for cnum, rs in files_per_chap.items():
    rs_sorted = sorted(rs, key=lambda r: -r['metrics']['body_chars'])
    heroes.append((cnum, rs_sorted[0]))

# 按 chapter 号的短章
short_heroes = [(c, h) for c, h in heroes if h['metrics']['body_chars']<1500]
print('短英雄代表章 (%d):' % len(short_heroes))
print('%-5s %-22s %6s %6s %6s' % ('chap', 'title', 'chars', 'cv', 'micro'))
for c, h in short_heroes[:30]:
    print('%-5d %-22s %6d %6.3f %6.3f' % (
        c, h['title'][:22], h['metrics']['body_chars'],
        h['metrics']['cv_sentence_len'], h['metrics']['micro']))

# 看 ch900-999 短英雄们的具体分布
print('\nch800-999 短英雄分布:')
buckets = Counter()
for c, h in short_heroes:
    if 800 <= c < 1000:
        buckets[c//10*10] += 1
for b in sorted(buckets):
    print('  %d-%d: %d' % (b, b+9, buckets[b]))

# 哪些标题短?
short_title = Counter(h['title'] for c, h in short_heroes if 800<=c<1000)
print('\nch800-999 短英雄的标题分布:')
for t, c in short_title.most_common(15):
    print('  %s: %d' % (t, c))
