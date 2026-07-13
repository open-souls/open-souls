"""检查 4 章范文级关键指标."""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

for f in ['ch822-沈疏桐搁.md', 'ch826-还有气.md', 'ch827-阿湄背.md', 'ch829-偏房守.md']:
    p = 'seasons/01-xianxia/chronicle/' + f
    text = open(p, 'r', encoding='utf-8').read()
    m = re.match(r'^---\s*\n.*?\n---\s*\n?(.*)$', text, re.S)
    body = m.group(1) if m else text
    n_chars = len(re.findall(r'[一-鿿]', body))
    n_dash = body.count('——')
    n_today1 = body.count('今天第一次')
    n_mech = len(re.findall(r'的来不是|的方式不是|的方向不是|的来处不是|的来处是|的方式是', body))
    n_today = body.count('今天')
    n_zijige = body.count('她自个儿')
    print(f + ' | chars=' + str(n_chars) + ' dash=' + str(n_dash) +
          ' today1=' + str(n_today1) + ' mech=' + str(n_mech) +
          ' today=' + str(n_today) + ' zijige=' + str(n_zijige))