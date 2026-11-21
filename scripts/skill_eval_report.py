#!/usr/bin/env python3
"""Minimal offline HTML report for *recorded* Skill evaluation, not a model runner.

A test harness must actually use the Skill and supply results with provenance.
Unreviewed judgments cannot silently become semantic accuracy statistics.
No network, external assets, learner prose, or invented observations.
"""
import argparse
import html
import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path

MAX_BYTES = 2_000_000
MAX_CASES = 2500
ACTIONS = {"clarify", "recheck", "repair", "transfer", "stop"}
DEFECTS = {"wrong_key", "multiple_answers", "ambiguous",
           "source_mismatch", "rubric_defect", "invalid_distractor",
           "scope_error", "duplicate_family", "other"}
RUN_KEYS = {"id", "mode", "reference", "model", "commit", "dataset", "date"}
CASE_KEYS = {"id", "test_id", "family", "kind", "truth", "decision",
             "defect", "caught_actual_defect", "expected_action", "selected_action",
             "input_tokens", "output_tokens", "latency_ms"}
TEXT = {
    "zh": {
        "page": "学习诊断 Skill · 评测报告",
        "demo": "合成演示 · 不代表真实模型效果",
        "actual": "真实运行记录 · 专家标注仅为提交者声明",
        "unverified": "缺少独立效标 · 不计算质量指标",
        "source": "证据级别", "items": "记录用例", "run": "运行",
        "defect": "缺陷检出率", "sound": "正确题放行率",
        "followup": "追问目标匹配率", "small": "样本不足，暂不报百分比",
        "none": "未测量", "ratio": "分子 / 分母", "interval": "Wilson 95%区间",
        "correlated": "存在重复题族；不显示独立样本区间",
        "risk": "优先处理的风险", "no_risk": "本次已标注用例未发现可列示的错误放行、误拦截或待裁决项；不代表没有风险。",
        "breakdown": "缺陷类别（只显示最多四类）",
        "caught": "已拦截", "other": "更多类别",
        "details": "展开用例与判定记录（不含原题、学生回答）",
        "cost": "展开运行成本与记录完整度",
        "method": "展开方法、来源与限制",
        "id": "用例", "test": "测试项", "gold": "独立标签",
        "decision": "模型决策", "issue": "缺陷类别",
        "review": "标准答案/审阅声明", "mode": "数据来源",
        "model": "模型", "commit": "提交", "dataset": "数据集",
        "date": "记录日期", "tokens": "实测输入/输出Token",
        "latency": "时延中位数", "p95": "P95时延",
        "coverage": "具有实际记录的样本", "ms": "毫秒",
        "unresolved": "未裁决/未知标准",
        "missing": "未知或未提供", "footer": "仅本地HTML，不访问网络。不将任何指标解释为学生掌握概率或教学收益。",
        "legend": "比例只由可核对的分子与分母计算；n<5不显示百分比；存在同题族相关性时不报告独立样本区间。",
        "declared": "参考标签与审核身份由数据提交者声明；脚本无法核验其真实性。正式教育测量需要合格真人复核。",
        "more": "仅展示最需排查的前50条；完整记录仍在原始受控输入中。",
    },
    "en": {
        "page": "Learning diagnosis Skill · evaluation report",
        "demo": "Synthetic demo · not real model performance",
        "actual": "Recorded model run · expert labels are self-declared",
        "unverified": "No independent reference · quality rates withheld",
        "source": "Evidence status", "items": "Cases", "run": "Run",
        "defect": "Defect detection", "sound": "Sound-item acceptance",
        "followup": "Follow-up target match", "small": "Too few cases for a rate",
        "none": "Not measured", "ratio": "Numerator / denominator", "interval": "Wilson 95% interval",
        "correlated": "Repeated families; independent-item interval withheld",
        "risk": "Priority failures", "no_risk": "No listed failures in these labeled cases; this does not prove absence of risk.",
        "breakdown": "Defect categories (up to four)",
        "caught": "Blocked", "other": "More categories",
        "details": "Expand case decisions (no question or learner text)",
        "cost": "Expand observed resource use",
        "method": "Expand method, provenance and limitations",
        "id": "Case", "test": "Test", "gold": "Reference label",
        "decision": "Model decision", "issue": "Defect",
        "review": "Declared review", "mode": "Data origin",
        "model": "Model", "commit": "Commit", "dataset": "Dataset",
        "date": "Recorded", "tokens": "Observed input/output tokens",
        "latency": "Median latency", "p95": "P95 latency",
        "coverage": "Cases with measured values", "ms": "ms",
        "unresolved": "Unresolved / unknown reference",
        "missing": "Unknown or absent", "footer": "Local HTML only; no network. Scores do not estimate latent mastery or learning gains.",
        "legend": "Rates use explicit numerators/denominators. For n<5, no percentage. Repeated item families suppress independence-based intervals.",
        "declared": "Reference labels and reviewer independence are user-provided declarations, not verified identities; qualified human review remains necessary.",
        "more": "Only the 50 most relevant cases are shown; controlled input retains all records.",
    }
}


