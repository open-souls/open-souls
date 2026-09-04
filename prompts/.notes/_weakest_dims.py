import json
from collections import defaultdict
d = json.load(open('prompts/.notes/2026-09-04-quality-grades.json', encoding='utf-8'))
grades = d['grades']

# Each dim avg
d7_per = [0] * 7
rubric_per = [0] * 7
pub_per = [0] * 6
n = len(grades)
for g in grades:
        for i in range(7):
            if i < len(g['d7']):
                d7_per[i] += g['d7'][i]
            if i < len(g['rubric']):
                rubric_per[i] += g['rubric'][i]
        for i in range(6):
            if i < len(g['pub']):
                pub_per[i] += g['pub'][i]

D7_NAMES = ['1 节奏', '2 用词', '3 潜台词', '4 感官', '5 对话', '6 视角', '7 克制']
RUBRIC_NAMES = ['1 钩子', '2 爽痛', '3 反差', '4 拉扯', '5 记忆点', '6 代入', '7 新']
PUB_NAMES = ['1 画面钩', '2 截图句', '3 独立', '4 cast3-5', '5 强开场', '6 强收尾']

print('7维文笔 dim averages (target 1.5+):')
for i, n7 in enumerate(D7_NAMES):
    print('  %-12s avg=%.2f/2' % (n7, d7_per[i] / n))

print()
print('rubric 14 dim averages (target 1.5+):')
for i, rn in enumerate(RUBRIC_NAMES):
    print('  %-12s avg=%.2f/2' % (rn, rubric_per[i] / n))

print()
print('出片 6 dim averages (target 1.5+):')
for i, pn in enumerate(PUB_NAMES):
    print('  %-12s avg=%.2f/2' % (pn, pub_per[i] / n))

print()
print('Total averages:')
print('  7维文笔 avg=%.2f/14' % (sum(d7_per) / n))
print('  rubric avg=%.2f/14' % (sum(rubric_per) / n))
print('  出片 avg=%.2f/12' % (sum(pub_per) / n))
