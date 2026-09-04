"""ingest_feedback.py — read 试读反馈_intake.csv and produce report."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / 'prompts' / '.notes' / '试读反馈_intake.csv'

DIMS = ['score', 'imagery', 'cp_push', 'heroine_agency', 'lastline_hook', 'addictive']

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
        vals = [int(float(r[d])) for r in rows if r.get(d) and r[d].strip()]
        if vals:
            avgs[d] = sum(vals) / len(vals)
    print('Per-chapter scores:')
    for r in rows:
        score = int(float(r.get('score', 0))) if r.get('score', '').strip() else 0
        tier = 'S' if score >= 5 else 'A' if score >= 4 else 'B' if score >= 3 else 'C' if score >= 2 else 'D'
        print('  {} ({}): score={} trial_tier={}  one_liner: {}'.format(
            r.get('chapter','?'), r.get('title','?'), score, tier, r.get('one_liner','')))
    print()
    print('Per-dim averages:')
    for d, v in avgs.items():
        print('  {}: {:.2f}'.format(d, v))
    return rows, avgs

if __name__ == '__main__':
    ingest()
