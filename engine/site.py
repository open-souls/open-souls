# -*- coding: utf-8 -*-
"""把 chronicle/*.md 连载编译成可读的网站数据 + EPUB。

产出（写进 docs/）：
  chronicle.json   每章 {n, season, title, date, cast, pov, hook, html}，给 index/read 两个 SPA 用
  <书名>.epub      整本电子书，可离线/导入阅读器

index.html / read.html 是静态壳，不在这里生成；它们 fetch chronicle.json 渲染。
"""
import os, re, json, glob, html, zipfile, datetime

def normalize_cast_name(name):
    """Strip editorial annotations like '叶观澜(暗线)' → '叶观澜'."""
    return re.sub(r"\s*[\(（].*?[\)）]\s*$", "", name).strip()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEASON_DIR = os.path.join(ROOT, "seasons", "01-xianxia")
CHRON_DIR = os.path.join(SEASON_DIR, "chronicle")
DRAFTS_DIR = os.path.join(SEASON_DIR, "drafts")
INTERLUDES_DIR = os.path.join(SEASON_DIR, "interludes")
DOCS = os.path.join(ROOT, "docs")
BOOK_TITLE = "镇狱之渊"
BOOK_AUTHOR = "众魂 · Open Souls"
BOOK_ID = "open-souls-zhenyuzhiyuan"


# ---------- 解析 ----------

def split_front_matter(text, source=None):
    """返回 (frontmatter_dict, body_str)。无 frontmatter 则 ({}, text)。"""
    if not text.startswith("---"):
        return {}, text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    import yaml
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        where = source or "<unknown>"
        raise SystemExit(f"frontmatter YAML 解析失败：{where}\n{e}")
    return fm, m.group(2)


def render_body(md):
    """把正文 markdown 渲染成 xhtml 片段。每个空行分隔的块=一段；--- = 分场线。

    只 strip 块内第一行的 `# 标题`，不丢掉整块（之前会把"标题紧跟正文"的首段一起吞掉）。
    """
    out = []
    for block in re.split(r"\n\s*\n", md.strip()):
        block = block.strip()
        if not block:
            continue
        if re.fullmatch(r"-{3,}|\*{3,}", block):
            out.append('<hr class="brk"/>')
            continue
        lines = block.split("\n")
        if lines and re.match(r"^#\s", lines[0]):     # 仅去掉标题行，保留正文
            lines = lines[1:]
            if not lines:
                continue
            block = "\n".join(lines)
        text = html.escape(block).replace("\n", "<br/>")
        out.append("<p>%s</p>" % text)
    return "\n".join(out)


def compute_present(html_text, declared_cast, all_chars):
    """基于正文 html 真实出现来算"出场"——不只信 frontmatter 的 cast 声明。

    返回在正文里出现的角色名列表（保序）。
    - declared_cast 里、html 里也出现的：留下
    - declared_cast 里、html 里没出现的：剔除（避免"写了没用"的水分）
    - declared_cast 之外、html 里出现的：也补上（修正 cast 漏写）
    """
    seen = []
    seen_set = set()
    for c in declared_cast:
        if c in html_text and c not in seen_set:
            seen.append(c); seen_set.add(c)
    for c in all_chars:
        if c in html_text and c not in seen_set:
            seen.append(c); seen_set.add(c)
    return seen


def load_dates():
    """从 INDEX.md 抽每回日期：'- 第82回《名》— … （2026-06-22）'。"""
    dates = {}
    idx = os.path.join(CHRON_DIR, "INDEX.md")
    if not os.path.exists(idx):
        return dates
    for line in open(idx, encoding="utf-8"):
        m = re.search(r"第\s*(\d+)\s*回.*?（(\d{4}-\d{2}-\d{2})）", line)
        if m:
            dates[int(m.group(1))] = m.group(2)
    return dates


