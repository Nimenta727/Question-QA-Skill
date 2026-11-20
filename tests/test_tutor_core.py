"""Behavioral contracts for the minimal AI tutoring loop (synthetic events)."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import tutor_core
from scripts.qa import read_bank

ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/"examples"/"sample_bank.json"
CLI=ROOT/"scripts"/"qa.py"


def event(item,score=1,confidence="sure",hint=False,session="s",misconception=None):
    result={"id":item["id"],"concept":item["concept"],"family":item.get("family",item["id"]),
            "level":item["level"],"type":item["type"],"score":score,
            "confidence":confidence,"hint_used":hint,"session":session,
            "at":"2026-11-21T09:00:00+00:00"}
    if misconception is not None:
        result["misconception"]=misconception
    return result


class CorePedagogyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items=read_bank(BANK)[0]["items"]

    def item(self,key):
        return next(q for q in self.items if q["id"]==key)

    def test_baseline_is_single_question_not_mastery_assumption(self):
        p=tutor_core.plan(self.items,[],{"id":"s","limit":6},self.item("ALG-001"))
        self.assertEqual("baseline",p["move"])
        self.assertTrue(p["must_ask_one_question"])
        self.assertEqual("not_enough_evidence",p["evidence_status"])
        self.assertFalse(p["observation"]["mastery_probability_available"])

    def test_wrong_answer_with_explicit_prerequisite_repairs_first(self):
        concept=self.item("ALG-004").copy()
        concept["prerequisites"]=["functions"]
        e=event(concept,score=0)
        p=tutor_core.plan([concept,self.item("ALG-005")],[e],
                          {"id":"s","limit":6},self.item("ALG-005"))
        self.assertEqual("repair_prerequisite",p["move"])
        self.assertEqual("matching",p["suggestion_fit"])
        self.assertEqual("error_cause_unverified",p["evidence_status"])

    def test_wrong_without_evidence_never_diagnoses_misconception(self):
        wrong=event(self.item("ALG-002"),score=0)
        p=tutor_core.plan(self.items,[wrong],{"id":"s","limit":6})
        self.assertEqual("clarify_reasoning",p["move"])
        self.assertEqual("error_cause_unverified",p["evidence_status"])
        self.assertIn("Do not declare",p["instruction"])

    def test_explicit_reviewer_tag_remains_self_report_not_truth(self):
        wrong=event(self.item("ALG-002"),score=0,misconception="distributive_property")
        p=tutor_core.plan(self.items,[wrong],{"id":"s","limit":6})
        self.assertEqual("reviewer_tag_not_independent_diagnosis",p["evidence_status"])
        self.assertNotIn("distributive_property",json.dumps(p))

    def test_partial_credit_prompts_reasoning_not_cloned_quiz(self):
        p=tutor_core.plan(self.items,[event(self.item("ALG-004"),score=.5)],
                          {"id":"s","limit":6})
        self.assertEqual("clarify_reasoning",p["move"])

    def test_correct_but_guessed_needs_distinct_family(self):
        source=self.item("ALG-001")
        different=self.item("ALG-002")
        p=tutor_core.plan(self.items,[event(source,1,"guess")],
                          {"id":"s","limit":6},different)
        self.assertEqual("verify_independently",p["move"])
        self.assertEqual("matching",p["suggestion_fit"])
        self.assertEqual("correctness_needs_independent_confirmation",p["evidence_status"])

    def test_same_family_variant_is_not_independent_confirmation(self):
        source=self.item("ALG-001")
        duplicate=self.item("ALG-002").copy()
        duplicate["family"]=source["id"]
        p=tutor_core.plan(self.items,[event(source,1,"unsure")],
                          {"id":"s","limit":6},duplicate)
        self.assertEqual("review_or_author_better_variant",p["suggestion_fit"])

    def test_hinted_success_requires_verification(self):
        p=tutor_core.plan(self.items,[event(self.item("ALG-001"),hint=True)],
                          {"id":"s","limit":6},self.item("ALG-002"))
        self.assertEqual("verify_independently",p["move"])

    def test_unassisted_success_asks_for_transfer(self):
        p=tutor_core.plan(self.items,[event(self.item("ALG-001"))],
                          {"id":"s","limit":6},self.item("ALG-004"))
        self.assertEqual("probe_transfer",p["move"])
        self.assertEqual("matching",p["suggestion_fit"])

    def test_low_level_repeat_does_not_pass_transfer_fit(self):
        q=self.item("ALG-001")
        p=tutor_core.plan(self.items,[event(q)],{"id":"s","limit":6},
                          self.item("ALG-005"))
        self.assertEqual("review_or_author_better_variant",p["suggestion_fit"])

    def test_stop_at_session_budget_even_if_item_remains(self):
        rows=[event(self.item("ALG-001")) for _ in range(6)]
        p=tutor_core.plan(self.items,rows,{"id":"s","limit":6},self.item("ALG-004"))
        self.assertEqual("close_and_review",p["move"])
        self.assertFalse(p["must_ask_one_question"])
        self.assertIsNone(p["suggested_reviewed_item"])
        self.assertEqual("session_budget",p["stop_reason"])

    def test_exhausted_bank_calls_for_reviewed_new_variant_not_fake_answer(self):
        one=self.item("ALG-001")
        p=tutor_core.plan([one],[event(one,0)],{"id":"s","limit":6})
        self.assertEqual("draft_source_anchored_item",p["move"])
        self.assertNotIn(one["answer"],p["instruction"])

    def test_session_scope_and_gap_summary(self):
        first=event(self.item("ALG-001"),score=0,session="s")
        other=event(self.item("ALG-005"),score=1,session="older")
        result=tutor_core.compact_session_report(self.items,[other,first],
                                                 {"id":"s","limit":6})
        self.assertEqual(1,result["answered"])
        self.assertIn("functions",result["untested_concepts"])
        self.assertIsNone(result["standardized_mastery_estimate"])
        self.assertFalse(result["retention_verified"])

    def test_no_answer_key_or_student_text_in_plan(self):
        stem_source=self.item("ALG-004")
        last=event(stem_source,0,misconception="PRIVATE_ANSWER_CONTENT")
        p=tutor_core.plan(self.items,[last],{"id":"s","limit":6},
                          self.item("ALG-003"))
        blob=json.dumps(p,ensure_ascii=False)
        for protected in ("PRIVATE_ANSWER_CONTENT",stem_source["answer"] if "answer" in stem_source else "ALL_VALUES",
                          self.item("ALG-003")["answer"],self.item("ALG-003")["explanation"],
                          stem_source["stem"],stem_source["rubric"][0]):
            self.assertNotIn(protected,blob)

    def test_multiple_partial_scores_must_not_be_called_observed_success(self):
        base=self.item("ALG-001")
        variant=self.item("ALG-002")
        events=[event(base,.5),event(variant,.5)]
        summary=tutor_core.compact_session_report([base,variant],events,
                                                   {"id":"s","limit":6})
        row=summary["concepts"][0]
        self.assertEqual(2,row["partially_correct"])
        self.assertEqual("further_independent_probe_needed",row["interpretation"])

    def test_cli_next_and_answer_surface_coach_without_grading_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            bank=Path(tmp)/"bank.json"
            state=Path(tmp)/"state.json"
            example=self.item("ALG-001")
            bank.write_text(json.dumps({"version":1,"subject":"test",
                                        "items":[example]},ensure_ascii=False),
                            encoding="utf-8")
            first=subprocess.run([sys.executable,str(CLI),"next",str(bank),
                                  "--state",str(state)],cwd=str(ROOT),
                                 capture_output=True,text=True)
            self.assertEqual(0,first.returncode,first.stderr)
            prompt=json.loads(first.stdout)
            self.assertEqual("baseline",prompt["tutor_intent"]["move"])
            self.assertNotIn("answer",prompt)
            again=subprocess.run([sys.executable,str(CLI),"next",str(bank),
                                  "--state",str(state)],cwd=str(ROOT),
                                 capture_output=True,text=True)
            self.assertEqual(prompt,json.loads(again.stdout))
            answer=subprocess.run([sys.executable,str(CLI),"answer",str(bank),
                                   "--state",str(state),"--response","A"],
                                  cwd=str(ROOT),capture_output=True,text=True)
            self.assertEqual(0,answer.returncode,answer.stderr)
            result=json.loads(answer.stdout)
            self.assertEqual(0,result["score"])
            self.assertEqual("draft_source_anchored_item",
                             result["tutor_next_move"]["move"])
            self.assertEqual(1,json.loads(state.read_text())["history"][0]["score"]==0)

    def test_cli_end_after_limit_returns_teaching_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            bank=Path(tmp)/"bank.json"
            state=Path(tmp)/"state.json"
            q=self.item("ALG-001")
            bank.write_text(json.dumps({"version":1,"subject":"test",
                                        "items":[q]},ensure_ascii=False),encoding="utf-8")
            start=subprocess.run([sys.executable,str(CLI),"start",str(bank),
                                  "--state",str(state),"--mode","quick","--limit","1"],
                                 cwd=str(ROOT),capture_output=True,text=True)
            self.assertEqual(0,start.returncode,start.stderr)
            subprocess.run([sys.executable,str(CLI),"next",str(bank),"--state",str(state)],
                           cwd=str(ROOT),check=True,capture_output=True)
            ans=subprocess.run([sys.executable,str(CLI),"answer",str(bank),
                                "--state",str(state),"--response","A"],
                               cwd=str(ROOT),capture_output=True,text=True)
            self.assertEqual("close_and_review",json.loads(ans.stdout)
                             ["tutor_next_move"]["move"])
            result=subprocess.run([sys.executable,str(CLI),"next",str(bank),
                                   "--state",str(state)],cwd=str(ROOT),
                                  capture_output=True,text=True)
            self.assertEqual(0,result.returncode,result.stderr)
            payload=json.loads(result.stdout)
            self.assertTrue(payload["complete"])
            self.assertEqual(1,payload["teaching_summary"]["answered"])


if __name__=="__main__":
    unittest.main()
