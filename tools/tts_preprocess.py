# -*- coding: utf-8 -*-
# TTS 预处理：将章节原文转为 edge-tts 兼容 SSML。
#
# ── edge-tts (rany2) 实际支持的 SSML ────────────────────────────
#   ✅ <speak> / <voice> / <prosody rate pitch volume>
#   ❌ <break>、<emphasis>、<mstts:express-as>（会导致整章无声）
#   ❌ 每章超过 2 个 <prosody> 元素（超过也无声）
#   ❌ <mstts:*> 系列（Azure Cognitive Services 专有，Edge TTS 不支持）
#
# ── 正确的情感增强策略：不生成 SSML，生成更好的文本 ────────────
#   控制表达力的最强杠杆是标点和句式，而非 SSML 标签：
#
#   | 效果         | 写法                              |
#   |-------------|-----------------------------------|
#   | 停顿/呼吸    | ……  —— → ……  段落分行              |
#   | 犹豫/迟疑    | 她……停了一下。 / 他，没说话。       |
#   | 情感加重     | 短句独立成行。反复。              |
#   | 对话语气     | 句末标点选择（？！。……）           |
#   | 叙述节奏     | 长句拆短、主谓拆开               |
#
#   LLM 作为"语音编译器"：把书面文字改写成口语节奏的文本，
#   再交给 Edge TTS，效果远胜于堆 SSML 标签。
#   （ElevenLabs 级别的质感 60-70% 来自文本预处理，非参数调优）
#
# 当前策略：章节标题用 <prosody rate="slow">（1个 prosody 配额），
# 正文纯文本，停顿靠中文标点 + 段落换行，破折号转省略号制造停顿感。
import re, sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

_U = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九']
_L = ['', '十', '百', '千']
_B = ['', '万', '亿']

def _n2zh(n):
    if n == 0: return '零'
    res, s = '', str(n)
    ln = len(s)
    for i, ch in enumerate(s):
        d = int(ch); pos = ln - i - 1
        bi, si = pos // 4, pos % 4
        if d: res += _U[d] + _L[si]
        else:
            if res and res[-1] != '零': res += '零'
        if si == 0 and bi > 0 and n // (10**(bi*4)) % 10000 != 0:
            res += _B[bi]
    res = res.rstrip('零')
    if res.startswith('一十'): res = res[1:]
    return res

def _r(m): return _n2zh(int(m.group()))

NL  = chr(10)
_OQ = chr(91) + chr(0x300C) + chr(0x300E) + chr(0x201C) + chr(0x201D) + chr(93)
_CQ = chr(91) + chr(0x300D) + chr(0x300F) + chr(93)
_DQ = chr(91) + chr(0x00B7) + chr(0x30FB) + chr(93)
_EM = chr(0x2014)   # EM DASH ——
_EL = chr(0x2026)   # 省略号 ……
_EL2 = _EL + _EL    # 双省略号（停顿感）

P_SLOW       = '<prosody rate=' + chr(34) + 'slow' + chr(34) + '>'
P_SLOW_CLOSE = '</prosody>'

def _para(p):
    s = re.sub(_OQ, '', p)
    s = re.sub(_CQ, '', s)
    s = re.sub(_DQ, '', s)
    s = re.sub('[0-9]+', _r, s)
    s = re.sub(_EM + '{1,2}', _EL2, s)   # 破折号 → 省略号（停顿感）
    return s

def preprocess(raw):
    lines = raw.strip().splitlines()
    if not lines: return '<speak></speak>'
    t0 = lines[0].strip()
    body = NL.join(lines[1:])
    pat = (chr(94) + chr(40) + chr(31532) + '[0-9]+' + chr(22238) + chr(41)
           + chr(91) + chr(0x00B7) + chr(0x30FB) + chr(32) + chr(93) + chr(43)
           + chr(40) + '.+' + chr(41) + chr(36))
    m = re.match(pat, t0)
    if m:
        num   = re.sub('[0-9]+', _r, m.group(1))
        ttl   = m.group(2).strip()
        thead = P_SLOW + num + '，' + ttl + '。' + P_SLOW_CLOSE
    else:
        thead = re.sub('[0-9]+', _r, t0)
    sep   = chr(91) + NL + chr(93) + '{2,}'
    paras = [_para(p.strip()) for p in re.split(sep, body) if p.strip()]
    body_text = NL.join(paras)
    return '<speak>' + thead + NL + NL + body_text + NL + '</speak>'

if __name__ == '__main__':
    parts = [
        chr(31532)+'1'+chr(22238)+' '+chr(183)+' '+chr(36864)+chr(23130)+chr(20070),
        chr(21306)+chr(22530)+chr(37324)+chr(20919)+chr(12290),
        '',
        chr(19981)+chr(27490)+chr(26159)+chr(38634)+chr(30340)+chr(32531)+chr(25925)+chr(12290),
        '',
        chr(0x300C)+chr(31614)+chr(20102)+chr(23427)+chr(65292)+chr(20320)+chr(36824)+chr(26159)+chr(26519)+chr(23478)+chr(20154)+chr(12290)+chr(0x300D),
        '',
        chr(0x300C)+chr(26159)+chr(25105)+chr(8212)+chr(8212)+chr(36864)+chr(20320)+chr(20204)+chr(12290)+chr(0x300D),
    ]
    print(preprocess(NL.join(parts)))