def collect(include_drafts=False):
    dates = load_dates()
    by_n = {}
    all_chars = set()
    sources = [CHRON_DIR]
    if include_drafts:
        sources.append(DRAFTS_DIR)
    sources.append(INTERLUDES_DIR)   # 插章固定包含（不是 drafts）
    # 第一遍：扫所有 cast，构造全局角色集合
    for src_dir in sources:
        if not os.path.isdir(src_dir):
            continue
        for path in glob.glob(os.path.join(src_dir, "*.md")):
            name = os.path.basename(path)
            if name == "INDEX.md":
                continue
            fm, _ = split_front_matter(open(path, encoding="utf-8").read(), source=path)
            for c in fm.get("cast", []) or []:
                all_chars.add(normalize_cast_name(c))
    # 第二遍：构造 entry，含 present（基于 html 真实出现）
    for src_dir in sources:
        if not os.path.isdir(src_dir):
            continue
        for path in glob.glob(os.path.join(src_dir, "*.md")):
            name = os.path.basename(path)
            if name == "INDEX.md":
                continue
            fm, body = split_front_matter(open(path, encoding="utf-8").read(), source=path)
            if not fm.get("cast"):          # 跳过扩写副本等非正章
                continue
            n = fm.get("chapter")
            interlude_code = None
            if n is None:
                mm = re.match(r"(\d+)", name)
                n = int(mm.group(1)) if mm else None
            elif isinstance(n, str) and n.startswith("I-"):
                # 插章：保留 "I-016" 作为 code，n 用 1000+ 偏移避开主线章号
                interlude_code = n
                mm = re.match(r"(\d+)", n[2:])   # 跳过 "I-" 前缀再取数字
                n = 1000 + int(mm.group(1)) if mm else None
            else:
                n = int(n)
            if n is None:
                continue
            html_text = render_body(body)
            declared = [normalize_cast_name(c) for c in (fm.get("cast", []) or [])]
            entry = {
                "n": n,
                "interlude": interlude_code,    # None for 主线，"I-016" for 插章
                "insert_after": fm.get("insert_after"),
                "season": fm.get("season", 1),
                "title": str(fm.get("title", "")).strip(),
                "cast": declared,
                "pov": fm.get("pov", ""),
                "hook": str(fm.get("hook", "")).strip(),
                "html": html_text,
                "present": compute_present(html_text, declared, all_chars),
            }
            # 同回多文件时，优先 frontmatter 字段更全的（有 hook 的）
            prev = by_n.get(n)
            if prev is None or (not prev["hook"] and entry["hook"]):
                by_n[n] = entry
    _fill_placeholders(by_n)  # 给已知缺口章号填 placeholder（让 index.html 视觉连续）
    return [by_n[n] for n in sorted(by_n)]


# ---------- 占位补充 ----------
#
# 按 docs/problematic_chapters.md 调研结果，有 144 个章号属于"缺口"：
#   * ch791-793 = §七.1 第二道墙封档（3 章）
#   * ch857-997 = "等治本样品，严禁写"（141 章）
# 为让 GitHub Pages 上 index.html 的章节目录在视觉上不出现断层，
# 在 chronicle.json 里给这些章号补一条 placeholder 条目。
# 前端 index.html 会给它们加 .pending class（半透明 + 标 "待开写"），
# 不允许点击跳转到 read.html，避免被误当真章阅读。
KNOWN_GAPS = {791, 792, 793} | set(range(857, 998))  # 144 章


def _fill_placeholders(by_n):
    for n in sorted(KNOWN_GAPS):
        if n in by_n:
            continue
        # season 跟随前一章；若无前一章则 fallback 1
        prev = max((k for k in by_n if k < n), default=None)
        prev_season = by_n[prev]["season"] if prev is not None else 1
        by_n[n] = {
            "n": n,
            "interlude": None,
            "insert_after": None,
            "season": prev_season,
            "title": "待开写",
            "cast": [],
            "pov": "",
            "hook": "本回按 §七.1 边界条件档暂留，等治本样品通过后开写。",
            "html": "<p><em>本章为待补占位（%d 回），详见 <code>docs/problematic_chapters.md §4.3</code>。</em></p>" % n,
            "present": [],
            "pending": True,
        }


# ---------- EPUB ----------

EPUB_CSS = """
body{font-family:"Noto Serif CJK SC",serif;line-height:1.9;margin:5% 6%;color:#1d1a17}
h1{font-size:1.4em;text-align:center;margin:1.6em 0 .2em;font-weight:600}
.meta{text-align:center;color:#8a7d63;font-size:.8em;margin-bottom:2em}
p{text-indent:2em;margin:.2em 0;text-align:justify}
hr.brk{border:0;text-align:center;margin:1.6em 0}
hr.brk:after{content:"\\2042";color:#b3a07a;font-size:1.1em}
"""

