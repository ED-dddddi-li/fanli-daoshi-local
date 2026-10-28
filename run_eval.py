"""第 4 步：对比实验。对所有已审核题目的所有学生代码，跑两种方法各一遍：

- 本作品：strategy.build（AI 写生成器+自校验） + difftest（差分测试+反例缩减） + hints（三层提示+泄题检查）
- B0：纯 AI 审代码（fanli/baseline.py）

每份代码写一行到 results/eval_raw.jsonl；汇总到 results/eval_summary.md。
B0 判为 wrong 时，把它给的反例实际运行，核对能否真实复现错误。

用法：python run_eval.py
"""
import copy
import csv
import importlib.util
import json
import os
import statistics
import sys
from datetime import datetime

from fanli import baseline, difftest, hints, llm, strategy
from fanli.sandbox import StudentRunner

PROBLEMS_DIR = "problems"
RESULTS_DIR = "results"
TOKEN_CSV = os.path.join(RESULTS_DIR, "token_usage.csv")


def load_fn(path, name):
    spec = importlib.util.spec_from_file_location("reference_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, name)


def norm(x):
    return json.loads(json.dumps(x, default=repr))


def input_length(args):
    """反例输入规模：列表/字符串按长度计，标量计 1。"""
    total = 0
    for a in args:
        total += len(a) if isinstance(a, (list, str)) else 1
    return total


def run_on(path, func_name, args):
    runner = StudentRunner(path, func_name)
    try:
        return runner.call(list(args))
    finally:
        runner.close()


def reproduce_cex(student_path, func_name, reference_fn, args):
    """这个反例能否真实暴露学生代码与参考解不一致。返回 (bool, 说明)。"""
    if not isinstance(args, list):
        return False, "反例参数不是位置参数列表"
    try:
        expected = norm(reference_fn(*copy.deepcopy(args)))
    except Exception as e:  # noqa: BLE001  参考解报错 → 反例越界/参数不合法
        return False, f"参考解在该输入上报错，反例无效: {type(e).__name__}"
    status, actual = run_on(student_path, func_name, args)
    if status == "error":
        return True, f"学生代码报错: {actual}"
    if status == "timeout":
        return True, "学生代码超时"
    if norm(actual) != expected:
        return True, f"学生输出 {actual!r} != 正确 {expected!r}"
    return False, f"学生输出与正确一致 ({actual!r})，反例无法复现错误"


def token_total():
    if not os.path.exists(TOKEN_CSV):
        return 0, 0
    rows = list(csv.reader(open(TOKEN_CSV, encoding="utf-8")))
    return sum(int(r[1]) for r in rows), sum(int(r[2]) for r in rows)


def reviewed_problem_dirs():
    out = []
    for name in sorted(os.listdir(PROBLEMS_DIR)):
        meta_path = os.path.join(PROBLEMS_DIR, name, "meta.json")
        if not os.path.exists(meta_path):
            continue
        meta = json.load(open(meta_path, encoding="utf-8"))
        if meta.get("reviewed_by_li") is True:
            out.append((os.path.join(PROBLEMS_DIR, name), meta))
    return out


def evaluate():
    problems = reviewed_problem_dirs()
    pt0, ct0 = token_total()
    raw_fp = open(os.path.join(RESULTS_DIR, "eval_raw.jsonl"), "w", encoding="utf-8")

    records = []
    gen_first_pass = gen_total = 0

    for pdir, meta in problems:
        func_name = meta["func_name"]
        problem_text = open(os.path.join(pdir, "problem.md"), encoding="utf-8").read()
        ref_path = os.path.join(pdir, "reference.py")
        reference_code = open(ref_path, encoding="utf-8").read()
        reference_fn = load_fn(ref_path, func_name)

        strat, src, log = strategy.build(problem_text, meta, reference_fn)
        gen_total += 1
        if src == "llm:attempt1":
            gen_first_pass += 1
        print(f"\n== {meta['id']}  生成器: {src}")
        for line in log:
            print("   [生成器]", line)

        sol_dir = os.path.join(pdir, "solutions")
        for name in sorted(os.listdir(sol_dir)):
            if not name.endswith(".py"):
                continue
            path = os.path.join(sol_dir, name)
            code = open(path, encoding="utf-8").read()
            expected = meta["expected_verdicts"].get(name)

            # ---- 本作品 ----
            cex = difftest.find_counterexample(strat, reference_fn, path, func_name)
            ours_verdict = "wrong" if cex else "correct"
            ours = {"verdict": ours_verdict, "cex_args": None, "cex_len": None,
                    "cex_reproduce": None, "hint_source": None, "hint_leak": None}
            if cex:
                h, hsrc, _ = hints.make_hints(problem_text, code, reference_code, cex, func_name)
                rep, rep_note = reproduce_cex(path, func_name, reference_fn, cex["args"])
                ours.update(cex_args=cex["args"], cex_len=input_length(cex["args"]),
                            cex_reproduce=rep, cex_reproduce_note=rep_note,
                            hint_source=hsrc, hint_leak=bool(hints.leak_check(h, reference_code)),
                            hints=h)

            # ---- B0 纯 AI ----
            data, b0_raw = baseline.review(problem_text, code, func_name)
            b0 = {"verdict": data["verdict"], "cex_args": data.get("counterexample_args"),
                  "cex_len": None, "cex_reproduce": None, "hint_leak": None}
            if data["verdict"] == "wrong":
                b0_hints = {k: data.get(k, "") for k in ("L1", "L2", "L3")}
                b0["hint_leak"] = bool(hints.leak_check(b0_hints, reference_code))
                b0["hints"] = b0_hints
                b0_args = data.get("counterexample_args")
                if isinstance(b0_args, list):
                    rep, rep_note = reproduce_cex(path, func_name, reference_fn, b0_args)
                    b0.update(cex_len=input_length(b0_args), cex_reproduce=rep,
                              cex_reproduce_note=rep_note)
                else:
                    b0["cex_reproduce"] = False
                    b0["cex_reproduce_note"] = "B0 未给出合法的位置参数列表"

            rec = {"problem": meta["id"], "solution": name, "expected": expected,
                   "ours": ours, "b0": b0}
            raw_fp.write(json.dumps(rec, ensure_ascii=False) + "\n")
            records.append(rec)
            print(f"   {name:<26} 期望={expected:<7} 本作品={ours_verdict:<7} B0={b0['verdict']}")

    raw_fp.close()
    pt1, ct1 = token_total()
    tokens = {"prompt": pt1 - pt0, "completion": ct1 - ct0, "total": (pt1 + ct1) - (pt0 + ct0)}
    write_summary(records, gen_first_pass, gen_total, tokens, len(problems))
    return records


def _rate(num, den):
    return f"{num/den:.0%}（{num}/{den}）" if den else "—（0/0）"


def _median(vals):
    return statistics.median(vals) if vals else None


def write_summary(records, gen_first_pass, gen_total, tokens, n_problems):
    wrong_recs = [r for r in records if r["expected"] == "wrong"]
    correct_recs = [r for r in records if r["expected"] == "correct"]
    n_programs = len(records)

    def metrics(key):
        detect = sum(1 for r in wrong_recs if r[key]["verdict"] == "wrong")
        fp = sum(1 for r in correct_recs if r[key]["verdict"] == "wrong")
        cex_recs = [r for r in records if r[key]["verdict"] == "wrong"
                    and r[key].get("cex_reproduce") is not None]
        repro = sum(1 for r in cex_recs if r[key]["cex_reproduce"])
        lens = [r[key]["cex_len"] for r in records if r[key].get("cex_len") is not None]
        hint_recs = [r for r in records if r[key]["verdict"] == "wrong"
                     and r[key].get("hint_leak") is not None]
        leak = sum(1 for r in hint_recs if r[key]["hint_leak"])
        return {
            "detect": _rate(detect, len(wrong_recs)),
            "fp": _rate(fp, len(correct_recs)),
            "repro": _rate(repro, len(cex_recs)),
            "median_len": _median(lens),
            "leak": _rate(leak, len(hint_recs)),
        }

    b0, ours = metrics("b0"), metrics("ours")
    gen_rate = _rate(gen_first_pass, gen_total)

    lines = []
    lines.append("# 对比实验汇总（第 4 步）\n")
    lines.append(f"- 模型：{llm.model_name()}")
    lines.append(f"- 运行日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}（本地时间）")
    lines.append(f"- 题目数：{n_problems}；学生程序数：{n_programs}"
                 f"（其中错解 {len(wrong_recs)}、正确解 {len(correct_recs)}）")
    lines.append(f"- 本次评测 token：prompt {tokens['prompt']} + completion {tokens['completion']} "
                 f"= 总计 {tokens['total']}\n")

    lines.append("| 指标 | B0（纯 AI） | 本作品 |")
    lines.append("| --- | --- | --- |")
    lines.append(f"| 错解检出率 | {b0['detect']} | {ours['detect']} |")
    lines.append(f"| 正确解误报率 | {b0['fp']} | {ours['fp']} |")
    lines.append(f"| 给出的反例能真实复现的比例 | {b0['repro']} | {ours['repro']} |")
    lines.append(f"| 反例输入长度中位数 | {b0['median_len']} | {ours['median_len']} |")
    lines.append(f"| 提示泄题检查不通过的比例 | {b0['leak']} | {ours['leak']} |")
    lines.append(f"| AI 生成器一次通过率 | 不适用 | {gen_rate} |\n")

    # 失败案例清单：误报、漏检、反例不能复现
    lines.append("## 失败案例清单（不挑好看的）\n")
    for label, key in (("B0（纯 AI）", "b0"), ("本作品", "ours")):
        fails = []
        for r in records:
            tag = f"{r['problem']}/{r['solution']}"
            m = r[key]
            if r["expected"] == "correct" and m["verdict"] == "wrong":
                fails.append(f"误报：{tag}（正确解被判 wrong）")
            if r["expected"] == "wrong" and m["verdict"] == "correct":
                fails.append(f"漏检：{tag}（错解被判 correct）")
            if m["verdict"] == "wrong" and m.get("cex_reproduce") is False:
                note = m.get("cex_reproduce_note", "")
                fails.append(f"反例不能复现：{tag}（{note}）")
            if r["expected"] == "wrong" and m["verdict"] == "parse_error":
                fails.append(f"解析失败：{tag}（B0 输出无法解析）")
        lines.append(f"**{label}**")
        if fails:
            lines.extend(f"- {x}" for x in fails)
        else:
            lines.append("- 无")
        lines.append("")

    out = os.path.join(RESULTS_DIR, "eval_summary.md")
    open(out, "w", encoding="utf-8").write("\n".join(lines))
    print(f"\n汇总已写入 {out}")
    print("\n".join(lines))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    evaluate()
