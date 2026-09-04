# -*- coding: utf-8 -*-
"""Improved chapter quality grader (v2)."""
from __future__ import annotations
import os, re, json, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHRON = ROOT / "seasons" / "01-xianxia" / "chronicle"
OUT = ROOT / "prompts" / ".notes" / "2026-09-04-quality-grades-v2.json"

sys.path.insert(0, str(ROOT / "engine"))
import prose_lint as PL  # noqa

RE_FRONT = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
RE_KV = re.compile(r"^([A-Za-z_]+):\s*(.*)$")
MOTIF_PATTERNS = [
    re.compile(r"刀柄"), re.compile(r"刀鞘"), re.compile(r"糖"),
    re.compile(r"砚"), re.compile(r"帕"), re.compile(r"信"),
    re.compile(r"灯火|灯芯|灯盏|灯"), re.compile(r"袖"),
    re.compile(r"瓷"), re.compile(r"门"), re.compile(r"镜"),
    re.compile(r"玉"), re.compile(r"杯|盏"), re.compile(r"桃花|桃花瓣"),
    re.compile(r"雪"), re.compile(r"火苗"), re.compile(r"茶|茶盏"),
]
ONOMATOPOEIA = re.compile(r"(嗒|咔|啪|嘭|咚|叮|铛|哐|砰|噼|噗|哧|咝|哚|嘀)")
SENSORY_VOCAB = re.compile(r"(手|袖|腕|指|掌|肘|肩|颈|耳|眉|眼|发|足|膝|腰|背|胸|口|唇|脸|皮|肤|肉|骨|血|汗|泪|疤|痕|窝|缝|口|边|角|面|底|上|下|里|外)(上|中|里|下|外|边|角|面|上|头|底)?")


def split_front_matter(text):
    m = RE_FRONT.match(text)
    if not m:
        return {}, text
    head = m.group(1)
    body = text[m.end():]
    out = {}
    cur_key, cur_buf = None, []
    for line in head.splitlines():
        if (line.startswith("  ") or line.startswith(" ")) and cur_key and line != cur_key + ":":
            cur_buf.append(line.lstrip(" "))
            continue
        if cur_key:
            out[cur_key] = "\n".join(cur_buf).strip()
        m2 = RE_KV.match(line)
        if m2:
            cur_key, val = m2.group(1), m2.group(2)
            cur_buf = [val] if val else []
        else:
            cur_key, cur_buf = None, []
    if cur_key:
        out[cur_key] = "\n".join(cur_buf).strip()
    return out, body


def clean_pipe(s):
    if not s:
        return ""
    if s.startswith("|"):
        s = s[1:]
    return re.sub(r"\n\s+", "\n", s).strip()


def grade_7d_v2(body):
    if not body:
        return [0] * 7
    han = re.findall(r"[一-鿿]", body)
    chars = len(han)
    sentences = [s for s in re.split(r"[。！？!?]", body) if s.strip()]
    paragraphs = [p for p in re.split(r"\n\s*\n", body) if p.strip()]

    single_line_paras = sum(1 for p in paragraphs if len(re.findall(r"[一-鿿]", p)) < 8)
    long_short_balance = 0
    if single_line_paras >= 3 and chars > 500:
        long_short_balance += 1
    if sentences:
        lens = [len(re.findall(r"[一-鿿]", s)) for s in sentences]
        mean = sum(lens) / len(lens)
        std = (sum((l - mean) ** 2 for l in lens) / len(lens)) ** 0.5
        cv = std / mean if mean else 0
        if cv > 0.55:
            long_short_balance += 1
    d1 = min(2, long_short_balance)

    filler = re.findall(r"(很|非常|十分|格外|异常|特别|极其|极度)\s*[一-鿿]+", body)
    generic = re.findall(r"(屋里|院中|夜很静|心里咚了一下|空气里|四周)", body)
    motif_hits = sum(len(p.findall(body)) for p in MOTIF_PATTERNS)
    d2 = 0
    if motif_hits >= 8:
        d2 += 1
    if not filler and not generic and motif_hits >= 12:
        d2 += 1
    d2 = min(2, d2)

    explicit_thought = re.findall(r"(她想|他想|他知道她|她知道|他心里|她心里|他觉得|她觉得)", body)
    reveal_phrases = re.findall(r"(她发现|他发现|原来|她终于明白|他终于明白)", body)
    subtext_markers = re.findall(r"(她认得|他认得|她[一-鿿]{1,3}知道|他[一-鿿]{1,3}知道|没让她|没让他|不必[一-鿿]{1,3}先|不必[一-鿿]{1,3}再)", body)
    d3 = 0
    if not explicit_thought and not reveal_phrases:
        d3 += 1
    if len(subtext_markers) >= 1:
        d3 += 1
    d3 = min(2, d3)

    sensory_count = len(SENSORY_VOCAB.findall(body))
    d4 = 0
    if sensory_count >= 10:
        d4 += 1
    if sensory_count >= 25:
        d4 += 1
    d4 = min(2, d4)

    cn_tags = sum(1 for kw in ["她说", "他道", "她道", "他问", "她答", "她顿", "他停", "他喊", "她笑"] if kw in body)
    eng_tags = re.findall(r"\b(he|she|they)\s+(said|asked|replied)", body, re.I)
    d5 = 0
    if eng_tags:
        d5 = 0
    elif cn_tags >= 2:
        d5 = 2
    elif cn_tags >= 1:
        d5 = 1
    else:
        d5 = 1

    pov_markers = re.findall(r"(她|他|阿湄|林夙|苏挽|林彻|林崇|叶观澜)", body)
    pov_count = len(set(pov_markers))
    god_view = re.findall(r"(其实|事实上|真相是|他们不知道)", body)
    if pov_count <= 5 and not god_view:
        d6 = 2
    elif pov_count <= 7 and not god_view:
        d6 = 1
    else:
        d6 = 0

    summary_words = re.findall(r"(那一刻她明白|这一刻他明白|原来这就是|她终于理解|他想这就是|她想这就是|他明白了|她明白了)", body)
    onomatopoeia = len(ONOMATOPOEIA.findall(body))
    d7 = 0
    if not summary_words:
        d7 += 1
    if onomatopoeia >= 2:
        d7 += 1
    d7 = min(2, d7)

    return [d1, d2, d3, d4, d5, d6, d7]


