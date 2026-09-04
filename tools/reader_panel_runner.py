# -*- coding: utf-8 -*-
"""Run / validate / aggregate the five-reader blindtest panel.

Entry point for docs/reader-subagent-workflow.md. This script is deterministic:
no LLM is invoked from here. Real-subagent calls are issued by the main Codex
session; the JSON outputs are then handed back to this script via filesystem.

P0 hardening (per the 2026-09-04 reader-panel audit):

    * L1 / L2 is decided from `source` + `isolation`, not from filename.
    * L2 must include `isolation.no_chronicle == true`; otherwise it falls back
      to L1 and the aggregated report calls it out explicitly.
    * `effective_n = L2_real + L1_diversified` is reported. It is the only
      sample size the report may speak about.
    * `diversity_score` (Jaccard on three signal axes) flags "echo panels"
      and downgrades any unanimous-L1 finding.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports" / "jinjiang-r20"
PACK_DIR = REPORTS / "blindtest_packs"
RESULTS_MD = REPORTS / "reader-blindtest-results.md"
GENERATE = ROOT / "tools" / "reader_blindtest_pack.py"
WORKFLOW_DOC = ROOT / "docs" / "reader-subagent-workflow.md"
PERSONA_FILE = ROOT / "prompts" / "reader" / "personas.json"

REQUIRED_KEYS = {
    "id", "label", "perspective", "drop", "love_relation",
    "next_chapter_focus", "stay_to_50", "stay_reason",
    "pattern_flags", "source", "isolation",
}
PATTERN_KEYS = {"info_not_action", "smart_drop", "passive_chain"}
PROVENANCE_KEYS = {"schema_version", "model_id", "reading_log", "pack_hash"}
ISOLATION_KEYS = {"no_chronicle", "no_frontmatter", "cwd", "persona_seed"}
PERSONA_IDS = ("1", "2", "3", "4", "5")
DIVERSITY_FLAG_JACCARD_FLOOR = 0.5
DIVERSITY_REASON_JACCARD_FLOOR = 0.4


def regenerate_blindtest() -> None:
    subprocess.run(
        [sys.executable, str(GENERATE)],
        check=True,
        cwd=str(ROOT),
    )


def load_personas() -> dict:
    if not PERSONA_FILE.exists():
        return {"personas": []}
    return json.loads(PERSONA_FILE.read_text(encoding="utf-8"))


def persona_prompt(persona_id: str) -> str:
    personas = {p["id"]: p for p in load_personas().get("personas", [])}
    p = personas.get(persona_id)
    if not p:
        raise SystemExit(f"unknown persona id {persona_id!r}")
    return (
        f"请以「{p['label']}」视角独立阅读以下 4 个盲读包：\n"
        f"  - reports/jinjiang-r20/blindtest_packs/open.md\n"
        f"  - reports/jinjiang-r20/blindtest_packs/mid_a.md\n"
        f"  - reports/jinjiang-r20/blindtest_packs/mid_b.md\n"
        f"  - reports/jinjiang-r20/blindtest_packs/latest.md\n"
        "禁止阅读 chronicle 原档、frontmatter、review、score 或 grader 输出；\n"
        "在 JSON 中通过 isolation.no_chronicle = true / no_frontmatter = true 自证。\n"
        f"阅读立场：{p['perspective']}\n"
        f"留下条件：{p['keep_if']}\n"
        f"触发弃读：{p['drop_if']}\n"
        f"反向自检（必须写明，不允许用同质化模板）：{p['must_disagree_with']}\n"
        "必填字段：schema_version=2 / model_id / pack_hash / reading_log（每个盲读包至少一条）/ id / label / perspective / drop / love_relation / "
        "next_chapter_focus / stay_to_50 / stay_reason / pattern_flags（必须含 "
        "info_not_action / smart_drop / passive_chain 三键）/ source / isolation。\n"
        "source 字段必须写明「真人 sub-agent（独立 fork 模型会话），通过 mcp 回到本会话」。"
    )


def _iter_reader_files() -> list[Path]:
    return sorted(REPORTS.glob("reader-*.json"))


def _classify(data: dict, path: Path) -> tuple[str, str]:
    """Return (kind, reason). kind ∈ {L2-real, L2-reader, L1-agent, prompt}.

    A file is L2-real only if `source` advertises 真人 sub-agent AND isolation
    claims it never read chronicle / frontmatter. A file with `真人` in the
    filename but missing isolation is treated as L1-agent and called out.
    """
    name = path.name
    if name.endswith("-prompt.txt"):
        return "prompt", "prompt template"
    source = (data.get("source") or "").strip()
    isolation = data.get("isolation") or {}
    modern = data.get("schema_version") == 2 and PROVENANCE_KEYS <= set(data)
    if source.startswith("真人读者") or source.startswith("真人 sub-agent"):
        kind = "L2-reader" if source.startswith("真人读者") else "L2-real"
        if modern and isolation.get("no_chronicle") and isolation.get("no_frontmatter"):
            return kind, "modern provenance + isolation"
        return "L1-agent", f"{kind} source missing modern provenance: {name}"
    if "真人" in name:
        return "L1-agent", f"filename advertises 真人 but source missing: {name}"
    return "L1-agent", "default L1"


def _jaccard(a: Iterable, b: Iterable) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / max(1, len(sa | sb))


def diversity_score(panel: list[dict]) -> dict:
    """Return per-axis Jaccard distances plus an overall echo verdict."""
    if len(panel) < 2:
        return {"flag_jaccard": 1.0, "drop_jaccard": 1.0, "reason_jaccard": 1.0,
                "echo_panel": False, "effective_l1": len(panel)}
    flag_sets = [tuple(sorted((k for k, v in (p.get("pattern_flags") or {}).items() if v))) for p in panel]
    drops = [str((p.get("drop") or {}).get("chapter")) for p in panel]
    reasons = [re.findall(r"[一-鿿A-Za-z]+", (p.get("stay_reason") or "")) for p in panel]
    pairs = []
    for i in range(len(panel)):
        for j in range(i + 1, len(panel)):
            pairs.append((i, j))
    flag_jacc = 1 - sum(_jaccard(flag_sets[i], flag_sets[j]) for i, j in pairs) / max(1, len(pairs))
    drop_jacc = 1 - sum(_jaccard([drops[i]], [drops[j]]) for i, j in pairs) / max(1, len(pairs))
    reason_jacc = 1 - sum(_jaccard(reasons[i], reasons[j]) for i, j in pairs) / max(1, len(pairs))
    # Use > comparison (not >=) so a panel at the floor is treated as diverse.
    echo = (
        flag_jacc < (1 - DIVERSITY_FLAG_JACCARD_FLOOR - 1e-9)
        or reason_jacc < (1 - DIVERSITY_REASON_JACCARD_FLOOR - 1e-9)
        or drop_jacc < 0.4
    )
    effective_l1 = 0 if echo else len(panel)
    return {
        "flag_jaccard": round(flag_jacc, 3),
        "drop_jaccard": round(drop_jacc, 3),
        "reason_jaccard": round(reason_jacc, 3),
        "echo_panel": echo,
        "effective_l1": effective_l1,
    }


def validate(verbose: bool = True) -> tuple[int, int, list[str], dict]:
    ok = 0
    issues: list[str] = []
    total = 0
    by_kind: Counter = Counter()
    for path in _iter_reader_files():
        total += 1
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            issues.append(f"{path.name}: parse error {exc}")
            continue
        missing = REQUIRED_KEYS - set(data.keys())
        flag_dict = data.get("pattern_flags") or {}
        missing |= PATTERN_KEYS - set(flag_dict.keys())
        isolation = data.get("isolation") or {}
        missing |= ISOLATION_KEYS - set(isolation.keys())
        source = data.get("source", "")
        if not source:
            missing.add("source")
        kind, reason = _classify(data, path)
        by_kind[kind] += 1
        if kind == "prompt":
            continue
        if missing:
            issues.append(f"{path.name}: missing keys {sorted(missing)}")
            continue
        if data.get("schema_version") == 2:
            provenance_missing = PROVENANCE_KEYS - set(data)
            if provenance_missing:
                issues.append(f"{path.name}: modern schema missing {sorted(provenance_missing)}")
                continue
            if not isinstance(data.get("reading_log"), list) or not data["reading_log"]:
                issues.append(f"{path.name}: reading_log must be a non-empty list")
                continue
        if kind == "L2-real" and not isolation.get("no_chronicle"):
            issues.append(f"{path.name}: L2-real isolation.no_chronicle must be true")
            continue
        ok += 1
        if verbose:
            display = kind if reason == "default L1" else f"{kind}: {reason}"
            print(f"  ok  {path.name}  ({display})")
    return ok, total, issues, by_kind


def _load_panel() -> tuple[list[tuple[Path, dict, str, str]], list[str]]:
    rows: list[tuple[Path, dict, str, str]] = []
    issues: list[str] = []
    for path in _iter_reader_files():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            issues.append(f"{path.name}: parse error {exc}")
            continue
        kind, reason = _classify(data, path)
        if kind == "prompt":
            continue
        if REQUIRED_KEYS - set(data.keys()):
            issues.append(f"{path.name}: missing keys")
            continue
        rows.append((path, data, kind, reason))
    return rows, issues


def effective_n(l2_real: int, l2_reader: int, diversity: dict) -> int:
    return l2_real + l2_reader + diversity["effective_l1"]


def aggregate() -> Path:
    rows, issues = _load_panel()
    agents = [d for _, d, k, _ in rows if k == "L1-agent"]
    l2_real = [d for _, d, k, _ in rows if k == "L2-real"]
    l2_reader = [d for _, d, k, _ in rows if k == "L2-reader"]
    flagged = [(path, reason) for path, _, k, reason in rows if k == "L1-agent" and reason != "default L1"]

    diversity = diversity_score(agents)
    eff_n = effective_n(len(l2_real), len(l2_reader), diversity)

    lines = [
        "# 盲读结果汇总",
        "",
        "时间：2026-09-04",
        "方法：5 份模型代理盲读（L1）+ 真人 sub-agent / 真人读者 ≥1 份（L2）；只读盲读包正文。",
        "边界：本结果不等同于真人读者反馈；L1 < 5 份或 L2 < 1 份时禁止聚合判断。",
        "",
        f"effective_n = {eff_n} (L2-real={len(l2_real)} + L2-reader={len(l2_reader)} + L1-effective={diversity['effective_l1']})",
        f"diversity_score = {diversity['flag_jaccard']} (flag) / {diversity['drop_jaccard']} (drop) / {diversity['reason_jaccard']} (reason)",
        f"echo_panel = {diversity['echo_panel']} ， L1 复读嫌疑高时 L1 不计入 effective_n",
        "provenance = schema_version=2 / model_id / reading_log / pack_hash are required for new records",
    ]

    if flagged:
        lines.append("")
        lines.append("### 真人文件名被降级为 L1（必须先修 isolation 才能进 L2）")
        for path, reason in flagged:
            lines.append(f"- {path.name}: {reason}")

    if not diversity["echo_panel"] and (l2_real or l2_reader):
        lines.append("")
        lines.append("L2 有效，读者分可作为升级证据。")
    elif not (l2_real or l2_reader):
        lines.append("")
        lines.append("L2 = 0。真人证据缺失；任何「读者会追 / 爆款」判断禁止。")

    if l2_real or l2_reader:
        lines.append("")
        lines.append("## 0. 真人（L2）采样")
        for r in (l2_real + l2_reader):
            drop = r.get("drop") or {}
            rel = (r.get("love_relation") or {}).get("name", "")
            lines.append(
                f"- id={r.get('id')} {r.get('label')}：弃读 {drop.get('chapter')}；"
                f"关系 {rel}；50 章意愿 {r.get('stay_to_50')}"
            )

    if not agents:
        lines.append("")
        lines.append("## 1. 模型代理（L1）数据不足")
        lines.append("L1 < 5 份，禁止聚合。")
    else:
        drop_counter, rel_counter, pattern_counter = Counter(), Counter(), Counter()
        stay_yes = 0
        for a in agents:
            d = a.get("drop") or {}
            if isinstance(d, dict) and d.get("chapter"):
                drop_counter[(d.get("pack"), d.get("chapter"))] += 1
            rel = (a.get("love_relation") or {}).get("name")
            if rel:
                rel_counter[rel] += 1
            if a.get("stay_to_50"):
                stay_yes += 1
            for k, v in (a.get("pattern_flags") or {}).items():
                if v:
                    pattern_counter[k] += 1
        lines.append("")
        lines.append("## 1. 模型代理（L1）热点")
        lines.append("### 弃读热点")
        for (pack, ch), n in drop_counter.most_common():
            lines.append(f"- {pack} {ch}：{n} 人")
        lines.append("")
        lines.append("### 关系追问热点")
        for rel, n in rel_counter.most_common():
            lines.append(f"- {rel}：{n} 人")
        lines.append("")
        lines.append("### 50 章留存")
        lines.append(f"- 愿意：{stay_yes} / {len(agents)}")
        lines.append("")
        lines.append("### 三类问题命中")
        for k in PATTERN_KEYS:
            lines.append(f"- {k}：{pattern_counter.get(k, 0)} 人")

        lines.append("")
        lines.append("## 2. 升级与下一轮改稿顺序（按 effective_n 阈值）")
        upgrades = []
        echo_note = "" if not diversity["echo_panel"] else "（L1 复读嫌疑高，仅作方向记录，不升级）"
        for k in PATTERN_KEYS:
            count = pattern_counter.get(k, 0) + sum(
                1 for r in (l2_real + l2_reader) if (r.get("pattern_flags") or {}).get(k)
            )
            if diversity["echo_panel"]:
                upgrades.append(f"{k}：L1 命中 {pattern_counter.get(k, 0)} 人；L2 命中 {sum(1 for r in (l2_real + l2_reader) if (r.get('pattern_flags') or {}).get(k))} 人{echo_note}")
            elif count >= 3:
                upgrades.append(f"{k}：命中 {count} 人，升级为结构任务。")
            else:
                upgrades.append(f"{k}：命中 {count} 人，未达 3 人门槛，仅作方向记录。")
        stay_yes_total = stay_yes + sum(1 for r in (l2_real + l2_reader) if r.get("stay_to_50"))
        if stay_yes_total < max(3, (len(agents) + len(l2_real) + len(l2_reader)) // 2):
            upgrades.append("中段包 50 章留存意愿不达标，结构任务。")
        if not upgrades:
            upgrades.append("本轮未触发硬升级，但需记录方向。")
        for u in upgrades:
            lines.append(f"- {u}")
        lines.append("")
        lines.append("下一轮建议顺序：")
        lines.append("1. 处理升级项。")
        lines.append("2. 处理关系追问热点。")
        lines.append("3. 处理弃读热点章节。")
        lines.append("4. 再次生成盲读包 + 重新校验 isolation / diversity，确认未恶化的方向。")

    if issues:
        lines.append("")
        lines.append("## 3. 校验问题")
        for issue in issues:
            lines.append(f"- {issue}")

    lines.append("")
    lines.append(f"## 4. 盲读包指纹（{_pack_hash()}）")
    lines.append("复测必须沿用同一指纹；想刷新读者记忆时用 `regenerate --new-seed`。")

    RESULTS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return RESULTS_MD


def _pack_hash() -> str:
    h = hashlib.sha256()
    if not PACK_DIR.exists():
        return "no-packs"
    for pack in sorted(PACK_DIR.glob("*.md")):
        h.update(pack.read_bytes())
    return h.hexdigest()[:16]


def cmd_check(_: argparse.Namespace) -> int:
    if not PACK_DIR.exists():
        regenerate_blindtest()
    ok, total, issues, by_kind = validate(verbose=True)
    print(f"reader files: {ok}/{total} pass  by_kind={dict(by_kind)}")
    if issues:
        print("issues:")
        for issue in issues:
            print(f"  -", issue)
        return 1
    return 0


def cmd_aggregate(_: argparse.Namespace) -> int:
    if not PACK_DIR.exists():
        regenerate_blindtest()
    out = aggregate()
    print(f"updated {out.relative_to(ROOT)}")
    return 0


def cmd_regenerate(args: argparse.Namespace) -> int:
    if args.new_seed:
        print("note: --new-seed requested; edit tools/reader_blindtest_pack.py to bump random.Random seed")
    regenerate_blindtest()
    print("regenerated blindtest packs")
    return 0


def cmd_emit_prompt(args: argparse.Namespace) -> int:
    text = persona_prompt(args.persona)
    out_path = REPORTS / f"reader-prompt-{args.persona}.txt"
    out_path.write_text(text, encoding="utf-8")
    print(f"wrote {out_path.relative_to(ROOT)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("check", help="validate every reader-*.json against required schema").set_defaults(func=cmd_check)
    sub.add_parser("aggregate", help="write reports/jinjiang-r20/reader-blindtest-results.md").set_defaults(func=cmd_aggregate)

    p_emit = sub.add_parser("emit-prompt", help="emit a per-persona prompt for a real subagent")
    p_emit.add_argument("persona", choices=PERSONA_IDS)
    p_emit.set_defaults(func=cmd_emit_prompt)

    p_regen = sub.add_parser("regenerate", help="regenerate blindtest packs")
    p_regen.add_argument("--new-seed", action="store_true")
    p_regen.set_defaults(func=cmd_regenerate)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())



