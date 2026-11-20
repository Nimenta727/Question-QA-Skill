"""Private reference-criterion comparison after independent frozen reviews."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import reviewer_pilot, reviewer_trial

ROOT=Path(__file__).resolve().parents[1]
CLI=ROOT/"scripts"/"reviewer_pilot.py"


def setup():
    cases=[{"case_id":"SECRET_CASE_%02d"%i,"criteria":2} for i in range(10)]
    plan={"study_type":"synthetic","authorized":False,"rubric_frozen":True,
          "case_ids_and_criterion_counts":cases}
    manifest={"stage":"prepared","study_type":"synthetic",
              "authorization_self_declared":False,
              "rubric_frozen_self_declared":True,
              "case_ids_and_criterion_counts":cases}
    a={"reviewer_slot":"A","cases":[]}
    b={"reviewer_slot":"B","cases":[]}
    reference={"expert_reference_self_declared":True,"cases":[]}
    for i,entry in enumerate(cases):
        label=entry["case_id"]
        expert=[1,0.5] if i%2 else [0,1]
        a_score=list(expert)
        b_score=list(expert)
        if i%3==0:
            a_score[0]=0 if expert[0]==1 else 1
        if i%4==0:
            b_score[1]=0
        a["cases"].append({"case_id":label,"scores":a_score})
        b["cases"].append({"case_id":label,"scores":b_score})
        reference["cases"].append({"case_id":label,"scores":expert})
    frozen=reviewer_trial.freeze(manifest,a,b,bootstraps=20,seed=2029)
    return manifest,frozen,a,b,reference


class FrozenExpertReferenceTests(unittest.TestCase):
    def test_metrics_are_aggregate_only(self):
        manifest,frozen,a,b,expert=setup()
        result=reviewer_pilot.evaluate(manifest,frozen,a,b,expert,bootstraps=50)
        self.assertEqual(10,result["metrics"]["cases"])
        self.assertEqual(20,result["metrics"]["rubric_decisions"])
        self.assertLess(result["metrics"]["reviewer_a_expert_reference_agreement"],1)
        self.assertLess(result["metrics"]["reviewer_b_expert_reference_agreement"],1)
        self.assertTrue(result["metrics"]["consensus_agreed_but_reference_disagreed"]>=0)
        self.assertEqual(2,len(result["case_bootstrap_a_minus_b_reference_agreement_ci95"]))
        dumped=json.dumps(result)
        self.assertNotIn("SECRET_CASE_",dumped)
        self.assertFalse(result["genuine_human_review_verified"])
        self.assertFalse(result["expert_correctness_independently_verified"])
        self.assertFalse(result["reviewer_blinding_verified"])

    def test_detects_post_freeze_score_tampering(self):
        manifest,frozen,a,b,expert=setup()
        b["cases"][0]["scores"][0]=0.5
        with self.assertRaisesRegex(ValueError,"hash changed"):
            reviewer_pilot.evaluate(manifest,frozen,a,b,expert)

    def test_detects_report_hash_tampering(self):
        manifest,frozen,a,b,expert=setup()
        frozen["first_round_packet_sha256"]["A"]="0"*64
        with self.assertRaisesRegex(ValueError,"hash changed"):
            reviewer_pilot.evaluate(manifest,frozen,a,b,expert)

    def test_requires_complete_expert_reference(self):
        manifest,frozen,a,b,expert=setup()
        expert["cases"].pop()
        with self.assertRaisesRegex(ValueError,"incomplete expert reference"):
            reviewer_pilot.evaluate(manifest,frozen,a,b,expert)

    def test_rejects_unverified_expert_assertion(self):
        manifest,frozen,a,b,expert=setup()
        expert["expert_reference_self_declared"]=False
        with self.assertRaisesRegex(ValueError,"self-declared"):
            reviewer_pilot.evaluate(manifest,frozen,a,b,expert)

    def test_rejects_extra_answer_text_or_duplicate_expert_rows(self):
        manifest,frozen,a,b,expert=setup()
        expert["cases"][0]["student_response"]="PRIVATE_RAW_STUDENT_ANSWER"
        with self.assertRaisesRegex(ValueError,"requires case_id and scores"):
            reviewer_pilot.evaluate(manifest,frozen,a,b,expert)
        expert["cases"][0].pop("student_response")
        expert["cases"][1]["case_id"]=expert["cases"][0]["case_id"]
        with self.assertRaisesRegex(ValueError,"duplicate"):
            reviewer_pilot.evaluate(manifest,frozen,a,b,expert)

    def test_frozen_cohort_must_match_manifest(self):
        manifest,frozen,a,b,expert=setup()
        frozen["cases"]=11
        with self.assertRaisesRegex(ValueError,"not bound"):
            reviewer_pilot.evaluate(manifest,frozen,a,b,expert)

    def test_perfect_rater_consensus_can_disagree_with_expert(self):
        manifest,frozen,a,b,expert=setup()
        for case in b["cases"]:
            source=next(x for x in a["cases"] if x["case_id"]==case["case_id"])
            case["scores"]=list(source["scores"])
        frozen=reviewer_trial.freeze(manifest,a,b,0)
        result=reviewer_pilot.evaluate(manifest,frozen,a,b,expert,0)
        self.assertEqual(1,result["metrics"]["reviewer_interagreement"])
        self.assertGreater(result["metrics"]["consensus_agreed_but_reference_disagreed"],0)
        self.assertIsNone(result["case_bootstrap_a_minus_b_reference_agreement_ci95"])

    def test_bootstrap_reproducible_by_case(self):
        manifest,frozen,a,b,expert=setup()
        one=reviewer_pilot.evaluate(manifest,frozen,a,b,expert,50,42)
        two=reviewer_pilot.evaluate(manifest,frozen,a,b,expert,50,42)
        self.assertEqual(one,two)

    def test_cli_outputs_aggregate_not_original_case_names(self):
        manifest,frozen,a,b,expert=setup()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            mapping={"manifest.json":manifest,"frozen.json":frozen,
                     "a.json":a,"b.json":b,"expert.json":expert}
            for filename,data in mapping.items():
                (root/filename).write_text(json.dumps(data),encoding="utf-8")
            outfile=root/"summary.json"
            cmd=[sys.executable,str(CLI),"--manifest",str(root/"manifest.json"),
                 "--frozen",str(root/"frozen.json"),
                 "--review-a",str(root/"a.json"),
                 "--review-b",str(root/"b.json"),
                 "--expert",str(root/"expert.json"),
                 "--output",str(outfile),"--bootstraps","25"]
            first=subprocess.run(cmd,capture_output=True,text=True,cwd=str(ROOT))
            self.assertEqual(0,first.returncode,first.stderr)
            text=outfile.read_text(encoding="utf-8")
            self.assertNotIn("SECRET_CASE_",text)
            self.assertEqual(10,json.loads(text)["metrics"]["cases"])
            again=subprocess.run(cmd,capture_output=True,text=True,cwd=str(ROOT))
            self.assertNotEqual(0,again.returncode)
            self.assertEqual(text,outfile.read_text(encoding="utf-8"))


if __name__=="__main__":
    unittest.main()