def grade_rubric_v2(body, hook_text, fm):
    han = re.findall(r"[一-鿿]", body)
    paragraphs = [p for p in re.split(r"\n\s*\n", body) if p.strip()]

    r1 = 2 if fm.get("_hook_evidenced") else 0
    if not fm.get("_hook_evidenced") and hook_text:
        r1 = 1

    emotion_words = re.findall(r"(撕|砸|摔|推|拒|断|收回|不答|不接|不认|抽|砍|留|替|还|翻|拆|问|答|喊|叫)", body)
    r2 = 0
    if len(emotion_words) >= 10:
        r2 += 1
    if len(emotion_words) >= 20:
        r2 += 1
    r2 = min(2, r2)

    reversal_v2 = 0
    if re.findall(r"(不[一-鿿]{1,3}但|不[一-鿿]{1,3}却|可是|然而)", body):
        reversal_v2 += 1
    if re.findall(r"(高[一-鿿]{0,2}矮|矮[一-鿿]{0,2}高|大[一-鿿]{0,2}小|小[一-鿿]{0,2}大|满[一-鿿]{0,2}空|空[一-鿿]{0,2}满|冷[一-鿿]{0,2}热|热[一-鿿]{0,2}冷)", body):
        reversal_v2 += 1
    r3 = min(2, reversal_v2)

    push_pull = re.findall(r"(替她|替他|替自己|不替|看见|不替看见|她没[一-鿿]{1,3}他|他没[一-鿿]{1,3}她|不[一-鿿]{1,3}替)", body)
    r4 = 0
    if len(push_pull) >= 4:
        r4 += 1
    if len(push_pull) >= 10:
        r4 += 1
    r4 = min(2, r4)

    sentences = [s.strip() for s in re.split(r"[。！？!?]", body) if s.strip()]
    short_quotes = [s for s in sentences if 5 <= len(re.findall(r"[一-鿿]", s)) <= 30]
    r5 = 0
    if len(short_quotes) >= 3:
        r5 += 1
    if len(short_quotes) >= 8:
        r5 += 1
    r5 = min(2, r5)

    sensory_count = len(SENSORY_VOCAB.findall(body))
    r6 = 0
    if sensory_count >= 8:
        r6 += 1
    if sensory_count >= 20:
        r6 += 1
    r6 = min(2, r6)

    template_loop = sum(len(re.findall(p, body)) for p in ["看向", "替她", "替他"])
    novel_anchors = sum(1 for p in MOTIF_PATTERNS if p.search(body))
    r7 = 0
    if template_loop < 4:
        r7 += 1
    if novel_anchors >= 6:
        r7 += 1
    r7 = min(2, r7)

    return [r1, r2, r3, r4, r5, r6, r7]


