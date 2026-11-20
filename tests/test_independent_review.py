"""Independent review, adjudication, evidence anchoring and privacy tests."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import assessment_engine
from scripts.qa import read_bank

ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/"examples"/"sample_bank.json"
QA=ROOT/"scripts"/"qa.py"
ANSWER="When a != 0, x=b/a. If a is 0 and b isn't, no solution. If a=b=0, any x works."


def packet(scores_a=(1,.5,0), scores_b=(1,.5,0)):
    reviews=[]
    for reviewer,values in (("teacher-A",scores_a),("agent-B",scores_b)):
        reviews.append({
            "reviewer_id": reviewer, "independent": True,
            "judgments": [{
                "score":value, "quote":"x=b/a",
                "evidence":"Reviewer checked the case against the algebraic reasoning.",
                "feedback":"Explain each boundary case more explicitly."
            } for value in values]
        })
    return {"reviews":reviews}


def arbitrate():
    return {"adjudicator_id":"teacher-C","decisions":[{
        "criterion_index":1, "score":0.5,
        "reason":"The first edge case was covered partially.",
        "quote":"x=b/a"
    }]}


def run(*args):
    return subprocess.run([sys.executable,str(QA),*map(str,args)],
                          text=True,capture_output=True,cwd=str(ROOT))


class DualReviewerEngineTests(unittest.TestCase):
    def test_full_agreement_no_adjudicator(self):
        result=assessment_engine.resolve(["one","two","three"],ANSWER,json.dumps(packet()))
        self.assertEqual("two_reviewer_agreement",result["method"])
        self.assertEqual(1.0,result["agreement"]["rate"])
        self.assertAlmostEqual(.5,result["score"])

    def test_disagreement_requires_arbitration(self):
        payload=packet(scores_b=(1,0,0))
        with self.assertRaisesRegex(ValueError,"review_disagreement"):
            assessment_engine.resolve(["one","two","three"],ANSWER,json.dumps(payload))

    def test_disagreement_third_party_decides(self):
        payload=packet(scores_b=(1,0,0))
        result=assessment_engine.resolve(["one","two","three"],ANSWER,
                                         json.dumps(payload),json.dumps(arbitrate()))
        self.assertEqual("adjudicated_rubric_review",result["method"])
        self.assertEqual([2],result["agreement"]["disputed_indices"])
        self.assertAlmostEqual(2/3,result["agreement"]["rate"])
        self.assertEqual([1,.5,0],[r["score"] for r in result["criteria"]])

    def test_forged_quote_rejected(self):
        review=packet()
        review["reviews"][0]["judgments"][1]["quote"]="not found in student text"
        with self.assertRaisesRegex(ValueError,"quote"):
            assessment_engine.resolve(["one","two","three"],ANSWER,json.dumps(review))

    def test_same_reviewer_rejected(self):
        review=packet()
        review["reviews"][1]["reviewer_id"]="teacher-A"
        with self.assertRaisesRegex(ValueError,"distinct"):
            assessment_engine.resolve(["one","two","three"],ANSWER,json.dumps(review))

    def test_adjudicator_cannot_self_arbitrate(self):
        review=packet(scores_b=(1,0,0))
        decision=arbitrate()
        decision["adjudicator_id"]="agent-B"
        with self.assertRaisesRegex(ValueError,"distinct"):
            assessment_engine.resolve(["one","two","three"],ANSWER,
                                      json.dumps(review),json.dumps(decision))

    def test_arbitrator_must_cover_only_disputed_criterion(self):
        review=packet(scores_b=(1,0,0))
        decision=arbitrate()
        decision["decisions"][0]["criterion_index"]=0
        with self.assertRaisesRegex(ValueError,"criterion"):
            assessment_engine.resolve(["one","two","three"],ANSWER,
                                      json.dumps(review),json.dumps(decision))

    def test_nonfinite_or_bool_score_rejected(self):
        review=packet()
        review["reviews"][1]["judgments"][0]["score"]=True
        with self.assertRaises(ValueError):
            assessment_engine.resolve(["one","two","three"],ANSWER,json.dumps(review))
        review["reviews"][1]["judgments"][0]["score"]=float("nan")
        with self.assertRaises(ValueError):
            assessment_engine.resolve(["one","two","three"],ANSWER,json.dumps(review))

    def test_extra_fields_rejected(self):
        review=packet()
        review["reviews"][0]["private_answer"]=ANSWER
        with self.assertRaisesRegex(ValueError,"reviewer record"):
            assessment_engine.resolve(["one","two","three"],ANSWER,json.dumps(review))

    def test_no_arbitration_for_agreed_scores(self):
        with self.assertRaisesRegex(ValueError,"not needed"):
            assessment_engine.resolve(["one","two","three"],ANSWER,json.dumps(packet()),
                                      json.dumps(arbitrate()))


class DualReviewCLITests(unittest.TestCase):
    def prepare(self,tmp):
        data,_=read_bank(BANK)
        manual=next(q for q in data["items"] if q["type"]=="manual")
        bank=Path(tmp)/"bank.json"
        state=Path(tmp)/"state.json"
        bank.write_text(json.dumps({"version":1,"subject":"test","items":[manual]},
                                   ensure_ascii=False),encoding="utf-8")
        start=run("next",bank,"--state",state)
        self.assertEqual(0,start.returncode,start.stderr)
        return bank,state

    def test_conflict_preserves_pending_then_adjudicates_without_leakage(self):
        with tempfile.TemporaryDirectory() as tmp:
            bank,state=self.prepare(tmp)
            answer_file=Path(tmp)/"private_answer.txt"
            answer_file.write_text(ANSWER,encoding="utf-8")
            reviews=Path(tmp)/"review.json"
            reviews.write_text(json.dumps(packet(scores_b=(1,0,0))),encoding="utf-8")
            waiting=run("answer",bank,"--state",state,"--response-file",answer_file,
                        "--independent-reviews","@"+str(reviews))
            self.assertEqual(2,waiting.returncode)
            self.assertIn("review_disagreement",waiting.stderr)
            self.assertIsNotNone(json.loads(state.read_text())["pending"])
            decision=Path(tmp)/"decisions.json"
            decision.write_text(json.dumps(arbitrate()),encoding="utf-8")
            done=run("answer",bank,"--state",state,"--response-file",answer_file,
                     "--independent-reviews","@"+str(reviews),
                     "--adjudication","@"+str(decision))
            self.assertEqual(0,done.returncode,done.stderr)
            out=json.loads(done.stdout)
            self.assertEqual("adjudicated_rubric_review",out["method"])
            self.assertEqual([1,.5,0],json.loads(state.read_text())["history"][0]["criterion_scores"])
            stored=state.read_text()
            self.assertEqual(1,json.loads(stored)["history"][0]["review_disputes"])
            self.assertNotIn("When a != 0",stored)
            self.assertNotIn("teacher-A",stored)
            self.assertNotIn("agent-B",stored)
            self.assertNotIn("teacher-C",stored)
            self.assertNotIn("x=b/a",stored)
            self.assertNotIn("Reviewer checked",stored)
            self.assertIsNone(json.loads(stored)["pending"])

    def test_no_response_file_or_response_rejected_without_state_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            bank,state=self.prepare(tmp)
            rejected=run("answer",bank,"--state",state,
                         "--independent-reviews",json.dumps(packet()))
            self.assertEqual(2,rejected.returncode)
            self.assertTrue(json.loads(state.read_text())["pending"])

    def test_old_manual_score_compatible(self):
        with tempfile.TemporaryDirectory() as tmp:
            bank,state=self.prepare(tmp)
            old=run("answer",bank,"--state",state,"--response","algebra",
                    "--score","0.5","--reason","legacy independent manual review")
            self.assertEqual(0,old.returncode,old.stderr)
            self.assertEqual(.5,json.loads(old.stdout)["score"])

    def test_combined_review_modes_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            bank,state=self.prepare(tmp)
            bad=run("answer",bank,"--state",state,"--response",ANSWER,
                    "--score","1","--independent-reviews",json.dumps(packet()))
            self.assertEqual(2,bad.returncode)
            self.assertTrue(json.loads(state.read_text())["pending"])


if __name__ == "__main__":
    unittest.main()
