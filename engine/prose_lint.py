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
# WARN：离好文笔还有距离。
MICRO_WARN = 0.30
AVGSEG_WARN = 4.5

# Stub manifest path（若存在，默认跳过其中列出的文件）
STUB_MANIFEST = os.path.join(
    ROOT, "seasons", "01-xianxia", "chronicle", "_STUB_MANIFEST.json"
)


def load_stub_set():
    """读 _STUB_MANIFEST.json，返回 stub 文件名集合。文件不存在则返回空集。"""
    if not os.path.isfile(STUB_MANIFEST):
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
               r"(?:很\s+|十分\s+|格外\s+|异常\s+|死一般\s+)?"
               r"(?:安静|寂静|静悄悄|静得|悄|凝重|沉静)"),
    re.compile(r"(?:屋里|院中|院子里|院里|屋内|屋子里|厅里|廊下|廊里)"
               r"[^一-鿿]{0,3}"
               r"(?:很\s+|十分\s+|格外\s+)?"
               r"(?:空|空荡|空落|空无一人)"),
    re.compile(r"(?:夜|风)\s*(?:很\s+|十分\s+|格外\s+)?"
               r"(?:静|深|漫长|寂寥)"),
    re.compile(r"(?:周围|四周)\s*(?:很\s+|一片\s+)?"
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

SEG_SPLIT = re.compile(r"[，。！？、：；\n]")
HAN = re.compile(r"[一-鿿]")


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
    }


def lint_file(path):
    text = open(path, encoding="utf-8").read()
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
    m = measure(body_of(text))
    if m["chars"] < 50:
        return [], [], m
    file_size = len(text.encode("utf-8"))
    errors = []
    warns = []
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
    if m["latin"]:
        warns.append(
            f"正文残留 {m['latin']} 处拉丁字母(交叉引用/标记?)，建议清掉"
        )
    return errors, warns, m


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
        errors, warns, m = lint_file(p)
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