"""Appeal corrections, versioned backups, data export/deletion (synthetic only)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import appeals, state_store
from scripts.qa import read_bank

ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/"examples"/"sample_bank.json"
QA=ROOT/"scripts"/"qa.py"


def run(*args):
    return subprocess.run([sys.executable,str(QA),*map(str,args)],
                          cwd=str(ROOT),capture_output=True,text=True)


class AppealTests(unittest.TestCase):
    def test_correct_score_updates_report_and_keeps_audit(self):
        with tempfile.TemporaryDirectory() as folder:
            state=Path(folder)/"score.json"
            self.assertEqual(0,run("next",BANK,"--state",state).returncode)
            answer=run("answer",BANK,"--state",state,"--response","D")
            self.assertEqual(0,answer.returncode,answer.stderr)
            record=json.loads(answer.stdout)
            event_id=record["event_id"]
            self.assertEqual(0,record["score"])
            opened=run("appeal-open","--state",state,"--event-id",event_id,
                       "--reason","possible_key_error")
            self.assertEqual(0,opened.returncode,opened.stderr)
            appeal_id=json.loads(opened.stdout)["appeal_id"]
            replay=run("appeal-open","--state",state,"--event-id",event_id,
                       "--reason","other")
            self.assertNotEqual(0,replay.returncode)
            not_ready=run("appeal-resolve","--state",state,
                          "--appeal-id",appeal_id,"--decision","correct",
                          "--reason","key_verified","--new-score","1")
            self.assertNotEqual(0,not_ready.returncode)
            self.assertEqual(0,json.loads(state.read_text(encoding="utf-8"))["history"][0]["score"])
            solved=run("appeal-resolve","--state",state,
                       "--appeal-id",appeal_id,"--decision","correct",
                       "--reason","key_verified","--new-score","1",
                       "--reviewer-confirmed")
            self.assertEqual(0,solved.returncode,solved.stderr)
            history=json.loads(state.read_text(encoding="utf-8"))
            self.assertEqual(1,history["history"][0]["score"])
            self.assertEqual("appeal_correction",history["history"][0]["method"])
            self.assertNotIn("misconception",history["history"][0])
            self.assertEqual(0,history["appeals"][0]["score_before"])
            self.assertEqual(1,history["appeals"][0]["score_after"])
            self.assertEqual("resolved",history["appeals"][0]["status"])
            self.assertFalse(any(k in state.read_text(encoding="utf-8") for k in
                                 ("Student original response","teacher full name")))
            report=run("report","--state",state,"--bank",BANK)
            self.assertEqual(0,report.returncode)
            self.assertEqual(1,json.loads(report.stdout)["appeal_summary"]["resolved"])
            repeat=run("appeal-resolve","--state",state,
                       "--appeal-id",appeal_id,"--decision","correct",
                       "--reason","key_verified","--new-score","1",
                       "--reviewer-confirmed")
            self.assertNotEqual(0,repeat.returncode)

    def test_legacy_index_lazily_gets_stable_id(self):
        state={"version":1,"history":[{"id":"x","concept":"m","level":"recall",
               "score":.5,"type":"short","at":"2026-11-20T12:00:00+00:00"}],
               "pending":None}
        opened=appeals.open_appeal(state,"other",index=0)
        self.assertEqual(state["history"][0]["event_id"],opened["event_id"])
        self.assertEqual("open",opened["status"])
        self.assertEqual(1,appeals.view(state)["open_count"])

    def test_uphold_and_nonexistent_event_protection(self):
        state={"version":1,"history":[{"event_id":"a","id":"q","score":1,
               "type":"single"}]}
        with self.assertRaises(ValueError):
            appeals.open_appeal(state,"other",event_id="none")
        a=appeals.open_appeal(state,"scoring_error",event_id="a")
        with self.assertRaises(ValueError):
            appeals.resolve_appeal(state,a["appeal_id"],"uphold","key_verified",True)
        result=appeals.resolve_appeal(state,a["appeal_id"],"uphold","appeal_upheld",True)
        self.assertEqual("uphold",result["decision"])
        self.assertEqual(1,state["history"][0]["score"])

    def test_manual_rubric_correction_cannot_disagree_with_average(self):
        state={"version":1,"history":[{"event_id":"m","id":"essay","type":"manual",
               "score":.5,"criterion_scores":[1,0]}],"pending":None}
        a=appeals.open_appeal(state,"rubric_dispute",event_id="m")
        arguments=(state,a["appeal_id"],"correct","rubric_rechecked",True)
        with self.assertRaises(ValueError):
            appeals.resolve_appeal(*arguments,new_score=1)
        with self.assertRaises(ValueError):
            appeals.resolve_appeal(*arguments,criterion_scores=[1,.5],new_score=1)
        with self.assertRaises(ValueError):
            appeals.resolve_appeal(*arguments,criterion_scores=[1,0])
        change=appeals.resolve_appeal(*arguments,criterion_scores=[1,1])
        self.assertEqual(1,change["score_after"])
        self.assertEqual([1,1],state["history"][0]["criterion_scores"])

    def test_objective_corrections_are_binary(self):
        state={"version":1,"history":[{"event_id":"a","id":"q","type":"single",
               "score":0}]}
        a=appeals.open_appeal(state,"scoring_error",event_id="a")
        with self.assertRaises(ValueError):
            appeals.resolve_appeal(state,a["appeal_id"],"correct",
                                   "scoring_corrected",True,new_score=.5)

    def test_appeal_open_status_does_not_mutate_grade(self):
        state={"version":1,"history":[{"event_id":"a","id":"q","type":"single",
               "score":0}]}
        a=appeals.open_appeal(state,"equivalent_answer",event_id="a")
        self.assertEqual(0,state["history"][0]["score"])
        self.assertEqual("open",a["status"])


class LifecycleTests(unittest.TestCase):
    @staticmethod
    def initial():
        return {"version":1,"history":[],"pending":None}

    def test_rotating_snapshots_keep_five_prior_versions(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"state.json"
            with state_store.locked_state(path):
                state_store.save(path,self.initial())
                for i in range(9):
                    data=self.initial()
                    data["history"]=[{"id":str(x),"score":1} for x in range(i+1)]
                    state_store.save(path,data)
            snapshots=state_store.list_snapshots(path)
            self.assertEqual(5,len(snapshots))
            self.assertTrue(all(x["valid"] for x in snapshots))
            self.assertEqual(9,state_store.inspect(path)["current"]["answers"])
            self.assertEqual(8,state_store.inspect(path)["last_good_backup"]["answers"])
            oldest=snapshots[0]["snapshot_id"]
            with state_store.locked_state(path):
                restored=state_store.recover(path,oldest)
            self.assertEqual(4,len(restored["history"]))
            self.assertTrue(state_store.inspect(path)["current"]["valid"])

    def test_corrupt_snapshot_is_not_restored(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"state.json"
            with state_store.locked_state(path):
                state_store.save(path,self.initial())
                state_store.save(path,{"version":1,"history":[{"id":"x"}]})
            snap=state_store.list_snapshots(path)[0]["snapshot_id"]
            (state_store.snapshots_path(path)/(snap+".json")).write_text("{bad")
            with state_store.locked_state(path):
                with self.assertRaisesRegex(ValueError,"invalid"):
                    state_store.recover(path,snap)

    def test_export_is_aggregate_by_default_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"state.json"
            dest=Path(folder)/"export.json"
            with state_store.locked_state(path):
                state_store.save(path,{"version":1,
                    "history":[{"id":"secret-id","score":.5,"concept":"math",
                                "response":"PRIVATE_STUDENT_RESPONSE"}],
                    "pending":None})
                result=state_store.export(path,dest)
                self.assertFalse(result["private"])
                with self.assertRaises(FileExistsError):
                    state_store.export(path,dest)
                with self.assertRaises(ValueError):
                    state_store.export(path,path,True)
            data=dest.read_text(encoding="utf-8")
            self.assertIn("math",data)
            self.assertNotIn("secret-id",data)
            self.assertNotIn("PRIVATE_STUDENT_RESPONSE",data)
            self.assertNotIn("history",data)

    def test_cli_private_export_requires_extra_confirmation(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"state.json"
            with state_store.locked_state(path):
                state_store.save(path,self.initial())
            output=Path(folder)/"private.json"
            rejected=run("state-export","--state",path,"--output",output,
                         "--include-private")
            self.assertNotEqual(0,rejected.returncode)
            self.assertFalse(output.exists())
            permitted=run("state-export","--state",path,"--output",output,
                          "--include-private","--confirm-private")
            self.assertEqual(0,permitted.returncode,permitted.stderr)
            self.assertEqual("private_full_state",json.loads(output.read_text(encoding="utf-8"))["type"])

    def test_cli_delete_requires_exact_confirmation_removes_only_owned(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"state.json"
            other=Path(folder)/"unrelated.txt"
            other.write_text("KEEP")
            with state_store.locked_state(path):
                state_store.save(path,self.initial())
                state_store.save(path,{"version":1,"history":[{"id":"x"}]})
            rejected=run("state-delete","--state",path)
            self.assertNotEqual(0,rejected.returncode)
            self.assertTrue(path.exists())
            done=run("state-delete","--state",path,"--confirm-delete","DELETE-LOCAL")
            self.assertEqual(0,done.returncode,done.stderr)
            self.assertFalse(path.exists())
            self.assertFalse(state_store.backup_path(path).exists())
            self.assertFalse(state_store.snapshots_path(path).exists())
            self.assertTrue(Path(str(path)+".lock").exists())
            self.assertEqual("KEEP",other.read_text(encoding="utf-8"))

    def test_snapshot_status_cli_has_no_private_response(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"state.json"
            with state_store.locked_state(path):
                state_store.save(path,{"version":1,"history":[
                    {"id":"private-id","score":.5,"response":"PRIVATE_TEXT"}]})
                state_store.save(path,{"version":1,"history":[]})
            r=run("state-snapshots","--state",path)
            self.assertEqual(0,r.returncode,r.stderr)
            self.assertNotIn("PRIVATE_TEXT",r.stdout)
            self.assertNotIn("private-id",r.stdout)
            self.assertEqual(1,len(json.loads(r.stdout)["snapshots"]))

    def test_cli_snapshot_rollback_requires_confirmation(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"state.json"
            with state_store.locked_state(path):
                state_store.save(path,self.initial())
                state_store.save(path,{"version":1,"history":[{"id":"x"}]})
            sid=state_store.list_snapshots(path)[0]["snapshot_id"]
            bad=run("state-recover","--state",path,"--snapshot",sid)
            self.assertEqual(2,bad.returncode)
            good=run("state-recover","--state",path,"--snapshot",sid,"--confirm")
            self.assertEqual(0,good.returncode,good.stderr)
            self.assertEqual([],json.loads(path.read_text(encoding="utf-8"))["history"])


if __name__=="__main__":
    unittest.main()
