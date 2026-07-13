"""measure 各章关键指标."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from engine.prose_lint import measure, body_of
files = ['ch822-沈疏桐搁.md', 'ch826-还有气.md', 'ch827-阿湄背.md', 'ch829-偏房守.md',
         'ch800-山顶见.md', 'ch810-四个位置.md', 'ch821-牛阿大粥.md', 'ch823-余伯合.md',
         'ch824-不在设计里.md', 'ch825-阿湄抱.md', 'ch828-林窈跟.md']
for f in files:
    p = 'seasons/01-xianxia/chronicle/' + f
    t = open(p, 'r', encoding='utf-8').read()
    b = body_of(t)
    m = measure(b)
    print(f + ' | chars=' + str(m['chars']) + ' micro=' + str(round(m['micro'], 3)) +
          ' avg=' + str(round(m['avg'], 2)) + ' dash_max=' + str(m['dash_max']) +
          ' eng=' + str(m['eng']) + ' filler=' + str(m['filler']))