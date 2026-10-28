# AI 工具使用记录

技术报告第四部分「团队分工与过程记录」要求说明 AI 参与了哪些环节，以及你如何审核、修改、验证。每次用 AI 辅助就在这里追加一行，写报告时直接整理。

| 日期 | 环节 | AI 做了什么 | 我做了什么审核 / 修改 / 验证 |
| --- | --- | --- | --- |
| 2026-10-24 | 首验代码骨架 | Claude 生成了 fanli/ 下的初版代码、示例题 p001、参考解、正确变体和两份错解、离线自测 | 待填写：逐行读懂代码；手动核对两份错解确实有错；在自己电脑上跑通并记录结果 |
| 2026-10-28 | 本机装环境、接入 LLM | Claude Code 在本机建虚拟环境、装依赖、跑 4 项离线自测与 p001 首验；因 DeepSeek 官方接口当日故障，改用 OpenRouter（deepseek/deepseek-chat-v3.1，OpenAI 兼容接口）；连跑 3 次首验 | 我本人把 OpenRouter 密钥填入 `.env`（已在 .gitignore，未提交）；确认 4 项自测通过、首验判定全对、提示来源为 llm、泄题检查通过 |
| 2026-10-28 | 扩充题库到 8 道 | Claude Code 起草 p002–p008 共 7 道题（题面、参考解、各 1 正确解 + 3 错解）；为 `fanli/strategy.py` 的 from_template 补 str、int_list_and_int 两种输入类型；每道题离线 + 真实 LLM 双路径跑 run_first_check 验证 | 我逐题过目参考解与 3 个错解、确认错解确有错；认可把 p005 字母表收窄为 a/b/A/B/空格（解决大字母表下大小写 bug 漏检）；确认 8 道全部判定与预期一致后，统一标 `reviewed_by_li: true` |
| 2026-10-28 | 对比实验（第 4 步） | Claude Code 新建 `fanli/baseline.py`（B0 纯 AI 审代码）与 `run_eval.py`；对 8 题 31 份代码跑本作品与 B0 两种方法，B0 的反例实际运行核对能否复现；生成 `results/eval_raw.jsonl` 与 `results/eval_summary.md` | 我查看汇总数字与失败案例清单；确认检出率两法打平属实（题目较简单），作品价值定位在反例可复现 + 最小化 + 生成器可验证 + 不泄题，不夸大 |
| 2026-10-28 | 演示与文档（第 5 步） | Claude Code 新建 `demo.py`（命令行逐层演示）；更新 README（评测结果段、demo/run_eval 用法）；补本记录 | 我跑了 demo 确认逐层输出正常；核对 README 数字与 eval_summary.md 一致、无学校信息 |