def grade_publishable(body, hook_text, fm):
    han = re.findall(r"[一-鿿]", body)
    sentences = [s.strip() for s in re.split(r"[。！？!?]", body) if s.strip()]

    visual_frames = 0
    for p in MOTIF_PATTERNS:
        if p.search(body):
            visual_frames += 1
    for sent in sentences:
        if re.search(r"(她站|他站|她坐|他坐|她蹲|他蹲|她扶|他扶|按住|压住|挂|提|抬|搁|握|抽)", sent):
            visual_frames += 1
    p1 = 2 if visual_frames >= 5 else (1 if visual_frames >= 2 else 0)

    short_quotes = [s for s in sentences if 5 <= len(re.findall(r"[一-鿿]", s)) <= 30]
    quotable = [s for s in short_quotes if "她" in s or "他" in s or "灯" in s or "糖" in s or "茶" in s]
    p2 = 2 if len(quotable) >= 3 else (1 if len(quotable) >= 1 else 0)

    new_anchors = sum(1 for p in MOTIF_PATTERNS if p.search(body))
    p3 = 2 if new_anchors >= 4 else (1 if new_anchors >= 2 else 0)

    cast = fm.get("cast", "")
    n_cast = cast.count(",") + 1 if cast else 0
    if n_cast >= 5:
        p4 = 0
    elif n_cast >= 3:
        p4 = 1
    else:
        p4 = 2

    body_no_title = re.sub(r"^#.*$", "", body, flags=re.M).strip()
    first_10_str = "".join(re.findall(r"[一-鿿]", body_no_title[:30])[:10])
    has_conflict = any(kw in first_10_str for kw in ["林", "苏", "阿", "叶", "余", "赤", "沈", "凌", "牛", "裴"])
    p5 = 2 if has_conflict else 1

    hook = clean_pipe(hook_text or "")
    hook_first = hook[:8]
    has_image = any(p.search(hook_first) for p in MOTIF_PATTERNS) if hook_first else False
    p6 = 2 if has_image else 1

    return [p1, p2, p3, p4, p5, p6]


def assess(path):
    text = path.read_text(encoding="utf8")
    fm, body = split_front_matter(text)
    hook_text = fm.get("hook", "")
    body_for_match = PL.body_of(text)
    hook_clean = clean_pipe(hook_text)
    first8 = hook_clean[:8]
    fm["_hook_evidenced"] = bool(first8 and first8 in body_for_match)

    d7 = grade_7d_v2(body)
    rubric = grade_rubric_v2(body, hook_text, fm)
    pub = grade_publishable(body, hook_text, fm)

    cn_match = re.match(r"^(?:ch)?(\d+)-", path.name)
    chapter = int(cn_match.group(1)) if cn_match else 0

    return {
        "file": path.name,
        "title": fm.get("title", ""),
        "chapter": chapter,
        "score_field": fm.get("score_field", fm.get("score", "")),
        "body_chars": len(re.findall(r"[一-鿿]", body)),
        "d7": d7,
        "d7_sum": sum(d7),
        "rubric": rubric,
        "rubric_sum": sum(rubric),
        "pub": pub,
        "pub_sum": sum(pub),
        "total_27": sum(d7) + sum(rubric) + sum(pub),
        "max_27": 27,
    }


def main():
    files = sorted(CHRON.glob("*.md"))
    files = [p for p in files if p.name not in ("INDEX.md", "_STUB_MANIFEST.json") and not p.name.startswith("test_")]

    grades = []
    for p in files:
        try:
            grades.append(assess(p))
        except Exception as e:
            print(f"FAIL {p.name}: {e}", file=sys.stderr)

    n = len(grades)
    jingpin = sum(1 for g in grades if g["d7_sum"] >= 12 and g["rubric_sum"] >= 12 and g["pub_sum"] >= 9)
    jingpin_super = sum(1 for g in grades if g["d7_sum"] == 14 and g["rubric_sum"] >= 12 and g["pub_sum"] >= 10)

    tier = {"S": 0, "A": 0, "B": 0, "C": 0, "D": 0, "E": 0}
    for g in grades:
        t = g["total_27"]
        if t >= 35: tier["S"] += 1
        elif t >= 33: tier["A"] += 1
        elif t >= 30: tier["B"] += 1
        elif t >= 27: tier["C"] += 1
        elif t >= 24: tier["D"] += 1
        else: tier["E"] += 1

    summary = {
        "n_chapters": n,
        "jingpin_chap": jingpin,
        "jingpin_super": jingpin_super,
        "tier": tier,
        "avg_d7": round(sum(g["d7_sum"] for g in grades) / n, 2),
        "avg_rubric": round(sum(g["rubric_sum"] for g in grades) / n, 2),
        "avg_pub": round(sum(g["pub_sum"] for g in grades) / n, 2),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"summary": summary, "grades": grades}, ensure_ascii=False, indent=1), encoding="utf8")
    print(f"Written: {OUT}", file=sys.stderr)

    print("\n=== Tier ===", file=sys.stderr)
    for k, v in tier.items():
        print(f"  Tier {k}: {v}", file=sys.stderr)

    print(f"\n=== {jingpin} jingpin chapters (d7>=12 AND rubric>=12 AND pub>=9) ===", file=sys.stderr)
    top = sorted([g for g in grades if g["d7_sum"] >= 12 and g["rubric_sum"] >= 12 and g["pub_sum"] >= 9],
                 key=lambda g: -g["total_27"])
    for g in top[:30]:
        print("  ch%4d %-30s d7=%2d rubric=%2d pub=%2d total=%2d" % (
            g["chapter"], g["file"][:30], g["d7_sum"], g["rubric_sum"], g["pub_sum"], g["total_27"]), file=sys.stderr)


if __name__ == "__main__":
    main()
