"""Behavioral tests for fail-closed, source-bound model question critiques."""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import model_audit, question_quality
from scripts.qa import read_bank

ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/"examples"/"sample_bank.json"
CLI=ROOT/"scripts"/"model_audit.py"


def completed_packet(bank,digest,source_path=None):
    packet=model_audit.make_template(bank,digest,source_path,"author-A")
    packet["auditor_id"]="separate-reviewer-B"
    packet["independence_self_declared"]=True
    warnings={q["id"]:[] for q in bank["items"]}
    for finding in question_quality.audit(bank,digest):
        if finding["severity"]=="warning" and finding.get("item_id") in warnings:
            warnings[finding["item_id"]].append(finding["code"])
    for q in bank["items"]:
        row=packet["items"][q["id"]]
        row["decision"]="pass"
        row["independent_answer"]=(
            q["answer"] if q["type"] in ("single","short") else
            "The learner must explain each necessary case with a valid derivation."
        )
        row["independent_solution"]=(
            "Independent reasoning checks all stated premises and solves "
            "the item before comparing the answer key; see the test fixture."
        )
        row["source_quote"]=(
            "SOURCE: independent authorized lesson text is provided here."
            if source_path is not None else "")
        row["accepted_alternatives"]=[]
        row["distractor_analyses"]=(
            {letter:"This option contradicts the independently derived "
                     "answer and represents a distinct test misconception."
             for letter in "ABCD" if letter != q["answer"]}
            if q["type"]=="single" else {})
        row["rubric_analyses"]=(
            ["This criterion has an independently testable observable "
             "success condition and is not duplicated by another criterion."
             for _ in q["rubric"]] if q["type"]=="manual" else [])
        for check in model_audit.CHECKS:
            row["checks"][check]={
                "result":"pass",
                "reason":"Specific reviewer analysis of premises and learning "
                         "objective for this synthetic regression case: "+q["id"]
            }
        row["acknowledged_static_warnings"]=warnings[q["id"]]
    return packet


class AuditContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank,cls.digest=read_bank(BANK)

    def test_blank_form_cannot_auto_approve(self):
        packet=model_audit.make_template(self.bank,self.digest)
        self.assertTrue(all(item["decision"]=="needs_review"
                            for item in packet["items"].values()))
        self.assertTrue(all(all(v["result"]=="uncertain" for v in q["checks"].values())
                            for q in packet["items"].values()))
        verdict=model_audit.verify(self.bank,self.digest,packet)
        self.assertEqual("blocked",verdict["gate"])
        self.assertFalse(verdict["actual_semantic_correctness_proven"])

    def test_well_formed_synthetic_reviews_have_limited_status(self):
        packet=completed_packet(self.bank,self.digest)
        result=model_audit.verify(self.bank,self.digest,packet)
        self.assertEqual("model_review_recorded_for_practice",result["gate"])
        self.assertTrue(result["can_present_for_formative_practice"])
        self.assertFalse(result["actual_semantic_correctness_proven"])
        self.assertFalse(result["actual_independent_reviewer_identity_proven"])
        self.assertFalse(result["suitable_for_high_stakes_exams_without_human_review"])
        self.assertNotIn('"options"',json.dumps(result))
        self.assertNotIn("3x=15",json.dumps(result))

    def test_author_cannot_claim_independent_review(self):
        packet=completed_packet(self.bank,self.digest)
        packet["auditor_id"]="author-A"
        r=model_audit.verify(self.bank,self.digest,packet)
        self.assertIn("independent_model_review_not_declared",
                      {x["code"] for x in r["failures"]})
        packet["auditor_id"]="another-reviewer"
        packet["independence_self_declared"]=False
        self.assertEqual("blocked",model_audit.verify(self.bank,self.digest,packet)["gate"])

    def test_bank_mutation_invalidates_all_review_packets(self):
        packet=completed_packet(self.bank,self.digest)
        bad=model_audit.verify(self.bank,"changed-bank-sha",packet)
        self.assertIn("bank_hash_mismatch",{x["code"] for x in bad["failures"]})

    def test_independent_wrong_answer_rejected_even_with_all_passes(self):
        packet=completed_packet(self.bank,self.digest)
        packet["items"]["ALG-001"]["independent_answer"]="A"
        bad=model_audit.verify(self.bank,self.digest,packet)
        self.assertIn("independent_answer_conflicts_with_key",
                      {x["code"] for x in bad["failures"]})

    def test_equivalent_short_math_answer_allowed_only_when_opted_in(self):
        packet=completed_packet(self.bank,self.digest)
        packet["items"]["ALG-003"]["independent_answer"]="14/2"
        result=model_audit.verify(self.bank,self.digest,packet)
        self.assertEqual("model_review_recorded_for_practice",result["gate"])
        packet["items"]["ALG-003"]["independent_answer"]="seven"
        result=model_audit.verify(self.bank,self.digest,packet)
        self.assertIn("independent_answer_conflicts_with_key",
                      {f["code"] for f in result["failures"]})

    def test_missing_one_criterion_and_unresolved_issue_blocks(self):
        packet=completed_packet(self.bank,self.digest)
        del packet["items"]["ALG-001"]["checks"]["novelty"]
        self.assertIn("review_criteria_incomplete",
                      {f["code"] for f in model_audit.verify(
                          self.bank,self.digest,packet)["failures"]})
        packet=completed_packet(self.bank,self.digest)
        packet["items"]["ALG-001"]["checks"]["ambiguity_and_conditions"]["result"]="uncertain"
        self.assertIn("review_criterion_not_passed",
                      {f["code"] for f in model_audit.verify(
                          self.bank,self.digest,packet)["failures"]})
        packet=completed_packet(self.bank,self.digest)
        packet["items"]["ALG-001"]["risk_notes"]=["Potential second valid answer"]
        self.assertIn("unresolved_risks",
                      {f["code"] for f in model_audit.verify(
                          self.bank,self.digest,packet)["failures"]})

    def test_empty_generic_checklist_prose_fails(self):
        packet=completed_packet(self.bank,self.digest)
        packet["items"]["ALG-001"]["checks"]["independent_solution"]["reason"]="OK"
        bad=model_audit.verify(self.bank,self.digest,packet)
        self.assertIn("review_criterion_incomplete",{f["code"] for f in bad["failures"]})

    def test_all_three_distractors_required_and_open_rubric_checked(self):
        packet=completed_packet(self.bank,self.digest)
        del packet["items"]["ALG-001"]["distractor_analyses"]["A"]
        bad=model_audit.verify(self.bank,self.digest,packet)
        self.assertIn("three_distractors_not_analyzed",{f["code"] for f in bad["failures"]})
        packet=completed_packet(self.bank,self.digest)
        packet["items"]["ALG-004"]["rubric_analyses"].pop()
        bad=model_audit.verify(self.bank,self.digest,packet)
        self.assertIn("rubric_not_independently_checked",{f["code"] for f in bad["failures"]})

    def test_static_warning_must_be_accepted_explicitly(self):
        packet=completed_packet(self.bank,self.digest)
        # This warning is emitted because the source is an original example.
        modified=copy.deepcopy(self.bank)
        modified["items"][0]["explanation"]="Short"
        packet["items"]["ALG-001"]["acknowledged_static_warnings"]=[]
        bad=model_audit.verify(modified,self.digest,packet)
        self.assertIn("static_warnings_unresolved",{f["code"] for f in bad["failures"]})

    def test_source_quote_must_exist_in_exact_supplied_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"lesson.txt"
            source.write_text("SOURCE: independent authorized lesson text is provided here.",
                              encoding="utf-8")
            course=copy.deepcopy(self.bank)
            for q in course["items"]:
                q["source"]="lesson:verified instructor extract"
            packet=completed_packet(course,self.digest,source)
            ok=model_audit.verify(course,self.digest,packet,source,True)
            self.assertTrue(ok["can_present_for_formative_practice"])
            packet["items"]["ALG-001"]["source_quote"]="This sentence was never in the lesson."
            bad=model_audit.verify(course,self.digest,packet,source,True)
            self.assertIn("source_quote_not_found",{f["code"] for f in bad["failures"]})
            packet=completed_packet(course,self.digest,source)
            source.write_text("changed source",encoding="utf-8")
            bad=model_audit.verify(course,self.digest,packet,source,True)
            self.assertIn("source_hash_mismatch",{f["code"] for f in bad["failures"]})

    def test_teacher_course_claim_rejected_without_source(self):
        packet=completed_packet(self.bank,self.digest)
        result=model_audit.verify(self.bank,self.digest,packet,require_course=True)
        self.assertIn("source_mode_invalid_or_course_required",
                      {f["code"] for f in result["failures"]})

    def test_course_mode_rejects_original_example_marked_as_teacher_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"lesson.txt"
            source.write_text("SOURCE: independent authorized lesson text is provided here.",
                              encoding="utf-8")
            packet=completed_packet(self.bank,self.digest,source)
            result=model_audit.verify(self.bank,self.digest,packet,source,True)
            self.assertIn("original_example_not_course_citation",
                          {x["code"] for x in result["failures"]})

    def test_cli_unapproved_template_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            template=Path(tmp)/"template.json"
            made=subprocess.run([sys.executable,str(CLI),str(BANK),"--template",
                                 str(template)],cwd=str(ROOT),text=True,capture_output=True)
            self.assertEqual(0,made.returncode,made.stderr)
            again=subprocess.run([sys.executable,str(CLI),str(BANK),"--template",
                                 str(template)],cwd=str(ROOT),text=True,capture_output=True)
            self.assertNotEqual(0,again.returncode)
            checked=subprocess.run([sys.executable,str(CLI),str(BANK),"--review",
                                    str(template)],cwd=str(ROOT),text=True,capture_output=True)
            self.assertEqual(2,checked.returncode)
            self.assertEqual("blocked",json.loads(checked.stdout)["gate"])

    def test_cli_accepted_synthetic_review_hides_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            review=Path(tmp)/"review.json"
            review.write_text(json.dumps(completed_packet(self.bank,self.digest)),
                              encoding="utf-8")
            test=subprocess.run([sys.executable,str(CLI),str(BANK),"--review",
                                 str(review)],cwd=str(ROOT),text=True,capture_output=True)
            self.assertEqual(0,test.returncode,test.stderr)
            data=json.loads(test.stdout)
            self.assertEqual("model_review_recorded_for_practice",data["gate"])
            self.assertNotIn('"answer"',test.stdout)
            self.assertNotIn('"question"',test.stdout)


if __name__=="__main__":
    unittest.main()
