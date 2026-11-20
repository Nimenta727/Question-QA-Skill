"""Independent observed evidence, historical baseline and question selection."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import adaptive_engine, diagnosis, evidence_engine, prediction_engine
from scripts.qa import read_bank

ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/"examples"/"sample_bank.json"
CLI=ROOT/"scripts"/"qa.py"


def cli(*args):
    return subprocess.run([sys.executable,str(CLI),*map(str,args)],
                          text=True,capture_output=True,cwd=str(ROOT))


def e(item, concept="linear-equations", score=1, day="2026-11-20",
      level="recall",confidence="sure"):
    return {"id":item,"family":item,"concept":concept,"level":level,
            "score":score,"type":"short","confidence":confidence,
            "difficulty":2,"hint_used":False,"at":day+"T10:00:00+00:00"}


class EvidenceTests(unittest.TestCase):
    def test_missing_evidence_is_not_zero_mastery(self):
        result=evidence_engine.profile([])
        self.assertEqual("untested",result["label"])
        self.assertIsNone(result["heuristic_evidence_index"])
        self.assertFalse(result["calibrated_probability"])
        self.assertFalse(result["gates"]["observed_on_multiple_utc_dates"])

    def test_independence_and_delayed_observations_are_separate(self):
        items=[e("a"),e("b"),e("c"),e("a",day="2026-11-21",level="transfer")]
        result=evidence_engine.profile(items)
        self.assertTrue(result["gates"]["at_least_three_independent_item_families"])
        self.assertTrue(result["gates"]["observed_on_multiple_utc_dates"])
        self.assertTrue(result["gates"]["verified_higher_order_success"])
        self.assertFalse(result["calibrated_probability"])
        self.assertEqual(diagnosis.estimate(items)["rate"],
                         result["heuristic_evidence_index"])

    def test_same_day_repeats_do_not_create_independent_families(self):
        items=[e("a"),e("a"),e("a")]
        result=evidence_engine.profile(items)
        self.assertEqual(1,result["independent_item_families"])
        self.assertIn("few_independent_item_families",result["missing_evidence"])


class BaselineTests(unittest.TestCase):
    def test_historical_average_independent_of_evidence_gates(self):
        rows=[e("q1",score=1),e("q2",score=0)]
        forecast=prediction_engine.history_baseline(rows)
        self.assertEqual(.5,forecast["smoothed_history_score"])
        self.assertEqual(.5,forecast["observed_mean"])
        self.assertFalse(forecast["calibrated"])
        self.assertFalse(forecast["is_mastery_probability"])
        self.assertNotIn("label",forecast)

    def test_zero_history_does_not_claim_mastery(self):
        forecast=prediction_engine.history_baseline([])
        self.assertIsNone(forecast["observed_mean"])
        self.assertEqual(0,forecast["observations"])

    def test_reject_invalid_scores_and_priors(self):
        with self.assertRaises(ValueError):
            prediction_engine.history_baseline([{"score":float("nan")}])
        with self.assertRaises(ValueError):
            prediction_engine.history_baseline([{"score":True}])
        with self.assertRaises(ValueError):
            prediction_engine.history_baseline([],prior=2)


class ExplainableSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank,_=read_bank(BANK)

    def test_preserves_existing_policy(self):
        rows=[e("ALG-001")]
        old=diagnosis.select_item(self.bank["items"],rows)
        new,why=adaptive_engine.choose(self.bank["items"],rows)
        self.assertEqual(old["id"],new["id"])
        self.assertEqual("rule_based_v02_unchanged",why["policy"])
        self.assertNotIn("answer",json.dumps(why))

    def test_repair_after_mistake(self):
        history=[e("ALG-001",score=0)]
        item,why=adaptive_engine.choose(self.bank["items"],history,
                                         session_history=history)
        self.assertIsNotNone(item)
        self.assertIn("follow_up_after_incorrect_answer",why["reason_codes"])

    def test_verification_after_guess(self):
        history=[e("ALG-001",score=1,confidence="guess")]
        item,why=adaptive_engine.choose(self.bank["items"],history,
                                         session_history=history)
        self.assertIsNotNone(item)
        self.assertIn("verify_uncertain_or_assisted_answer",why["reason_codes"])

    def test_asks_no_item_when_focus_is_exhausted(self):
        item,reason=adaptive_engine.choose(self.bank["items"],[],
                                            session_history=[
                                                e(q["id"]) for q in self.bank["items"]
                                                if q["concept"]=="proportions"],
                                            focus="proportions")
        self.assertIsNone(item)
        self.assertIsNone(reason)

    def test_cli_next_selection_stable_and_no_answer_leakage(self):
        with tempfile.TemporaryDirectory() as tmp:
            state=Path(tmp)/"state.json"
            first=cli("next",BANK,"--state",state)
            self.assertEqual(0,first.returncode,first.stderr)
            obj=json.loads(first.stdout)
            self.assertIn("selection",obj)
            self.assertNotIn("answer",obj)
            self.assertNotIn("explanation",obj)
            second=cli("next",BANK,"--state",state)
            self.assertEqual(obj,json.loads(second.stdout))
            stored=state.read_text()
            self.assertIn("selection",stored)

    def test_cli_json_survives_legacy_windows_code_page(self):
        # Emulate a Windows shell that cannot encode Chinese glyphs.
        import os
        with tempfile.TemporaryDirectory() as tmp:
            state=Path(tmp)/"state.json"
            env=os.environ.copy()
            env["PYTHONIOENCODING"]="cp1252:strict"
            env["PYTHONUTF8"]="0"
            child=subprocess.run([sys.executable,str(CLI),"next",str(BANK),
                                  "--state",str(state)],capture_output=True,
                                 text=True,encoding="ascii",env=env)
            self.assertEqual(0,child.returncode,child.stderr)
            data=json.loads(child.stdout)
            self.assertIn("question",data)
            self.assertIn("selection",data)
            self.assertTrue(data["question"])
            self.assertTrue(any(ord(c)>127 for c in data["question"]))

    def test_cli_report_keeps_backcompat_but_separates_engines(self):
        with tempfile.TemporaryDirectory() as tmp:
            state=Path(tmp)/"state.json"
            self.assertEqual(0,cli("next",BANK,"--state",state).returncode)
            self.assertEqual(0,cli("answer",BANK,"--state",state,
                                    "--response","B").returncode)
            rep=cli("report","--state",state,"--bank",BANK)
            self.assertEqual(0,rep.returncode,rep.stderr)
            data=json.loads(rep.stdout)
            row=next(x for x in data["concepts"] if x["count"]>0)
            self.assertIn("rate",row)
            self.assertIn("evidence_profile",row)
            self.assertIn("prediction_baseline",row)
            self.assertFalse(row["prediction_baseline"]["calibrated"])


if __name__=="__main__":
    unittest.main()
