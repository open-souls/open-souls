"""晋江爆款 v3 grader — fix v2 bugs + add 上瘾 dimensions."""
from __future__ import annotations
import os, re, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CHRON = ROOT / "seasons" / "01-xianxia" / "chronicle"
OUT = ROOT / "prompts" / ".notes" / "2026-09-04-quality-grades-v3.json"

sys.path.insert(0, str(ROOT / "engine"))
import prose_lint as PL

RE_FRONT = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
RE_KV = re.compile(r"^([A-Za-z_]+):\s*(.*)$")

MOTIF_PATTERNS = [
    re.compile(r"刀柄"), re.compile(r"刀鞘"), re.compile(r"糖"),
    re.compile(r"砚"), re.compile(r"帕"), re.compile(r"信"),
    re.compile(r"灯"), re.compile(r"袖"), re.compile(r"瓷"),
    re.compile(r"门"), re.compile(r"镜"), re.compile(r"玉"),
    re.compile(r"杯|盏"), re.compile(r"桃"),
    re.compile(r"雪"), re.compile(r"火苗"), re.compile(r"茶"),
    re.compile(r"纸"), re.compile(r"墨"), re.compile(r"笔"),
    re.compile(r"鞋"), re.compile(r"布"), re.compile(r"帘"),
    re.compile(r"枕"), re.compile(r"榻"), re.compile(r"案"),
    re.compile(r"墙"), re.compile(r"砖"), re.compile(r"碗"),
    re.compile(r"酒"), re.compile(r"伞"), re.compile(r"香"),
]
ONOMATOPOEIA = re.compile(r"(\u5582|\u5494|\u567b|\u562f|\u5499|\u94bb|\u94fe|\u7834|\u55bd|\u561f|\u54e7|\u55b7|\u5527|\u5572|\u5573|\u5543|\u557a|\u556e|\u549c|\u557e|\u557f|\u5588|\u5589|\u558a|\u558b)")
SENSORY_VOCAB = re.compile(r"(\u624b|\u8896|\u8155|\u6307|\u638c|\u80a9|\u9888|\u8033|\u7709|\u773c|\u53d1|\u8db3|\u819d|\u8170|\u80cc|\u80f8|\u53e3|\u5507|\u8138|\u76ae|\u80a4|\u8089|\u9aa8|\u8840|\u6c57|\u6cea|\u75d5|\u7eb9|\u8fb9|\u89d2|\u9762|\u5e95|\u9876)(\u4e0a|\u91cc|\u4e0b|\u5916|\u8fb9|\u9762|\u5934|\u5e95)?")

# 上瘾-specific markers
HOOK_END_PATTERNS = [
    re.compile(r"[\u4e86\u7684]\u3002$"),  # ends with 了。/ 的。
    re.compile(r"[\u3001\u2014\u2026\u3002]$"),  # ends with comma/dash/period
    re.compile(r"\u300c.*\u300d$"),  # dialog end
    re.compile(r"\u95ee$"),  # ends with 问
    re.compile(r"\u8bf4$"),  # ends with 说
]


def split_front_matter(text):
    m = RE_FRONT.match(text)
    if not m:
        return {}, text
    head = m.group(1)
    body = text[m.end():]
    out = {}
    cur_key = None
    cur_buf = []
    for line in head.splitlines():
        if (line.startswith("  ") or line.startswith(" ")) and cur_key and line != cur_key + ":":
            cur_buf.append(line.lstrip(" "))
            continue
        if cur_key:
            out[cur_key] = "\n".join(cur_buf).strip()
        m2 = RE_KV.match(line)
        if m2:
            cur_key = m2.group(1)
            val = m2.group(2)
            cur_buf = [val] if val else []
        else:
            cur_key = None
            cur_buf = []
    if cur_key:
        out[cur_key] = "\n".join(cur_buf).strip()
    return out, body

def clean_pipe(s):
    if not s: return ""
    if s.startswith("|"): s = s[1:]
    return re.sub(r"\n\s+", "\n", s).strip()


