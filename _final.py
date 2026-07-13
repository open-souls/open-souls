# -*- coding: utf-8 -*-
import subprocess, sys, os
sys.stdout.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE = r'c:\Users\stanc\github\open-souls'

# 1. Check if dossier.md is tracked
print('=== dossier.md status ===')
r = subprocess.run(['git', 'ls-files', '--error-unmatch', 'souls/容昀/dossier.md'],
                   capture_output=True, cwd=BASE)
print(f'ls-files rc={r.returncode}')
print(f'stdout: {r.stdout.decode("utf-8", errors="replace")[:200]}')
print(f'stderr: {r.stderr.decode("utf-8", errors="replace")[:200]}')

# 2. Try git log for dossier
print('\n=== dossier.md git log ===')
r = subprocess.run(['git', 'log', '--oneline', '--', 'souls/容昀/dossier.md'],
                   capture_output=True, cwd=BASE)
print(r.stdout.decode('utf-8', errors='replace')[:500])
print('stderr:', r.stderr.decode('utf-8', errors='replace')[:200])

# 3. Try git log for souls
print('\n=== souls git log ===')
r = subprocess.run(['git', 'log', '--oneline', '--', 'souls/'],
                   capture_output=True, cwd=BASE)
print(r.stdout.decode('utf-8', errors='replace')[:500])

# 4. Check overall git log
print('\n=== Last 5 commits ===')
r = subprocess.run(['git', 'log', '--oneline', '-5'],
                   capture_output=True, cwd=BASE)
print(r.stdout.decode('utf-8', errors='replace'))

# 5. Check untracked for dossier
r = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard', 'souls/容昀/'],
                   capture_output=True, cwd=BASE)
print(f'\n=== Untracked in souls/容昀/ ===\n{r.stdout.decode("utf-8", errors="replace")}')
