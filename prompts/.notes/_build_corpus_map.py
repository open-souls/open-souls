# -*- coding: utf-8 -*-
"""Read every chapter and produce a 晋江爆款 gap assessment (v2)."""
from __future__ import annotations
import os, re, json, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHRON = ROOT / "seasons" / "01-xianxia" / "chronicle"
OUT = ROOT / "prompts" / ".notes" / "2026-09-04-corpus-map.json"

RE_FRONT = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
RE_KV = re.compile(r"^([A-Za-z_]+):\s*(.*)$")
TEMPLATE_PHRASES = [
    "看向", "搁的看向", "擦的看向", "收的看向", "替的看向",
    "替她", "替他", "替自己", "替他挡", "替她挡",
    "压得不重", "她自己", "她自己蹲", "她认得",
]

def split_front_matter(text: str):
    m = RE_FRONT.match(text)
    if not m:
        return {}, text
    head = m.group(1)
    body = text[m.end():]
    out = {}
    cur_key = None
    cur_buf = []
    for line in head.splitlines():
        if line.startswith("  ") and cur_key:
            cur_buf.append(line[2:])
            continue
        if cur_key:
            out[cur_key] = "\n".join(cur_buf).strip()
        m2 = RE_KV.match(line)
        if m2:
            cur_key, val = m2.group(1), m2.group(2)
            cur_buf = [val] if val else []
        else:
            cur_key = None
            cur_buf = []
    if cur_key:
        out[cur_key] = "\n".join(cur_buf).strip()
    return out, body

def clean_pipe(s: str):
    """Strip YAML pipe prefix and per-line indentation; collapse newlines."""
    if not s:
        return ""
    if s.startswith("|"):
        s = s[1:]
    s = re.sub(r"\n\s+", "\n", s)
    return s.strip()

def parse_cast(cast_str: str):
    if not cast_str:
        return []
    s = cast_str.strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    parts = [p.strip() for p in re.split(r"[,，、]", s) if p.strip()]
    return parts

def parse_ships(ships_str: str):
    if not ships_str:
        return []
    out = []
    for line in ships_str.splitlines():
        m = re.match(r"\s*([^\s:：][^:：]*?):\s*(.*)$", line)
        if m:
            pair, desc = m.group(1).strip(), m.group(2).strip()
            out.append((pair, desc))
    return out

def chapter_sort_key(filename: str):
    base = filename[:-3] if filename.endswith(".md") else filename
    m = re.match(r"^(?:ch)?(\d+)-", base)
    if m:
        return int(m.group(1))
    return 99999

def body_metrics(body: str):
    body_no_title = re.sub(r"^#[^\n]*\n", "", body, count=1)
    text = body_no_title.strip()
    chars = len(text)
    sentences = re.split(r"[。！？!?]", text)
    sentences = [s for s in sentences if s.strip()]
    short_sent = sum(1 for s in sentences if 0 < len(s.strip()) <= 6)
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    para_lens = [len(p) for p in paragraphs]
    avg_para = (sum(para_lens) / len(para_lens)) if para_lens else 0
    micro = (short_sent / len(sentences)) if sentences else 0
    if sentences:
        lens = [len(s) for s in sentences]
        mean = sum(lens) / len(lens)
        var = sum((l - mean) ** 2 for l in lens) / len(lens)
        std = var ** 0.5
        cv = std / mean if mean else 0
    else:
        cv = 0.0
    c = {}
    for w in TEMPLATE_PHRASES:
        c[w] = text.count(w)
    # 钩子动词多样性 — 出现过的视觉/动作动词种类数
    action_verbs = re.findall(r"(看见|看见|听见|闻见|摸见|尝见|擦|按|抬|低|转|蹲|起|坐|站|握|抽|压|替|留|走|跑|追|接|推|拽|抱|搂|揽|扶|挡|砍|抹|吹|落|翻|合|开|关|闭|睁|合|拧|挂|放|搁|塞|压|扔|摔|踩|踏|跳|跃|跨|迈|冲|扑|跃|追|撵|赶|骂|喊|叫|唤|哭|笑|嘶|哼|叹|笑|怒|骂|叫|答|问|答|回|答|说|言|道|讲|叙|诉|陈|诉|报|告|喊|叫|嘶|吼|呵|嗔|恼|嘲|讥|讽|嘘|叹|哭|嚎|嘶|哼|喘息|呼吸|喘|叹|吁|默|沉吟|沉吟|沉吟|哼|叹气|喘息)", text)
    verb_div = len(set(action_verbs))
    return {
        "body_chars": chars,
        "sentences": len(sentences),
        "short_sent": short_sent,
        "micro": round(micro, 3),
        "avg_para": round(avg_para, 1),
        "para_count": len(paragraphs),
        "cv_sentence_len": round(cv, 3),
        "template_phrase_counts": c,
        "dialog_count": text.count("「"),
        "verb_diversity": verb_div,
    }

def hook_evidence(hook_text: str, body: str):
    if not hook_text:
        return {"hook_text": "", "len": 0, "first8_in_body": False, "evidence": False}
    h = clean_pipe(hook_text)
    first8 = h[:8].replace("\n", "")
    return {
        "hook_text": h,
        "len": len(h),
        "first8": first8,
        "first8_in_body": first8 in body if first8 else False,
        "evidence": first8 in body if first8 else False,
    }

