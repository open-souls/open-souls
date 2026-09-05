# -*- coding: utf-8 -*-
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
"""文笔上线门 / prose quality gate.

确定性地扫描 chronicle/*.md 的正文，卡住把这部连载写垮的几类退化：

  1. 中英文混写——正文里冒出英文对话标签（he said / she said / he stopped …）
     或成串拉丁字母。这是中文网文，正文里不该有英文叙述。
  2. 逗号碎句——把句子剁成「她，没有敲门，直接推开，进来」这种一两字一顿的
     机械碎片。用「微碎片率」(1-3 字短句占比) 和「平均段长」来量。
  3. 填充描写——「屋里安静/院里安静/心里咚了一下/夜很静」这种用形容词+动词糊弄
     过去、没在写景也没在写人的懒笔。一句话讲不出在写什么，就删。
  4. 破折号过载——单段 5 个以上「——」，节奏被拖成散文诗，晋江读者一眼看出机器味。
  5. §七.1 第二道墙——「X 的来处是 Y」/「X 的方式不是 X」/动词+朝+自反代词的
     后置「朝」公式（例：「擦朝苏挽自己擦的」「走朝他自己走的」）。这是 subagent
     翻译「只写感知不写心理」机械化的产物，作者亲写也破不掉（Loop #91）。
  6. 章节字数下限——config.yaml target_chapter_chars: 1500。低于这个数的章节
     不叫章节，叫占位 stub。

两档：
  ERROR  退回，CI 失败。卡的是已经垮掉的机械腔（前期正常章节都过得去）。
  WARN   提个醒。卡的是离「好文笔」还有距离、但还没垮的章节。

Stub 豁免：默认跳过 chronicle/_STUB_MANIFEST.json 里的文件（占位 stub，与
真章同号并存，不属于连载正文）。加 --include-stubs 一并扫。

用法：
  python engine/prose_lint.py                          # 扫全部（默认跳过 stub）
  python engine/prose_lint.py --include-stubs          # 一并扫 stub
  python engine/prose_lint.py path/to/ch.md            # 只扫指定文件
  python engine/prose_lint.py --warn-as-error          # WARN 也当失败（更严）
"""
import os
import re
import sys
import glob
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- 阈值 ----
# ERROR：垮掉的机械腔。前期正常章节（约 ch1-149）都在这条线之内。
MICRO_ERROR = 0.42            # 微碎片率（1-3 汉字的短句占比）上限
AVGSEG_ERROR = 3.5            # 平均段长（每个逗号/句读之间的汉字数）下限
DASH_PARAGRAPH_ERROR = 5     # 单段破折号（——）上限
MIN_CHAPTER_CHARS = 1500      # 章节汉字下限（config.yaml target_chapter_chars）
CHAO_POSTPOSITIONAL_ERROR = 2  # 后置「朝」公式出现次数上限（动词+朝+自反代词）
X_LAI_CHU_ERROR = 3           # 「X 的来处是 Y」「X 的方式不是 X」出现次数上限
FIRST_BREAK_ERROR = 3         # 「就第一刹让」机械动作碎解链出现次数上限
DIRECTION_FORMULA_ERROR = 3   # 「X 的方向朝着 Y」同构句式出现次数上限
# WARN：离好文笔还有距离。
MICRO_WARN = 0.30
AVGSEG_WARN = 4.5

