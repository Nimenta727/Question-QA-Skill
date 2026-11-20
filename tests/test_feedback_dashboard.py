"""Assessment and dashboard regression tests, Python standard library only."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from scripts.feedback import assess_rubric, parse_judgments
from scripts.dashboard import aggregate, dashboard_html, knowledge_svg
from scripts.qa import read_bank

ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/"examples"/"sample_bank.json"
QA=ROOT/"scripts"/"qa.py"
DASH=ROOT/"scripts"/"dashboard.py"


def run(script, *args):
    return subprocess.run([sys.executable,str(script),*map(str,args)],
                          cwd=str(ROOT),capture_output=True,text=True)


def review():
    return [{"score":1,"evidence":"showed all algebraic steps",
             "feedback":"clear and correct"},
            {"score":0.5,"evidence":"described case without justification",
             "feedback":"justify the condition"},
            {"score":0,"evidence":"case absent","feedback":"cover the remaining case"}]


class RubricTests(unittest.TestCase):
    def test_criterion_scoring(self):
        result=assess_rubric(["a","b","c"],json.dumps(review()))
        self.assertAlmostEqual(0.5,result["score"])
        self.assertEqual(["b","c"],result["improve"])
        self.assertEqual("criterion_rubric_review",result["method"])

    def test_missing_criterion_rejected(self):
        with self.assertRaises(ValueError):
            parse_judgments("[]",["x"])

    def test_invalid_criterion_score_rejected(self):
        with self.assertRaises(ValueError):
            parse_judgments(json.dumps([{"score":0.8,"evidence":"x",
                                        "feedback":"y"}]),["x"])

    def test_missing_evidence_rejected(self):
        with self.assertRaises(ValueError):
            parse_judgments(json.dumps([{"score":1,"evidence":"",
                                        "feedback":"y"}]),["x"])

    def test_extra_fields_rejected(self):
        with self.assertRaises(ValueError):
            parse_judgments(json.dumps([{"score":1,"evidence":"x",
                                        "feedback":"y","answer":"secret"}]),["x"])

    def test_review_does_not_persist_answer_or_evidence(self):
        data,_=read_bank(BANK)
        item=next(x for x in data["items"] if x["type"]=="manual")
        with tempfile.TemporaryDirectory() as tmp:
            bank=Path(tmp)/"bank.json"
            state=Path(tmp)/"state.json"
            bank.write_text(json.dumps({"version":1,"subject":"test",
                                        "items":[item]},ensure_ascii=False),encoding="utf-8")
            self.assertEqual(0,run(QA,"next",bank,"--state",state).returncode)
            secret="PRIVATE_ANSWER_DO_NOT_STORE"
            result=run(QA,"answer",bank,"--state",state,"--response",secret,
                       "--reason","reviewed independently",
                       "--rubric-judgments",json.dumps(review()))
            self.assertEqual(0,result.returncode,result.stderr)
            self.assertAlmostEqual(0.5,json.loads(result.stdout)["score"])
            contents=state.read_text()
            self.assertNotIn(secret,contents)
            self.assertNotIn("showed all algebraic steps",contents)
            self.assertNotIn("clear and correct",contents)
            self.assertEqual([1.0,0.5,0.0],
                             json.loads(contents)["history"][0]["criterion_scores"])

    def test_invalid_review_preserves_pending(self):
        data,_=read_bank(BANK)
        item=next(x for x in data["items"] if x["type"]=="manual")
        with tempfile.TemporaryDirectory() as tmp:
            bank=Path(tmp)/"bank.json"
            state=Path(tmp)/"state.json"
            bank.write_text(json.dumps({"version":1,"subject":"test",
                                        "items":[item]},ensure_ascii=False),encoding="utf-8")
            run(QA,"next",bank,"--state",state)
            result=run(QA,"answer",bank,"--state",state,"--response","x",
                       "--reason","reviewed","--rubric-judgments","[]")
            self.assertNotEqual(0,result.returncode)
            self.assertIsNotNone(json.loads(state.read_text())["pending"])

    def test_equivalent_short_requires_explicit_review(self):
        data,_=read_bank(BANK)
        item=next(x for x in data["items"] if x["type"]=="short")
        with tempfile.TemporaryDirectory() as tmp:
            bank=Path(tmp)/"bank.json"
            state=Path(tmp)/"state.json"
            bank.write_text(json.dumps({"version":1,"subject":"test",
                                        "items":[item]},ensure_ascii=False),encoding="utf-8")
            run(QA,"next",bank,"--state",state)
            bad=run(QA,"answer",bank,"--state",state,"--response","07",
                    "--review-equivalent")
            self.assertNotEqual(0,bad.returncode)
            good=run(QA,"answer",bank,"--state",state,"--response","07",
                     "--review-equivalent","--reason","leading zero is same integer")
            self.assertEqual(0,good.returncode,good.stderr)
            self.assertEqual("reviewed_equivalent_answer",json.loads(good.stdout)["method"])
            self.assertNotIn('"response"',state.read_text())

    def test_choice_cannot_override_key(self):
        data,_=read_bank(BANK)
        item=next(x for x in data["items"] if x["type"]=="single")
        with tempfile.TemporaryDirectory() as tmp:
            bank=Path(tmp)/"bank.json"
            state=Path(tmp)/"state.json"
            bank.write_text(json.dumps({"version":1,"subject":"test",
                                        "items":[item]},ensure_ascii=False),encoding="utf-8")
            run(QA,"next",bank,"--state",state)
            got=run(QA,"answer",bank,"--state",state,"--response","B",
                    "--review-equivalent","--reason","must not override choice")
            self.assertNotEqual(0,got.returncode)


class DashboardTests(unittest.TestCase):
    def test_never_embeds_answers_questions_or_responses(self):
        bank={"subject":"Algebra","items":[{"id":"one","concept":"x",
              "type":"short","level":"recall","answer":"SECRET_ANSWER",
              "stem":"SECRET_QUESTION","prerequisites":[]}]}
        history=[{"id":"one","concept":"x","level":"recall","type":"short",
                  "score":1,"confidence":"sure",
                  "response":"SECRET_RESPONSE","at":"2026-11-20T10:00:00+00:00"}]
        page=dashboard_html(aggregate(bank,history))
        for marker in ("SECRET_ANSWER","SECRET_QUESTION","SECRET_RESPONSE"):
            self.assertNotIn(marker,page)

    def test_unsafe_source_escaped(self):
        bank={"subject":'<img src=x onerror=alert(1)>',"items":[
              {"id":"a","concept":"<script>alert(5)</script>",
               "type":"single","level":"recall","prerequisites":[]}]}
        page=dashboard_html(aggregate(bank,[]))
        self.assertNotIn('<img src=x onerror=alert(1)>',page)
        self.assertNotIn('<script>alert(5)</script>',page)
        self.assertIn("&lt;script&gt;",page)

    def test_untested_concept_visible(self):
        bank={"subject":"test","items":[{"id":"x","concept":"unknown",
              "type":"short","level":"recall","prerequisites":[]}]}
        result=aggregate(bank,[])
        self.assertEqual("untested",result["concepts"][0]["status"])
        self.assertEqual(0,result["total"])

    def test_stored_criterion_scores_aggregated(self):
        bank={"subject":"test","items":[{"id":"a","concept":"x",
              "type":"manual","level":"apply","rubric":["reason","answer"],
              "prerequisites":[]}]}
        hist=[{"id":"a","concept":"x","level":"apply","score":0.5,
               "criterion_scores":[1,0],"confidence":"none",
               "at":"2026-11-20T12:00:00+00:00"}]
        data=aggregate(bank,hist)
        self.assertEqual(2,len(data["criteria"]))
        self.assertIn("reason",dashboard_html(data))

    def test_cli_bilingual_and_self_contained(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/"learning.html"
            got=run(DASH,BANK,"--state",Path(tmp)/"none.json",
                    "--output",target,"--lang","en")
            self.assertEqual(0,got.returncode,got.stderr)
            page=target.read_text(encoding="utf-8")
            self.assertIn('<html lang="en">',page)
            self.assertIn("Concept map",page)
            self.assertNotIn("<script src=",page)
            self.assertNotIn("https://",page)

    def test_prerequisites_and_trend_are_rendered(self):
        bank={"subject":"test","items":[
            {"id":"a","concept":"parent","level":"recall","type":"short",
             "prerequisites":[]},
            {"id":"b","concept":"child","level":"apply","type":"short",
             "prerequisites":["parent"]}]}
        hist=[{"id":"a","concept":"parent","level":"recall","score":1,
               "confidence":"sure","at":"2026-11-20T10:00:00+00:00"}]
        data=aggregate(bank,hist)
        self.assertEqual([("parent","child")],data["edges"])
        self.assertIn("polyline",dashboard_html(data))
        self.assertIn("marker-end",knowledge_svg(data))


if __name__=="__main__":
    unittest.main()
