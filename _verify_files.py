# -*- coding: utf-8 -*-
import os, sys
sys.stdout.reconfigure(encoding='utf-8')

base = r'c:\Users\stanc\github\open-souls'

# Files to check
files = [
    'seasons/01-xianxia/chronicle/ch998-林彻站.md',
    'seasons/01-xianxia/chronicle/ch999-苏挽在.md',
    'souls/容昀/soul.md',
    'souls/容昀/dossier.md',
    '0]',
]
for f in files:
    p = os.path.join(base, f)
    if os.path.exists(p):
        size = os.path.getsize(p)
        print(f'EXISTS {size:>8}b  {f}')
    else:
        print(f'MISSING          {f}')

# Check if ch506-583 exist
print('\n--- ch506-583 ---')
for i in range(506, 584):
    matches = []
    for d in os.listdir(os.path.join(base, 'seasons/01-xianxia/chronicle')):
        if d.startswith(f'ch{i}-') and d.endswith('.md'):
            matches.append(d)
    if not matches:
        print(f'MISSING ch{i}')

# Check if ch594-699 exist
print('\n--- ch594-699 ---')
missing = []
for i in range(594, 700):
    found = False
    for d in os.listdir(os.path.join(base, 'seasons/01-xianxia/chronicle')):
        if d.startswith(f'ch{i}-') and d.endswith('.md'):
            found = True
            break
    if not found:
        missing.append(i)
if missing:
    print(f'Missing: {missing[:30]}... ({len(missing)} total)')
else:
    print('All present')

# Check if ch701-790 exist
print('\n--- ch701-790 ---')
missing = []
for i in range(701, 791):
    found = False
    for d in os.listdir(os.path.join(base, 'seasons/01-xianxia/chronicle')):
        if d.startswith(f'ch{i}-') and d.endswith('.md'):
            found = True
            break
    if not found:
        missing.append(i)
if missing:
    print(f'Missing: {missing[:30]}... ({len(missing)} total)')
else:
    print('All present')

# Check if ch794-830 exist (the ch83x ch84x etc. are listed in earlier view)
print('\n--- ch794-830 ---')
missing = []
for i in range(794, 831):
    found = False
    for d in os.listdir(os.path.join(base, 'seasons/01-xianxia/chronicle')):
        if d.startswith(f'ch{i}-') and d.endswith('.md'):
            found = True
            break
    if not found:
        missing.append(i)
if missing:
    print(f'Missing: {missing}')

# Show ch830-857 files specifically
print('\n--- ch830-857 files ---')
for d in sorted(os.listdir(os.path.join(base, 'seasons/01-xianxia/chronicle'))):
    if d.startswith('ch8') and d[3:6].isdigit():
        n = int(d[3:6])
        if 830 <= n <= 857:
            print(f'  {d}')
