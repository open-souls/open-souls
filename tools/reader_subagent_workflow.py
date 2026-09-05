import json, subprocess
from collections import Counter
from pathlib import Path

ROOT = Path('.').resolve()
SUMMARY = ROOT / 'reports' / 'jinjiang-r20' / 'blindtest-summaries.json'
RESULTS_MD = ROOT / 'reports' / 'jinjiang-r20' / 'reader-blindtest-results.md'
GENERATE = ROOT / 'tools' / 'reader_blindtest_pack.py'
REQUIRED_KEYS = {'id','label','perspective','drop','love_relation','next_chapter_focus','stay_to_50','pattern_flags','source'}
PATTERN_KEYS = {'info_not_action','smart_drop','passive_chain'}


def regenerate_blindtest():
    subprocess.run(['py','-3','-X','utf8',str(GENERATE)], check=True, cwd=str(ROOT))


def collect_results():
    agents, real, issues = [], [], []
    for path in sorted((ROOT / 'reports' / 'jinjiang-r20').glob('reader-*.json')):
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except Exception as exc:
            issues.append(f'{path.name}: parse error {exc}')
            continue
        missing = REQUIRED_KEYS - set(data.keys())
        missing |= PATTERN_KEYS - set(data.get('pattern_flags', {}).keys())
        if missing:
            issues.append(f'{path.name}: missing keys {sorted(missing)}')
            continue
        if '\u771f\u4eba' in path.name:
            real.append(data)
        else:
            agents.append(data)
    return agents, real, issues


def aggregate(agents, real):
    lines = ['# 盲读结果汇总','','时间：2026-09-04','方法：5 份模型代理盲读 + 真人 sub-agent 至少 1 份；只读盲读包正文。','边界：本结果不等同于真人读者反馈，仍需补齐真人 sub-agent。','']
    if real:
        lines.append('## 0. 真人 sub-agent 采样')
        for r in real:
            lines.append(f"- id={r['id']} {r['label']}：弃读 {r['drop']}；关系 {r['love_relation']['name']}；50 章意愿 {r['stay_to_50']}")
        lines.append('')
    lines.append('## 1. 模型代理热点')
    drop_counter, rel_counter, pattern_counter = Counter(), Counter(), Counter()
    stay_yes = 0
    for a in agents:
        drop = a.get('drop')
        if isinstance(drop, dict) and drop.get('chapter'):
            drop_counter[(drop.get('pack'), drop['chapter'])] += 1
        rel = a.get('love_relation', {}).get('name')
        if rel:
            rel_counter[rel] += 1
        if a.get('stay_to_50'):
            stay_yes += 1
        for k, v in a.get('pattern_flags', {}).items():
            if v:
                pattern_counter[k] += 1
    lines.append('### 弃读热点')
    for (pack, ch), n in drop_counter.most_common():
        lines.append(f'- {pack} {ch}：{n} 人')
    lines.append('')
    lines.append('### 关系追问热点')
    for rel, n in rel_counter.most_common():
        lines.append(f'- {rel}：{n} 人')
    lines.append('')
    lines.append('### 50 章留存')
    lines.append(f'- 愿意：{stay_yes} / {len(agents)}')
    lines.append('')
    lines.append('### 三类问题命中')
    for k in PATTERN_KEYS:
        lines.append(f'- {k}：{pattern_counter.get(k, 0)} 人')
    lines.append('')
    lines.append('## 2. 升级与下一轮改稿顺序')
    upgrades = []
    for k in PATTERN_KEYS:
        count = pattern_counter.get(k, 0) + sum(1 for r in real if r.get('pattern_flags', {}).get(k))
        if count >= 3:
            upgrades.append(f'{k}：命中 {count} 人，升级为结构任务。')
    if stay_yes + sum(1 for r in real if r.get('stay_to_50')) < 3:
        upgrades.append('中段包 50 章留存意愿不达标，结构任务。')
    if not upgrades:
        upgrades.append('本轮未触发硬升级，但需记录方向。')
    for u in upgrades:
        lines.append(f'- {u}')
    lines.append('')
    lines.append('下一轮建议顺序：')
    lines.append('1. 处理升级项。')
    lines.append('2. 处理关系追问热点。')
    lines.append('3. 处理弃读热点章节。')
    lines.append('4. 再次生成盲读包，确认未恶化的方向。')
    return '\n'.join(lines) + '\n'


def main():
    regenerate_blindtest()
    agents, real, issues = collect_results()
    print(f'agents={len(agents)} real={len(real)} issues={len(issues)}')
    for issue in issues:
        print(' -', issue)
    md = aggregate(agents, real)
    RESULTS_MD.write_text(md, encoding='utf-8')
    print('updated', RESULTS_MD.relative_to(ROOT))


if __name__ == '__main__':
    main()