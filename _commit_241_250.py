# -*- coding: utf-8 -*-
import os, subprocess, sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

os.chdir(r'c:\Users\stanc\github\open-souls\seasons\01-xianxia\chronicle')

files = [
    'ch241-\u6797\u5d07\u770b.md',
    'ch242-\u7076\u8fb9.md',
    'ch243-\u82cf\u633d\u7aef\u7cd6.md',
    'ch244-\u6797\u5f7b\u770b\u6797\u5919.md',
    'ch245-\u6797\u53d9\u7b49.md',
    'ch246-\u6797\u5d07\u4fe1.md',
    'ch247-\u7076\u8fb9\u96ea.md',
    'ch248-\u6797\u5f7b\u7ad9.md',
    'ch249-\u82cf\u633d\u5728.md',
    'ch250-\u6797\u53d9\u770b.md',
]

# Verify all files exist
missing = [f for f in files if not os.path.exists(f)]
if missing:
    print('MISSING:', missing)
else:
    print('All 10 files exist. Adding to git...')

# git add each file
for f in files:
    r = subprocess.run(['git', 'add', f], capture_output=True, text=True, encoding='utf-8')
    if r.returncode != 0:
        print('GIT ADD FAILED for', f, r.stderr)

# git commit
r = subprocess.run(['git', 'commit', '-m', 'Add ch241-250: \u7b2c\u4e8c\u767e\u4e94\u5341\u56de milestone - \u6797\u53d9\u770b', '--quiet'], capture_output=True, text=True, encoding='utf-8')
print('Commit rc:', r.returncode)
if r.stdout: print('stdout:', r.stdout)
if r.stderr: print('stderr:', r.stderr)

# git log
r = subprocess.run(['git', 'log', '--oneline', '-3'], capture_output=True, text=True, encoding='utf-8')
print('Recent commits:', r.stdout)