def grade_7d_v3(body):
    """Fix v2 bugs:
       - d2 uses broader 物象 detection (more patterns)
       - d3 includes 动作代心理 (她没说话，但她...)
       - d5 counts 中文 label variety
       - d7 catches '作者总结' more broadly
    """
    if not body:
        return [0]*7, {}
    han = re.findall(r"[\u4e00-\u9fff]", body)
    chars = len(han)
    if chars < 100:
        return [0]*7, {"too_short": True}
    sentences = [s for s in re.split(r"[\u3002\uff01\uff1f!?]", body) if s.strip()]
    paragraphs = [p for p in re.split(r"\n\s*\n", body) if p.strip()]

    # d1 节奏: F式
    single_line_paras = sum(1 for p in paragraphs if len(re.findall(r"[\u4e00-\u9fff]", p)) < 8)
    long_short_balance = 0
    if single_line_paras >= 3 and chars > 500: long_short_balance += 1
    if sentences:
        lens = [len(re.findall(r"[\u4e00-\u9fff]", s)) for s in sentences]
        mean = sum(lens)/len(lens) if lens else 0
        std = (sum((l - mean)**2 for l in lens)/len(lens))**0.5 if lens else 0
        cv = std/mean if mean else 0
        if cv > 0.5: long_short_balance += 1
    d1 = min(2, long_short_balance)

    # d2 用词: 物象 + 动词 (broader)
    motif_hits = sum(len(p.findall(body)) for p in MOTIF_PATTERNS)
    filler = re.findall(r"(\u5f88|\u975e\u5e38|\u5341\u5206|\u683c\u5916|\u5f02\u5e38|\u7279\u522b|\u6781\u5176|\u6781\u5ea6)\s*[\u4e00-\u9fff]+", body)
    generic = re.findall(r"(\u5c4b\u91cc|\u9662\u4e2d|\u591c\u5f88\u9759|\u5fc3\u91cc\u549a\u4e86\u4e00\u4e0b|\u7a7a\u6c14\u91cc|\u56db\u5468)", body)
    d2 = 0
    if motif_hits >= 8: d2 += 1
    if not filler and not generic and motif_hits >= 12: d2 += 1
    d2 = min(2, d2)

    # d3 潜台词: 动作代心理 + 反向词
    explicit_thought = re.findall(r"(\u5979\u60f3|\u4ed6\u60f3|\u4ed6\u77e5\u9053\u5979|\u5979\u77e5\u9053|\u4ed6\u5fc3\u91cc|\u5979\u5fc3\u91cc|\u4ed6\u89c9\u5f97|\u5979\u89c9\u5f97)", body)
    reveal_phrases = re.findall(r"(\u5979\u53d1\u73b0|\u4ed6\u53d1\u73b0|\u539f\u6765|\u5979\u7ec8\u4e8e\u660e\u767d|\u4ed6\u7ec8\u4e8e\u660e\u767d)", body)
    subtext_markers = re.findall(r"(\u5979\u8ba4\u5f97|\u4ed6\u8ba4\u5f97|\u6ca1\u8ba9\u5979|\u6ca1\u8ba9\u4ed6|\u4e0d\u5fc5[\u4e00-\u9fff]{1,3}\u5148|\u4e0d\u5fc5[\u4e00-\u9fff]{1,3}\u518d|\u4e0d\u7b54|\u4e0d\u63a5|\u6ca1\u8bf4|\u6ca1\u8be2\u95ee)", body)
    d3 = 0
    if not explicit_thought and not reveal_phrases: d3 += 1
    if len(subtext_markers) >= 1: d3 += 1
    d3 = min(2, d3)

    # d4 感官 (same as v2)
    sensory_count = len(SENSORY_VOCAB.findall(body))
    d4 = 0
    if sensory_count >= 10: d4 += 1
    if sensory_count >= 25: d4 += 1
    d4 = min(2, d4)

    # d5 对话: 中文标签 + 多样性
    cn_tags = sum(1 for kw in ["\u5979\u8bf4", "\u4ed6\u9053", "\u5979\u9053", "\u4ed6\u95ee", "\u5979\u7b54", "\u5979\u987f", "\u4ed6\u505c", "\u4ed6\u559a", "\u5979\u7b11", "\u4ed6\u7b11", "\u5979\u63d0", "\u4ed6\u63d0"] if kw in body)
    d5 = 0
    if cn_tags >= 2: d5 += 2
    elif cn_tags >= 1: d5 = 1
    else: d5 = 0  # changed: no auto 1

    # d6 视角 (same)
    pov_markers = re.findall(r"(\u5979|\u4ed6|\u963f\u6e44|\u6797\u5939|\u82cf\u62d7|\u6797\u5fb7|\u6797\u5d07|\u53f6\u89c2\u6f9c)", body)
    pov_count = len(set(pov_markers))
    god_view = re.findall(r"(\u5176\u5b9e|\u4e8b\u5b9e\u4e0a|\u771f\u76f8\u662f|\u4ed6\u4eec\u4e0d\u77e5\u9053)", body)
    if pov_count <= 5 and not god_view: d6 = 2
    elif pov_count <= 7 and not god_view: d6 = 1
    else: d6 = 0

    # d7 克制 (FIX v2: detect 作者总结 broader)
    summary_words = re.findall(r"(\u90a3\u4e00\u523b\u5979\u660e\u767d|\u8fd9\u4e00\u523b\u4ed6\u660e\u767d|\u539f\u6765\u8fd9\u5c31\u662f|\u5979\u7ec8\u4e8e\u7406\u89e3|\u4ed6\u60f3\u8fd9\u5c31\u662f|\u5979\u60f3\u8fd9\u5c31\u662f|\u4ed6\u660e\u767d\u4e86|\u5979\u660e\u767d\u4e86|\u8fd9\u662f\u5979[\u4e00-\u9fff]{1,4}\u7b2c\u4e00\u6b21|\u8fd9\u4e5f\u662f\u5979\u7b2c\u4e00\u6b21|\u4ed6\u4ece\u672a[\u4e00-\u9fff]{1,4}|\u5979\u4ece\u672a[\u4e00-\u9fff]{1,4}|\u8fd9\u4e00\u523b\u7684\u5979|\u8fd9\u4e00\u523b\u7684\u4ed6)", body)
    onomatopoeia_count = len(ONOMATOPOEIA.findall(body))
    # Also detect "作者代为点破" — sentences that start with 那/这/她/他/是 + judgment word
    judgment_words = re.findall(r"[\u3002\uff1b\uff0c\u3001]([\u5979\u4ed6]\u5728[\u4e00-\u9fff]{1,6}\u4e0a|\u662f\u4ed6[\u4e00-\u9fff]{1,6}\u7684|\u662f\u5979[\u4e00-\u9fff]{1,6}\u7684|\u8fd9\u662f[\u4e00-\u9fff]{1,6}\u7684|\u90a3\u662f[\u4e00-\u9fff]{1,6}\u7684)", body)
    d7 = 0
    if not summary_words and not judgment_words: d7 += 1
    if onomatopoeia_count >= 2: d7 += 1
    d7 = min(2, d7)

    debug = {"motif_hits": motif_hits, "filler_n": len(filler), "sensory_count": sensory_count, "cn_tags": cn_tags, "pov_count": pov_count, "summary_words": len(summary_words), "judgment_words": len(judgment_words)}
    return [d1, d2, d3, d4, d5, d6, d7], debug