def _object(value, allowed, required, name):
    if not isinstance(value, dict):
        raise ValueError(name + " must be an object")
    extra = set(value) - allowed
    missing = required - set(value)
    if extra or missing:
        raise ValueError("%s unexpected/missing fields: %s / %s" %
                         (name, sorted(extra), sorted(missing)))


def _str(value, field, max_length=128):
    if not isinstance(value, str) or not value.strip() or len(value) > max_length:
        raise ValueError(field + " must be nonempty bounded text")
    return value


def _number(value, field, integer=False):
    if value is None:
        return
    types = (int,) if integer else (int, float)
    if type(value) not in types or value < 0 or value > 1_000_000_000_000 or not math.isfinite(value):
        raise ValueError(field + " must be a nonnegative finite number or null")


def read_report(path):
    path = Path(path)
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("report input exceeds 2MB")
    data = json.loads(path.read_text(encoding="utf-8"))
    _object(data, {"schema_version", "run", "cases"},
            {"schema_version", "run", "cases"}, "payload")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ValueError("schema_version must be 1")
    run = data["run"]
    _object(run, RUN_KEYS, RUN_KEYS, "run")
    for key in RUN_KEYS:
        _str(run[key], "run." + key)
    if run["mode"] not in {"synthetic_demo", "actual_model"}:
        raise ValueError("invalid run.mode")
    if run["reference"] not in {"synthetic_labels", "expert_adjudicated",
                                 "model_only", "none"}:
        raise ValueError("invalid run.reference")
    if run["mode"] == "synthetic_demo" and run["reference"] != "synthetic_labels":
        raise ValueError("synthetic demo must use synthetic_labels")
    if run["mode"] == "actual_model" and run["reference"] == "synthetic_labels":
        raise ValueError("real runs may not claim synthetic references as expert labels")
    cases = data["cases"]
    if not isinstance(cases, list) or len(cases) > MAX_CASES:
        raise ValueError("cases must be an array with at most 2500 entries")
    seen = set()
    for case in cases:
        _object(case, CASE_KEYS, {"id", "test_id", "family", "kind"}, "case")
        for k in ("id", "test_id", "family"):
            _str(case[k], "case." + k)
        if case["id"] in seen:
            raise ValueError("duplicate case id")
        seen.add(case["id"])
        if case["test_id"] not in {("RM-%02d" % i) for i in range(1, 13)}:
            raise ValueError("unknown RM test id")
        if case["kind"] not in {"audit", "tutoring"}:
            raise ValueError("invalid case kind")
        if case["kind"] == "audit":
            if case.get("truth", "unknown") not in {"defective", "sound", "unknown"}:
                raise ValueError("invalid audit reference truth")
            if case.get("decision", "uncertain") not in {"block", "accept", "uncertain"}:
                raise ValueError("invalid audit decision")
            if case.get("defect") is not None and case["defect"] not in DEFECTS:
                raise ValueError("invalid defect category")
            caught = case.get("caught_actual_defect")
            if caught is not None and type(caught) is not bool:
                raise ValueError("caught_actual_defect must be a boolean")
            if case.get("truth") == "defective" and case.get("decision") == "block":
                if type(caught) is not bool:
                    raise ValueError("blocked defective case requires independently adjudicated defect match")
            elif caught is not None:
                raise ValueError("caught_actual_defect only applies to blocked defective cases")
            if case.get("expected_action") is not None or case.get("selected_action") is not None:
                raise ValueError("audit rows cannot contain tutor actions")
        else:
            if any(case.get(k) is not None for k in ("truth", "decision", "defect", "caught_actual_defect")):
                raise ValueError("tutoring rows cannot contain audit labels")
            if case.get("expected_action") not in ACTIONS | {None}:
                raise ValueError("invalid reference action")
            if case.get("selected_action") not in ACTIONS | {None}:
                raise ValueError("invalid model action")
        for k in ("input_tokens", "output_tokens"):
            _number(case.get(k), k, integer=True)
        _number(case.get("latency_ms"), "latency_ms")
    return data


