"""Question quality, arithmetic guardrails and reviewed-bank digest tests."""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.question_quality import _number, audit, check_witness, report
from scripts.qa import read_bank

ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/"examples"/"sample_bank.json"
QUALITY=ROOT/"scripts"/"question_quality.py"


def sample():
    bank, digest=read_bank(BANK)
    return copy.deepcopy(bank), digest


class QualityMathTests(unittest.TestCase):
    def test_exact_rationals(self):
        self.assertEqual(5,_number("(19-4)/3"))
        self.assertEqual(1,_number("1/3+1/3+1/3"))
        self.assertEqual(-2,_number("-5+3"))

    def test_no_exec_or_attribute_access(self):
        for expr in ("__import__('os').system('echo x')","1**2000",
                     "x+1","[1,2]","(1).__class__","1/0","10**1000"):
            with self.subTest(expr=expr):
                with self.assertRaises((ValueError, SyntaxError)):
                    _number(expr)

    def test_bounded_depth_and_large_values(self):
        with self.assertRaises(ValueError):
            _number("("+("1+"*40)+"1"+(")"*40))

    def test_key_matches_number_witness(self):
        q=sample()[0]["items"][0]
        q["verification"]={"kind":"arithmetic","expression":"(19-4)/3"}
        self.assertIsNone(check_witness(q))
        q["answer"]="B"
        self.assertIn("mismatch",check_witness(q))

    def test_mathematical_equivalent_distractor(self):
        q=sample()[0]["items"][0]
        q["verification"]={"kind":"arithmetic","expression":"(19-4)/3"}
        q["options"][0]="10/2"
        self.assertIn("multiple numerically equivalent",check_witness(q))

    def test_manual_witness_unsupported(self):
        q=next(i for i in sample()[0]["items"] if i["type"]=="manual")
        q["verification"]={"kind":"arithmetic","expression":"2+3"}
        self.assertIn("only supported",check_witness(q))


class QualityReportTests(unittest.TestCase):
    def test_sample_has_no_severe_structure_or_duplicate(self):
        bank,digest=sample()
        result=report(bank,digest)
        self.assertEqual(0,result["counts"]["error"])
        self.assertEqual("review_required",result["quality_status"])

    def test_exact_duplicate_detected(self):
        bank,digest=sample()
        bank["items"][1]["stem"]=bank["items"][0]["stem"]
        codes={f["code"] for f in audit(bank,digest)}
        self.assertIn("duplicate_stem",codes)

    def test_near_duplicate_detected(self):
        bank,digest=sample()
        bank["items"][1]["stem"]=bank["items"][0]["stem"]+"？"
        codes={f["code"] for f in audit(bank,digest)}
        self.assertIn("duplicate_stem",codes)
        long_stem = ("请计算下列代数表达式，并说明每一步变形的依据，"
                     "然后判断最终的数学结论是否成立：3x+4=19")
        bank["items"][0]["stem"]=long_stem
        bank["items"][1]["stem"]=long_stem.replace("19","18")
        codes={f["code"] for f in audit(bank,digest)}
        self.assertIn("near_duplicate_stem",codes)

    def test_criterion_duplicate_detected(self):
        bank,digest=sample()
        manual=next(i for i in bank["items"] if i["type"]=="manual")
        manual["rubric"].append(manual["rubric"][0])
        codes={f["code"] for f in audit(bank,digest)}
        self.assertIn("duplicate_rubric_criteria",codes)

    def test_digest_binds_review_to_exact_bank(self):
        bank,digest=sample()
        reviews={q["id"]:dict(reviewer="teacher-reviewer",answer_verified=True,
                              source_verified=True,scope_checked=True,
                              ambiguity_checked=True,fairness_checked=True,
                              rubric_checked=True)
                 for q in bank["items"]}
        reviewed=report(bank,digest,{"bank_sha256":digest,"items":reviews})
        self.assertTrue(reviewed["review_attested"])
        bad=report(bank,digest,{"bank_sha256":"wrong","items":reviews})
        self.assertEqual("blocked",bad["quality_status"])
        reviews[bank["items"][0]["id"]]["source_verified"]=False
        incomplete=report(bank,digest,{"bank_sha256":digest,"items":reviews})
        self.assertIn("incomplete_independent_review",
                      [x["code"] for x in incomplete["findings"]])

    def test_no_correct_answers_in_audit_output(self):
        bank,digest=sample()
        result=json.dumps(report(bank,digest))
        self.assertNotIn("3x + 4 = 19",result)
        self.assertNotIn("3x=15",result)
        self.assertNotIn('"options"',result)

    def test_strict_requires_independent_review(self):
        r=subprocess.run([sys.executable,str(QUALITY),str(BANK),"--strict"],
                         text=True,capture_output=True)
        self.assertEqual(2,r.returncode)
        self.assertEqual("blocked",json.loads(r.stdout)["quality_status"])

    def test_non_strict_exploratory_audit(self):
        r=subprocess.run([sys.executable,str(QUALITY),str(BANK)],
                         text=True,capture_output=True)
        self.assertEqual(0,r.returncode,r.stderr)
        self.assertIn("counts",json.loads(r.stdout))


if __name__=="__main__":
    unittest.main()
