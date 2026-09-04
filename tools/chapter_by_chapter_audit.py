# -*- coding: utf-8 -*-
"""逐章生成晋江连载审读账本，供人工改稿使用。"""
from pathlib import Path
from collections import Counter
import json
import re

ROOT = Path(__file__).resolve().parents[1]
CHRON = ROOT / "seasons" / "01-xianxia" / "chronicle"
OUT = ROOT / "reports" / "jinjiang-r20"
END = re.compile(r"^---\s*$", re.M)
HAN = re.compile(r"[一-鿿]")
DIALOGUE = re.compile(r'[「『“"]')
ACTION = re.compile(r"走|来|去|问|答|拿|放|递|收|拆|开|关|砍|挡|写|烧|抬|转身|停|进|出|抓|握|见|听|闻|落|动")
ENDING_ACTION = re.compile(r"走|来|去|问|答|拿|放|递|收|拆|开|关|砍|挡|写|烧|抬|转身|停|进|出|抓|握|见|听|闻|落|动|翻|掀|按|推|拉|伸|签|捡|回头|转身")
ENDING_INTENT = re.compile(r"明日|明天|下一回|下回|还要|要去|要问|要见|必须|等着|会来|尚未|未曾|没(?:有)?(?:再)?|不(?:再|会|肯)|不知道|不知")
ENDING_EVIDENCE = re.compile(r"忽然|却|还在|门外|有人|脚步|声音|血|信|字|落款|敲|来人|名字|影子|刀柄|门缝|灯火")
ENDING_OBJECT = re.compile(r"书|药|碗|碟|灯|火|门|窗|院|巷|路|柴|纸|刀|锅|粥|水|土|糖|笔|信|牌|柜|绳|镜|影|袖|袂|帘|风|灯芯|布袋|石|木|绳|门缝")
EDITORIAL = re.compile(r"下一章|切(?:苏挽|林夙|叶观澜|林窈|阿湄|林叙)|余项同上|编辑|生成稿|维度[一二三四五六七八九0-9]")
FORMULA = re.compile(r"方向(?:朝|朝着|落在|落下)|不必替上一世|不必替(?:谁|自己)|的(?:来处|方式|方向)是")
FILLER = re.compile(r"(?:屋里|院中|院子里|院里|屋内|屋子里|厅里|廊下|廊里|门外|四周|周遭|巷子里|空气里?|夜|风)(?:.{0,3})(?:很|十分|格外|异常|死一般)?(?:安静|寂静|静悄悄|静得|空荡|空无一人|很静|深)")

def split(text):
    marks = list(END.finditer(text))
    if len(marks) < 2:
        return "", text
    return text[marks[0].end():marks[1].start()], text[marks[1].end():]

def clean(body):
    body = re.sub(r"^#.*$", "", body, flags=re.M)
    body = body.replace("---", "")
    return body.strip()

def chapter_num(path, fm):
    m = re.search(r"^chapter:\s*(\d+)", fm, re.M)
    return int(m.group(1)) if m else int(re.match(r"(\d+)-", path.name).group(1))

def title(fm, path):
    m = re.search(r"^title:\s*(.+)$", fm, re.M)
    return m.group(1).strip() if m else path.stem

