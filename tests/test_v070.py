"""Math equivalence, state transactions and blinded-review aggregates."""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from scripts import math_equivalence as me
from scripts import reviewer_study as rs
from scripts import state_store
from scripts.qa import grade, read_bank, validate_bank

ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/"examples"/"sample_bank.json"
QA=ROOT/"scripts"/"qa.py"
STUDY=ROOT/"scripts"/"reviewer_study.py"


def run_qa(*args):
    return subprocess.run([sys.executable,str(QA),*map(str,args)],
                          cwd=str(ROOT),text=True,capture_output=True)


class MathematicalEquivalenceTests(unittest.TestCase):
    def test_rational_exact_equivalence(self):
        self.assertTrue(me.matches("7","14/2",{"kind":"rational"}))
        self.assertTrue(me.matches("0.5","(1+1)/4",{"kind":"rational"}))
        self.assertFalse(me.matches("0.5","0.6",{"kind":"rational"}))

    def test_polynomials_with_cancellation_and_factorization(self):
        spec={"kind":"polynomial","variables":["x"]}
        self.assertTrue(me.matches("x+x","2*x",spec))
        self.assertTrue(me.matches("x**2-1","(x+1)*(x-1)",spec))
        self.assertFalse(me.matches("x**2-1","x**2+1",spec))
        self.assertTrue(me.matches("2*(x+y)","2*x+2*y",
                                   {"kind":"polynomial","variables":["x","y"]}))

    def test_unsafe_or_unsupported_expressions(self):
        spec={"kind":"polynomial","variables":["x"]}
        expressions=["__import__('os').system('calc')","x/x","1/0",
                     "x**100000000","x**-1","x.__class__",
                     "(lambda: 1)()", "sum([1,2])","2x","[2,4]",
                     "10**10","10**100", "True", "5j", "x if True else 0"]
        for expression in expressions:
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    me.polynomial(expression,("x",))

    def test_resource_limits(self):
        with self.assertRaises(ValueError):
            me.polynomial("1+"*65+"1")
        with self.assertRaises(ValueError):
            me.polynomial("x**4*x**4*x",("x",))
        with self.assertRaises(ValueError):
            me.polynomial("999999999*999999999*999999999*999999999")
        with self.assertRaises(ValueError):
            me.polynomial("("*20+"x"+")"*20,("x",))

    def test_bad_spec_fails_before_grading(self):
        for spec in ({"kind":"polynomial","variables":["z"]},
                     {"kind":"rational","variables":["x"]},
                     {"kind":"polynomial","variables":["x","x"]},
                     {"kind":"anything"},True):
            with self.subTest(spec=spec):
                with self.assertRaises(ValueError):
                    me.validate_spec(spec)
        bank,_=read_bank(BANK)
        item=next(i for i in bank["items"] if i["type"]=="short")
        item["answer_equivalence"]={"kind":"polynomial","variables":["x"]}
        item["answer"]="x+1"
        self.assertTrue(validate_bank(bank))

    def test_old_short_answer_unchanged(self):
        data,_=read_bank(BANK)
        q=next(x for x in data["items"] if x["type"]=="short"
               and "answer_equivalence" not in x)
        score,method=grade(q,"14/2")
        self.assertEqual(method,"exact_key")
        self.assertEqual(0,score)

    def test_explicit_equivalence_on_pending_question(self):
        bank,_=read_bank(BANK)
        item=next(x for x in bank["items"] if x["id"]=="ALG-003")
        self.assertEqual({"kind":"rational"},item["answer_equivalence"])
        with tempfile.TemporaryDirectory() as folder:
            b=Path(folder)/"one.json"
            state=Path(folder)/"student.json"
            b.write_text(json.dumps({"version":1,"subject":"test","items":[item]},
                                    ensure_ascii=False),encoding="utf-8")
            next_=run_qa("next",b,"--state",state)
            self.assertEqual(0,next_.returncode,next_.stderr)
            result=run_qa("answer",b,"--state",state,"--response","14/2")
            self.assertEqual(0,result.returncode,result.stderr)
            got=json.loads(result.stdout)
            self.assertEqual("verified_math_equivalence",got["method"])
            self.assertEqual(1,got["score"])
            self.assertNotIn("14/2",state.read_text(encoding="utf-8"))

    def test_unverifiable_expression_does_not_consume_pending(self):
        bank,_=read_bank(BANK)
        item=next(x for x in bank["items"] if x["id"]=="ALG-003")
        with tempfile.TemporaryDirectory() as folder:
            b=Path(folder)/"one.json"
            state=Path(folder)/"student.json"
            b.write_text(json.dumps({"version":1,"subject":"test","items":[item]},
                                    ensure_ascii=False),encoding="utf-8")
            run_qa("next",b,"--state",state)
            invalid=run_qa("answer",b,"--state",state,"--response","seven")
            self.assertEqual(2,invalid.returncode)
            self.assertIn("math_equivalence_unverified",invalid.stderr)
            self.assertIsNotNone(json.loads(state.read_text())["pending"])
            reviewed=run_qa("answer",b,"--state",state,
                            "--response","seven","--review-equivalent",
                            "--reason","Teacher checked English word seven")
            self.assertEqual(0,reviewed.returncode,reviewed.stderr)
            self.assertEqual("reviewed_equivalent_answer",json.loads(reviewed.stdout)["method"])


