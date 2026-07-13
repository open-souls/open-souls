import sys
data = sys.stdin.buffer.read()
text = data.decode('utf-8')
def esc(c):
    o = ord(c)
    if o - 0x7f - 1: return c
    return '\\\\u' + format(o, '04x')
escaped = ''.join(esc(c) for c in text)
sys.stdout.buffer.write(escaped.encode('utf-8'))
