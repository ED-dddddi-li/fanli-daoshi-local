# 反例导师：本机操作文档（给 Claude Code 和 Li 看）

Claude Code 在本目录启动时会自动读这份文件。Li 只需要说「按 CLAUDE.md 做第 N 步」。每一步做完都要停下，向 Li 汇报结果，等 Li 确认后再做下一步。

## 背景

- 这是 Li 参加「第八届全球校园人工智能算法精英大赛·AI+开源」的作品，单人参赛。
- **截止时间：2026-10-30 20:00 北京时间**，也就是 Li 本地（UTC-7）**10-30 早上 5:00**。计划在本地 10-29 晚上提交，所以最晚 10-29 中午要拿到评测数据。
- 作品做的事：学生交一个 Python 函数，工具先用 AI 读题写 Hypothesis 输入生成器，再用参考解自校验，然后做差分测试并缩减出最小反例，最后基于反例给三层提示，不泄露答案。代码结构见 README.md。
- 10-24 已在云端离线跑通：示例题 p001 的 3 份代码判定全部正确，`tests/` 的 4 项自测全部通过。**真实 LLM 这条路还没跑过。**

## 必须遵守

1. **不编造任何结果。** 报告里的数字只能来自 `results/` 里真实跑出来的文件。没跑完就写「未完成」。
2. **API 密钥只放在 `.env`。** 不打印、不写进任何其他文件、不提交到 git。由 Li 自己把密钥粘贴进 `.env`。
3. **参考解和「错解确实有错」需要 Li 人工确认。** AI 可以起草题目、参考解和错解，但每道题都要 Li 看过，并在 `meta.json` 里写上 `"reviewed_by_li": true` 之后，才能计入评测。
4. **每次 AI 辅助都要记一笔**，写进 `AI_USAGE.md`，包括做了什么、Li 怎么审核的。比赛规则要求在报告里说明这些。
5. **不出现学校名称、校徽或指导教师信息**，代码、README、题目、截图里都不行。
6. **控制 API 花费。** 每步结束后汇总 `results/token_usage.csv` 的 token 数。累计接近 100 元就停下来问 Li。
7. **只运行自建题目和同学自愿提交的代码。** 子进程隔离不是安全沙箱。
8. 运行环境是 Windows。命令默认用 PowerShell，路径不要写死成 Linux 格式。

