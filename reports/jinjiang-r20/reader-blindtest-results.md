# 盲读结果汇总

时间：2026-09-04
方法：5 份模型代理盲读（L1）+ 真人 sub-agent / 真人读者 ≥1 份（L2）；只读盲读包正文。
边界：本结果不等同于真人读者反馈；L1 < 5 份或 L2 < 1 份时禁止聚合判断。

agent_n = 0 （读者端 sub-agent 模拟 + 研究端 sub-agent 审查，仅参考，不计 effective_n）
human_reader_n = 0 （真人读者 / 真人 sub-agent 有效 JSON 数，升级 effective_n 的真凭据）
platform_signal_n = 0 （晋江站内收藏 / 营养液 / 霸王票接入数；本季未接入）

effective_n = 0 (L2-real=0 + L2-reader=0 + L1-effective=0)
diversity_score = 1.0 (flag) / 1.0 (drop) / 1.0 (reason)
echo_panel = False ， L1 复读嫌疑高时 L1 不计入 effective_n
provenance = schema_version=2 / model_id / reading_log / pack_hash are required for new records

## pack_hash drift 警告（stale，不计入 effective_n）
- reader-1-真人.json: pack_hash=f64e35b7cac0c896 current=892df4c69d659635
- reader-1.json: pack_hash=f64e35b7cac0c896 current=892df4c69d659635
- reader-2.json: pack_hash=f64e35b7cac0c896 current=892df4c69d659635
- reader-3.json: pack_hash=f64e35b7cac0c896 current=892df4c69d659635
- reader-4.json: pack_hash=f64e35b7cac0c896 current=892df4c69d659635
- reader-5.json: pack_hash=f64e35b7cac0c896 current=892df4c69d659635

盲读包文本已变，旧 reader JSON 的 pack_hash 与当前不一致；
必须重新生成 reader JSON 才能恢复 L1 / L2 计数。

current pack_hash = 892df4c69d659635

L2 = 0。真人证据缺失；任何「读者会追 / 爆款」判断禁止。

## 1. 模型代理（L1）数据不足
L1 < 5 份，禁止聚合。

## 4. 盲读包指纹（892df4c69d659635）
复测必须沿用同一指纹；想刷新读者记忆时用 `regenerate --new-seed`。

注意：本轮有 pack_hash drift 条目（见顶部警告），旧 reader JSON 已不计入 effective_n。

## 5. 词表拦截清单 (per 5-reader-cross-workflow.md §9.5)
- 0 命中（本季 effective_n = 0，语言门禁尚未触发）
