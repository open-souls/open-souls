"""ingest_feedback.py — read 试读反馈_intake.csv and produce report."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / 'prompts' / '.notes' / '试读反馈_intake.csv'

DIMS = ['score', 'imagery', 'cp_push', 'heroine_agency', 'lastline_hook', 'addictive']

def parse_score(s):
    s = (s or '').strip()
    if not s or s == '_':
        return None
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return None

def ingest():
    if not CSV.exists():
        print('CSV not found:', CSV)
        return
    rows = []
    with CSV.open(encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    if not rows:
        print('No rows in CSV')
        return
    avgs = {}
    for d in DIMS:
        vals = [parse_score(r[d]) for r in rows]
        vals = [v for v in vals if v is not None]
        if vals:
            avgs[d] = sum(vals) / len(vals)
    print('Per-chapter scores:')
    for r in rows:
        score = parse_score(r.get('score'))
        if score is None:
            tier = '_'
        else:
            tier = 'S' if score >= 5 else 'A' if score >= 4 else 'B' if score >= 3 else 'C' if score >= 2 else 'D'
        print('  {} ({}): score={} trial_tier={}  one_liner: {}'.format(
            r.get('chapter','?'), r.get('title','?'), score if score is not None else '_', tier, r.get('one_liner','_') or '_'))
    print()
    print('Per-dim averages (over filled rows):')
    if avgs:
        for d, v in avgs.items():
            print('  {}: {:.2f}'.format(d, v))
    else:
        print('  (no rows filled)')
    return rows, avgs

if __name__ == '__main__':
    ingest()
