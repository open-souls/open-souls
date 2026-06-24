"""Anthropic call with scene-weighted model routing. Mock mode = zero tokens, full loop."""
import os, json, re, urllib.request

TIERS = {"light": "claude-haiku-4-5", "heavy": "claude-sonnet-4-6", "peak": "claude-opus-4-8"}


def route(w):
    return TIERS["peak"] if w >= 8 else TIERS["heavy"] if w >= 5 else TIERS["light"]


def complete(system, user, scene_weight=3, max_tokens=1100):
    if os.environ.get("VILLAGE_MOCK") == "1" or not os.environ.get("ANTHROPIC_API_KEY"):
        return _mock(user)
    body = json.dumps({
        "model": route(scene_weight), "max_tokens": max_tokens,
        "system": system, "messages": [{"role": "user", "content": user}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=body,
        headers={"content-type": "application/json",
                 "x-api-key": os.environ["ANTHROPIC_API_KEY"],
                 "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.load(r)
    return "".join(b.get("text", "") for b in data.get("content", []))


def parse_json(text):
    text = re.sub(r"```(json)?", "", text).strip()
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("LLM 没返回 JSON:\n" + text[:300])
    return json.loads(m.group(0))


def _mock(user):
    cast = re.findall(r"姓名: (\S+?)（", user)
    a = cast[0] if cast else "甲"
    b = cast[1] if len(cast) > 1 else a

    if "【策划这一回" in user:
        return json.dumps({
            "hook": "她转身时，他终于把那句话说出口——却没人听见",
            "payoff": "憋了三回的真心，终于露了半张脸",
            "contrast": f"{a} 嘴上不在乎、心里早数着对方的脚步声",
            "trope": "slow burn（西）+ デレ瞬间（日）",
            "pov": a, "turn": "第三个人推门进来，时机最坏",
        }, ensure_ascii=False)

    if "【按方案写正文】" in user:
        newcomers = re.findall(r"新登场\(本季第一次\): (\S+)", user)
        incarn = {n: ("刚搬来的陌生人" if n in newcomers else "城里的老面孔") for n in cast}
        strong = "【上一稿被打回" in user
        if strong:
            body = (f"{a}没回头。她知道只要回头，就守不住那句『我无所谓』。"
                    f"{b}在身后开了口，声音轻得像怕惊动什么。她脚步顿了半秒——"
                    f"就这半秒，把她所有的逞强出卖干净。门在这时被人推开，"
                    f"风灌进来，把那句没说完的话吹散。她终于回头，却只看见空了的门口，"
                    f"和地上那盏倒了的灯——那盏灯，那晚之后再没亮过。")
            title = f"{a}回头那半秒"
        else:
            body = (f"{a}和{b}在便利店遇到了。两个人聊了几句，{b}说了些关心的话，"
                    f"{a}也回应了。气氛还不错，谁都没说什么过分的话。夜就这样平静地过去了。")
            title = f"{a}与{b}的一个晚上"
        return json.dumps({
            "chapter_title": title, "chapter": body, "incarnations": incarn,
            "updates": [{"from": a, "to": b, "affection_delta": 1, "trust_delta": -1,
                         "tension_delta": 2, "feeling": "逞强被看穿了"}],
            "memories": [{"who": a, "text": f"在{b}面前又没守住那句逞强", "importance": 7}],
            "reflection": None,
        }, ensure_ascii=False)

    if "【文笔检阅" in user:  # 独立编辑复读：mock 一律放行
        return json.dumps({"verdict": "pass", "problems": []}, ensure_ascii=False)

    if "【文笔重写" in user:  # 只改文笔层：mock 原样返回正文
        chap = user.split("正文：", 1)[-1].rsplit("只输出 JSON", 1)[0].strip()
        return json.dumps({"chapter": chap}, ensure_ascii=False)

    if "【审校" in user:
        chap = user.split("正文：", 1)[-1]
        if "再没亮过" in chap:
            return json.dumps({"scores": {"钩子": 2, "爽痛": 2, "反差": 2, "拉扯": 2,
                               "记忆点": 2, "代入": 1, "新": 1}, "total": 12,
                               "safe": True, "safety_reason": "", "fix": ""}, ensure_ascii=False)
        return json.dumps({"scores": {"钩子": 0, "爽痛": 1, "反差": 1, "拉扯": 1,
                           "记忆点": 1, "代入": 1, "新": 2}, "total": 7, "safe": True,
                           "safety_reason": "",
                           "fix": "结尾把话说圆了，没钩子。删掉收束，留一个没解开的悬，让逞强在最后一句被一个画面戳穿。"},
                          ensure_ascii=False)
    return "{}"
