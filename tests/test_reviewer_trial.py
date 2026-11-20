"""Pseudonymous research approval gates and independent first-round freeze."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import reviewer_trial

ROOT=Path(__file__).resolve().parents[1]
TRIAL=ROOT/"scripts"/"reviewer_trial.py"


def plan(study_type="synthetic",authorized=False):
    return {"study_type":study_type,"authorized":authorized,
            "rubric_frozen":True,
            "case_ids_and_criterion_counts":[
                {"case_id":"case-%02d"%i,"criteria":2 if i%2==0 else 3}
                for i in range(12)]}


def packet(manifest,slot,variant=0):
    cases=[]
    for idx,item in enumerate(manifest["case_ids_and_criterion_counts"]):
        n=item["criteria"]
        values=[1 if (idx+j)%3==0 else 0.5 for j in range(n)]
        if slot=="B" and variant and idx%3==0:
            values[0]=0
        cases.append({"case_id":item["case_id"],"scores":values})
    return {"reviewer_slot":slot,"cases":cases}


class ProtocolSafetyTests(unittest.TestCase):
    def test_real_data_requires_external_authorization_claim(self):
        with self.assertRaisesRegex(ValueError,"authorization"):
            reviewer_trial.validate_plan(plan("authorized_real_self_declared",False))
        self.assertEqual(12,len(reviewer_trial.validate_plan(
            plan("authorized_real_self_declared",True))))
        changed=plan()
        changed["rubric_frozen"]=False
        with self.assertRaisesRegex(ValueError,"freeze scoring rubric"):
            reviewer_trial.validate_plan(changed)

    def test_prepare_creates_independent_task_packs_without_student_answers(self):
        with tempfile.TemporaryDirectory() as tmp:
            private=Path(tmp)/"study-data"
            result=reviewer_trial.prepare(plan(),private)
            self.assertEqual(12,result["cases"])
            manifest=json.loads((private/"private-manifest.json").read_text())
            self.assertEqual("prepared",manifest["stage"])
            first=json.loads((private/"reviewer-A-tasks.json").read_text())
            second=json.loads((private/"reviewer-B-tasks.json").read_text())
            self.assertEqual("A",first["reviewer_slot"])
            self.assertEqual("B",second["reviewer_slot"])
            self.assertEqual({x["case_id"] for x in first["case_ids_and_criterion_counts"]},
                             {x["case_id"] for x in second["case_ids_and_criterion_counts"]})
            self.assertNotIn("scores",json.dumps(first))
            self.assertNotIn("student_response",json.dumps(manifest))
            self.assertFalse(result["human_authorization_verified_by_software"])

    def test_freeze_aggregates_only_and_fixes_packet_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            private=Path(tmp)/"study-data"
            reviewer_trial.prepare(plan(),private)
            manifest=json.loads((private/"private-manifest.json").read_text())
            a,b=packet(manifest,"A"),packet(manifest,"B",1)
            result=reviewer_trial.freeze(manifest,a,b,bootstraps=30,seed=2028)
            self.assertEqual("first_round_frozen",result["stage"])
            self.assertEqual(12,result["cases"])
            self.assertEqual(2,len(result["first_round_packet_sha256"]))
            self.assertGreater(result["agreement"]["disputed_cases"],0)
            self.assertEqual(result["agreement"]["disputed_cases"],
                             result["agreement"]["unresolved_cases"])
            self.assertNotIn("case-00",json.dumps(result))
            self.assertFalse(result["reviewer_independence_verified_by_software"])
            self.assertEqual(result["first_round_packet_sha256"],
                             reviewer_trial.freeze(manifest,a,b,30,2028)
                             ["first_round_packet_sha256"])

    def test_no_missing_or_duplicate_case_can_freeze(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"private"
            reviewer_trial.prepare(plan(),p)
            manifest=json.loads((p/"private-manifest.json").read_text())
            a,b=packet(manifest,"A"),packet(manifest,"B")
            b["cases"].pop()
            with self.assertRaisesRegex(ValueError,"missing"):
                reviewer_trial.freeze(manifest,a,b)
            b=packet(manifest,"B")
            b["cases"][1]["case_id"]=b["cases"][0]["case_id"]
            with self.assertRaisesRegex(ValueError,"duplicate"):
                reviewer_trial.freeze(manifest,a,b)

    def test_reviewer_slots_and_rubric_mismatch_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"private"
            reviewer_trial.prepare(plan(),p)
            manifest=json.loads((p/"private-manifest.json").read_text())
            a,b=packet(manifest,"A"),packet(manifest,"B")
            b["reviewer_slot"]="A"
            with self.assertRaisesRegex(ValueError,"reviewer B"):
                reviewer_trial.freeze(manifest,a,b)
            b=packet(manifest,"B")
            b["cases"][0]["scores"]=[1]
            with self.assertRaisesRegex(ValueError,"rubric length"):
                reviewer_trial.freeze(manifest,a,b)

    def test_third_party_finalization_bound_to_frozen_review_packets(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/"study"
            reviewer_trial.prepare(plan(),folder)
            manifest=json.loads((folder/"private-manifest.json").read_text())
            first=packet(manifest,"A")
            second=packet(manifest,"B",1)
            frozen=reviewer_trial.freeze(manifest,first,second,bootstraps=0)
            disputes=[]
            for a,b in zip(first["cases"],second["cases"]):
                for i,(left,right) in enumerate(zip(a["scores"],b["scores"])):
                    if left!=right:
                        disputes.append({"case_id":a["case_id"],"criterion_index":i,
                                         "score":left,"reason_code":"rubric_clarification"})
            c={"adjudicator_id":"reviewer-C","independent_self_declared":True,
               "decisions":disputes}
            final=reviewer_trial.finalize(manifest,frozen,first,second,c)
            self.assertEqual("adjudication_complete",final["stage"])
            self.assertEqual(len(disputes),final["disputed_criteria_adjudicated"])
            self.assertEqual(0,final["unresolved_cases"])
            self.assertFalse(final["independent_adjudicator_identity_verified"])
            self.assertNotIn("case-00",json.dumps(final))
            altered=copy.deepcopy(second)
            altered["cases"][0]["scores"][0]=1-altered["cases"][0]["scores"][0]
            with self.assertRaisesRegex(ValueError,"differ from immutable"):
                reviewer_trial.finalize(manifest,frozen,first,altered,c)
            missing=copy.deepcopy(c)
            missing["decisions"].pop()
            with self.assertRaisesRegex(ValueError,"all frozen"):
                reviewer_trial.finalize(manifest,frozen,first,second,missing)
            duplicated=copy.deepcopy(c)
            duplicated["decisions"].append(copy.deepcopy(disputes[0]))
            with self.assertRaisesRegex(ValueError,"only each disputed"):
                reviewer_trial.finalize(manifest,frozen,first,second,duplicated)
            unagreed=copy.deepcopy(c)
            unagreed["decisions"][0]["criterion_index"]=1
            with self.assertRaisesRegex(ValueError,"only each disputed"):
                reviewer_trial.finalize(manifest,frozen,first,second,unagreed)

    def test_cli_finalize_does_not_leak_pseudonyms_or_replace_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/"private"
            reviewer_trial.prepare(plan(),folder)
            manifest=json.loads((folder/"private-manifest.json").read_text())
            a,b=packet(manifest,"A"),packet(manifest,"B",1)
            frozen=reviewer_trial.freeze(manifest,a,b,bootstraps=0)
            disputes=[]
            for first,second in zip(a["cases"],b["cases"]):
                for i,(x,y) in enumerate(zip(first["scores"],second["scores"])):
                    if x!=y:
                        disputes.append({"case_id":first["case_id"],
                                         "criterion_index":i,"score":x,
                                         "reason_code":"other"})
            inputs=[frozen,a,b,{"adjudicator_id":"independent-C",
                    "independent_self_declared":True,"decisions":disputes}]
            filenames=[]
            for idx,item in enumerate(inputs):
                p=Path(tmp)/("input%d.json"%idx)
                p.write_text(json.dumps(item),encoding="utf-8")
                filenames.append(p)
            target=Path(tmp)/"final.json"
            cmd=[sys.executable,str(TRIAL),"finalize",
                 "--manifest",str(folder/"private-manifest.json"),
                 "--first-round",str(filenames[0]),
                 "--review-a",str(filenames[1]),
                 "--review-b",str(filenames[2]),
                 "--adjudication",str(filenames[3]),"--output",str(target)]
            first=subprocess.run(cmd,cwd=str(ROOT),capture_output=True,text=True)
            self.assertEqual(0,first.returncode,first.stderr)
            self.assertEqual("adjudication_complete",json.loads(target.read_text())["stage"])
            self.assertNotIn("case-",target.read_text())
            retry=subprocess.run(cmd,cwd=str(ROOT),capture_output=True,text=True)
            self.assertNotEqual(0,retry.returncode)

    def test_cli_freezes_non_overwriting_aggregate_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            source=folder/"plan.json"
            private=folder/"study"
            source.write_text(json.dumps(plan()),encoding="utf-8")
            cmd=[sys.executable,str(TRIAL)]
            created=subprocess.run(cmd+["prepare","--plan",str(source),
                                       "--output-dir",str(private)],
                                   cwd=str(ROOT),capture_output=True,text=True)
            self.assertEqual(0,created.returncode,created.stderr)
            manifest=json.loads((private/"private-manifest.json").read_text())
            a,b=private/"a.json",private/"b.json"
            a.write_text(json.dumps(packet(manifest,"A")),encoding="utf-8")
            b.write_text(json.dumps(packet(manifest,"B",1)),encoding="utf-8")
            target=folder/"aggregate.json"
            command=cmd+["freeze","--manifest",str(private/"private-manifest.json"),
                         "--review-a",str(a),"--review-b",str(b),"--output",str(target),
                         "--bootstraps","25"]
            frozen=subprocess.run(command,cwd=str(ROOT),capture_output=True,text=True)
            self.assertEqual(0,frozen.returncode,frozen.stderr)
            self.assertTrue(target.exists())
            content=target.read_text()
            self.assertNotIn("case-",content)
            self.assertEqual("first_round_frozen",json.loads(content)["stage"])
            retry=subprocess.run(command,cwd=str(ROOT),capture_output=True,text=True)
            self.assertNotEqual(0,retry.returncode)
            self.assertEqual(content,target.read_text())


if __name__=="__main__":
    unittest.main()
