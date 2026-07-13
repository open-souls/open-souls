# -*- coding: utf-8 -*-
"""
Final cleanup:
1. Delete junk file '0]'
2. Commit .gitignore change (so engine/_*.py etc. are ignored going forward)
3. Commit root helper scripts (dev tools used during the rewrite session)
4. Push all commits to origin/main
"""
import subprocess, sys, os, time

sys.stdout.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE = r'c:\Users\stanc\github\open-souls'

def run(cmd, check=True):
    """Run command, return (rc, stdout, stderr)."""
    r = subprocess.run(cmd, capture_output=True, cwd=BASE)
    out = r.stdout.decode('utf-8', errors='replace')
    err = r.stderr.decode('utf-8', errors='replace')
    if check and r.returncode != 0:
        print(f'FAILED ({r.returncode}): {cmd}')
        if out: print(f'  STDOUT: {out[:300]}')
        if err: print(f'  STDERR: {err[:300]}')
    return r.returncode, out, err

# 1. Delete junk file
junk = os.path.join(BASE, '0]')
if os.path.exists(junk):
    os.remove(junk)
    print(f'Deleted junk file: 0]')

# 2. Get all untracked helper scripts
rc, out, _ = run(['git', 'ls-files', '--others', '--exclude-standard'])
untracked = [l for l in out.splitlines() if l.strip()]
print(f'Untracked files remaining: {len(untracked)}')
for f in untracked[:20]:
    print(f'  {f}')

# 3. Stage .gitignore
rc, _, err = run(['git', 'add', '.gitignore'])
print(f'git add .gitignore: rc={rc}')

# 4. Commit .gitignore
rc, out, _ = run(['git', 'commit', '-m', 'Update .gitignore: exclude engine scratch files (engine/_*.{py,txt,json,repr})'])
print(f'commit .gitignore: rc={rc}')
if out: print(out.strip()[:300])

# 5. Stage and commit helper scripts (dev tools)
if untracked:
    print(f'\n=== Committing {len(untracked)} dev tools ===')
    rc, _, err = run(['git', 'add', '--'] + untracked)
    print(f'git add: rc={rc}')
    if err: print(f'  STDERR: {err[:200]}')

    msg = f'Add dev tools used in chapter rewrite session ({len(untracked)} scripts)'
    rc, out, _ = run(['git', 'commit', '-m', msg])
    print(f'commit: rc={rc}')
    if out: print(out.strip()[:500])

# 6. Final status
print('\n=== Final git status ===')
rc, out, _ = run(['git', 'status', '--short'])
lines = out.splitlines()
print(f'Uncommitted: {len(lines)}')
for l in lines[:10]:
    print(f'  {l}')

# 7. Push to origin
print('\n=== Push to origin ===')
rc, out, err = run(['git', 'push', 'origin', 'main'], check=False)
print(f'git push rc={rc}')
if out: print(f'STDOUT: {out[:500]}')
if err: print(f'STDERR: {err[:500]}')
