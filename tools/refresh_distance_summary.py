#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Refresh reports/jinjiang-r20/distance-summary.md from chapter-distance.json.

Single source of truth: the JSON. The summary is regenerated; never hand-edited.
Bucket bands match docs/standards/jinjiang-blowup-baseline.md section 6.

Usage:
    py -3 -X utf8 tools/refresh_distance_summary.py
"""
from __future__ import annotations

import json
import statistics
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports" / "jinjiang-r20"
JSON_PATH = REPORTS / "chapter-distance.json"
MD_PATH = REPORTS / "distance-summary.md"


def main() -> int:
    if not JSON_PATH.is_file():
        print(f"missing {JSON_PATH}; run jinjiang_chapter_distance.py first")
        return 1
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    recs = data.get("records") or []
    if not recs:
        print("no records in chapter-distance.json")
        return 1

    es = [r.get("engineering_min", 0) or 0 for r in recs]
    avg = statistics.mean(es)
    buckets = {"<5": 0, "5-6.99": 0, "7-7.99": 0, "8-8.49": 0, ">=8.5": 0}
    for e in es:
        if e < 5:
            buckets["<5"] += 1
        elif e < 7:
            buckets["5-6.99"] += 1
        elif e < 8:
            buckets["7-7.99"] += 1
        elif e < 8.5:
            buckets["8-8.49"] += 1
        else:
            buckets[">=8.5"] += 1

    fail_counts = {f"E{i}": 0 for i in range(1, 6)}
    e_keys = {
        "E1": "E1_open_conflict",
        "E2": "E2_mid_turn",
        "E3": "E3_hook_stop",
        "E4": "E4_agency",
        "E5": "E5_relationship_cost",
    }
    for r in recs:
        e = r.get("engineering", {})
        for short, full in e_keys.items():
            if (e.get(full) or 0) < 7:
                fail_counts[short] += 1

    recs_sorted = sorted(recs, key=lambda r: (r.get("engineering_min", 0) or 0,
                                              -int(r.get("chapter", 0))))
    bottom = recs_sorted[:15]
    top = recs_sorted[-10:][::-1]

    panel = data.get("panel", {}) or {}
    panel_files = panel.get("files", 0)
    l2_real = panel.get("l2", 0)

    lines = [
        "# Distance to Jinjiang blowup - full season engineering snapshot",
        "",
        f"> Generated: {date.today().isoformat()} (regenerated from chapter-distance.json)",
        "> Source: tools/jinjiang_chapter_distance.py + tools/chapter_by_chapter_audit.py",
        f"> Range: {len(recs)} chapter records",
        "> Baseline: docs/standards/jinjiang-blowup-baseline.md section 6",
        "> Honest note: R-track real reader evidence = 0 valid samples (L2-real = "
        f"{l2_real}, L1-effective filtered by echo_panel).",
        "> This report only measures the engineering side distance.",
        "",
        "## 1. One-line answer",
        "",
        f"After the frontmatter-strip fix, **{sum(1 for e in es if e >= 8.5)} chapters** "
        f"clear the engineering 8.5 blowup line and **{sum(1 for e in es if 7 <= e < 8.5)} "
        f"({sum(1 for e in es if 7 <= e < 8.5) * 100 / len(es):.1f}%)** sit in the 7-8.49 "
        "publish-eligible band.",
        "",
        "## 2. Engineering score distribution (E_min = min(E1..E5))",
        "",
        "| bucket | chapters | share | meaning |",
        "|---|---:|---:|---|",
        f"| <5 | {buckets['<5']} | {buckets['<5'] * 100 / len(es):.1f}% | clearly needs rewrite (structural) |",
        f"| 5-6.99 | {buckets['5-6.99']} | {buckets['5-6.99'] * 100 / len(es):.1f}% | needs choice or action |",
        f"| 7-7.99 | {buckets['7-7.99']} | {buckets['7-7.99'] * 100 / len(es):.1f}% | near entry, fix one dim |",
        f"| 8-8.49 | {buckets['8-8.49']} | {buckets['8-8.49'] * 100 / len(es):.1f}% | publish-ready single-chapter |",
        f"| >=8.5 | {buckets['>=8.5']} | {buckets['>=8.5'] * 100 / len(es):.1f}% | blowup-engineered single-chapter |",
        "",
        f"Average E_min: **{avg:.2f}/10**. This is the engineering floor; do not cite it as 接近爆款.",
        "",
        "## 3. Per-dimension fail counts (E_dim < 7.0)",
        "",
        "| dim | failing chapters | meaning |",
        "|---|---:|---|",
        f"| E1 opening conflict | {fail_counts['E1']} | opens on scenery or character relations, no action or resistance |",
        f"| E2 mid-turn choice | {fail_counts['E2']} | POV never makes a real mid-chapter choice, just records or passes through |",
        f"| E3 ending hook | {fail_counts['E3']} | ends on mood or generalization, leaves no specific next-chapter question |",
        f"| E4 POV agency | {fail_counts['E4']} | agency-verb density is too low, POV feels like an observer |",
        f"| E5 relationship cost | {fail_counts['E5']} | named characters are present but no relationship moves |",
        "",
        "## 4. Reader blindtest layer (R-track)",
        "",
        f"- panel_files: {panel_files} (L2-real = {l2_real}, L1 downgraded by echo_panel)",
        "- Any judgment of the form 读者会追 / 爆款 / 上瘾 is FORBIDDEN. This is the hard boundary from jinjiang-blowup-baseline.md section 0.",
        "",
        "## 5. Distance to the three gates",
        "",
        "| gate | engineering pass count | real pass count with R-track | gap |",
        "|---|---:|---:|---|",
        f"| publish (min>=7.0) | {sum(1 for e in es if e >= 7)} | 0 | reader evidence missing |",
        f"| blowup chapter (min>=8.5) | {sum(1 for e in es if e >= 8.5)} | 0 | same |",
        f"| addictive (5 consecutive chapters >=8.5 AND R>=7.5) | n/a | 0 | same |",
        "",
        "## 6. Bottom 15 chapters by E_min (next-round rewrite candidates)",
        "",
        "| chapter | E_min | E1 | E2 | E3 | E4 | E5 | file |",
        "|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in bottom:
        e = r.get("engineering", {})
        lines.append(
            f"| {r['chapter']} | {r.get('engineering_min', 0):.0f} | "
            f"{e.get('E1_open_conflict', 0)} | {e.get('E2_mid_turn', 0)} | "
            f"{e.get('E3_hook_stop', 0)} | {e.get('E4_agency', 0)} | "
            f"{e.get('E5_relationship_cost', 0)} | "
            f"`{r['file']}` |"
        )
    lines += [
        "",
        "## 7. Top 10 chapters by E_min (model-paragraph candidates)",
        "",
        "| chapter | E_min | E1 | E2 | E3 | E4 | E5 | file |",
        "|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in top:
        e = r.get("engineering", {})
        lines.append(
            f"| {r['chapter']} | {r.get('engineering_min', 0):.0f} | "
            f"{e.get('E1_open_conflict', 0)} | {e.get('E2_mid_turn', 0)} | "
            f"{e.get('E3_hook_stop', 0)} | {e.get('E4_agency', 0)} | "
            f"{e.get('E5_relationship_cost', 0)} | "
            f"`{r['file']}` |"
        )
    lines += [
        "",
        "## 8. Distance is regenerated, never hand-edited",
        "",
        "Refresh with: `py -3 -X utf8 tools/refresh_distance_summary.py`",
        "after `py -3 -X utf8 tools/jinjiang_chapter_distance.py --out reports/jinjiang-r20/chapter-distance.json`",
        "",
    ]
    MD_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"refreshed {MD_PATH} ({len(es)} chapters)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