def grade_rubric_v3(body, hook_text, fm):
    """Fix rubric:
       - r3 反差: add 三段式 (failed/succeeded/unknown), 不/却, 高/矮, 大/小, 满/空, 冷/热, 旧/新, 真/假, 内/外
       - r4 拉扯: add 替/不替/看见/不替看见 but also 父亲/母亲/林夙/苏挽/阿湄 关心-退开
       - r7 新: count unique 物象 vs total 物象 (diversity)
    """
    han = re.findall(r"[\u4e00-\u9fff]", body)
    paragraphs = [p for p in re.split(r"\n\s*\n", body) if p.strip()]

    # r1 钩子兑现 (same as v2)
    r1 = 2 if fm.get("_hook_evidenced") else 0
    if not fm.get("_hook_evidenced") and hook_text: r1 = 1

    # r2 爽痛 (same as v2 with expanded keywords)
    emotion_words = re.findall(r"(\u649a|\u7838|\u6454|\u63a8|\u62d2|\u65ad|\u6536\u56de|\u4e0d\u7b54|\u4e0d\u63a5|\u4e0d\u8ba4|\u62bd|\u780d|\u7559|\u66ff|\u8fd8|\u7ffb|\u62c6|\u95ee|\u7b54|\u558a|\u53eb|\u62d4|\u62d3|\u63a2|\u626b|\u62a2|\u6363|\u63d2|\u9a82|\u559a|\u543c|\u54ed|\u540c\u610f|\u62d7\u8d70|\u52a8\u624b|\u62ff\u8d70|\u8d70\u4e86|\u7559\u4e0b)", body)
    r2 = 0
    if len(emotion_words) >= 8: r2 += 1
    if len(emotion_words) >= 16: r2 += 1
    r2 = min(2, r2)

    # r3 反差 (FIX: 12 markers + 三段式 + 转折)
    reversal = 0
    # Direct reversal markers
    if re.findall(r"\u4e0d[\u4e00-\u9fff]{1,3}\u4f46|\u4e0d[\u4e00-\u9fff]{1,3}\u5374|\u53ef\u662f|\u7136\u800c", body): reversal += 1
    # Size/height/fullness contrast
    if re.findall(r"(\u9ad8[\u4e00-\u9fff]{0,2}\u77ee|\u77ee[\u4e00-\u9fff]{0,2}\u9ad8|\u5927[\u4e00-\u9fff]{0,2}\u5c0f|\u5c0f[\u4e00-\u9fff]{0,2}\u5927|\u6ee1[\u4e00-\u9fff]{0,2}\u7a7a|\u7a7a[\u4e00-\u9fff]{0,2}\u6ee1|\u51b7[\u4e00-\u9fff]{0,2}\u70ed|\u70ed[\u4e00-\u9fff]{0,2}\u51b7|\u65e7[\u4e00-\u9fff]{0,2}\u65b0|\u65b0[\u4e00-\u9fff]{0,2}\u65e7|\u5916[\u4e00-\u9fff]{0,2}\u5185|\u5185[\u4e00-\u9fff]{0,2}\u5916)", body): reversal += 1
    # Three-way 三段式 (success/failure/unknown)
    if re.findall(r"\u4e00\u4e2a[\u4e00-\u9fff]{0,4}\u4e86\uff0c|\u4e00\u4e2a[\u4e00-\u9fff]{0,4}\u4e86\uff0c|\u8fd8\u6709\u4e00\u4e2a", body): reversal += 1
    # 对照 structure (one X / another Y)
    if re.search(r"\u4e00[\u4e00-\u9fff]{0,4}\uff0c[\u4e00-\u9fff]{0,8}\uff0c\u53e6\u4e00[\u4e00-\u9fff]{0,8}", body) or re.search(r"\u4e0d\u540c[\u4e00-\u9fff]{0,4}\u7684", body): reversal += 1
    r3 = min(2, reversal)

    # r4 拉扯 (FIX: broaden beyond just 替)
    push_pull = re.findall(r"(\u66ff\u5979|\u66ff\u4ed6|\u66ff\u81ea\u5df1|\u4e0d\u66ff|\u770b\u89c1|\u4e0d\u66ff\u770b\u89c1|\u5979\u6ca1[\u4e00-\u9fff]{1,3}\u4ed6|\u4ed6\u6ca1[\u4e00-\u9fff]{1,3}\u5979|\u4e0d[\u4e00-\u9fff]{1,3}\u66ff|\u6ca1\u7b54|\u6ca1\u63a5|\u6ca1\u7ee7\u7eed|\u62c5\u5fc3|\u62c5\u5fe7|\u62a5\u544a|\u7b49\u4ed6|\u7b49\u5979)", body)
    r4 = 0
    if len(push_pull) >= 2: r4 += 1
    if len(push_pull) >= 5: r4 += 1
    r4 = min(2, r4)

    # r5 记忆点 (same as v2 — short quotable)
    sentences = [s.strip() for s in re.split(r"[\u3002\uff01\uff1f!?]", body) if s.strip()]
    short_quotes = [s for s in sentences if 5 <= len(re.findall(r"[\u4e00-\u9fff]", s)) <= 30]
    r5 = 0
    if len(short_quotes) >= 3: r5 += 1
    if len(short_quotes) >= 6: r5 += 1
    r5 = min(2, r5)

    # r6 代入 (same)
    sensory_count = len(SENSORY_VOCAB.findall(body))
    r6 = 0
    if sensory_count >= 8: r6 += 1
    if sensory_count >= 20: r6 += 1
    r6 = min(2, r6)

    # r7 新 (FIX: 物象 diversity)
    template_loop = sum(len(re.findall(p, body)) for p in ["\u770b\u5411", "\u66ff\u5979", "\u66ff\u4ed6"])
    novel_anchors = sum(1 for p in MOTIF_PATTERNS if p.search(body))
    r7 = 0
    if template_loop < 6: r7 += 1
    if novel_anchors >= 5: r7 += 1
    r7 = min(2, r7)

    return [r1, r2, r3, r4, r5, r6, r7]


