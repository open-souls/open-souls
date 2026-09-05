# 盲读结果汇总

时间：2026-09-04
方法：5 份模型代理盲读（L1）+ 真人 sub-agent / 真人读者 ≥1 份（L2）；只读盲读包正文。
边界：本结果不等同于真人读者反馈；L1 < 5 份或 L2 < 1 份时禁止聚合判断。

effective_n = 0 (L2-real=0 + L2-reader=0 + L1-effective=0)
diversity_score = 0.167 (flag) / 1.0 (drop) / 1.0 (reason)
echo_panel = True ， L1 复读嫌疑高时 L1 不计入 effective_n
provenance = schema_version=2 / model_id / reading_log / pack_hash are required for new records

current pack_hash = f64e35b7cac0c896

### 真人文件名被降级为 L1（必须先修 isolation 才能进 L2）
- reader-1-真人.json: L2-real source missing modern provenance: reader-1-真人.json

L2 = 0。真人证据缺失；任何「读者会追 / 爆款」判断禁止。

## 1. 模型代理（L1）热点
### 弃读热点
- mid_a 506：1 人
- mid_a 504：1 人
- mid_a 505：1 人
- mid_b 682：1 人
- mid_a 502：1 人
- open 4：1 人

### 关系追问热点
- 林彻×林夙：1 人
- 林夙×苏挽：1 人
- 林夙×阿湄：1 人
- 苏挽×林窈：1 人
- 林崇×林夙：1 人
- 阿湄×苏挽：1 人

### 50 章留存
- 愿意：1 / 6

### 三类问题命中
- passive_chain：5 人
- info_not_action：6 人
- smart_drop：0 人

## 2. 升级与下一轮改稿顺序（按 effective_n 阈值）
- passive_chain：L1 命中 5 人；L2 命中 0 人（L1 复读嫌疑高，仅作方向记录，不升级）
- info_not_action：L1 命中 6 人；L2 命中 0 人（L1 复读嫌疑高，仅作方向记录，不升级）
- smart_drop：L1 命中 0 人；L2 命中 0 人（L1 复读嫌疑高，仅作方向记录，不升级）
- 中段包 50 章留存意愿不达标，结构任务。

下一轮建议顺序：
1. 处理升级项。
2. 处理关系追问热点。
3. 处理弃读热点章节。
4. 再次生成盲读包 + 重新校验 isolation / diversity，确认未恶化的方向。

## 4. 盲读包指纹（f64e35b7cac0c896）
复测必须沿用同一指纹；想刷新读者记忆时用 `regenerate --new-seed`。
