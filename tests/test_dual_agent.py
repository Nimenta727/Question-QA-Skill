"""Offline role-isolation, revision and fail-closed tests for dual-agent workflow.

Synthetic scripted clients are NOT actual independent model audits.
"""
import copy
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import dual_agent, question_quality
from scripts.qa import read_bank

ROOT=Path(__file__).resolve().parents[1]
DEMO=ROOT/"examples"/"sample_bank.json"
CLI=ROOT/"scripts"/"dual_agent.py"
QA=ROOT/"scripts"/"qa.py"


class ScriptedAgents:
    """Fake author/reviewer calls with an observable, isolated order."""
    def __init__(self, fail_first=False, tamper_blind=False, invalid_draft=False):
        self.calls=[]
        self.fail_first=fail_first
        self.tamper_blind=tamper_blind
        self.invalid_draft=invalid_draft
        self.original=read_bank(DEMO)[0]["items"][0]
        self.round=0

    def ask(self,role,instructions,payload):
        self.calls.append((role,instructions,copy.deepcopy(payload)))
        if role=="author":
            self.round+=1
            if self.invalid_draft:
                return {"id":"DA-001","stem":"Bad item without schema"}
            q=copy.deepcopy(self.original)
            q["id"]="DA-001"
            if self.round>1:
                q["stem"]=q["stem"]+" 请写明等式的适用条件。"
            return q
        if "BLIND FIRST PASS" in instructions:
            self._assert_blind_payload(payload)
            return {
                "independent_answer":"C",
                "independent_solution":"Algebraic rearrangement gives x = 5 after subtracting four and dividing by three.",
                "alternatives":[], "risks":[], "source_quote":""
            }
        if "ADVERSARIAL SECOND PASS" not in instructions:
            raise AssertionError("wrong reviewer instruction")
        q=payload["authored_bank"]["items"][0]
        template=copy.deepcopy(payload["audit_template"])
        template["auditor_id"]=dual_agent.REVIEWER_ID
        template["independence_self_declared"]=True
        row=template["items"][q["id"]]
        row["decision"]="pass"
        blind=payload["first_pass"]
        row["independent_answer"]=blind["independent_answer"]
        row["independent_solution"]=blind["independent_solution"]
        row["source_quote"]=blind["source_quote"]
        row["accepted_alternatives"]=[]
        row["distractor_analyses"]={
            letter:"Independent solution refutes this distractor based on the full equation."
            for letter in "ABCD" if letter != q["answer"]}
        row["rubric_analyses"]=[]
        for name in row["checks"]:
            row["checks"][name]={
                "result":"pass",
                "reason":"Independent critical examination of question premises and answer for "+name
            }
        row["acknowledged_static_warnings"]=[
            finding["code"] for finding in payload["deterministic_findings"]
            if finding["severity"]=="warning" and finding.get("item_id")==q["id"]]
        if self.fail_first and self.round==1:
            row["decision"]="needs_review"
            row["checks"]["ambiguity_and_conditions"]={
                "result":"fail","reason":"The wording contains a disputed condition and needs clearer constraints."}
            row["risk_notes"]=["Unresolved condition in first draft."]
        if self.tamper_blind:
            row["independent_answer"]="A"
        return template

    def _assert_blind_payload(self,payload):
        q=payload["question"]
        for forbidden in ("answer","explanation","aliases","rubric",
                          "answer_equivalence","verification","misconceptions"):
            if forbidden in q:
                raise AssertionError("blind reviewer saw hidden key field: "+forbidden)
        if "course_source_text" not in payload:
            raise AssertionError("blind reviewer missing source-mode declaration")


