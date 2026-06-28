import re, glob, sys

sys.stdout.reconfigure(encoding='utf-8')

chapters = {}
files = sorted(glob.glob('seasons/01-xianxia/chronicle/48*.md') + glob.glob('seasons/01-xianxia/chronicle/49*.md') + glob.glob('seasons/01-xianxia/chronicle/50*.md'))
for fn in files:
    fn_norm = fn.replace('\\', '/')
    m = re.match(r'seasons/01-xianxia/chronicle/(\d+)-', fn_norm)
    if not m:
        continue
    ch_num = int(m.group(1))
    if ch_num < 481 or ch_num > 502:
        continue
    with open(fn, 'r', encoding='utf-8') as f:
        text = f.read()
    fm_match = re.search(r'^---\n(.*?)\n---', text, re.DOTALL)
    if not fm_match:
        continue
    fm = fm_match.group(1)
    cast_match = re.search(r'^cast:\s*\[(.*?)\]', fm, re.MULTILINE | re.DOTALL)
    if not cast_match:
        continue
    cast_str = cast_match.group(1)
    raw = [c.strip() for c in cast_str.split(',') if c.strip()]
    cast = [re.sub(r'\s*\(.*?\)\s*$', '', c).strip() for c in raw]
    chapters[ch_num] = cast

print(f'Loaded {len(chapters)} chapters')
print()
print('=== Per-chapter cast ===')
for ch in sorted(chapters):
    print(f'  ch{ch}: {chapters[ch]}')

print()
print('=== High-freq chars (limit 8) ===')
high_freq = ['苏挽', '阿湄', '凌朔', '牛阿大']
for char in high_freq:
    cur_gap = 0
    gap_start = None
    longest = (None, None, 0)
    for ch in range(481, 503):
        if ch in chapters and char in chapters[ch]:
            if cur_gap > longest[2] and gap_start is not None:
                longest = (gap_start, ch - 1, cur_gap)
            cur_gap = 0
            gap_start = None
        else:
            if cur_gap == 0:
                gap_start = ch
            cur_gap += 1
    if cur_gap > longest[2] and gap_start is not None:
        longest = (gap_start, 502, cur_gap)
    if longest[2] > 0:
        flag = ' WARN-OVER-8' if longest[2] > 8 else ''
        print(f'  {char}: longest gap {longest[2]} ch (ch{longest[0]}-ch{longest[1]}){flag}')
    else:
        print(f'  {char}: present throughout 22 ch range')

print()
print('=== Mid-freq chars (limit 12) ===')
mid_freq = ['裴无咎', '余伯', '沈疏桐']
for char in mid_freq:
    cur_gap = 0
    gap_start = None
    longest = (None, None, 0)
    for ch in range(481, 503):
        if ch in chapters and char in chapters[ch]:
            if cur_gap > longest[2] and gap_start is not None:
                longest = (gap_start, ch - 1, cur_gap)
            cur_gap = 0
            gap_start = None
        else:
            if cur_gap == 0:
                gap_start = ch
            cur_gap += 1
    if cur_gap > longest[2] and gap_start is not None:
        longest = (gap_start, 502, cur_gap)
    if longest[2] > 0:
        flag = ' WARN-OVER-12' if longest[2] > 12 else ''
        print(f'  {char}: longest gap {longest[2]} ch (ch{longest[0]}-ch{longest[1]}){flag}')
    else:
        print(f'  {char}: present throughout 22 ch range')