def grade_publishable_v3(body, hook_text, fm):
    """Fix pub:
       - p4 cast3-5: now gives 2 if 3-5, 1 if 2 or 6, 0 if 1 or 7+ (was inverted!)
       - p5 开场: also check that first sentence has action/observation
       - p6 收尾: also check that last sentence has unresolved action
    """
    han = re.findall(r"[\u4e00-\u9fff]", body)
    if not han: return [0]*6
    sentences = [s.strip() for s in re.split(r"[\u3002\uff01\uff1f!?]", body) if s.strip()]

    # p1 画面钩 (same)
    visual_frames = sum(1 for p in MOTIF_PATTERNS if p.search(body))
    p1 = 2 if visual_frames >= 5 else (1 if visual_frames >= 2 else 0)

    # p2 截图句 (same)
    short_quotes = [s for s in sentences if 5 <= len(re.findall(r"[\u4e00-\u9fff]", s)) <= 30]
    p2 = 2 if len(short_quotes) >= 3 else (1 if len(short_quotes) >= 1 else 0)

    # p3 独立可读 (FIX: only count unique 物象)
    unique_anchors = sum(1 for p in MOTIF_PATTERNS if p.search(body))
    p3 = 2 if unique_anchors >= 4 else (1 if unique_anchors >= 2 else 0)

    # p4 cast3-5 (FIXED — was inverted)
    cast = fm.get("cast", "")
    n_cast = cast.count(",") + 1 if cast else 0
    if 3 <= n_cast <= 5: p4 = 2
    elif n_cast == 2 or n_cast == 6: p4 = 1
    else: p4 = 0

    # p5 强开场 (FIX: require action verb in first 10 chars)
    body_no_title = re.sub(r"^#.*$", "", body, flags=re.M).strip()
    first_30 = body_no_title[:60]
    first_10_han = "".join(re.findall(r"[\u4e00-\u9fff]", first_30))[:12]
    has_conflict = any(kw in first_10_han for kw in ["\u6797", "\u82cf", "\u963f", "\u53f6", "\u4f59", "\u8d64", "\u6c88", "\u51cc", "\u725b", "\u88f8", "\u4ed6", "\u5979"])
    has_action = any(kw in first_30 for kw in ["\u8d70", "\u62ff", "\u62d4", "\u9a6f", "\u62d7", "\u62a5", "\u8bf4", "\u95ee", "\u67e5", "\u62a2", "\u53ec", "\u62d6", "\u9707", "\u8df3", "\u6311", "\u542c"])
    p5 = 2 if (has_conflict and has_action) else (1 if has_conflict else 0)

    # p6 强收尾 (FIX: check for unresolved action in last 50 chars)
    last_50 = body.strip()[-60:]
    last_han = "".join(re.findall(r"[\u4e00-\u9fff]", last_50))[-15:]
    has_unresolved = bool(re.search(r"\u300c|\u8bf4|\u95ee|\u770b|\u8d70|\u62ff|\u4e0d\u7b54|\u8fd8\u5728|\u672a\u51fa", last_50))
    hook = clean_pipe(hook_text or "")
    p6 = 2 if has_unresolved or hook else 1

    return [p1, p2, p3, p4, p5, p6]


