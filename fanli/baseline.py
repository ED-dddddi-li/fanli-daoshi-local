"""B0 对比基线：纯 AI 审代码。

把题目和学生代码直接交给同一个 LLM，要求它自己判对错、给反例和三层提示。
不做差分测试、不做反例缩减、不做泄题检查——用来和本作品对比。
"""
import json
import re

from . import llm

BASELINE_SYSTEM = """你是编程助教，审查 Python 初学者提交的代码是否正确实现了题目要求。
只输出一个 JSON 对象，不要解释、不要代码块标记，格式：
{"verdict": "correct 或 wrong", "counterexample_args": [按顺序排列的位置参数], "expected": 该输入下的正确输出, "L1": "...", "L2": "...", "L3": "..."}
- verdict：代码是否正确实现题目要求。
- 若判为 wrong：counterexample_args 给一个能让代码出错的输入（函数的位置参数按顺序组成列表，哪怕只有一个参数也要用列表包起来）；expected 给该输入下的正确输出；L1/L2/L3 给三层递进提示。
- 若判为 correct：counterexample_args 用 null，expected 用 null，L1/L2/L3 用空字符串。
严禁输出修改后的代码、完整解法或任何代码块。"""


def _normalize_verdict(v):
    v = str(v).lower()
    if "wrong" in v:
        return "wrong"
    if "correct" in v:
        return "correct"
    return "parse_error"


def review(problem_text, student_code, func_name):
    """返回 (data, raw)。data 含 verdict/counterexample_args/expected/L1/L2/L3。

    解析失败时 verdict='parse_error'。
    """
    user = (f"题目：\n{problem_text}\n\n函数名：{func_name}\n\n"
            f"学生代码：\n{student_code}")
    raw = llm.chat(BASELINE_SYSTEM, user, temperature=0.2)
    data = {"verdict": "parse_error", "counterexample_args": None, "expected": None,
            "L1": "", "L2": "", "L3": ""}
    m = re.search(r"\{.*\}", raw, flags=re.S)
    if m:
        try:
            parsed = json.loads(m.group(0))
            data.update(parsed)
            data["verdict"] = _normalize_verdict(parsed.get("verdict"))
        except (ValueError, TypeError):
            pass
    return data, raw