class StateTransactionTests(unittest.TestCase):
    @staticmethod
    def initial():
        return {"version":1,"history":[],"pending":None}

    def test_backup_tracks_previous_valid_snapshot_and_recover(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"state.json"
            with state_store.locked_state(path):
                state_store.save(path,self.initial())
                updated=self.initial()
                updated["history"]=[{"id":"safe", "score":1}]
                state_store.save(path,updated)
            inspection=state_store.inspect(path)
            self.assertEqual(1,inspection["current"]["answers"])
            self.assertEqual(0,inspection["last_good_backup"]["answers"])
            self.assertTrue(inspection["can_restore"])
            with state_store.locked_state(path):
                state_store.recover(path)
            self.assertEqual([],json.loads(path.read_text())["history"])

    def test_corrupt_state_cannot_replace_valid_backup(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"state.json"
            with state_store.locked_state(path):
                state_store.save(path,self.initial())
                state_store.save(path,self.initial())
            saved=state_store.backup_path(path).read_bytes()
            path.write_bytes(b"{bad-json")
            with state_store.locked_state(path):
                with self.assertRaises(ValueError):
                    state_store.save(path,self.initial())
            self.assertEqual(saved,state_store.backup_path(path).read_bytes())
            self.assertTrue(state_store.inspect(path)["can_restore"])
            self.assertFalse(state_store.inspect(path)["current"]["valid"])
            with state_store.locked_state(path):
                state_store.recover(path)
            self.assertEqual(self.initial(),json.loads(path.read_text()))

    def test_recovery_requires_explicit_confirmation(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"state.json"
            with state_store.locked_state(path):
                state_store.save(path,self.initial())
                state_store.save(path,self.initial())
            missing=run_qa("state-recover","--state",path)
            self.assertEqual(2,missing.returncode)
            done=run_qa("state-recover","--state",path,"--confirm")
            self.assertEqual(0,done.returncode,done.stderr)
            check=run_qa("state-check","--state",path)
            self.assertEqual(0,check.returncode)
            self.assertTrue(json.loads(check.stdout)["current"]["valid"])

    def test_multiple_processes_do_not_lose_updates(self):
        # Real subprocesses share the same OS advisory file lock.
        code = (
            "import json,sys,time;"
            "from scripts import state_store as s;"
            "p=sys.argv[1];"
            "\nwith s.locked_state(p,timeout=15):"
            "\n d=json.loads(open(p,encoding='utf-8').read());"
            "\n time.sleep(.02);"
            "\n d['history'].append({'id':'from-subprocess'});"
            "\n s.save(p,d)"
        )
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"state.json"
            with state_store.locked_state(path):
                state_store.save(path,self.initial())
            children=[subprocess.Popen([sys.executable,"-c",code,str(path)],
                                       cwd=str(ROOT),stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE) for _ in range(8)]
            for child in children:
                _,err=child.communicate(timeout=25)
                self.assertEqual(0,child.returncode,err.decode("utf-8",errors="replace"))
            current=json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(8,len(current["history"]))
            backup=json.loads(state_store.backup_path(path).read_text(encoding="utf-8"))
            self.assertEqual(7,len(backup["history"]))

    def test_second_process_times_out_when_lock_held(self):
        code=("from scripts import state_store as s;import sys;"
              "\ntry:"
              "\n with s.locked_state(sys.argv[1],timeout=.15): pass"
              "\nexcept TimeoutError: print('BUSY'); sys.exit(0)"
              "\nraise AssertionError('lock not enforced')")
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"state.json"
            with state_store.locked_state(path):
                proc=subprocess.run([sys.executable,"-c",code,str(path)],
                                    cwd=str(ROOT),capture_output=True,text=True,timeout=10)
            self.assertEqual(0,proc.returncode,proc.stderr)
            self.assertIn("BUSY",proc.stdout)


class ReviewerAgreementTests(unittest.TestCase):
    @staticmethod
    def fixture():
        return {"study_type":"synthetic","cases":[
            {"case_id":"PRIVATE_CASE_A","scores_a":[1,.5,0],
             "scores_b":[1,0,0],"final":[1,.5,0]},
            {"case_id":"PRIVATE_CASE_B","scores_a":[0,0],
             "scores_b":[0,0]},
            {"case_id":"PRIVATE_CASE_C","scores_a":[1,1],
             "scores_b":[1,1]},
            {"case_id":"PRIVATE_CASE_D","scores_a":[.5,1],
             "scores_b":[.5,.5],"final":[.5,.5]},
            {"case_id":"PRIVATE_CASE_E","scores_a":[0,1],
             "scores_b":[0,1]},
            {"case_id":"PRIVATE_CASE_F","scores_a":[1,.5],
             "scores_b":[1,1]}]}

    def test_private_aggregate_excludes_case_identifiers(self):
        report=rs.report(self.fixture(),draws=30)
        self.assertEqual(6,report["assessment"]["cases"])
        self.assertEqual(1,report["assessment"]["unresolved_cases"])
        raw=json.dumps(report)
        self.assertNotIn("PRIVATE_CASE_",raw)
        self.assertFalse(report["human_participation_verified"])
        self.assertFalse(report["validity_or_correctness_established"])
        self.assertEqual(2,len(report["case_cluster_bootstrap_exact_agreement_ci95"]))

    def test_synthetic_kappa_exact_and_perfect_agreement(self):
        same=[([0.,0.5,1.],[0.,0.5,1.],None)]
        self.assertAlmostEqual(1,rs.summarize(same)["quadratic_weighted_kappa"])
        constant=[([1.],[1.],None)]*5
        self.assertIsNone(rs.summarize(constant)["quadratic_weighted_kappa"])

    def test_invalid_inputs_rejected(self):
        for field in ("scores_a","scores_b"):
            data=self.fixture()
            data["cases"][0][field]=[True]
            with self.subTest(field=field),self.assertRaises(ValueError):
                rs.read_cases(data)
        duplicate=self.fixture()
        duplicate["cases"][1]["case_id"]="PRIVATE_CASE_A"
        with self.assertRaises(ValueError):
            rs.read_cases(duplicate)
        forbidden=self.fixture()
        forbidden["cases"][0]["final"]=[0,.5,0]
        with self.assertRaisesRegex(ValueError,"arbitration"):
            rs.read_cases(forbidden)

    def test_reproducible_case_bootstrap(self):
        rows=rs.read_cases(self.fixture())
        self.assertEqual(rs.interval(rows,40,2027),rs.interval(rows,40,2027))
        self.assertIsNone(rs.interval(rows,draws=0))

    def test_cli_aggregates_without_ids(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"input.json"
            output=Path(folder)/"aggregate.json"
            path.write_text(json.dumps(self.fixture()),encoding="utf-8")
            r=subprocess.run([sys.executable,str(STUDY),"--input",str(path),
                              "--output",str(output),"--bootstraps","20"],
                             cwd=str(ROOT),capture_output=True,text=True)
            self.assertEqual(0,r.returncode,r.stderr)
            text=output.read_text(encoding="utf-8")
            self.assertNotIn("PRIVATE_CASE",text)
            self.assertTrue(json.loads(text)["assessment"]["cases"]==6)


if __name__=="__main__":
    unittest.main()