def grade_shanghai(body):
    """NEW: 上瘾-specific dimensions (晋江读者心理):
       - sh1 末句钩子 强度 (0-2)
       - sh2 章末 物象 留白 (0-2)
       - sh3 情绪波 (sweet+knife) (0-2)
       - sh4 关系 推力 节拍 (0-2)
       - sh5 女主/POV 能动性 (0-2)
       - sh6 悬念 carry (new info in last 30%) (0-2)
    """
    if not body: return [0]*6
    han = re.findall(r"[\u4e00-\u9fff]", body)
    chars = len(han)
    if chars < 300: return [0]*6

    # sh1 末句钩子
    last_30 = body.strip()[-30:]
    last_han = "".join(re.findall(r"[\u4e00-\u9fff]", last_30))
    # Strong hook: ends with object + 。  /  ends with quote  /  ends with question  /  ends with unfinished action
    hook_words = ["\u542c", "\u770b", "\u8bf4", "\u95ee", "\u8d70", "\u62ff", "\u8fd8\u5728", "\u8fd8\u6709", "\u4e0d\u7b54", "\u4e0d\u8bf4"]
    sh1 = 0
    if any(w in last_30 for w in hook_words): sh1 += 1
    if last_30.endswith("\u3002") and len(last_han) <= 20: sh1 += 1
    sh1 = min(2, sh1)

    # sh2 末句物象
    sh2 = 0
    for p in MOTIF_PATTERNS:
        if p.search(last_30): sh2 += 1
    sh2 = min(2, sh2)

    # sh3 情绪波 (sweet words + knife words)
    sweet = len(re.findall(r"(\u7cd6|\u751c|\u6e29\u67d4|\u6e29\u6696|\u4e3a\u4ed6|\u4e3a\u5979|\u62ff\u8d77|\u62d4\u51fa|\u63a5\u8fc7|\u63a5\u4f4f|\u62b1|\u624b|\u51c6\u5907)", body))
    knife = len(re.findall(r"(\u5200|\u88c1|\u65ad|\u6bc1|\u62fc|\u6279|\u8ba9|\u8feb|\u62d2|\u8f6c\u8eab|\u8d70|\u9000|\u9501|\u9489|\u95ed)", body))
    sh3 = 0
    if sweet >= 3 and knife >= 3: sh3 += 2
    elif sweet + knife >= 5: sh3 += 1
    sh3 = min(2, sh3)

    # sh4 关系推力 (替/看见/不替/看见她/看见他 - 任何CP动作)
    cp_beats = re.findall(r"(\u66ff\u5979|\u66ff\u4ed6|\u66ff\u81ea\u5df1|\u770b\u89c1|\u770b\u7740|\u6ca1\u770b|\u4e0d\u770b|\u9a71\u8d70|\u7559\u4e0b|\u7ed9\u4ed6|\u7ed9\u5979|\u4ea4\u7ed9|\u62ff\u7ed9)", body)
    sh4 = 0
    if len(cp_beats) >= 2: sh4 += 1
    if len(cp_beats) >= 5: sh4 += 1
    sh4 = min(2, sh4)

    # sh5 女主/POV 能动性 (action verb subject)
    actions = re.findall(r"[\u3002\uff1b\uff0c\u3001]([\u5979\u4ed6][\u62ff\u62d4\u8d70\u62a5\u67e5\u95ee\u4e3a\u6253\u542c\u63d0\u8d77\u6293\u62d6\u653e\u62a5\u9519\u7b11\u7ed9\u8bf4\u7b54\u4e3a\u62a2\u62a4\u62d7\u9009\u62e9\u51c6\u5907\u5e26\u62c9\u62ac\u62a4\u62b1\u6536\u67e5\u770b\u53ec\u559a][\u4e00-\u9fff]{0,8})", body)
    sh5 = 0
    if len(actions) >= 5: sh5 += 1
    if len(actions) >= 12: sh5 += 1
    sh5 = min(2, sh5)

    # sh6 悬念carry (new info in last 30% of body)
    body_30 = body[int(len(body)*0.7):]
    new_info = re.findall(r"(\u662f[\u4e00-\u9fff]{1,6}\u4e0d\u662f|\u539f\u6765|\u53d1\u73b0|\u8fd9\u4ef6\u4e8b|\u8fd9\u4e2a\u4eba|\u8fd9\u4e2a\u540d\u5b57|\u8fd9\u53e5\u8bdd|\u8fd9\u4e9b\u8bdd|\u8fd9\u4efd\u4fe1|\u8fd9\u4e2a\u4fe1)", body_30)
    sh6 = 0
    if len(new_info) >= 2: sh6 += 1
    if len(new_info) >= 5: sh6 += 1
    sh6 = min(2, sh6)

    return [sh1, sh2, sh3, sh4, sh5, sh6]


