# -*- coding: utf-8 -*-
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
chron = 'seasons/01-xianxia/chronicle'
files = sorted(os.listdir(chron))
for n in [506, 584, 700, 998, 999, 831, 850, 855]:
    matches = [f for f in files if f.startswith(f'ch{n}-')]
    print(f'ch{n}: {matches}')
print('--- ch99* files ---')
for f in files:
    if f.startswith('ch99'):
        print(f'  {f}')
print('--- ch50* sample ---')
for f in files:
    if f.startswith('ch50'):
        print(f'  {f}')