def audit(path):
    raw = path.read_text(encoding="utf-8")
    fm, body = split(raw)
    body = clean(body)
    paragraphs = [x.strip() for x in body.split("\n\n") if x.strip()]
    sentences = [x.strip() for x in re.split(r"[。！？]", body) if HAN.search(x)]
    starts = [x[:6] for x in sentences if len(x) >= 6]
    repeated = [k for k,v in Counter(sentences).items() if len(k) >= 8 and v >= 2]
    ending = next((x for x in reversed(body.splitlines()) if x.strip()), "")
    ending_window = "\n\n".join(paragraphs[-2:]) if paragraphs else ending
    ending_question = "？" in ending_window or "?" in ending_window
    ending_intent = bool(ENDING_INTENT.search(ending_window))
    ending_evidence = bool(ENDING_EVIDENCE.search(ending_window))
    ending_action = bool(ENDING_ACTION.search(ending_window))
    ending_object = bool(ENDING_OBJECT.search(ending_window))
    ending_tail = "".join(paragraphs[-1:])[-40:] if paragraphs else ending
    # Strong hooks: future-intent, evidence-noun phrase, or question. Marginal but acceptable: action + object.
    hook = ending_question or ending_intent or ending_evidence or (ending_action and ending_object)
    editor_hits = EDITORIAL.findall(body)
    formula_hits = FORMULA.findall(body)
    filler_hits = FILLER.findall(body)
    action_count = len(ACTION.findall(body))
    dialogue_count = len(DIALOGUE.findall(body))
    chars = len(HAN.findall(body))
    issues=[]
    if chars < 1500: issues.append("短章")
    if editor_hits: issues.append("编辑标记")
    if len(formula_hits) >= 3: issues.append("公式回环")
    if len(repeated) >= 3: issues.append("句子重复")
    if chars >= 1500 and action_count < 8: issues.append("推进偏弱")
    if not hook: issues.append("章尾弱")
    if filler_hits: issues.append("填充描写")
    if len(starts) >= 20 and len(set(starts))/len(starts) < .62: issues.append("开句同构")
    return {
      "chapter": chapter_num(path,fm), "file": str(path.relative_to(ROOT)), "title": title(fm,path),
      "chars": chars, "paragraphs": len(paragraphs), "sentences": len(sentences),
      "dialogue_marks": dialogue_count, "action_verbs": action_count,
      "ending": ending, "hook_signal": hook, "editorial_hits": editor_hits,
      "formula_hits": formula_hits, "filler_hits": filler_hits, "repeated_sentences": repeated[:12],
      "issue_tags": issues,
      "binge_score": min(10, max(0, 10 - len(issues) - (0 if hook else 1) + (1 if dialogue_count >= 4 else 0) + (1 if action_count >= 12 else 0)))
    }

rows=[]
for path in sorted(CHRON.glob("*.md")):
    if path.name in {"INDEX.md", "test_write.md"}: continue
    rows.append(audit(path))
rows.sort(key=lambda x:x["chapter"])
summary={
  "chapters": len(rows), "range": [rows[0]["chapter"], rows[-1]["chapter"]],
  "issue_counts": dict(Counter(tag for r in rows for tag in r["issue_tags"])),
  "avg_chars": round(sum(r["chars"] for r in rows)/len(rows),1),
  "avg_binge_score": round(sum(r["binge_score"] for r in rows)/len(rows),2),
  "low_score_chapters": [r["chapter"] for r in rows if r["binge_score"] <= 5],
  "editorial_leak_chapters": [r["chapter"] for r in rows if "编辑标记" in r["issue_tags"]],
  "formula_loop_chapters": [r["chapter"] for r in rows if "公式回环" in r["issue_tags"]],
  "short_chapters": [r["chapter"] for r in rows if "短章" in r["issue_tags"]],
}
data={"method":"deterministic whole-corpus read-through; human literary acceptance still required","summary":summary,"chapters":rows}
OUT.mkdir(parents=True, exist_ok=True)
(OUT/"chapter-by-chapter-audit.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
md=["# 逐章晋江上瘾审读账本","","本账本覆盖当前 chronicle 的每一回。它是结构化初审，不把规则分数冒充真人试读。","",f"- 章节：{summary['chapters']}（第{summary['range'][0]}回至第{summary['range'][1]}回）",f"- 平均正文汉字：{summary['avg_chars']}",f"- 平均上瘾初筛分：{summary['avg_binge_score']}/10",""]
md += ["## 阻塞分布"]
for k,v in sorted(summary["issue_counts"].items(),key=lambda x:(-x[1],x[0])): md.append(f"- {k}：{v} 回")
md += ["","## 改稿顺序","","1. 先清掉编辑标记和公式回环。","2. 再修短章，补的是选择、阻力、代价或新信息，不是空描写。","3. 再按 50 回为一组检查章尾钩子和情感线升降。","4. 最后做 3 至 5 名真实目标读者盲读，确认上瘾感。","","## 每回摘要"]
for r in rows:
 tags="、".join(r["issue_tags"]) or "通过初筛"
 md.append(f"- 第{r['chapter']}回《{r['title']}》：{r['chars']}字；钩子={'有' if r['hook_signal'] else '弱'}；问题={tags}；末句：{r['ending']}")
(OUT/"chapter-by-chapter-audit.md").write_text("\n".join(md)+"\n",encoding="utf-8")
print(json.dumps(summary,ensure_ascii=False,indent=2))
ENDING_OBJECT = re.compile(r"书|药|碗|碟|灯|火|门|窗|院|巷|路|柴|纸|刀|锅|粥|水|土|糖|笔|信|牌|柜|碗|绳|镜|影|袖|袂|门|帘|风|刀柄|灯芯|布袋")
