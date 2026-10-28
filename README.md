# 反例导师

给 Python 初学者的反例驱动分层提示工具。学生提交一个函数后，工具先找出一个**真实跑出来的最小反例**，再据此给出三层递进提示，不直接给答案。

当前状态：题库 8 道（整数列表 / 字符串 / 列表+整数），已完成与「纯 AI 审代码」基线的对比实验，结果见 [评测结果](#评测结果)。本机操作步骤见 [CLAUDE.md](CLAUDE.md)。

## 流程

1. **AI 读题写生成器**：LLM 把题目里的输入约束翻译成 Hypothesis 输入策略（`fanli/strategy.py`）。
2. **生成器自校验**：用参考解跑生成的输入，参考解报错就把错误反馈给 LLM 重写，最多 2 次，仍失败则退回人工输入模板。
3. **差分测试与缩减**：Hypothesis 对比学生代码与参考解，发现不一致后自动缩减到最小反例（`fanli/difftest.py`）。学生代码在独立子进程里运行，单次调用超时 2 秒（`fanli/sandbox.py`）。
4. **三层提示**：LLM 只看到题目、学生代码和已验证的反例，看不到参考解。输出再经过泄题检查，不通过就退回模板提示（`fanli/hints.py`）。

没有配置 API 密钥时，第 1 步用人工输入模板，第 4 步用模板提示，流程仍能完整跑通。

## 安装与运行（Windows / macOS / Linux）

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q tests                              # 离线自测，不花 API 费用
python run_first_check.py problems/p001_second_largest  # 首验
```

要接入 LLM，把 `.env.example` 复制成 `.env`，填入密钥，再跑一次首验。token 用量会记录在 `results/token_usage.csv`。

命令行演示（逐层展示反例和提示，每层按回车，方便录屏）：

```bash
python demo.py problems/p003_range_span problems/p003_range_span/solutions/bug_assume_min_zero.py
```

跑完整对比实验（对所有已审核题目，比较本作品与纯 AI 基线）：

```bash
python run_eval.py        # 生成 results/eval_raw.jsonl 和 results/eval_summary.md
```

## 评测结果

对 8 道题、31 份学生程序，比较**本作品**与 **B0（把题目和代码直接交给同一个 LLM 审）**，每种方法各跑一遍。完整数据见 [`results/eval_summary.md`](results/eval_summary.md)。

| 指标 | B0（纯 AI） | 本作品 |
| --- | --- | --- |
| 错解检出率 | 100%（23/23） | 100%（23/23） |
| 正确解误报率 | 0%（0/8） | 0%（0/8） |
| 给出的反例能真实复现的比例 | 91%（21/23） | 100%（23/23） |
| 反例输入长度中位数 | 3 | 1 |
| 提示泄题检查不通过的比例 | 0%（0/23） | 0%（0/23） |
| AI 生成器一次通过率 | 不适用 | 88%（7/8） |

在这批入门题上，强模型纯靠读代码也能判对对错，两种方法的检出率与误报率打平。差距体现在**反例质量**：本作品的反例来自差分测试实跑，100% 能复现且已缩到最小（中位数长度 1 vs 3）；而 B0 给出的反例中有 2 个无法复现错误——这正是纯 AI 的典型问题。具体模型、日期与每一个失败案例都列在汇总文件里。

## 题目格式

每道题一个目录：`problem.md` 题面（自己写，不复制刷题平台原文）、`reference.py` 参考解、`meta.json`（函数名、输入模板、各学生解的预期判定）、`solutions/` 学生代码。

## 安全边界

子进程隔离不是安全沙箱。只运行自建题库和同学自愿提交的代码，不要用于接收任意公开上传。

## 依赖与许可

| 依赖 | 许可证 | 用法 |
| --- | --- | --- |
| Hypothesis | MPL-2.0 | 作为依赖调用，未修改源码 |
| openai（Python SDK） | Apache-2.0 | 调用 OpenAI 兼容接口 |
| pytest | MIT | 测试 |

版本与许可证请在提交前对照各项目仓库再核实一次。本项目代码以 MIT 许可发布。
