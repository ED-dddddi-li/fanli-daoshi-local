"""命令行演示：对一道题 + 一份学生代码，逐层展示最小反例和三层提示。

用法：
    python demo.py problems/p003_range_span problems/p003_range_span/solutions/bug_assume_min_zero.py

每打印一步后按回车继续，方便录屏。没配 .env 时自动走离线降级，流程照样完整。
"""
import importlib.util
import json
import os
import sys

from fanli import difftest, hints, llm, strategy


def load_fn(path, name):
    spec = importlib.util.spec_from_file_location("reference_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, name)


def pause(msg="（按回车继续）"):
    try:
        input(msg)
    except EOFError:
        print()


def main(problem_dir, student_path):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    meta = json.load(open(os.path.join(problem_dir, "meta.json"), encoding="utf-8"))
    problem_text = open(os.path.join(problem_dir, "problem.md"), encoding="utf-8").read()
    ref_path = os.path.join(problem_dir, "reference.py")
    reference_code = open(ref_path, encoding="utf-8").read()
    reference_fn = load_fn(ref_path, meta["func_name"])
    func_name = meta["func_name"]
    student_code = open(student_path, encoding="utf-8").read()

    line = "=" * 60
    print(line)
    print(f"反例导师演示  |  题目：{meta['title']}  |  函数：{func_name}")
    print(f"LLM：{llm.model_name() if llm.available() else '未配置（离线降级）'}")
    print(line)
    print("\n【题面】\n" + problem_text.strip())
    print("\n【学生提交的代码】\n" + student_code.strip())
    pause("\n按回车：让 AI 读题写输入生成器 …")

    strat, src, log = strategy.build(problem_text, meta, reference_fn)
    print(f"\n【第 1 步：AI 生成器】来源 {src}")
    for ln in log:
        print("  -", ln)
    pause("\n按回车：开始差分测试，寻找并缩减最小反例 …")

    cex = difftest.find_counterexample(strat, reference_fn, student_path, func_name)
    if cex is None:
        print("\n【结果】未发现反例，判定：correct ✅")
        print("（在当前输入范围内，学生代码与参考解表现一致。）")
        return
    args_str = ", ".join(repr(a) for a in cex["args"])
    print(f"\n【第 2 步：最小反例】判定：wrong ❌")
    print(f"  调用：{func_name}({args_str})")
    print(f"  期望输出：{cex['expected']!r}")
    print(f"  实际结果（{cex['kind']}）：{cex['actual']!r}")
    pause("\n按回车：基于反例生成三层提示（不泄露答案）…")

    h, hsrc, issues = hints.make_hints(problem_text, student_code, reference_code, cex, func_name)
    for k, tip in (("L1", "指出哪一类输入会出错"), ("L2", "给出反例，引导手动模拟"),
                   ("L3", "指向最可疑的代码行")):
        print(f"\n  {k}（{tip}）：{h[k]}")
        if k != "L3":
            pause()
    print(f"\n【提示来源】{hsrc}  |  泄题检查：{'通过' if not issues else issues}")
    print("\n" + line)
    print("演示结束：反例真实可复现、已缩到最小，三层提示逐步加深且不含答案。")
    print(line)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法：python demo.py <题目目录> <学生代码路径>")
        print("示例：python demo.py problems/p003_range_span "
              "problems/p003_range_span/solutions/bug_assume_min_zero.py")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
