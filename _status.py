# -*- coding: utf-8 -*-
import subprocess, sys, os

os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

r = subprocess.run(['git','status','--short'], capture_output=True)
# Decode bytes manually
out = r.stdout.decode('utf-8', errors='replace')
lines = out.splitlines()
print(f'TOTAL: {len(lines)}')
print('--- FIRST 30 ---')
for l in lines[:30]:
    print(l)
print('--- LAST 30 ---')
for l in lines[-30:]:
    print(l)
