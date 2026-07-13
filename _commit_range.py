# -*- coding: utf-8 -*-
"""Commit a range of chapters."""
import os, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

os.chdir(r'c:\Users\stanc\github\open-souls\seasons\01-xianxia\chronicle')

TITLES = [
    '\u6797\u5d07\u770b', '\u7076\u8fb9', '\u82cf\u633d\u7aef\u7cd6',
    '\u6797\u5f7b\u770b\u6797\u5919', '\u6797\u53d9\u7b49', '\u6797\u5d07\u4fe1',
    '\u7076\u8fb9\u96ea', '\u6797\u5f7b\u7ad9', '\u82cf\u633d\u5728', '\u6797\u53d9\u770b',
]

start = int(sys.argv[1])
end = int(sys.argv[2])

files = []
for i in range(start, end + 1):
    title = TITLES[(i - 1) % 10]
    files.append('ch{:03d}-{}.md'.format(i, title))

# Verify
missing = [f for f in files if not os.path.exists(f)]
if missing:
    print('MISSING:', missing)
    sys.exit(1)

# git add
for f in files:
    r = subprocess.run(['git', 'add', f], capture_output=True, text=True, encoding='utf-8')
    if r.returncode != 0:
        print('ADD FAIL:', f, r.stderr)
        sys.exit(1)

# commit
msg = sys.argv[3]
r = subprocess.run(['git', 'commit', '-m', msg, '--quiet'], capture_output=True, text=True, encoding='utf-8')
print('commit rc:', r.returncode)
if r.stderr: print('stderr:', r.stderr)

r = subprocess.run(['git', 'log', '--oneline', '-2'], capture_output=True, text=True, encoding='utf-8')
print('log:', r.stdout)
