# -*- coding: utf-8 -*-
"""
Commit remaining untracked files:
- 349 chronicle chapters (ch506-790, ch831-857, ch998-999 + special event titles)
- 2 soul files (soul.md, dossier.md) for 容昀

Strategy:
1. Update .gitignore to exclude engine/_*.py, engine/_*.txt, engine/_*.json (scratch)
2. Commit chapters in batches of 75
3. Final commit for soul files
4. Push to origin
"""
import subprocess, sys, os, re

sys.stdout.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE = r'c:\Users\stanc\github\open-souls'

def run(cmd_list, cwd=None, check=True):
    """Run a subprocess command (list form, no shell)."""
    if isinstance(cmd_list, str):
        cmd_list = cmd_list.split()
    print(f'> {" ".join(cmd_list[:3])}...')
    r = subprocess.run(cmd_list, capture_output=True, cwd=cwd or BASE)
    out = r.stdout.decode('utf-8', errors='replace')
    err = r.stderr.decode('utf-8', errors='replace')
    if out.strip():
        print(out.strip()[:500])
    if err.strip():
        print(f'[STDERR] {err.strip()[:500]}')
    if check and r.returncode != 0:
        print(f'FAILED: {cmd_list}')
        sys.exit(1)
    return r

# === 1. Update .gitignore ===
gitignore_path = os.path.join(BASE, '.gitignore')
with open(gitignore_path, 'r', encoding='utf-8') as f:
    gi = f.read()
new_lines = ['engine/_*.py', 'engine/_*.txt', 'engine/_*.json', 'engine/_*.repr']
to_add = [l for l in new_lines if l not in gi]
if to_add:
    print(f'Adding to .gitignore: {to_add}')
    with open(gitignore_path, 'a', encoding='utf-8') as f:
        f.write('\n'.join([''] + to_add) + '\n')

# === 2. Get list of untracked chapter files ===
r = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard'], capture_output=True, cwd=BASE)
untracked = r.stdout.decode('utf-8', errors='replace').splitlines()

# Filter to chapter files
chapter_files = sorted([f for f in untracked if f.startswith('seasons/01-xianxia/chronicle/') and f.endswith('.md')])
soul_files = sorted([f for f in untracked if f.startswith('souls/容昀/')])
print(f'Chapter files: {len(chapter_files)}')
print(f'Soul files: {len(soul_files)}')

# Group chapters by chapter number to understand structure
# Each chapter number may have multiple files (cycle + event)
def chapter_num(f):
    m = re.match(r'seasons/01-xianxia/chronicle/ch(\d+)-', f)
    return int(m.group(1)) if m else 0

by_num = {}
for f in chapter_files:
    n = chapter_num(f)
    by_num.setdefault(n, []).append(f)

# Show chapter number range
nums = sorted(by_num.keys())
print(f'Chapter range: ch{nums[0]} to ch{nums[-1]}')
print(f'Chapter numbers: {len(nums)} unique')
print(f'Total files: {len(chapter_files)}')

# === 3. Commit chapters in batches of 75 ===
BATCH_SIZE = 75
chapters_sorted = sorted(chapter_files)

commit_count = 0
for i in range(0, len(chapters_sorted), BATCH_SIZE):
    batch = chapters_sorted[i:i+BATCH_SIZE]
    first_num = chapter_num(batch[0])
    last_num = chapter_num(batch[-1])
    msg = f'Add ch{first_num}-{last_num} ({len(batch)} files)'
    if i == 0:
        msg += ' [first batch]'
    print(f'\n=== Commit {commit_count+1}: {msg} ({len(batch)} files) ===')

    # git add files
    add_cmd = ['git', 'add', '--'] + batch
    r = subprocess.run(add_cmd, capture_output=True, cwd=BASE)
    if r.returncode != 0:
        print(f'ADD FAILED: {r.stderr.decode("utf-8", errors="replace")}')
        sys.exit(1)

    # git commit
    commit_cmd = ['git', 'commit', '-m', msg]
    r = subprocess.run(commit_cmd, capture_output=True, cwd=BASE)
    out = r.stdout.decode('utf-8', errors='replace')
    err = r.stderr.decode('utf-8', errors='replace')
    print(out.strip()[:400])
    if 'nothing to commit' in out+err:
        print(f'  (nothing to commit - already committed?)')
    elif r.returncode != 0:
        print(f'COMMIT FAILED: {err}')
        sys.exit(1)
    else:
        commit_count += 1
    # Brief pause between commits
    import time
    time.sleep(0.2)

# === 4. Commit soul files ===
if soul_files:
    print(f'\n=== Final: Commit {len(soul_files)} soul files ===')
    add_cmd = ['git', 'add', '--'] + soul_files
    r = subprocess.run(add_cmd, capture_output=True, cwd=BASE)
    msg = f'Add 容昀 character dossier ({len(soul_files)} files)'
    commit_cmd = ['git', 'commit', '-m', msg]
    r = subprocess.run(commit_cmd, capture_output=True, cwd=BASE)
    print(r.stdout.decode('utf-8', errors='replace').strip()[:400])
    if r.returncode == 0:
        commit_count += 1

print(f'\n=== Total commits made: {commit_count} ===')

# === 5. Show final git status ===
print('\n=== Final git status (top 30) ===')
r = subprocess.run(['git', 'status', '--short'], capture_output=True, cwd=BASE)
out = r.stdout.decode('utf-8', errors='replace')
lines = out.splitlines()
print(f'Total uncommitted: {len(lines)}')
for l in lines[:30]:
    print(l)
