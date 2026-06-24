# -*- coding: utf-8 -*-
"""Replace English he said / she said / he stopped / she stopped with Chinese.

Preserves the rhythm of the surrounding compressed style — only swaps the
English narrative tag for Chinese equivalent.
"""
import re, os, sys

ROOT = r"C:\Users\stanc\github\open-souls\seasons\01-xianxia\chronicle"

# Match English tag patterns and replace.
REPLACEMENTS = [
    (re.compile(r'\bshe said\b', re.I), "她道"),
    (re.compile(r'\bhe said\b', re.I), "他道"),
    (re.compile(r'\bshe stopped\b', re.I), "她停了一下"),
    (re.compile(r'\bhe stopped\b', re.I), "他停了一下"),
]

def fix_file(path):
    text = open(path, encoding="utf-8").read()
    orig = text
    n = 0
    for rgx, repl in REPLACEMENTS:
        text, k = rgx.subn(repl, text)
        n += k
    if text != orig:
        open(path, "w", encoding="utf-8").write(text)
    return n

def main():
    chap_range = sys.argv[1] if len(sys.argv) > 1 else "301-424"
    start, end = map(int, chap_range.split("-"))
    files = []
    for f in os.listdir(ROOT):
        m = re.match(r"^(\d+)-", f)
        if m and start <= int(m.group(1)) <= end:
            files.append(os.path.join(ROOT, f))
    files.sort()
    total = 0
    n_files = 0
    for p in files:
        n = fix_file(p)
        if n:
            print(f"  fixed {n:2d} english tags in {os.path.basename(p)}")
            total += n
            n_files += 1
    print(f"\nTotal: {total} english tags replaced across {n_files} chapters.")

if __name__ == "__main__":
    main()