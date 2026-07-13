import sys, base64
data = sys.stdin.buffer.read()
encoded = base64.b64encode(data).decode('ascii')
sys.stdout.write(encoded)