def assess_one(path: Path):
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"file": path.name, "error": str(e)}
    fm, body = split_front_matter(text)
    title = fm.get("title", "")
    cast = parse_cast(fm.get("cast", ""))
    pov = fm.get("pov", "")
    line = fm.get("line", "")
    thread = fm.get("thread", "")
    beat = fm.get("beat", "")
    score = fm.get("score", "")
    ships = parse_ships(fm.get("ships", ""))
    hook_text = fm.get("hook", "")
    review_text = fm.get("review", "")
    metrics = body_metrics(body)
    hook = hook_evidence(hook_text, body)
    chnum = chapter_sort_key(path.name)
    template_loop = False
    tp = metrics["template_phrase_counts"]
    if tp.get("看向", 0) >= 6 or tp.get("替她", 0) >= 8 or tp.get("替他", 0) >= 8 or tp.get("她自己", 0) >= 10:
        template_loop = True
    gap_reasons = []
    if metrics["body_chars"] < 1500:
        gap_reasons.append("字数不足(<1500)")
    if not hook["evidence"]:
        gap_reasons.append("钩子未兑现")
    if not ships:
        gap_reasons.append("无关系节拍")
    if not pov:
        gap_reasons.append("缺 POV")
    if metrics["micro"] > 0.5:
        gap_reasons.append("微碎片率过高(>0.5)")
    if metrics["avg_para"] < 30:
        gap_reasons.append("平均段长过短(<30)")
    if metrics["cv_sentence_len"] < 0.3:
        gap_reasons.append("句长单调(cv<0.3)")
    if template_loop:
        gap_reasons.append("模板回环")
    if not line:
        gap_reasons.append("缺 line 标签")
    if line == "混合":
        gap_reasons.append("line=混合(已退役)")
    if "男频" in line:
        gap_reasons.append("line 仍标男频")
    if line and not any(t in line for t in ["女频", "古言", "言情", "仙侠", "混合"]):
        gap_reasons.append(f"line 标签异常:{line}")
    if metrics["verb_diversity"] < 8:
        gap_reasons.append("动词种类单调(<8)")
    return {
        "file": path.name,
        "chapter": chnum,
        "title": title,
        "cast_size": len(cast),
        "cast": cast,
        "pov": pov,
        "line": line,
        "score_field": score,
        "ships_count": len(ships),
        "thread_len": len(thread),
        "beat_len": len(beat),
        "hook": hook,
        "review_len": len(review_text),
        "metrics": metrics,
        "template_loop": template_loop,
        "gap_reasons": gap_reasons,
    }

def main():
    files = sorted(CHRON.glob("*.md"))
    files = [p for p in files if p.name not in ("INDEX.md",) and not p.name.startswith("test_") and not p.name.startswith("_")]
    print(f"扫描 {len(files)} 章", file=sys.stderr)
    rows = []
    for i, p in enumerate(files, 1):
        r = assess_one(p)
        rows.append(r)
        if i % 200 == 0:
            print(f"  ...{i}", file=sys.stderr)
    n = len(rows)
    n_short = sum(1 for r in rows if r["metrics"]["body_chars"] < 1500)
    n_hook_fail = sum(1 for r in rows if not r["hook"]["evidence"])
    n_template = sum(1 for r in rows if r["template_loop"])
    n_no_ships = sum(1 for r in rows if r["ships_count"] == 0)
    n_no_pov = sum(1 for r in rows if not r["pov"])
    n_no_line = sum(1 for r in rows if not r["line"])
    n_line_hunhe = sum(1 for r in rows if r["line"] == "混合")
    n_line_nanpin = sum(1 for r in rows if r["line"] == "男频")
    n_low_verb = sum(1 for r in rows if r["metrics"]["verb_diversity"] < 8)
    score_dist = Counter(r["score_field"].replace("|\n", "").strip() for r in rows)
    line_dist = Counter(r["line"] for r in rows)
    avg_chars = sum(r["metrics"]["body_chars"] for r in rows) / n
    title_counter = Counter(r["title"] for r in rows if r["title"])
    buckets = Counter()
    for r in rows:
        c = r["metrics"]["body_chars"]
        if c < 500: buckets["<500"] += 1
        elif c < 1000: buckets["500-1000"] += 1
        elif c < 1500: buckets["1000-1500"] += 1
        elif c < 2500: buckets["1500-2500"] += 1
        elif c < 4000: buckets["2500-4000"] += 1
        else: buckets[">=4000"] += 1
    # 30分门槛估算（每项分）
    score30_dist = Counter()
    for r in rows:
        reasons = r["gap_reasons"]
        if not reasons:
            score30_dist["接近30分(0-1 gap)"] += 1
        elif len(reasons) <= 2:
            score30_dist["26-28分(2-3 gap)"] += 1
        elif len(reasons) <= 4:
            score30_dist["22-25分(4-5 gap)"] += 1
        else:
            score30_dist["<22分(>=6 gap)"] += 1
    summary = {
        "total_chapters": n,
        "avg_body_chars": round(avg_chars, 1),
        "short_chapters_lt1500": n_short,
        "hook_evidence_fail": n_hook_fail,
        "template_loop_count": n_template,
        "no_ships": n_no_ships,
        "no_pov": n_no_pov,
        "no_line": n_no_line,
        "line_hunhe": n_line_hunhe,
        "line_nanpin": n_line_nanpin,
        "low_verb_diversity": n_low_verb,
        "score_dist": dict(score_dist),
        "line_dist": dict(line_dist),
        "body_char_buckets": dict(buckets),
        "score30_dist": dict(score30_dist),
        "top_titles": title_counter.most_common(30),
    }
    out = {"summary": summary, "chapters": rows}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Written: {OUT}", file=sys.stderr)
    print("\n=== Summary ===", file=sys.stderr)
    for k, v in summary.items():
        if k == "top_titles":
            print(f"top_titles ({len(v)}):", file=sys.stderr)
            for t, c in v[:15]:
                print(f"   {c:>3}  {t}", file=sys.stderr)
        else:
            print(f"  {k}: {v}", file=sys.stderr)

if __name__ == "__main__":
    main()
