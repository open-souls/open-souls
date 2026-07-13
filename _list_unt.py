# -*- coding: utf-8 -*-
import subprocess, sys, os
sys.stdout.reconfigure(encoding='utf-8')
r = subprocess.run(['git','status','--short'], capture_output=True)
out = r.stdout.decode('utf-8', errors='replace')
lines = [l for l in out.splitlines() if l.strip()]

# Group by directory
from collections import defaultdict
groups = defaultdict(list)
for l in lines:
    parts = l.split(None, 1)
    if len(parts) < 2:
        groups['(no path)'].append(l)
        continue
    f = parts[1]
    if '/' in f:
        top = f.split('/', 1)[0]
    else:
        top = '(root)'
    groups[top].append(l)

for top in sorted(groups.keys()):
    files = groups[top]
    print(f'== {top} ({len(files)}) ==')
    if top == 'seasons':
        # Just show chronicle count and range
        chronicles = [f.split(None,1)[1] for f in files if 'chronicle' in f]
        print(f'  chronicle files: {len(chronicles)}')
        # Get chapter numbers
        import re
        nums = []
        for c in chronicles:
            m = re.match(r'.*/ch(\d+)-', c)
            if m:
                nums.append(int(m.group(1)))
        if nums:
            nums.sort()
            print(f'  range: ch{min(nums)}-ch{max(nums)}')
            # Find gaps
            full = set(range(min(nums), max(nums)+1))
            missing = sorted(full - set(nums))
            if missing:
                print(f'  missing in range: {missing[:30]}{"..." if len(missing)>30 else ""}')
    elif top in ('engine', 'docs', 'souls', 'prompts', 'tools'):
        for l in files:
            print(f'  {l}')
    else:
        for l in files[:30]:
            print(f'  {l}')
        if len(files) > 30:
            print(f'  ... and {len(files)-30} more')
    print()
