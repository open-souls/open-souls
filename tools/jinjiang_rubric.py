# -*- coding: utf-8 -*-
"""Generate a read-only Jinjiang rubric scoreboard for the novel."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHRONICLE = ROOT / "seasons" / "01-xianxia" / "chronicle"
REPORTS = ROOT / "reports" / "jinjiang-r20"
AUDIT_PATH = REPORTS / "chapter-by-chapter-audit.json"
FRONTMATTER = re.compile(r"^---\s*$([\s\S]*?)^---\s*$", re.M)
HAN = re.compile(r"[一-鿿]")
ACTION = re.compile(r"走|来|去|问|答|拿|放|递|收|拆|开|关|挡|写|烧|抬|转身|停|进|出|抓|握|听|闻|落|动|转|挪|按|拂|盯|擦|撕|换|验|翻|压|推|扶")
RESISTANCE = re.compile(r"却|但|不肯|不能|没有|未|拦|拒绝|停住|不让|来不及|门外|追")
DECISION = re.compile(r"决定|改为|改成|只[把将]|不再|不肯|拒绝|主动|亲自|自己开|自己拿|自己写|签下|不签")


def read_chapter(path: Path) -> tuple[int, str, str]:
    raw_text = path.read_text(encoding="utf-8")
    match = FRONTMATTER.search(raw_text)
    front_text = match.group(1) if match else ""
    body_text = raw_text[match.end():] if match else raw_text
    chapter_match = re.search(r"^chapter:\s*(\d+)", front_text, re.M)
    chapter_number = int(chapter_match.group(1)) if chapter_match else int(path.name.split("-", 1)[0])
    pov_match = re.search(r"^pov:\s*(.+)$", front_text, re.M)
    pov_name = pov_match.group(1).strip() if pov_match else ""
    return chapter_number, pov_name, body_text.strip()


def chapter_score(body_text: str, audit_row: dict) -> dict:
    paragraphs = [item.strip() for item in body_text.split("\n\n") if item.strip()]
    first_paragraph = paragraphs[0] if paragraphs else ""
    middle_text = "\n\n".join(paragraphs[1:-1])
    open_actions = len(ACTION.findall(first_paragraph[:180]))
    open_conflict = 10 if open_actions >= 2 and RESISTANCE.search(first_paragraph) else 7 if open_actions else 4
    mid_turn = 10 if DECISION.search(middle_text) else 6 if ACTION.search(middle_text) else 4
    hook_stop = 10 if audit_row.get("hook_signal") else 4
    agency = min(10, 4 + len(DECISION.findall(body_text)))
    named_characters = len(set(re.findall(r"苏挽|林夙|阿湄|林崇|林彻|林窈|林叙|叶观澜|余伯|凌朔|裴无咎|牛阿大", body_text)))
    relationship_cost = min(10, 4 + max(0, named_characters - 2) // 2 + (2 if DECISION.search(body_text) else 0))
    return {
        "open_conflict": open_conflict,
        "mid_turn": mid_turn,
        "hook_stop": hook_stop,
        "agency": agency,
        "relationship_cost": relationship_cost,
        "payoff_clock": 5,
        "engineering_score": round((open_conflict + mid_turn + hook_stop + agency + relationship_cost + 5) / 6, 2),
    }


def main() -> None:
    audit_rows = json.loads(AUDIT_PATH.read_text(encoding="utf-8")).get("chapters", [])
    audit_by_chapter = {row["chapter"]: row for row in audit_rows}
    bucket_scores = defaultdict(list)
    for path in CHRONICLE.glob("*.md"):
        if path.name in {"INDEX.md", "test_write.md"} or not path.name[:1].isdigit():
            continue
        chapter_number, pov_name, body_text = read_chapter(path)
        if not HAN.search(body_text):
            continue
        bucket_scores[(chapter_number - 1) // 50 + 1].append(
            (chapter_number, chapter_score(body_text, audit_by_chapter.get(chapter_number, {})))
        )
    scoreboard = []
    for bucket_number, chapter_scores in sorted(bucket_scores.items()):
        chapter_scores.sort()
        count = len(chapter_scores)
        averages = {
            metric: round(sum(scores[metric] for _, scores in chapter_scores) / count, 2)
            for metric in ["open_conflict", "mid_turn", "hook_stop", "agency", "relationship_cost", "payoff_clock", "engineering_score"]
        }
        scoreboard.append({
            "bucket": bucket_number,
            "range": [chapter_scores[0][0], chapter_scores[-1][0]],
            "count": count,
            "averages": averages,
            "weak_hooks": sum(1 for chapter_number, _ in chapter_scores if not audit_by_chapter.get(chapter_number, {}).get("hook_signal")),
        })
    overall_score = round(sum(row["averages"]["engineering_score"] for row in scoreboard) / len(scoreboard), 2)
    overall_weak_hooks = round(sum(row["weak_hooks"] for row in scoreboard) / sum(row["count"] for row in scoreboard), 3)
    output = {
        "rubric": "reports/jinjiang-r20/jinjiang-rubric.md",
        "buckets": scoreboard,
        "overall": {"engineering_score": overall_score, "weak_hook_share": overall_weak_hooks},
        "boundary": "Engineering score is a mechanical signal. It cannot establish reader addiction or market success.",
    }
    (REPORTS / "rubric-scoreboard.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown_lines = [
        "# 晋江 rubric 差距分（工程口径）",
        "",
        "来源：`tools/jinjiang_rubric.py`。只读，不改正文。",
        f"总工程平均：{overall_score}/10。该分数有机械上限，不是市场分。",
        f"章尾弱占比：{overall_weak_hooks * 100:.1f}%。",
        "",
        "| bucket | 范围 | 章数 | open | mid | hook | agency | rel | payoff | 总分 | 弱钩数 |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in scoreboard:
        averages = row["averages"]
        markdown_lines.append(
            f"| {row['bucket']:02d} | {row['range'][0]}-{row['range'][1]} | {row['count']} | "
            f"{averages['open_conflict']} | {averages['mid_turn']} | {averages['hook_stop']} | "
            f"{averages['agency']} | {averages['relationship_cost']} | {averages['payoff_clock']} | "
            f"{averages['engineering_score']} | {row['weak_hooks']} |"
        )
    markdown_lines.extend(["", "边界：只有真人盲读才能补齐读者层证据；两份分数独立，取最低。"])
    (REPORTS / "rubric-scoreboard.md").write_text("\n".join(markdown_lines) + "\n", encoding="utf-8")
    print(json.dumps({"buckets": len(scoreboard), "overall": output["overall"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