def wilson(success, total):
    """95% Wilson binomial interval; only appropriate for independent trials."""
    if total <= 0 or not 0 <= success <= total:
        raise ValueError("invalid binomial counts")
    z = 1.959963984540054
    p = success / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    # Floating-point cancellation at k=0/n gives tiny positive lower bounds;
    # the exact binomial boundary of the Wilson formula is zero/one.
    lo = 0.0 if success == 0 else max(0.0, center - margin)
    hi = 1.0 if success == total else min(1.0, center + margin)
    return lo, hi


def summarize(payload):
    cases = payload["cases"]
    run = payload["run"]
    eligible = run["mode"] == "synthetic_demo" or (
        run["mode"] == "actual_model" and run["reference"] == "expert_adjudicated")
    audit = [x for x in cases if x["kind"] == "audit"]
    tutor = [x for x in cases if x["kind"] == "tutoring"]
    defective = [x for x in audit if x.get("truth") == "defective"]
    sound = [x for x in audit if x.get("truth") == "sound"]
    referenced_tutor = [x for x in tutor if x.get("expected_action") in ACTIONS]

    def metric(rows, predicate):
        n = len(rows)
        k = sum(bool(predicate(x)) for x in rows)
        unique = len({x["family"] for x in rows}) == n
        ci = wilson(k, n) if eligible and n >= 5 and unique else None
        return {"numerator": k if eligible else None, "denominator": n if eligible else None,
                "rate": k / n if eligible and n >= 5 else None,
                "wilson_95": ci, "independent_families": unique,
                "sample_size": n}

    scores = {
        "defect_detection": metric(defective, lambda x: x.get("decision") == "block" and x.get("caught_actual_defect") is True),
        "sound_acceptance": metric(sound, lambda x: x.get("decision") == "accept"),
        "tutoring_match": metric(referenced_tutor,
                                 lambda x: x.get("selected_action") == x.get("expected_action"))
    }
    failures = []
    for c in cases:
        if c["kind"] == "audit":
            if (c.get("truth") == "defective" and c.get("decision") == "block"
                    and c.get("caught_actual_defect") is False):
                failures.append(("unmatched_block", c))
            elif c.get("truth") == "defective" and c.get("decision") == "accept":
                failures.append(("missed_defect", c))
            elif c.get("truth") == "sound" and c.get("decision") == "block":
                failures.append(("false_alarm", c))
            elif c.get("decision", "uncertain") == "uncertain" or c.get("truth", "unknown") == "unknown":
                failures.append(("unresolved", c))
        elif c.get("expected_action") in ACTIONS and c.get("selected_action") != c["expected_action"]:
            failures.append(("followup_mismatch", c))
        elif c.get("expected_action") not in ACTIONS:
            failures.append(("unresolved", c))
    costs = {}
    for key in ("input_tokens", "output_tokens", "latency_ms"):
        values = [x[key] for x in cases if x.get(key) is not None]
        costs[key] = {"coverage": len(values), "total_cases": len(cases),
                      "total": sum(values) if key != "latency_ms" and values else None,
                      "median": statistics.median(values) if values else None,
                      "p95": sorted(values)[math.ceil(.95 * len(values)) - 1]
                      if key == "latency_ms" and len(values) >= 20 else None}
    return {"evidence": ("synthetic_demo" if run["mode"] == "synthetic_demo"
                         else "declared_expert_reference" if eligible else "unverified"),
            "cases": len(cases), "audited": len(audit), "tutored": len(tutor),
            "scores": scores, "failure_types": dict(Counter(x[0] for x in failures)),
            "unresolved": sum(x[0] == "unresolved" for x in failures),
            "failures": failures, "costs": costs}


def _e(value):
    return html.escape(str(value), quote=True)