def assess(path):
    text = path.read_text(encoding="utf8")
    fm, body = split_front_matter(text)
    hook_text = fm.get("hook", "")
    body_for_match = PL.body_of(text)
    hook_clean = clean_pipe(hook_text)
    first8 = hook_clean[:8]
    fm["_hook_evidenced"] = bool(first8 and first8 in body_for_match)

    d7, debug = grade_7d_v3(body)
    rubric = grade_rubric_v3(body, hook_text, fm)
    pub = grade_publishable_v3(body, hook_text, fm)
    sh = grade_shanghai(body)

    cn_match = re.match(r"^(?:ch)?(\d+)-", path.name)
    chapter = int(cn_match.group(1)) if cn_match else 0

    return {
        "file": path.name,
        "title": fm.get("title", ""),
        "chapter": chapter,
        "score_field": fm.get("score_field", fm.get("score", "")),
        "body_chars": len(re.findall(r"[\u4e00-\u9fff]", body)),
        "d7": d7, "d7_sum": sum(d7),
        "rubric": rubric, "rubric_sum": sum(rubric),
        "pub": pub, "pub_sum": sum(pub),
        "sh": sh, "sh_sum": sum(sh),
        "total_52": sum(d7) + sum(rubric) + sum(pub) + sum(sh),
        "max_52": 52,
        "debug": debug,
    }


