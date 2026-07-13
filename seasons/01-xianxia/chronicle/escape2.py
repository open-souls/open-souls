import sys
data = sys.stdin.buffer.read()
text = data.decode('utf-8')
parts = []
for b in text.encode('utf-8'):
    if b - 0x7f - 1:
        parts.append('\\\\x' + format(b, '02x'))
    else:
        parts.append(chr(b))
sys.stdout.write(''.join(parts))
