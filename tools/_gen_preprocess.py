"""Generator: writes tts_preprocess.py using only ASCII in this source."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')

NL = chr(10)
DQ = chr(34)   # "
SQ = chr(39)   # '

def q(s):
    return DQ + s + DQ

def sq(s):
    return SQ + s + SQ

# chinese chars we need
yi   = chr(19968)   # 一
er   = chr(20108)   # 二
san  = chr(19977)   # 三
si   = chr(22235)   # 四
wu   = chr(20116)   # 五
liu  = chr(20845)   # 六
qi   = chr(19971)   # 七
ba   = chr(20843)   # 八
jiu  = chr(20061)   # 九
shi  = chr(21313)   # 十
bai  = chr(30334)   # 百
qian = chr(20191)   # 千
wan  = chr(19975)   # 万
yi2  = chr(20159)   # 亿
ling = chr(38646)   # 零
ju   = chr(12290)   # 。
dou  = chr(65292)   # ，

lines = [
    '# -*- coding: utf-8 -*-',
    'import re, sys',
    'if sys.stdout.encoding != ' + q('utf-8') + ':',
    '    sys.stdout.reconfigure(encoding=' + q('utf-8') + ')',
    '',
    '_U = [' + q('') + ', ' + q(yi) + ', ' + q(er) + ', ' + q(san) + ', ' + q(si) + ',',
    '      ' + q(wu) + ', ' + q(liu) + ', ' + q(qi) + ', ' + q(ba) + ', ' + q(jiu) + ']',
    '_L = [' + q('') + ', ' + q(shi) + ', ' + q(bai) + ', ' + q(qian) + ']',
    '_B = [' + q('') + ', ' + q(wan) + ', ' + q(yi2) + ']',
    '',
    'def _n2zh(n):',
    '    if n == 0: return ' + q(ling),
    '    res, s = ' + q('') + ', str(n)',
    '    ln = len(s)',
    '    for i, ch in enumerate(s):',
    '        d = int(ch); pos = ln - i - 1',
    '        bi, si = pos // 4, pos % 4',
    '        if d: res += _U[d] + _L[si]',
    '        else:',
    '            if res and res[-1] != ' + q(ling) + ': res += ' + q(ling),
    '        if si == 0 and bi > 0 and n // (10**(bi*4)) % 10000 != 0:',
    '            res += _B[bi]',
    '    res = res.rstrip(' + q(ling) + ')',
    '    if res.startswith(' + q(yi + shi) + '): res = res[1:]',
    '    return res',
    '',
    'def _r(m): return _n2zh(int(m.group()))',
    '',
    '# char classes built at runtime',
    '_OQ = ' + q('[') + ' + chr(0x300C) + chr(0x300E) + chr(0x201C) + chr(0x201D) + ' + q(']'),
    '_CQ = ' + q('[') + ' + chr(0x300D) + chr(0x300F) + ' + q(']'),
    '_DQ = ' + q('[') + ' + chr(0x00B7) + chr(0x30FB) + ' + q(']'),
    '_EM = chr(0x2014)',
    '_EL = chr(0x2026)',
    '',
    'def _dlg(t):',
    '    pat = ' + q('[') + ' + chr(0x300C) + chr(0x300E) + chr(0x201C) + ' + q(']'),
    '    return bool(re.match(pat, t))',
    '',
    'def _para(p):',
    '    s = re.sub(_OQ, ' + q('') + ', p)',
    '    s = re.sub(_CQ, ' + q('') + ', s)',
    '    s = re.sub(_DQ, ' + q('') + ', s)',
    '    s = re.sub(' + sq('[0-9]+') + ', _r, s)',
    '    s = re.sub(_EM + ' + sq('{1,2}') + ', ' + sq('<break time=' + DQ + '500ms' + DQ + '/>') + ', s)',
    '    s = re.sub(_EL + ' + sq('{1,2}') + ', ' + sq('<break time=' + DQ + '700ms' + DQ + '/>') + ', s)',
    '    clean = len(re.sub(' + q('<[^>]+>') + ', ' + q('') + ', s).strip())',
    '    if clean <= 8 and s.rstrip().endswith(' + q(ju) + ') and not _dlg(p):',
    '        s = (' + sq('<break time=' + DQ + '400ms' + DQ + '/>')
        + ' + ' + sq('<prosody rate=' + DQ + '-10%' + DQ + '>') + ' + s',
    '             + ' + sq('</prosody><break time=' + DQ + '400ms' + DQ + '/>') + ')',
    '    return s',
    '',
    'NL = chr(10)',
    '',
    'def _join(paras, orig):',
    '    if not paras: return ' + q(''),
    '    out = []',
    '    for i, p in enumerate(paras):',
    '        out.append(p)',
    '        if i < len(paras) - 1:',
    '            br = (' + sq('<break time=' + DQ + '200ms' + DQ + '/>') + ' if (_dlg(orig[i]) or _dlg(orig[i+1]))',
    '                  else ' + sq('<break time=' + DQ + '350ms' + DQ + '/>' ) + ')',
    '            out.append(br)',
    '    return NL.join(out)',
    '',
    'def preprocess(raw):',
    '    lines = raw.strip().splitlines()',
    '    if not lines: return ' + q('<speak></speak>'),
    '    t0 = lines[0].strip()',
    '    body = NL.join(lines[1:])',
    '    pat = (' + q('^(') + chr(31532) + q('[0-9]+') + chr(22238) + q(')') + ' + ' + sq('[') + ' + chr(0x00B7) + chr(0x30FB) + sq(' ') + ' + ' + sq(']+') + ' + ' + q('(.+)$') + ')',
    '    m = re.match(pat, t0)',
    '    if m:',
    '        num = re.sub(' + sq('[0-9]+') + ', _r, m.group(1))',
    '        ttl = m.group(2).strip()',
    '        thead = (' + sq('<prosody rate=' + DQ + 'slow' + DQ + '>') + ' + num',
    '                 + ' + q(dou) + ' + ttl + ' + q(ju),
    '                 + ' + sq('</prosody><break time=' + DQ + '1500ms' + DQ + '/>') + ')',
    '    else:',
    '        thead = re.sub(' + sq('[0-9]+') + ', _r, t0)',
    '    paras = [p.strip() for p in re.split(' + sq('[' + chr(10) + ']{2,}') + ', body) if p.strip()]',
    '    ssml = [_para(p) for p in paras]',
    '    return ' + q('<speak>') + ' + thead + NL + _join(ssml, paras) + NL + ' + q('</speak>'),
    '',
    'if __name__ == ' + q('__main__') + ':',
    '    sample = (',
    '        ' + q(chr(31532) + '1' + chr(22238) + ' ' + chr(183) + ' ' + chr(36864) + chr(23130) + chr(20070)) + ',',
    '        ' + q(chr(21306) + chr(22530) + chr(37324) + chr(20919) + chr(12290)) + ',',
    '        ' + q(chr(19981) + chr(27490) + chr(26159) + chr(38634) + chr(30340) + chr(32531) + chr(25925) + chr(12290)) + ',',
    '        chr(0x300C) + ' + q(chr(31614) + chr(20102) + chr(23427) + chr(65292) + chr(20320) + chr(36824) + chr(26159) + chr(26519) + chr(23478) + chr(20154) + chr(12290)) + ' + chr(0x300D),',
    '        chr(0x300C) + ' + q(chr(26159) + chr(25105) + chr(8212) + chr(8212) + chr(36864) + chr(20320) + chr(20204) + chr(12290)) + ' + chr(0x300D)',
    '    )',
    '    print(preprocess(' + q(chr(10)) + '.join(sample)))',
]

out = os.path.join(os.path.dirname(__file__), 'tts_preprocess.py')
with open(out, 'w', encoding='utf-8') as f:
    f.write(NL.join(lines) + NL)
print('wrote', out)