def render(payload, summary, lang="zh"):
    s = TEXT[lang]
    run = payload["run"]
    evidence = summary["evidence"]
    label = s["demo"] if evidence == "synthetic_demo" else (
        s["actual"] if evidence == "declared_expert_reference" else s["unverified"])
    def card(key, name):
        m = summary["scores"][key]
        n = m["denominator"]
        if n is None or not n:
            value = "—"
            note = s["none"]
        elif m["rate"] is None:
            value = "—"
            note = f'{s["ratio"]}: {m["numerator"]}/{n} · {s["small"]}'
        else:
            value = "%.1f%%" % (100 * m["rate"])
            note = f'{s["ratio"]}: {m["numerator"]}/{n}'
            if m["wilson_95"] is not None:
                low, high = m["wilson_95"]
                note += " · %s %.1f–%.1f%%" % (s["interval"], low * 100, high * 100)
            elif not m["independent_families"]:
                note += " · " + s["correlated"]
        return '<section class="metric"><div class="muted">%s</div><strong>%s</strong><small>%s</small></section>' % (
            _e(name), _e(value), _e(note))
    cards = "".join(card(key, s[name]) for key, name in (
        ("defect_detection", "defect"), ("sound_acceptance", "sound"),
        ("tutoring_match", "followup")))

    labels = {
        "missed_defect": "错误题被放行 / Defective accepted",
        "unmatched_block": "拦截原因不匹配实际缺陷 / Wrong defect reason",
        "false_alarm": "正确题被拦截 / Sound blocked",
        "followup_mismatch": "追问目标不匹配 / Follow-up mismatch",
        "unresolved": "未裁决 / Unresolved",
    }
    risks = summary["failures"] if evidence != "unverified" else []
    risk_rows = "".join(
        '<li><span>%s · %s · %s</span><b>%s</b></li>' %
        (_e(c["id"]), _e(c["test_id"]), _e(c["family"]), _e(labels[k]))
        for k, c in risks[:4])
    if not risk_rows:
        risk_rows = '<p class="muted">%s</p>' % _e(
            s["unverified"] if evidence == "unverified" else s["no_risk"])
    else:
        risk_rows = "<ul class='risk-list'>" + risk_rows + "</ul>"
    if len(risks) > 4:
        risk_rows += '<p class="muted">+%d</p>' % (len(risks) - 4)
    categories = Counter(x.get("defect") or "other" for x in payload["cases"]
                         if x["kind"] == "audit" and x.get("truth") == "defective")
    cat_rows = []
    for key, count in categories.most_common(4):
        caught = sum(c.get("caught_actual_defect") is True for c in payload["cases"]
                     if c["kind"] == "audit" and c.get("truth") == "defective"
                     and (c.get("defect") or "other") == key)
        width = (caught / count * 100) if count else 0
        cat_rows.append('<div class="bar-row"><div><span>%s</span><span>%s %d/%d</span></div>'
                        '<div class="bar" role="img" aria-label="%s: %d/%d">'
                        '<span style="width:%.2f%%"></span></div></div>' %
                        (_e(key), _e(s["caught"]), caught, count, _e(key), caught, count, width))
    chart = "".join(cat_rows) if summary["evidence"] != "unverified" else ""
    if not chart:
        chart = '<p class="muted">%s</p>' % _e(s["none"])
    elif len(categories) > 4:
        chart += '<p class="muted">%s: %d</p>' % (_e(s["other"]), len(categories) - 4)
    selected = sorted(payload["cases"], key=lambda c: (
        0 if any(c is item for _, item in risks) else 1, c["id"]))[:50]
    trs = []
    for c in selected:
        gold = c.get("truth", c.get("expected_action")) or "unknown"
        decision = c.get("decision", c.get("selected_action")) or "uncertain"
        issue = c.get("defect") or "—"
        trs.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" %
                   tuple(_e(x) for x in (c["id"], c["test_id"], gold, decision, issue)))
    table = ('<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' %
             ("".join("<th>%s</th>" % _e(s[k]) for k in ("id", "test", "gold", "decision", "issue")),
              "".join(trs))) if trs else '<p class="muted">%s</p>' % _e(s["none"])
    if len(payload["cases"]) > len(selected):
        table += '<p class="muted">%s</p>' % _e(s["more"])

    costs = summary["costs"]
    tok_in, tok_out, latency = (costs[k] for k in ("input_tokens", "output_tokens", "latency_ms"))
    def recorded(data, attr="total", unit=""):
        val = data[attr]
        return (_e(val) + unit if val is not None else _e(s["none"])) + (
            " (%d/%d %s)" % (data["coverage"], data["total_cases"], _e(s["coverage"])))
    cost_info = ("<p>%s: %s / %s</p><p>%s: %s</p><p>%s: %s</p>" %
                 (_e(s["tokens"]), recorded(tok_in), recorded(tok_out),
                  _e(s["latency"]), recorded(latency, "median", " " + _e(s["ms"])),
                  _e(s["p95"]), recorded(latency, "p95", " " + _e(s["ms"]))))
    meta = "".join("<tr><th>%s</th><td>%s</td></tr>" %
                   (_e(s[k]), _e(run[v])) for k, v in (
                       ("run", "id"), ("mode", "mode"), ("review", "reference"),
                       ("model", "model"), ("commit", "commit"),
                       ("dataset", "dataset"), ("date", "date")))
    return """<!doctype html><html lang="%s"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'">
<title>%s</title><style>
:root{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;color:#182631;background:#f5f7f8}
*{box-sizing:border-box}body{margin:0}.wrap{max-width:910px;margin:auto;padding:30px 22px 70px}
h1{font-size:1.5rem;line-height:1.3;margin:0 0 8px}h2{font-size:1.02rem;margin:0 0 15px}
p{line-height:1.55}.muted,small{color:#576777;font-size:.81rem}.badge{display:inline-block;padding:7px 11px;
border-radius:8px;background:#e8edf0;color:#344554;font-weight:650;font-size:.8rem}
.panel{background:white;border:1px solid #dfe6e9;border-radius:12px;padding:20px;margin-top:17px}
.metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:20px}
.metric{border:1px solid #dfe6e9;border-radius:12px;padding:14px;background:white;min-width:0}
.metric strong{display:block;font-size:1.8rem;margin:6px 0;font-variant-numeric:tabular-nums}
.metric small{display:block;line-height:1.5}.risk-list{padding:0;list-style:none;margin:0}
.risk-list li{border-top:1px solid #e9eef1;padding:12px 0;display:flex;justify-content:space-between;gap:14px;font-size:.85rem}
.risk-list b{font-weight:600;color:#894b3d}.bar-row{margin-bottom:14px}.bar-row>div:first-child{display:flex;
justify-content:space-between;font-size:.85rem;gap:15px;margin-bottom:6px}
.bar{height:9px;border-radius:20px;background:#e5eaf0;overflow:hidden}.bar span{height:100%%;
display:block;background:#416b87;border-radius:20px}details{margin-top:13px;border:1px solid #dfe6e9;
border-radius:11px;background:white;padding:15px 18px}summary{cursor:pointer;font-weight:600;font-size:.9rem}
table{border-collapse:collapse;width:100%%;font-size:.83rem;margin-top:16px}th,td{text-align:left;
padding:10px;border-bottom:1px solid #edf0f2;word-break:break-word}th{color:#596879;font-weight:600}
.table-scroll{overflow-x:auto}footer{margin-top:22px;font-size:.78rem;color:#697885}
@media(max-width:680px){.metrics{grid-template-columns:1fr}.wrap{padding:18px 12px}
.panel{padding:16px}.risk-list li{display:block}.risk-list b{display:block;margin-top:5px}}
</style></head><body><main class="wrap"><header><h1>%s</h1><span class="badge">%s</span>
<p class="muted">%s: %s · %s: %d · %s: %s</p></header>
<div class="metrics">%s</div>
<section class="panel"><h2>%s</h2>%s</section>
<section class="panel"><h2>%s</h2>%s</section>
<details><summary>%s</summary><div class="table-scroll">%s</div></details>
<details><summary>%s</summary>%s</details>
<details><summary>%s</summary><table>%s</table>
<p class="muted">%s</p><p class="muted">%s</p></details>
<footer>%s</footer></main></body></html>""" % (
        "zh-CN" if lang == "zh" else "en",
        _e(s["page"]), _e(s["page"]), _e(label),
        _e(s["run"]), _e(run["id"]), _e(s["items"]), len(payload["cases"]),
        _e(s["source"]), _e(run["reference"]), cards, _e(s["risk"]), risk_rows,
        _e(s["breakdown"]), chart, _e(s["details"]), table,
        _e(s["cost"]), cost_info, _e(s["method"]), meta,
        _e(s["legend"]), _e(s["declared"]), _e(s["footer"]))


def main(argv=None):
    p = argparse.ArgumentParser(description="Render source-bounded offline Skill evaluation report")
    p.add_argument("input", help="JSON results recorded by an actual harness or explicitly synthetic demo")
    p.add_argument("--output", required=True, help="local output HTML")
    p.add_argument("--lang", choices=("zh", "en"), default="zh")
    p.add_argument("--summary", help="optional aggregate-only JSON output")
    args = p.parse_args(argv)
    try:
        payload = read_report(args.input)
        result = summarize(payload)
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(payload, result, args.lang), encoding="utf-8")
        if args.summary:
            # Deliberately omit case identifiers and free-text from public aggregates.
            public = {k: v for k, v in result.items() if k != "failures"}
            s = Path(args.summary)
            s.parent.mkdir(parents=True, exist_ok=True)
            s.write_text(json.dumps(public, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"report": str(target), "evidence": result["evidence"],
                          "cases": result["cases"]}, ensure_ascii=False))
        return 0
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
