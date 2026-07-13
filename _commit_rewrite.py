#!/usr/bin/env python3
"""Stage and commit the rewritten chapters in efficient batches."""
import sys
import subprocess
from pathlib import Path

ROOT = Path(r'c:\Users\stanc\github\open-souls')
CHRONICLE = ROOT / 'seasons' / '01-xianxia' / 'chronicle'

# Ranges to commit (modified chapters) - 50 chapters per batch
ranges = [
    (291, 340, 'Rewrite ch291-340'),
    (341, 400, 'Rewrite ch341-400'),
    (401, 460, 'Rewrite ch401-460'),
    (461, 505, 'Rewrite ch461-505'),
]

# ch791-793 are separate (the "封档" gap-fill)
separate_ranges = [
    ('ch791-林崇看.md', 'Add ch791 (gap fill)'),
    ('ch792-灶边.md', 'Add ch792 (gap fill)'),
    ('ch793-苏挽端糖.md', 'Add ch793 (gap fill)'),
]

# ch858-997 is a single big batch
big_ranges = [
    (list(range(858, 998)), 'Rewrite ch858-997'),
]

# ch998-999 + 容昀 dossier (final)
final = [
    ('ch998-林彻站.md', 'Add ch998'),
    ('ch999-苏挽在.md', 'Add ch999'),
    ('souls/容昀/dossier.md', 'Add 容昀 dossier'),
    ('souls/容昀/soul.md', 'Add 容昀 soul'),
]

def run(cmd, cwd):
    """Run a shell command and return its output."""
    result = subprocess.run(cmd, shell=True, cwd=str(cwd), capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def git_add(files):
    """Add a list of files using git add."""
    cmd = 'git add ' + ' '.join(f'"{f}"' for f in files)
    rc, out, err = run(cmd, ROOT)
    return rc, out, err


def git_commit(msg):
    """Commit with the given message."""
    cmd = f'git commit -m "{msg}" 2>nul'
    rc, out, err = run(cmd, ROOT)
    return rc, out, err


def main():
    # Phase 1: ranges
    for start, end, msg in ranges:
        files = [str(CHRONICLE / f'ch{n}-{title}.md') for n in range(start, end + 1)
                 for title in ['林崇看', '灶边', '苏挽端糖', '林彻看林夙', '林叙等', '林崇信',
                               '灶边雪', '林彻站', '苏挽在', '林叙看']]
        # Filter to only files that exist
        files = [f for f in files if Path(f).exists()]
        if not files:
            print(f"SKIP {msg} - no files")
            continue
        rc, out, err = git_add(files)
        if rc != 0:
            print(f"FAIL add {msg}: {err}")
            continue
        rc, out, err = git_commit(msg)
        print(f"{msg}: {out.strip() or 'no output'}")

    # Phase 2: ch791-793
    for fname, msg in separate_ranges:
        f = str(CHRONICLE / fname)
        if not Path(f).exists():
            print(f"SKIP {msg} - file missing")
            continue
        rc, _, _ = git_add([f])
        rc, out, err = git_commit(msg)
        print(f"{msg}: {out.strip() or 'no output'}")

    # Phase 3: ch858-997 in chunks
    chunk_size = 50
    nums = list(range(858, 998))
    for i in range(0, len(nums), chunk_size):
        chunk = nums[i:i+chunk_size]
        files = []
        for n in chunk:
            for title in ['林彻站', '苏挽在', '林叙看', '林崇看', '灶边', '苏挽端糖',
                          '林彻看林夙', '林叙等', '林崇信', '灶边雪']:
                f = CHRONICLE / f'ch{n}-{title}.md'
                if f.exists():
                    files.append(str(f))
        if not files:
            continue
        rc, out, err = git_add(files)
        rc, out, err = git_commit(f'Rewrite ch{chunk[0]}-{chunk[-1]}')
        print(f"ch{chunk[0]}-{chunk[-1]}: {out.strip() or 'no output'}")

    # Phase 4: final
    for fname, msg in final:
        f = str(ROOT / fname)
        if not Path(f).exists():
            print(f"SKIP {msg} - file missing")
            continue
        rc, _, _ = git_add([f])
        rc, out, err = git_commit(msg)
        print(f"{msg}: {out.strip() or 'no output'}")


if __name__ == '__main__':
    main()