# Stub manifest path（若存在，默认跳过其中列出的文件）
# Try to load min_chars from config.yaml so the CLI enforces the
# configured chapter length (target_chapter_chars: 1500).  Falls back
# to MIN_CHAPTER_CHARS if config is missing.
def _load_min_chars():
    cfg = os.path.join(ROOT, "config.yaml")
    if not os.path.isfile(cfg):
        return MIN_CHAPTER_CHARS
    try:
        import yaml
        with open(cfg, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        return int(data.get("target_chapter_chars", MIN_CHAPTER_CHARS))
    except Exception:
        return MIN_CHAPTER_CHARS

MIN_CHAPTER_CHARS_FROM_CONFIG = _load_min_chars()

STUB_MANIFEST = os.path.join(
    ROOT, "seasons", "01-xianxia", "chronicle", "_STUB_MANIFEST.json"
)


def load_stub_set():
    """Read _STUB_MANIFEST.json, return stub filename set.

    Compatible with two files format:
      - files: [{"filename": "..."}, ...]   (legacy dict list)
      - files: ["...", ...]                  (new string list, post P0)
    """
    if not os.path.isfile(STUB_MANIFEST):
        return set()
    try:
        with open(STUB_MANIFEST, encoding="utf-8") as fh:
            data = json.load(fh)
        out = set()
        for entry in data.get("files", []):
            if isinstance(entry, dict):
                fn = entry.get("filename", "")
                if fn:
                    out.add(fn)
            elif isinstance(entry, str):
                if entry:
                    out.add(entry)
        return {x for x in out if x}
    except Exception:
        return set()
    try:
        with open(STUB_MANIFEST, encoding="utf-8") as fh:
            data = json.load(fh)
        return {entry["filename"] for entry in data.get("files", [])}
    except Exception:
        return set()


# 正文里出现即判中英混写：英文对话标签
ENG_TAG = re.compile(
    r"\b(he|she|they|it|we|you|i)\s+"
    r"(said|stopped|asked|paused|nodded|added|replied|whispered|murmured|"
    r"thought|looked|smiled|laughed|continued|answered|went)\b",
    re.I,
)
# 其它成串拉丁字母（白名单：ch123 这类交叉引用、纯标记），WARN 级
LATIN_RUN = re.compile(r"[A-Za-z]{2,}")
LATIN_OK = re.compile(r"^(ch|end|of)$", re.I)  # 交叉引用 / 编辑标记残留，不当 ERROR

# 填充描写——「屋里安静/院里静悄悄/夜很静」这种用形容词糊弄过去的懒笔。
FILLER = [
    re.compile(r"(?:屋里|院中|院子里|院里|屋内|屋子里|屋子|厅里|廊下|廊里|门外|"
               r"四周|周遭|巷子里|空气里?|气氛中|夜|风)"
               r"[^一-鿿]{0,3}"
               r"(?:很\s*|十分\s*|格外\s*|异常\s*|死一般\s*)?"
               r"(?:安静|寂静|静悄悄|静得|悄|凝重|沉静)"),
    re.compile(r"(?:屋里|院中|院子里|院里|屋内|屋子里|厅里|廊下|廊里)"
               r"[^一-鿿]{0,3}"
               r"(?:很\s*|十分\s*|格外\s*)?"
               r"(?:空|空荡|空落|空无一人)"),
    re.compile(r"(?:夜|风)\s*(?:很\s*|十分\s*|格外\s*)?"
               r"(?:静|深|漫长|寂寥)"),
    re.compile(r"(?:周围|四周)\s*(?:很\s*|一片\s*)?"
               r"(?:安静|寂静|静悄悄)"),
]
# 「心里咚/扑通/咯噔」 — 用拟声糊弄感受
FILLER_HEART = re.compile(
    r"心里\s*(?:咚|扑通|咯噔)(?:\s*(?:一?[下了]?[一下跳])?)?"
)

# §七.1 第二道墙病体公式（Loop #91 §四.2 实测：作者亲写也破不掉）
# 公式 1：后置「朝」= 动词+朝+自反代词/他/她
#   例：「擦朝苏挽自己擦的」「走朝他自己走的」「停朝他按在桌面那一按」
#   排除合法前置朝：「朝那张图扫了一眼」「朝他看」（方向介词）
CHAO_POSTPOSITIONAL = re.compile(
    r"[一-鿿]{1,3}朝(?:他|她|我|你|您|自个儿|自己)"
    r"[^。！？\n]{0,30}?"
    r"(?:[一-鿿]{1,3}(?:的|了|着|过|一)|$)"
)
# 公式 2：「X 的来处是 Y」「X 的方式不是 X」「X 的方向是他自己」
#   例：「不必的方式不是林窈。是林夙自己。」「没偏的方向不是叶观澜——是林夙自己」
X_LAI_CHU = re.compile(
    r"(?:[一-鿿]{1,4})的"
    r"(?:来处|方式|方向|位|位是|路径|路)"
    r"(?:不是|是他|是她|是我|是自己)"
)
# 公式 3：「就第一刹让 X 先朝 Y」（机械动作碎解链）
FIRST_BREAK = re.compile(r"就(?:第|头)一刹让")
# A neighboring failure mode to the old postpositional-"朝" formula:
# the whole sentence keeps rotating through "...的方向朝着..." with only
# nouns swapped. A couple of intentional uses are fine; repeated uses are a
# generation loop and must be revised before publication.
DIRECTION_FORMULA = re.compile(
    r"(?:[一-鿿]{1,8}的?)?方向(?:朝(?:向|着)|落在|落下|不必替|是)"
)
# 同一批退化稿常把“上一世/替谁/自己守”当作动作的后置解释，
# 通过换名词无限重复。少量语义使用可以存在，达到阈值即视为生成回路。
SELF_REPAIR_FORMULA = re.compile(
    r"(?:不必替(?:上一世|前世|谁)|(?:他|她|我)?自己守)"
)
SELF_REPAIR_FORMULA_ERROR = 3
# “某某的方式，是……那种/那一路”是同一类把动作翻译成自我解释的墙。
WALL_FORMULA = re.compile(
    r"(?:[一-鿿]{1,8}的方式\s*[，,:：]?\s*(?:是|不是)|"
    r"[一-鿿]{1,8}的方式[^。！？\n]{0,20}那种|自己那一路)"
)
WALL_FORMULA_ERROR = 2

# Section 7.2: template-loop detector. Catches the dedupe_phrases
# side effect where 160 chapters collapsed into the same template.
# Strong signal: open_div < 0.62 + open_top >= 8 + kan-yang >= 15 + bu-ti >= 4
# catches 160/160 broken, 0/640 good (verified 2026-09-04).
TEMPLATE_LOOP_DIV = 0.62
TEMPLATE_LOOP_TOP = 8
TEMPLATE_LOOP_XIANG = 15
TEMPLATE_LOOP_SELF_REPAIR = 4

# 机器稿还会把物象位置和“自我承担”拆成同一个短语反复回放。少量
# 意象回声可以是作者风格；超过这条线，通常已经不是伏笔而是生成循环。
MOTIF_SLOT = re.compile(r"那一(?:寸|截|道|笔|料|侧|层|行|刻|处|回|声|端|角|点)")
SELF_CLAIM = re.compile(r"(?:我|他|她)自己")
MACHINE_MOTIF_ERROR = 30
MACHINE_SELF_CLAIM_ERROR = 18

# 晋江工艺红旗（batch 14）：低烈度物象回环、自我回环、单字断章。
# JJ_LINT_NAYIX: 见 _count_nayix(body) 手写计数器（regex 会因 那 ∈ [一-鿿] 而吞掉下一段）
JJ_LINT_NAYIX_WARN = 6
JJ_LINT_NAYIX_ERROR = 40  # 研究分层参考；不作为默认 ERROR


def _count_nayix(body):
    """Count non-overlapping 那-一-X phrases (X = 1-3 chinese chars, X != 那).

    The regex r"那一[一-鿿]{1,3}" is greedy and U+90A3 (那) is inside
    [一-鿿] (U+4E00..U+9FFF), so the regex swallows the next 那. This
    hand-rolled counter walks the string left-to-right and consumes the
    X suffix explicitly, producing a non-overlapping count that matches
    what the project considers "那一X" in editor review.
    """
    count = 0
    i = 0
    n = len(body)
    while i < n - 1:
        if body[i] == "那" and body[i + 1] == "一":
            j = i + 2
            k = 0
            while j < n and k < 3:
                ch = body[j]
                if "\u4e00" <= ch <= "\u9fff" and ch != "那":
                    j += 1
                    k += 1
                else:
                    break
            if k >= 1:
                count += 1
                i = j
                continue
        i += 1
    return count


JJ_LINT_ZIJI = re.compile(r"自己")
JJ_LINT_ZIJI_WARN_DIV = 4
JJ_LINT_ZIJI_ERROR_DIV = 2
JJ_LINT_TAIL = re.compile(r"^[一-鿿]{1,2}[。！？…」』]?$")

SEG_SPLIT = re.compile(r"[，。！？、：；\n]")
HAN = re.compile(r"[一-鿿]")


def _split_sentences(body):
    sents = re.split(r'[。！？\n]', body)
    return [s.strip() for s in sents if len(s.strip()) >= 4]


def _open_diversity(body):
    sents = _split_sentences(body)
    if len(sents) < 20:
        return 1.0
    opens = [s[:4] for s in sents]
    return len(set(opens)) / len(opens)


def _open_top(body):
    from collections import Counter
    sents = _split_sentences(body)
    if not sents:
        return 0
    opens = [s[:4] for s in sents]
    return max(Counter(opens).values())


def body_of(text):
    """去掉 frontmatter、标题行、分场线，留正文。"""
    # 去 BOM 和统一换行
    if text.startswith("\ufeff"):
        text = text[1:]
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    m = re.match(r"^---\s*\n.*?\n---\s*\n?(.*)$", text, re.S)
    b = m.group(1) if m else text
    b = re.sub(r"^#.*$", "", b, flags=re.M)           # 标题行
    b = re.sub(r"^\s*\*.*?\*\s*$", "", b, flags=re.M)  # *编辑标记* 整行
    b = b.replace("---", "")                          # 分场线
    return b


def measure(body):
    han = HAN.findall(body)
    chars = len(han)
    segs = [s for s in SEG_SPLIT.split(body) if HAN.search(s)]
    seglens = [len(HAN.findall(s)) for s in segs]
    micro = (sum(1 for L in seglens if 1 <= L <= 3) / len(seglens)) if seglens else 0.0
    avg = (sum(seglens) / len(seglens)) if seglens else 99.0
    eng = ENG_TAG.findall(body)
    latin = [w for w in LATIN_RUN.findall(body) if not LATIN_OK.match(w)]
    filler = sum(len(p.findall(body)) for p in FILLER) + len(FILLER_HEART.findall(body))
    paragraphs = [p for p in body.split("\n\n") if p.strip()]
    dash_max = max((p.count("——") for p in paragraphs), default=0)
    chao_postp = CHAO_POSTPOSITIONAL.findall(body)
    x_laichu = X_LAI_CHU.findall(body)
    first_break = FIRST_BREAK.findall(body)
    direction_formula = DIRECTION_FORMULA.findall(body)
    self_repair_formula = SELF_REPAIR_FORMULA.findall(body)
    wall_formula = WALL_FORMULA.findall(body)
    motif_slot = MOTIF_SLOT.findall(body)
    self_claim = SELF_CLAIM.findall(body)
    jj_nayix = _count_nayix(body)
    jj_ziji = JJ_LINT_ZIJI.findall(body)
    body_lines = [line for line in body.splitlines() if line.strip()]
    last_line = body_lines[-1].strip() if body_lines else ""
    jj_tail = bool(JJ_LINT_TAIL.match(last_line))
    return {
        "chars": chars,
        "micro": micro,
        "avg": avg,
        "eng": len(eng),
        "latin": len(latin),
        "filler": filler,
        "dash_max": dash_max,
        "chao_postp": len(chao_postp),
        "x_laichu": len(x_laichu),
        "first_break": len(first_break),
        "direction_formula": len(direction_formula),
        "self_repair_formula": len(self_repair_formula),
        "wall_formula": len(wall_formula),
        "motif_slot": len(motif_slot),
        "self_claim": len(self_claim),
        "jj_nayix": jj_nayix,
        "jj_ziji": len(jj_ziji),
        "jj_tail": jj_tail,
        "body_lines": len(body_lines),
        "open_div": _open_diversity(body),
        "open_top": _open_top(body),
        "xiang_count": body.count("看向"),
        "self_repair_count": body.count("不必替"),
    }


def machine_echo_hits(body):
    """Return high-confidence repetition loops for generated chapter review.

    This is intentionally stricter than the historical prose lint only when a
    caller asks for strict editorial review. A recurring image remains legal;
    a chapter that keeps rephrasing the same location or ``X自己`` claim is
    returned for human revision instead of being mistaken for polished prose.
    """
    metrics = measure(body)
    hits = {}
    if metrics["motif_slot"] >= MACHINE_MOTIF_ERROR:
        hits["motif_slot"] = metrics["motif_slot"]
    if metrics["self_claim"] >= MACHINE_SELF_CLAIM_ERROR:
        hits["self_claim"] = metrics["self_claim"]
    return hits


def lint_text(text, min_chars=None, file_size=None, strict=False):
    """Lint chapter text in memory using the same rules as the CLI.

    ``min_chars`` is intentionally opt-in: historical chapters keep the
    existing CLI behavior, while newly generated chapters can require the
    configured target length before they are published.
    """
    # 按章豁免：frontmatter 里 prose_lint_exempt: true 的章节跳过文笔门。
    fm_m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if fm_m:
        try:
            import yaml
            fm = yaml.safe_load(fm_m.group(1)) or {}
        except Exception:
            fm = {}
        if fm.get("prose_lint_exempt"):
            return [], [], {"chars": 0, "exempt": True}
    errors = []
    warns = []
    m = measure(body_of(text))
    if min_chars is not None and m["chars"] < min_chars:
        errors.append(
            f"章节字数不足：{m['chars']} < {min_chars}，生成稿不得以 stub 形式上线"
        )
    if m["chars"] < 50:
        return errors, warns, m
    file_size = file_size or 0
    if m["eng"]:
        errors.append(
            f"中英混写：正文出现 {m['eng']} 处英文对话标签"
            f"(he said / she said …)，改成中文"
        )
    if m["micro"] > MICRO_ERROR:
        errors.append(
            f"逗号碎句：微碎片率 {m['micro']*100:.0f}% > "
            f"{MICRO_ERROR*100:.0f}%，把一两字一顿的碎句合成通顺短句"
        )
    if m["avg"] < AVGSEG_ERROR:
        errors.append(
            f"逗号碎句：平均段长 {m['avg']:.1f} < {AVGSEG_ERROR}"
            f"（句子被剁太碎）"
        )
    if m["filler"]:
        errors.append(
            f"填充描写：{m['filler']} 处「屋里安静/院里静/夜很静/心里咚」"
            f"之类——删了，或换成具体写景写人"
        )
    if m["dash_max"] >= DASH_PARAGRAPH_ERROR:
        errors.append(
            f"破折号过载：单段最多 {m['dash_max']} 个「——」"
            f"(>={DASH_PARAGRAPH_ERROR})，节奏被拖成散文诗，分段或换叙述"
        )
    # §七.1 第二道墙
    if m["chao_postp"] >= CHAO_POSTPOSITIONAL_ERROR:
        errors.append(
            f"§七.1 后置「朝」公式：{m['chao_postp']} 处"
            f"「动词+朝+自反代词」(例:擦朝X自己擦的)。"
            f"作者亲写也破不掉(Loop #91)。改成方向介词或换主语"
        )
    if m["x_laichu"] >= X_LAI_CHU_ERROR:
        errors.append(
            f"§七.1 「X 的来处/方式/方向是 Y」公式：{m['x_laichu']} 处。"
            f"机械翻译公式,改写具体动作/感官锚点"
        )
    if m["first_break"] >= FIRST_BREAK_ERROR:
        errors.append(
            f"§七.1 「就第一刹让」机械动作碎解链：{m['first_break']} 处。"
            f"每个动作被拆 3-5 步,零留白,违反范文 F 单字砸句"
        )
    if m["direction_formula"] >= DIRECTION_FORMULA_ERROR:
        errors.append(
            f"句式回环：{m['direction_formula']} 处「X的方向朝着/落在/不必替Y」"
            f"同构句式，疑似生成循环。保留必要方向描写，其余改成具体动作、感官或对话"
        )
    if m["self_repair_formula"] >= SELF_REPAIR_FORMULA_ERROR:
        errors.append(
            f"自我修复回环：{m['self_repair_formula']} 处「不必替上一世/自己守」"
            f"后置解释，疑似生成循环。把重复解释改成现场动作、关系压力或具体物件"
        )
    # Section 7.2 template-loop ERROR check
    if (m["open_div"] < TEMPLATE_LOOP_DIV
            and m["open_top"] >= TEMPLATE_LOOP_TOP
            and m["xiang_count"] >= TEMPLATE_LOOP_XIANG
            and m["self_repair_count"] >= TEMPLATE_LOOP_SELF_REPAIR):
        errors.append(
            "Section 7.2 template loop: opening 4-char diversity "
            + str(round(m['open_div'], 2))
            + ", top opening "
            + str(m['open_top'])
            + " times, kan-yang "
            + str(m['xiang_count'])
            + ", bu-ti "
            + str(m['self_repair_count'])
            + ". Rewrite per Jinjiang: change POV / props / action / hook."
        )

    if m["wall_formula"] >= WALL_FORMULA_ERROR:
        errors.append(
            f"自指解释回环：{m['wall_formula']} 处「某某的方式，是……那种/那一路」"
            f"，把动作改成可观察的身体、物件或对话变化"
        )
    # JJ-LINT-01 / 02 batch 14 —— WARN-only（不升级 ERROR；推 push 不阻断）
    # JJ-LINT-01 的 40 阈值保留为研究分层参考，默认 lint 仍只给 WARN。
    # 改稿时可人工看 WARN 自查。
    if strict:
        echo_hits = machine_echo_hits(body_of(text))
        if "motif_slot" in echo_hits:
            errors.append(
                f"物象位置回环：{echo_hits['motif_slot']} 处「那一X」位置短语，"
                "同一物象被机械换名复述；保留关键意象，其余改成动作、冲突或信息"
            )
        if "self_claim" in echo_hits:
            errors.append(
                f"自我承担回环：{echo_hits['self_claim']} 处「我/他/她自己」后置解释，"
                "删掉口号式自证，让选择用代价、物件或他人反应落地"
            )
    # WARN 级
    if not errors:
        if m["micro"] > MICRO_WARN:
            warns.append(
                f"微碎片率 {m['micro']*100:.0f}% 偏高(>{MICRO_WARN*100:.0f}%)，可再揉顺"
            )
        if m["avg"] < AVGSEG_WARN:
            warns.append(f"平均段长 {m['avg']:.1f} 偏短(<{AVGSEG_WARN})")
        if 1 <= m["first_break"] <= 2:
            warns.append(
                f"§七.1 「就第一刹让」出现 {m['first_break']} 次,"
                f"临界,自查是否开始染病"
            )
        if m["chao_postp"] == 1:
            warns.append("§七.1 后置「朝」出现 1 次,临界,自查是否误用")
    # 字数下限——只在「文件很大但正文很薄」时 WARN（真正短篇如 ch001 不算病）
        if file_size > 8000 and m["chars"] < 1000:
            warns.append(
                f"文件 {file_size}B 但正文仅 {m['chars']} 字——"
                f"若非 stub 占位则需扩写（config.yaml 下限 1500）"
            )
        # 晋江工艺红旗（batch 14）WARN 段
        _ziji_lines = m.get("body_lines", 0) or 1
        if m["jj_nayix"] >= JJ_LINT_NAYIX_WARN:
            warns.append(
                "JJ-LINT-01 物象回环临界：" + str(m["jj_nayix"]) + " 处「那一X」 (>= " + str(JJ_LINT_NAYIX_WARN) + ");"
                "删除整句,不换同义词,自查是否开始染病"
            )
        if (m["jj_ziji"] * JJ_LINT_ZIJI_WARN_DIV > _ziji_lines
                and _ziji_lines > 4):
            warns.append(
                "JJ-LINT-02 自己回环临界：" + str(m["jj_ziji"]) + " 处 / " + str(_ziji_lines) + " 行 ( > 行数/" + str(JJ_LINT_ZIJI_WARN_DIV) + ");"
                "把动作主语换成具名角色,自查是否开始染病"
            )
        if m.get("jj_tail"):
            warns.append(
                "JJ-LINT-07 单字断章:章末 <= 2 汉字 (M3 章尾钩禁用);"
                "至少扩到「她/他 + 一个未完成动作」"
            )
    if m["latin"]:
        warns.append(
            f"正文残留 {m['latin']} 处拉丁字母(交叉引用/标记?)，建议清掉"
        )
    # P1 weld follow-up: line: 混合 is the old 男频+女频 ambiguity tag.
    # After 2026-09-04 weld, primary reader is 女频言情. 混合 is a
    # transition-state tag that should be retired.
    _line_m = re.search(r"^line:\s*(.+)", text, re.M)
    if _line_m and _line_m.group(1).strip() == "混合":
        warns.append(
            "P1 weld follow-up: line: 混合 已退役。"
            "第一季主受众已焊为女频言情，"
            "请改 line 为 古言 / 古言仙侠 / 现言 / 玄幻言情 之一。"
        )
    return errors, warns, m


def lint_file(path, strict=False, min_chars=None):
    text = open(path, encoding="utf-8").read()
    return lint_text(text, file_size=len(text.encode("utf-8")), strict=strict, min_chars=min_chars)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    flags = {a for a in sys.argv[1:] if a.startswith("-")}
    warn_as_error = "--warn-as-error" in flags
    include_stubs = "--include-stubs" in flags
    stub_set = set() if include_stubs else load_stub_set()
    targets = args or sorted(glob.glob(
        os.path.join(ROOT, "seasons", "*", "chronicle", "*.md")
    ))
    # 只扫真正章节文件：名字以数字开头（001-xxx.md）或 ch<数字>-xxx.md
    # 排除 _STUB_MANIFEST.json 之类元数据文件
    targets = [p for p in targets if re.match(r"^(\d|ch\d)", os.path.basename(p)) and not os.path.basename(p).startswith("_")]
    skipped = 0
    if stub_set:
        before = len(targets)
        targets = [p for p in targets if os.path.basename(p) not in stub_set]
        skipped = before - len(targets)
    bad = False
    n_err = 0
    n_warn = 0
    n_exempt = 0
    for p in targets:
        errors, warns, m = lint_file(p, strict=False, min_chars=MIN_CHAPTER_CHARS_FROM_CONFIG)
        rel = os.path.relpath(p, ROOT)
        if m.get("exempt"):
            n_exempt += 1
            print(f"○ {rel}  (prose_lint_exempt)")
            continue
        if errors:
            bad = True
            n_err += 1
            print(f"✗ {rel}")
            for e in errors:
                print(f"   ERROR  {e}")
            for w in warns:
                print(f"   warn   {w}")
        elif warns:
            n_warn += 1
            print(f"⚠ {rel}")
            for w in warns:
                print(f"   warn   {w}")
            if warn_as_error:
                bad = True
    if skipped:
        stub_note = f"，{skipped} 个 stub 跳过"
    elif include_stubs:
        stub_note = "（含 stub）"
    else:
        stub_note = ""
    print(
        f"\n扫了 {len(targets)} 章{stub_note}：{n_exempt} 章豁免，"
        f"{n_err} 章退回(ERROR)，{n_warn} 章有提醒(WARN)。"
    )
    if bad:
        print("文笔没过线。中文叙述、把碎句揉成通顺短句，再上线。")
        sys.exit(1)
    print("文笔过线。")


if __name__ == "__main__":
    main()
