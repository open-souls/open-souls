#!/usr/bin/env bash
# 全量预检: 古言/重romance/那种/锚点bloat签名/souls_read/line/cast — 用法: bash tools/prescreen.sh 081 082 ...
G2='未曾|须臾|眸|踱|唯有|缓缓|半晌|方才|亦是|已然|慢条斯理|心下|正欲|若无其事|坐于|搁于|铺在掌心|细细|翌日|尚未|立于|归鞘|皆未|直至|步履|走至|未作|一无所获|内息|蹙眉|誊抄|独辟|虬劲|手执|抬眸|笑意从容|置于|各归|另置|日色|眼皮未抬|约莫|寂然|已近|悄然'
HEAVY='眸色|眸光|须臾|慢条斯理|抬眸|若无其事|笑意从容|坐于原|铺在掌心|缓缓道|神色微凝'
for c in "$@"; do
  fn=$(ls seasons/01-xianxia/chronicle/$c-*.md 2>/dev/null); [ -z "$fn" ] && { echo "ch$c: no file"; continue; }
  bd(){ awk 'BEGIN{fm=0} /^---$/{fm++; next} fm>=2' "$fn"; }
  gy=$(bd|grep -oE "$G2"|wc -l); hv=$(bd|grep -oE "$HEAVY"|wc -l); nz=$(bd|grep -oc '是[^，。]*的那种')
  bl=$(bd|awk '{if(length($0)>80 && index($0,"且")>0 && index($0,"的那种")>0)print}'|wc -l)
  fp=$(grep -c '反派' "$fn")
  shipsblk(){ awk '/^ships:/{p=1;next} p&&/^[a-z_]+:/{exit} p' "$fn"; }
  sc_chain=$(shipsblk|grep -cE 'ch[0-9]{3}\+ch[0-9]{3}')
  sc_qie=$(shipsblk|awk '{n=gsub(/且/,"且"); if(n>1)print}'|wc -l)
  sb=$((sc_chain + sc_qie))
  st=$( [ -f prompts/.results/ch$c.md ] && head -1 prompts/.results/ch$c.md|tr -d '\r' || echo "no-verdict")
  sc=$( [ -f prompts/.results/ch$c.md ] && grep -m1 '^score:' prompts/.results/ch$c.md|tr -d '\r' )
  sr=$( [ -f prompts/.results/ch$c.md ] && grep -m1 souls_read prompts/.results/ch$c.md|tr -d '\r'|sed 's/.*souls_read://'|cut -c1-22 )
  flag=""; [ "$gy" -gt 8 ] && flag+="[古言>8]"; [ "$hv" -gt 0 ] && flag+="[romance$hv]"; [ "$nz" -gt 2 ] && flag+="[那种>2]"; [ "$bl" -gt 0 ] && flag+="[bloat$bl]"; [ "$fp" -gt 0 ] && flag+="[反派$fp]"; [ "$sb" -gt 0 ] && flag+="[ships臃肿$sb]"
  echo "ch$c ($(basename "$fn")): $st $sc | pov:$(grep -m1 '^pov:' "$fn"|tr -d '\r'|sed 's/pov://') line:$(grep -m1 '^line:' "$fn"|tr -d '\r'|sed 's/line://') | 古言$gy heavy$hv 那种$nz bloat$bl | souls:$sr ${flag:-✓clean}"
done
