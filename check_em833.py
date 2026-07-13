"""检查 ch833 em-dash 段."""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
f = 'seasons/01-xianxia/chronicle/ch833-准备死.md'
text = open(f, 'r', encoding='utf-8').read()
m = re.match(r'^---\s*\n.*?\n---\s*\n?(.*)$', text, re.S)
body = m.group(1) if m else text
paras = [p for p in body.split('\n\n') if p.strip()]
for i, p in enumerate(paras):
    n = p.count('——')
    marker = ' <-- OVER' if n >= 5 else ''
    print('PARA', i, 'em=', n, marker, '|', p[:60])
    if n >= 4:
        print('  FULL:', p)