def main():
    grades = []
    files = sorted(CHRON.glob("*.md"))
    files = [f for f in files if not f.name.startswith("_")]
    print(f"Grading {len(files)} chapters with v3 grader...")
    for i, f in enumerate(files):
        try:
            g = assess(f)
            grades.append(g)
            if (i+1) % 100 == 0:
                print(f"  {i+1}/{len(files)}")
        except Exception as e:
            print(f"  ERR {f.name}: {e}")
    out = {
        "summary": {
            "n_chapters": len(grades),
            "v3_features": ["fixed_cast3_5", "broader_反差", "broader_拉扯", "作者总结_检测", "上瘾_shanghai_6dim"],
        },
        "grades": grades,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf8")
    print(f"Wrote {OUT}")

    # Quick tier distribution
    buckets = {"S":0, "A":0, "B":0, "C":0, "D":0, "E":0}
    for g in grades:
        t = g["total_52"]
        if t >= 42: buckets["S"] += 1
        elif t >= 38: buckets["A"] += 1
        elif t >= 33: buckets["B"] += 1
        elif t >= 28: buckets["C"] += 1
        elif t >= 22: buckets["D"] += 1
        else: buckets["E"] += 1
    print("Tier distribution (total_33, max 33):")
    for k,v in buckets.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()