class DualAgentTests(unittest.TestCase):
    def test_success_with_distinct_calls_and_strict_qa_next(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/"private-questions"
            fake=ScriptedAgents()
            result=dual_agent.run_cycle(fake,"Solving linear equations","Algebra",
                                        output,rounds=2,
                                        author_model="model-A",reviewer_model="model-B")
            self.assertEqual("recorded_model_review_for_formative_practice",
                             result["result"])
            self.assertEqual(["author","reviewer","reviewer"],
                             [role for role,_,_ in fake.calls])
            self.assertTrue(result["distinct_model_names"])
            self.assertEqual(3,result["model_calls"])
            self.assertTrue((output/"approved-bank.json").exists())
            self.assertTrue((output/"approved-audit.json").exists())
            self.assertEqual("approved",result["trace"][0]["result"])
            first=output/"draft-01.json"
            with self.assertRaises(FileExistsError):
                dual_agent._private_write(output,first.name,{"oops":"overwrite"})
            state=Path(tmp)/"student.json"
            checked=subprocess.run([
                sys.executable,str(QA),"next",str(output/"approved-bank.json"),
                "--state",str(state),"--require-model-audit",
                "--model-audit",str(output/"approved-audit.json")
            ],cwd=str(ROOT),capture_output=True,text=True)
            self.assertEqual(0,checked.returncode,checked.stderr)
            prompt=json.loads(checked.stdout)
            self.assertEqual("recorded_model_review_for_practice",
                             prompt["model_audit_status"])
            self.assertNotIn("answer",prompt)
            self.assertNotIn("explanation",prompt)

    def test_first_failure_round_trip_second_revision_and_reaudit(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake=ScriptedAgents(fail_first=True)
            result=dual_agent.run_cycle(fake,"Understand equality","Algebra",
                                        Path(tmp)/"run",rounds=2)
            self.assertEqual("recorded_model_review_for_formative_practice",
                             result["result"])
            self.assertEqual(2,result["rounds_used"])
            self.assertEqual(["author","reviewer","reviewer",
                              "author","reviewer","reviewer"],
                             [x[0] for x in fake.calls])
            self.assertEqual("blocked",result["trace"][0]["result"])
            self.assertEqual("approved",result["trace"][1]["result"])
            feedback=fake.calls[3][2]["previous_review"]
            self.assertIn("ambiguity_and_conditions",
                          str(feedback["disputed_checks"]))
            first=json.loads((Path(tmp)/"run"/"audit-01.json").read_text(encoding="utf-8"))
            second=json.loads((Path(tmp)/"run"/"audit-02.json").read_text(encoding="utf-8"))
            self.assertNotEqual(first["bank_sha256"],second["bank_sha256"])

    def test_failed_review_never_publishes_bank(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake=ScriptedAgents(fail_first=True)
            output=Path(tmp)/"blocked"
            result=dual_agent.run_cycle(fake,"Equation reasoning","Algebra",
                                        output,rounds=1)
            self.assertEqual("blocked",result["result"])
            self.assertFalse((output/"approved-bank.json").exists())
            self.assertFalse((output/"approved-audit.json").exists())
            self.assertTrue((output/"summary.json").exists())

    def test_blind_answer_cannot_change_after_opening_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=dual_agent.run_cycle(ScriptedAgents(tamper_blind=True),
                                        "Equation","Algebra",Path(tmp)/"run",rounds=1)
            self.assertEqual("blocked",result["result"])
            self.assertIn("blind_solution_changed_after_key_reveal",
                          result["trace"][0]["failure_codes"])

    def test_invalid_author_not_sent_to_reviewer(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake=ScriptedAgents(invalid_draft=True)
            result=dual_agent.run_cycle(fake,"Reasoning","Math",Path(tmp)/"run",rounds=2)
            self.assertEqual("blocked",result["result"])
            self.assertEqual(["author","author"],[call[0] for call in fake.calls])
            self.assertFalse((Path(tmp)/"run"/"approved-bank.json").exists())

    def test_existing_output_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/"run"
            dest.mkdir()
            with self.assertRaises(FileExistsError):
                dual_agent.run_cycle(ScriptedAgents(),"Equations","Algebra",dest)

    def test_input_validation_and_max_round_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                dual_agent.run_cycle(ScriptedAgents(),"A","Math",Path(tmp)/"x",rounds=5)
            with self.assertRaises(ValueError):
                dual_agent.run_cycle(ScriptedAgents()," ","Math",Path(tmp)/"y")

    def test_missing_key_must_fail_before_network(self):
        with mock.patch.dict(os.environ,{},clear=True):
            with self.assertRaisesRegex(ValueError,"OPENAI_API_KEY"):
                dual_agent.OpenAIResponsesClient("author","reviewer")

    def test_cli_course_source_requires_explicit_remote_permission(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"private-source.txt"
            source.write_text("teacher lesson text",encoding="utf-8")
            output=Path(tmp)/"out"
            cmd=[sys.executable,str(CLI),"--topic","equations",
                 "--subject","algebra","--source-file",str(source),
                 "--author-model","model1","--reviewer-model","model2",
                 "--out-dir",str(output)]
            proc=subprocess.run(cmd,cwd=str(ROOT),capture_output=True,text=True)
            self.assertEqual(2,proc.returncode)
            self.assertIn("--allow-remote-source",proc.stderr)
            self.assertFalse(output.exists())

    def test_no_api_key_does_not_create_output_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/"out"
            env=dict(os.environ)
            env.pop("OPENAI_API_KEY",None)
            cmd=[sys.executable,str(CLI),"--topic","equations",
                 "--subject","algebra","--author-model","model1",
                 "--reviewer-model","model2","--out-dir",str(output)]
            proc=subprocess.run(cmd,cwd=str(ROOT),capture_output=True,text=True,env=env)
            self.assertEqual(2,proc.returncode)
            self.assertFalse(output.exists())

    def test_response_transport_never_stores_chat_and_uses_fixed_endpoint(self):
        key="synthetic-key-not-a-real-credential"
        fake_response={
            "status":"completed",
            "output":[{"type":"message","content":[{"type":"output_text",
                       "text":json.dumps({"ok":True})}]}]}
        class Response(io.BytesIO):
            def __enter__(self):
                return self
            def __exit__(self,*args):
                return False
        request_data=[]
        def stub(request,timeout):
            request_data.append((request,timeout))
            return Response(json.dumps(fake_response).encode("utf-8"))
        with mock.patch("urllib.request.urlopen",side_effect=stub):
            client=dual_agent.OpenAIResponsesClient("author-model","review-model",api_key=key)
            result=client.ask("reviewer","You are a reviewer.",{"question":"test"})
        self.assertEqual({"ok":True},result)
        self.assertEqual(dual_agent.API_URL,request_data[0][0].full_url)
        body=json.loads(request_data[0][0].data)
        self.assertEqual("review-model",body["model"])
        self.assertIs(body["store"],False)
        self.assertNotIn("previous_response_id",body)
        self.assertNotIn(key,json.dumps(body))

    def test_output_directory_private_on_posix(self):
        if os.name == "nt":
            self.skipTest("Windows file ACLs differ from POSIX mode bits")
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/"run"
            dual_agent.run_cycle(ScriptedAgents(),"Math","Math",output,rounds=1)
            self.assertEqual(0o700,output.stat().st_mode & 0o777)
            for path in output.iterdir():
                self.assertEqual(0o600,path.stat().st_mode & 0o777)


if __name__=="__main__":
    unittest.main()
