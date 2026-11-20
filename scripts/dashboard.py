#!/usr/bin/env python3
"""Generate a fully offline, bilingual dashboard from local learning evidence.

No network requests or third-party packages. Only summary statistics, source
concept names, reviewed misconception codes and criterion labels enter HTML.
Raw learner responses, item texts, solutions and evidence quotes never enter it.
"""
import argparse
import html
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

try:
    from .qa import read_bank, read_state, due_date
    from .diagnosis import estimate
except ImportError:
    from qa import read_bank, read_state, due_date
    from diagnosis import estimate


LEVELS = ("recall", "understand", "apply", "analyze", "transfer")
LABELS_ZH = {
    "untested": "未测", "insufficient_evidence": "证据不足",
    "needs_review": "需要复习", "developing": "持续观察",
    "tentatively_strong": "暂定较强"
}
LABELS_EN = {
    "untested": "Untested", "insufficient_evidence": "Insufficient evidence",
    "needs_review": "Needs review", "developing": "Developing",
    "tentatively_strong": "Tentatively strong"
}


def clean(text):
    return html.escape(str(text), quote=True)


def aggregate(bank, history):
    items = {q["id"]: q for q in bank["items"]}
    concepts = {q["concept"] for q in bank["items"]}
    groups = defaultdict(list)
    by_level = defaultdict(list)
    by_day = defaultdict(list)
    mistakes = Counter()
    criteria = defaultdict(list)
    graph_edges = set()
    for q in bank["items"]:
        groups[q["concept"]]
        for parent in q.get("prerequisites", []):
            if parent in concepts:
                graph_edges.add((parent, q["concept"]))
    for e in history:
        concept = e.get("concept")
        if concept not in concepts or type(e.get("score")) not in (int, float):
            continue
        groups[concept].append(e)
        if e.get("level") in LEVELS:
            by_level[e["level"]].append(e["score"])
        if e.get("misconception"):
            mistakes[str(e["misconception"])[:100]] += 1
        try:
            day = datetime.fromisoformat(e["at"].replace("Z", "+00:00"))
            if day.tzinfo is None:
                day = day.replace(tzinfo=timezone.utc)
            by_day[day.astimezone(timezone.utc).date().isoformat()].append(e["score"])
        except (KeyError, ValueError, TypeError, AttributeError):
            pass
        item = items.get(e.get("id"))
        if item and item["type"] == "manual":
            values = e.get("criterion_scores")
            if isinstance(values, list):
                for criterion, value in zip(item["rubric"], values):
                    if type(value) in (float, int) and 0 <= value <= 1:
                        criteria[(concept, criterion)].append(value)
    profiles = []
    for concept, events in sorted(groups.items()):
        result = estimate(events)
        dates = [due_date([e for e in events if e.get("level") == level])
                 for level in LEVELS if any(e.get("level") == level for e in events)]
        profiles.append({
            "name": concept, "status": result["label"], "rate": result["rate"],
            "count": len(events), "families": result["families"],
            "days": result["days"], "levels": result["levels"],
            "gaps": result["gaps"], "flags": result["flags"],
            "review": min((d for d in dates if d), default=None)
        })
    return {
        "subject": bank["subject"],
        "total": sum(len(x) for x in groups.values()),
        "covered": sum(bool(x) for x in groups.values()),
        "concepts": profiles,
        "edges": sorted(graph_edges),
        "levels": [{"name": name, "n": len(by_level[name]),
                    "mean": sum(by_level[name])/len(by_level[name]) if by_level[name] else None}
                   for name in LEVELS],
        "trend": [{"day": name, "n": len(vals), "mean": sum(vals)/len(vals)}
                  for name, vals in sorted(by_day.items())],
        "mistakes": [{"name": name, "count": count}
                     for name, count in sorted(mistakes.items(), key=lambda x: (-x[1], x[0]))],
        "criteria": [{"concept": c, "name": name, "n": len(vals),
                      "mean": sum(vals)/len(vals)}
                     for (c, name), vals in sorted(criteria.items())]
    }


def bar(percentage, cls="fill"):
    return '<div class="track"><span class="' + cls + '" style="width:' + str(
        max(0, min(100, round(percentage)))) + '%"></span></div>'


