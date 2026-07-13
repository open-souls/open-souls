"""查找每段 em-dash 数."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
f = 'seasons/01-xianxia/chronicle/ch830-林夙醒.md'
text = open(f, 'r', encoding='utf-8').read()
parts = text.split('---')
# body after frontmatter
import re
m = re.match(r'^---\s*\n.*?\n---\s*\n?(.*)$', text, re.S)
body = m.group(1) if m else text
paras = [p for p in body.split('\n\n') if p.strip()]
for i, p in enumerate(paras):
    n = p.count('——')
    print(f'PARA {i}: em={n} | {p[:80]}')
    if n >= 4:
        print('  FULL:', p)