## 第 1 步：装环境并跑离线自测（约 15 分钟）

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -q tests
python run_first_check.py problems/p001_second_largest
```

如果 PowerShell 不允许运行激活脚本，先执行 `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`。

**通过标准：** 4 项测试通过；首验输出最后一行是「全部判定与预期一致：是」。中文乱码时，先执行 `$env:PYTHONIOENCODING="utf-8"` 再跑一次。

## 第 2 步：接入真实 LLM 并跑首验（约 20 分钟）

1. 把 `.env.example` 复制为 `.env`，**由 Li 本人**填入 `LLM_API_KEY`。DeepSeek 用默认配置即可；用通义千问时，把 `LLM_BASE_URL` 和 `LLM_MODEL` 改成百炼的 OpenAI 兼容地址和模型名。
2. 执行 `python run_first_check.py problems/p001_second_largest`，连跑 3 次。
3. 向 Li 汇报以下内容：
   - 每次 `[生成器]` 日志：AI 写的策略表达式是什么，第几次通过的。
   - 3 份代码的判定是否仍然全对。
   - L1/L2/L3 提示的原文，提示来源是 `llm` 还是被拦截后退回的模板。
   - token 用量。

**通过标准：** 判定全对，提示来源是 `llm`。如果 AI 生成器 3 次都没通过，或者提示总被泄题检查拦截，不要换选题。把日志给 Li 看，然后修改 `fanli/strategy.py` 或 `fanli/hints.py` 里的提示词。

## 第 3 步：扩充题库到 8 道（约 2.5 小时，最重要的一步）

在 `problems/` 下新建 7 道题（p002–p008），格式和 p001 完全相同。每道题包含：

- `problem.md`：题面**自己写**，不复制 LeetCode 等平台的原文。要写清输入范围、是否可为空。
- `reference.py`：参考解，写得越直白越好。
- `solutions/`：1 份写法不同的正确解，加 3 份错解。错解要覆盖初学者的常见错误：差一、空输入、负数、重复元素、边界值、忘记处理大小写或空格。每份错解第一行用注释写明错在哪。
- `meta.json`：`func_name`、`input_template`、`expected_verdicts`、`reviewed_by_li`。

题型建议：整数列表 3 道，字符串 3 道，「列表 + 一个整数」2 道（比如 `count_greater(nums, k)`）。

`fanli/strategy.py` 里的 `from_template` 目前只支持 `int_list`，需要补上：

| type | 参数 | 生成的参数元组 |
| --- | --- | --- |
| `str` | `min_len`, `max_len`, `alphabet`（可选，默认小写字母、空格、大写字母） | `(字符串,)` |
| `int_list_and_int` | 列表的四个参数，加 `k_min`, `k_max` | `(列表, 整数)` |

补完后，对每道题运行 `run_first_check.py`，确认判定和 `expected_verdicts` 一致。不一致时**先检查错解是不是真的有错**，不要直接改预期。然后把 8 道题的列表给 Li 逐题确认，确认后标 `reviewed_by_li: true`。

**时间不够时：** 8 道是底线，不要再加题。

## 第 4 步：写评测脚本，跑对比实验（约 2 小时）

新建 `run_eval.py`。对所有 `reviewed_by_li` 为 true 的题目、所有学生代码，跑两种方法，每种跑 1 遍。

**B0 纯 AI 审代码**（新建 `fanli/baseline.py`）：把题目和学生代码交给同一个 LLM，要求输出 JSON：

```json
{"verdict": "correct 或 wrong", "counterexample_args": [...], "expected": ..., "L1": "...", "L2": "...", "L3": "..."}
```

如果 B0 判为 wrong，就把它给的 `counterexample_args` **实际运行一遍**，用学生代码和参考解各跑一次，记录这个反例能不能复现错误。这是最有说服力的对比：纯 AI 说的反例经常是错的。

**本作品**：直接复用 `strategy.build` + `difftest.find_counterexample` + `hints.make_hints`。

每份代码输出一行，写入 `results/eval_raw.jsonl`。然后汇总成 `results/eval_summary.md`，包含下表，每格写「比例（分子/分母）」：

| 指标 | B0 | 本作品 |
| --- | --- | --- |
| 错解检出率 | | |
| 正确解误报率 | | |
| 给出的反例能真实复现的比例 | | |
| 反例输入长度中位数 | | |
| 提示泄题检查不通过的比例 | | |
| AI 生成器一次通过率 | 不适用 | |

汇总文件里还要写明：模型名、运行日期、题目数、程序数、总 token 数，并列出**每一个失败案例**（误报、漏检、反例不能复现）。不要只挑好看的结果。

B1（AI 写固定单元测试）按原计划已经砍掉，不要做。

**通过标准：** `eval_summary.md` 生成成功，Li 看过数字。把这个文件发给项目里的 Claude，用来写技术报告。

## 第 5 步：演示入口与提交仓库（约 1 小时）

1. 新建 `demo.py`，只做命令行演示：`python demo.py problems/p003_xxx path/to/student.py`。逐层打印反例和提示，每层之间按回车继续，方便录屏。时间够再考虑 Gradio，不够就不做。
2. 更新 README：加一段「评测结果」，指向 `results/eval_summary.md`；加上 demo 的用法。
3. 在 `AI_USAGE.md` 里补齐本机这几步的记录。
4. 推送到 GitHub。私有仓库也可以，但要保证评审期间能访问。提交前用 `git status` 确认 `.env` 没有被提交，再搜一遍有没有写进学校名。

## 第 6 步：交给项目里的 Claude 写材料

把这些发到项目对话里：`results/eval_summary.md`、仓库链接、`AI_USAGE.md`，以及一两张 demo 截图。项目里的 Claude 负责起草：技术报告（按附件 2 大纲）、作品名称（不超过 20 字）、作品简介（不超过 300 字）、开源及第三方资源使用清单、3–5 分钟视频的分镜脚本。录视频和最终提交由 Li 自己完成。

## 时间表（Li 本地时间）

| 时间 | 完成 |
| --- | --- |
| 10-28 | 第 1–3 步 |
| 10-29 上午 | 第 4–5 步，拿到评测数据 |
| 10-29 下午 | 第 6 步，录视频，报告导出 PDF（不超过 10MB） |
| 10-29 晚上 | 提交（对应北京时间 10-30 上午，留出半天余量） |

如果 10-29 中午还没有评测数据，就按这个顺序砍：Gradio → 题目减到 6 道 → 提示质量的人工打分。核心流程、正确解误报测试、和 B0 的对比不能砍。