def knowledge_svg(data):
    """Deterministic SVG prerequisite map; plain nodes if no links exist."""
    names = [x["name"] for x in data["concepts"]]
    if not names:
        return '<p class="muted">No concepts available.</p>'
    n = len(names)
    columns = min(3, max(1, n))
    rows = (n + columns - 1)//columns
    width = 860
    w, h = 240, 76
    xgap = (width - columns*w) / (columns+1)
    positions = {name: (xgap+(index%columns)*(w+xgap), 28+(index//columns)*120)
                 for index, name in enumerate(names)}
    total_height = 42 + rows*120
    svg = ['<svg role="img" aria-label="Concept map / 知识图谱" viewBox="0 0 860 '
           + str(total_height) + '" preserveAspectRatio="xMidYMin meet">'
           '<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="7" refY="4"'
           ' orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#7396ae"/></marker></defs>']
    for first, second in data["edges"]:
        if first not in positions or second not in positions:
            continue
        ax, ay = positions[first]
        bx, by = positions[second]
        svg.append('<path d="M ' + str(ax+w/2) + ' ' + str(ay+h/2)
                   + ' L ' + str(bx+w/2) + ' ' + str(by+h/2)
                   + '" stroke="#7396ae" opacity=".65" stroke-width="1.5"'
                     ' marker-end="url(#arrow)" />')
    for entry in data["concepts"]:
        x, y = positions[entry["name"]]
        status = entry["status"]
        stroke = {"needs_review": "#edae87", "tentatively_strong": "#67d1c3",
                  "untested": "#77869b"}.get(status, "#89a6ec")
        label = entry["name"]
        if len(label) > 24:
            label = label[:21] + "..."
        svg.append('<g><title>' + clean(entry["name"]) + ' · ' + clean(status)
                   + '</title><rect x="' + str(x) + '" y="' + str(y)
                   + '" width="' + str(w) + '" height="' + str(h)
                   + '" rx="11" fill="var(--node)" stroke="' + stroke
                   + '" stroke-width="2"/><text x="' + str(x+15) + '" y="'
                   + str(y+32) + '" fill="var(--ink)" font-size="15">'
                   + clean(label) + '</text><text x="' + str(x+15) + '" y="'
                   + str(y+55) + '" fill="var(--muted)" font-size="12">'
                   + clean(LABELS_ZH.get(status, status)) + ' / '
                   + clean(LABELS_EN.get(status, status)) + '</text></g>')
    svg.append('</svg>')
    return "".join(svg)


def trend_svg(rows):
    if not rows:
        return '<p class="muted" data-zh="尚无历史记录。" data-en="No historical responses yet.">尚无历史记录。</p>'
    w, h = 860, 190
    pad = 43
    points = []
    for index, row in enumerate(rows):
        x = pad+(w-2*pad)*(index/(len(rows)-1) if len(rows)>1 else 0.5)
        y = h-pad-row["mean"]*(h-2*pad)
        points.append((x,y))
    line = " ".join(("%g,%g" % point) for point in points)
    parts = ['<svg viewBox="0 0 860 190" role="img" aria-label="Observed response trend / 作答历史走势">']
    for value in (0,0.5,1):
        y = h-pad-value*(h-2*pad)
        parts.append('<line x1="' + str(pad) + '" y1="' + str(y) + '" x2="'
                     + str(w-pad) + '" y2="' + str(y)
                     + '" stroke="var(--line)" stroke-dasharray="4 5"/>'
                     '<text x="5" y="' + str(y+5) + '" font-size="12" fill="var(--muted)">'
                     + str(int(value*100)) + '%</text>')
    parts.append('<polyline fill="none" stroke="var(--accent)" stroke-width="3" points="'
                 + line + '"/>')
    for (x,y), row in zip(points, rows):
        parts.append('<circle cx="' + str(x) + '" cy="' + str(y)
                     + '" r="4" fill="var(--accent)"><title>'
                     + clean(row["day"]) + ': ' + str(round(100*row["mean"]))
                     + '% (' + str(row["n"]) + ')</title></circle>')
    parts.append('</svg><p class="muted small">')
    parts.append(clean(rows[0]["day"]) + ' — ' + clean(rows[-1]["day"])
                 + ' · ' + str(len(rows)) + ' UTC days</p>')
    return "".join(parts)


CSS = """
:root {color-scheme: dark; --bg:#080e19;--node:#17283c;--panel:#131e30;--ink:#ecf3ff;--muted:#a6bbd1;--accent:#65d2bc;--line:#32445a;--blue:#94aeff;}
@media(prefers-color-scheme:light){:root{color-scheme:light;--bg:#f4f7fc;--node:#eff4fb;--panel:#fff;--ink:#1b2a3e;--muted:#506680;--accent:#167e78;--line:#cbd9e6;--blue:#5366b1;}}
*{box-sizing:border-box}body{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;background:var(--bg);color:var(--ink);margin:0;line-height:1.55}
main{max-width:1130px;margin:auto;padding:26px 20px 80px}header{display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:15px}
h1{font-size:clamp(25px,4vw,40px);line-height:1.2;margin:0}h2{font-size:19px;margin:0 0 14px}h3{font-size:15px;margin:0 0 10px}
p{margin:7px 0 14px}.small{font-size:12px}.muted{color:var(--muted)}
.note{border-left:3px solid var(--accent);padding:10px 14px;background:var(--panel);border-radius:6px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(195px,1fr));gap:14px;margin:20px 0}.stat,.panel{background:var(--panel);border:1px solid var(--line);border-radius:13px;padding:18px}
.stat strong{display:block;font-size:30px;font-variant-numeric:tabular-nums}.stat span{color:var(--muted)}
.sections{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:14px}
.wide{grid-column:1/-1}.row{display:flex;justify-content:space-between;gap:14px;align-items:baseline;margin:13px 0}
.track{height:9px;background:var(--line);border-radius:100px;overflow:hidden;flex:1;min-width:70px}
.fill{display:block;height:100%;background:var(--accent);border-radius:100px}
svg{display:block;width:100%;height:auto;overflow:visible}
table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;border-bottom:1px solid var(--line);padding:10px 7px;vertical-align:top}
th{color:var(--muted);font-weight:600}td.num{text-align:right;font-variant-numeric:tabular-nums}
.tablewrap{overflow-x:auto}.tag{border:1px solid var(--line);border-radius:20px;padding:2px 8px;font-size:12px;white-space:nowrap}
button{border:1px solid var(--line);background:var(--panel);color:var(--ink);padding:8px 12px;border-radius:9px;cursor:pointer}
button:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
.tabs{display:flex;gap:8px;align-items:center}body.lang-en .zh,body:not(.lang-en) .en{display:none}
a{color:var(--blue)}details{padding:8px 0}summary{cursor:pointer}
@media print{body{background:white;color:black}.stat,.panel,.note{border:1px solid #aaa;background:white}button{display:none}.track{border:1px solid #aaa}}
"""


def dashboard_html(payload, language="zh"):
    labels = LABELS_EN if language == "en" else LABELS_ZH
    concepts = payload["concepts"]
    covered = payload["covered"]
    total = len(concepts)
    review = sum(p["status"] == "needs_review" for p in concepts)
    gaps = sum(p["status"] in ("untested","insufficient_evidence") for p in concepts)
    heads = '<!doctype html><html lang="' + clean(language) + '"><head><meta charset="utf-8">'
    heads += '<meta name="viewport" content="width=device-width,initial-scale=1">'
    heads += '<meta http-equiv="Content-Security-Policy" content="default-src &#39;none&#39;; style-src &#39;unsafe-inline&#39;; script-src &#39;unsafe-inline&#39;; img-src data:">'
    heads += '<title>' + clean(payload["subject"]) + ' | Learning dashboard</title><style>' + CSS + '</style></head>'
    body = '<body class="' + ('lang-en' if language == "en" else '') + '"><main><header>'
    body += '<div><p class="muted small">Question-QA-Skill · Offline Dashboard / 离线看板</p>'
    body += '<h1>' + clean(payload["subject"]) + '</h1><p class="muted">'
    body += '<span class="zh">学习状态与回答分析</span><span class="en">Learning evidence & response analysis</span></p></div>'
    body += '<div class="tabs"><button type="button" id="zh" aria-label="中文">中文</button>'
    body += '<button type="button" id="en" aria-label="English">English</button></div></header>'
    body += '<p class="note"><span class="zh">本页全部离线生成，只含汇总数据。观察正确率与诊断指数不是经标定的掌握概率；缺少证据不代表能力差。</span>'
    body += '<span class="en">Fully offline aggregates only. Observed accuracy and heuristic index are not calibrated mastery probabilities. Missing evidence does not imply low ability.</span></p>'
    body += '<section class="grid" aria-label="Summary">'
    for number, zh, en in [(payload["total"],"已记录作答","Recorded answers"),
                            (str(covered)+'/'+str(total),"已覆盖知识点","Covered concepts"),
                            (review,"需要关注","Needs review"),
                            (gaps,"未测或证据不足","Untested / low evidence")]:
        body += '<div class="stat"><strong>' + clean(number) + '</strong><span class="zh">'
        body += clean(zh) + '</span><span class="en">' + clean(en) + '</span></div>'
    body += '</section><div class="sections"><section class="panel wide">'
    body += '<h2><span class="zh">知识结构与先修关系</span><span class="en">Concept map & prerequisites</span></h2>'
    body += knowledge_svg(payload) + '</section>'
    body += '<section class="panel wide"><h2><span class="zh">知识点证据详情</span><span class="en">Evidence per concept</span></h2>'
    body += '<div class="tablewrap"><table><thead><tr>'
    for zh,en in [("知识点","Concept"),("当前判断","Status"),("题数","Answers"),
                  ("独立题族","Families"),("观察日期","Days"),("下一复习","Review")]:
        body += '<th><span class="zh">'+zh+'</span><span class="en">'+en+'</span></th>'
    body += '</tr></thead><tbody>'
    for c in concepts:
        body += '<tr><td>' + clean(c["name"]) + '</td><td><span class="tag">'
        body += '<span class="zh">'+clean(LABELS_ZH[c["status"]])+'</span>'
        body += '<span class="en">'+clean(LABELS_EN[c["status"]])+'</span></span></td>'
        body += '<td class="num">'+str(c["count"])+'</td><td class="num">'+str(c["families"])+'</td>'
        body += '<td class="num">'+str(c["days"])+'</td><td>'+clean(c["review"] or '—')+'</td></tr>'
    body += '</tbody></table></div></section><section class="panel">'
    body += '<h2><span class="zh">认知层次作答表现</span><span class="en">Observed score by cognitive level</span></h2>'
    for level in payload["levels"]:
        body += '<div class="row"><span>'+clean(level["name"])+' ('+str(level["n"])+')</span>'
        if level["mean"] is None:
            body += '<span class="muted">—</span>'
        else:
            body += bar(100*level["mean"])+'<span>'+str(round(100*level["mean"]))+'%</span>'
        body += '</div>'
    body += '<p class="muted small"><span class="zh">这里只显示各层次已记录题目的平均得分，不代表能力水平。</span>'
    body += '<span class="en">Mean score on observed items, not a proficiency estimate.</span></p></section>'
    body += '<section class="panel"><h2><span class="zh">答题误区（已审核标签）</span>'
    body += '<span class="en">Reviewer-tagged mistakes</span></h2>'
    if not payload["mistakes"]:
        body += '<p class="muted"><span class="zh">暂未记录误区标签。</span><span class="en">No reviewed misconception tags yet.</span></p>'
    for m in payload["mistakes"]:
        body += '<div class="row"><span>'+clean(m["name"])+'</span><span class="tag">'+str(m["count"])+'</span></div>'
    body += '</section><section class="panel wide"><h2><span class="zh">历史作答变化（按 UTC 日期）</span>'
    body += '<span class="en">Observed response trend by UTC date</span></h2>'
    body += trend_svg(payload["trend"]) + '</section>'
    body += '<section class="panel wide"><h2><span class="zh">主观题评分标准分析</span>'
    body += '<span class="en">Open-response rubric criteria</span></h2>'
    if not payload["criteria"]:
        body += '<p class="muted"><span class="zh">尚无逐项审阅的主观题记录。</span>'
        body += '<span class="en">No structured open-answer reviews recorded.</span></p>'
    else:
        body += '<div class="tablewrap"><table><thead><tr><th>Concept</th><th>Criterion</th>'
        body += '<th>Reviews</th><th>Observed score</th></tr></thead><tbody>'
        for r in payload["criteria"]:
            body += '<tr><td>'+clean(r["concept"])+'</td><td>'+clean(r["name"])+'</td>'
            body += '<td>'+str(r["n"])+'</td><td>'+str(round(100*r["mean"]))+'%</td></tr>'
        body += '</tbody></table></div>'
    body += '</section></div>'
    body += '<footer><p class="muted small"><span class="zh">独立题族、时间和认知层次的证据可能不足。数据来自本地状态文件。'
    body += '这不是考试能力预测系统。可以直接使用浏览器打印或保存为 PDF。</span>'
    body += '<span class="en">Independent item, time and cognitive evidence may be missing. '
    body += 'Data is local. This is not a calibrated exam predictor. Print to PDF from the browser.</span></p></footer>'
    body += '</main><script>'
    body += """(function(){function setLang(x){document.body.classList.toggle('lang-en',x==='en');document.documentElement.lang=x==='en'?'en':'zh';document.getElementById('zh').setAttribute('aria-pressed',String(x!=='en'));document.getElementById('en').setAttribute('aria-pressed',String(x==='en'));}document.getElementById('zh').addEventListener('click',function(){setLang('zh');});document.getElementById('en').addEventListener('click',function(){setLang('en');});setLang(document.body.classList.contains('lang-en')?'en':'zh');})();"""
    body += '</script></body></html>\n'
    return heads + body


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline learning dashboard / 本地学习可视化")
    parser.add_argument("bank", help="source bank, used for concept metadata only")
    parser.add_argument("--state", default=".qa-state.json")
    parser.add_argument("--output", default="learning-dashboard.html")
    parser.add_argument("--lang", choices=("zh","en"), default="zh")
    args = parser.parse_args(argv)
    try:
        bank, _ = read_bank(args.bank)
        state = read_state(args.state)
        content = dashboard_html(aggregate(bank, state["history"]), args.lang)
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(json.dumps({"created": str(target), "bytes": len(content.encode("utf-8")),
                          "answers": len(state["history"])}, ensure_ascii=False))
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print("error: "+str(exc),file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
