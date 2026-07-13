"""列出剩余章节."""
import sys, os, glob
sys.stdout.reconfigure(encoding='utf-8')
files = sorted(glob.glob('seasons/01-xianxia/chronicle/ch83*.md') +
               glob.glob('seasons/01-xianxia/chronicle/ch84*.md') +
               glob.glob('seasons/01-xianxia/chronicle/ch85*.md'))
for f in files:
    print(os.path.basename(f), os.path.getsize(f))