XHTML = ('<?xml version="1.0" encoding="utf-8"?>\n'
         '<!DOCTYPE html>\n'
         '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh"><head>'
         '<meta charset="utf-8"/><title>{title}</title>'
         '<link rel="stylesheet" type="text/css" href="style.css"/></head>'
         '<body>{body}</body></html>')


def build_epub(chapters, out_path):
    z = zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED)
    z.writestr("mimetype", "application/epub+zip", zipfile.ZIP_STORED)
    z.writestr("META-INF/container.xml",
               '<?xml version="1.0"?>\n<container version="1.0" '
               'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
               '<rootfiles><rootfile full-path="OEBPS/content.opf" '
               'media-type="application/oebps-package+xml"/></rootfiles></container>')
    z.writestr("OEBPS/style.css", EPUB_CSS)

    files = []
    for c in chapters:
        fn = "chap%03d.xhtml" % c["n"]
        body = ('<h1>第%d回 · %s</h1>%s'
                % (c["n"], html.escape(c["title"]), c["html"]))
        z.writestr("OEBPS/" + fn,
                   XHTML.format(title="第%d回 %s" % (c["n"], html.escape(c["title"])), body=body))
        files.append((fn, c))

    manifest = '\n'.join('<item id="c%03d" href="%s" media-type="application/xhtml+xml"/>' % (c["n"], fn)
                         for fn, c in files)
    spine = '\n'.join('<itemref idref="c%03d"/>' % c["n"] for _, c in files)
    today = datetime.date.today().isoformat()
    opf = ('<?xml version="1.0" encoding="utf-8"?>\n'
           '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid">'
           '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
           '<dc:identifier id="bookid">urn:uuid:%s</dc:identifier>'
           '<dc:title>%s</dc:title><dc:creator>%s</dc:creator>'
           '<dc:language>zh-CN</dc:language>'
           '<meta property="dcterms:modified">%sT00:00:00Z</meta></metadata>'
           '<manifest>'
           '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
           '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>'
           '<item id="css" href="style.css" media-type="text/css"/>'
           '%s</manifest><spine toc="ncx">%s</spine></package>'
           % (BOOK_ID, html.escape(BOOK_TITLE), html.escape(BOOK_AUTHOR), today, manifest, spine))
    z.writestr("OEBPS/content.opf", opf)

    navlis = '\n'.join('<li><a href="%s">第%d回 %s</a></li>' % (fn, c["n"], html.escape(c["title"]))
                       for fn, c in files)
    z.writestr("OEBPS/nav.xhtml",
               XHTML.format(title="目录",
                            body='<nav epub:type="toc" xmlns:epub="http://www.idpf.org/2007/ops">'
                                 '<h1>目录</h1><ol>%s</ol></nav>' % navlis))

    points = '\n'.join('<navPoint id="n%03d" playOrder="%d"><navLabel><text>第%d回 %s</text></navLabel>'
                       '<content src="%s"/></navPoint>'
                       % (c["n"], i + 1, c["n"], html.escape(c["title"]), fn)
                       for i, (fn, c) in enumerate(files))
    z.writestr("OEBPS/toc.ncx",
               '<?xml version="1.0" encoding="utf-8"?>\n'
               '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">'
               '<head><meta name="dtb:uid" content="urn:uuid:%s"/></head>'
               '<docTitle><text>%s</text></docTitle><navMap>%s</navMap></ncx>'
               % (BOOK_ID, html.escape(BOOK_TITLE), points))
    z.close()


# ---------- main ----------

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--include-drafts", action="store_true",
                   help="也读 seasons/*/drafts/ 下的草稿（默认只读 chronicle/）")
    args = p.parse_args()
    os.makedirs(DOCS, exist_ok=True)
    chapters = collect(include_drafts=args.include_drafts)
    with open(os.path.join(DOCS, "chronicle.json"), "w", encoding="utf-8") as f:
        json.dump(chapters, f, ensure_ascii=False, separators=(",", ":"))
    epub_path = os.path.join(DOCS, BOOK_TITLE + ".epub")
    build_epub(chapters, epub_path)
    # 给前端一个固定文件名的副本，省得 URL 编码中文
    build_epub(chapters, os.path.join(DOCS, "book.epub"))
    print("built %d chapters -> docs/chronicle.json + epub" % len(chapters))


if __name__ == "__main__":
    main()
