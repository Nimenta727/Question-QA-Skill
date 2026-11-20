"""ASSISTments 2015 causal replay, student isolation and source integrity tests."""
import csv
import json
import random
import tempfile
import unittest
from pathlib import Path

from scripts import evaluate_assist2015 as assist
from scripts import evaluate as core


def make_file(directory, count=70, attempts=8, shuffle=False):
    path=Path(directory)/("source-shuffle.csv" if shuffle else "source.csv")
    data=[]
    for student in range(count):
        for index in range(attempts):
            data.append({
                "user_id":"u%d"%student,
                "log_id":str(student*10000 + index*10 + 1),
                "sequence_id":"s%d"%(index%2),
                "correct":str((student+index*2)%5>1 and 1 or 0)
            })
    if shuffle:
        random.Random(101).shuffle(data)
    with path.open("w",encoding="utf-8",newline="") as out:
        w=csv.DictWriter(out,fieldnames=["user_id","log_id","sequence_id","correct"])
        w.writeheader()
        w.writerows(data)
    return path


class TestIndependentASSIST2015(unittest.TestCase):
    def test_learner_sampling_independent_of_file_order(self):
        with tempfile.TemporaryDirectory() as d:
            a=make_file(d)
            b=make_file(d,shuffle=True)
            events_a,audit_a=assist.load(a,seed=2026,max_learners=40)
            events_b,audit_b=assist.load(b,seed=2026,max_learners=40)
            self.assertEqual(40,audit_a["sample_learners_usable"])
            self.assertEqual(40,audit_b["sample_learners_usable"])
            self.assertEqual(
                [(x["learner"],x["order"],x["correct"]) for x in events_a],
                [(x["learner"],x["order"],x["correct"]) for x in events_b])

    def test_never_infer_independent_item_families_or_dates(self):
        with tempfile.TemporaryDirectory() as d:
            events,audit=assist.load(make_file(d),max_learners=40)
            self.assertFalse(audit["item_ids_available"])
            self.assertFalse(audit["real_timestamps_available"])
            a=next(x for x in events if x["concept"]=="s0")
            subset=[e for e in events if e["learner"]==a["learner"]
                    and e["concept"]==a["concept"]]
            self.assertEqual(1,len({e["family"] for e in subset}))
            self.assertEqual(1,len({e["at"] for e in subset}))
            self.assertEqual("insufficient_evidence",core.estimate(subset)["label"])

    def test_disjoint_and_genuine_next_response_prediction(self):
        with tempfile.TemporaryDirectory() as d:
            events,audit=assist.load(make_file(d),max_learners=60)
            parts=core.split_rows(events,2026)
            users={k:{r["learner"] for r in es} for k,es in parts.items()}
            self.assertFalse(users["test"] & users["validation"])
            self.assertFalse(users["test"] & users["train"])
            prior,ps=core.priors(parts["train"])
            observations=core.replay(parts["test"],prior,ps,min_history=2)
            self.assertGreater(len(observations),0)
            self.assertTrue(all(e["n_history"]>=2 for e in observations))

    def test_no_future_leakage_in_replay(self):
        with tempfile.TemporaryDirectory() as d:
            events,_=assist.load(make_file(d),max_learners=40)
            parts=core.split_rows(events,2026)
            prior,skills=core.priors(parts["train"])
            test=parts["test"]
            before=core.replay(test,prior,skills,min_history=2)
            target=test[-1]
            modified=[dict(x) for x in test]
            modified[-1]["correct"]=1-modified[-1]["correct"]
            modified[-1]["score"]=float(modified[-1]["correct"])
            after=core.replay(modified,prior,skills,min_history=2)
            key=target["learner"]
            concept=target["concept"]
            # Final recorded observation in its learner/skill sequence might
            # be within the eligible sequence, and must not affect its own prediction.
            orig=[x for x in before if x["learner"]==key and x["concept"]==concept]
            newer=[x for x in after if x["learner"]==key and x["concept"]==concept]
            self.assertTrue(orig)
            self.assertEqual(orig[-1]["diagnostic_index"],newer[-1]["diagnostic_index"])
            self.assertEqual(orig[-1]["local_history"],newer[-1]["local_history"])
            self.assertNotEqual(orig[-1]["target"],newer[-1]["target"])

    def test_report_is_aggregated(self):
        with tempfile.TemporaryDirectory() as d:
            events,audit=assist.load(make_file(d),max_learners=60)
            out=assist.evaluate(events,audit,bootstraps=10)
            self.assertIn("within_concept_macro_auc",out["test"])
            self.assertNotIn('"learner":',json.dumps(out))
            self.assertNotIn('"user_id":',json.dumps(out))
            self.assertEqual("do_not_add_yet",out["readiness"]["bkt_irt_decision"])

    def test_conflicting_duplicates_raise(self):
        with tempfile.TemporaryDirectory() as d:
            f=make_file(d)
            with f.open("a",encoding="utf-8") as out:
                out.write("u0,1,s0,1\n")
                out.write("u0,1,s0,0\n")
            # For a sampled user rather than relying on u0's hash rank.
            with self.assertRaisesRegex(ValueError,"conflicting repeated"):
                assist.load(f,max_learners=70)

    def test_input_limit_is_enforced(self):
        with tempfile.TemporaryDirectory() as d:
            f=make_file(d)
            with self.assertRaisesRegex(ValueError,"limit exceeded"):
                assist.load(f,max_rows=100)

    def test_bad_header_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"invalid.csv"
            f.write_text("id,answer\n1,1\n",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"requires four known"):
                assist.load(f)

    def test_reject_tiny_fake_samples(self):
        with tempfile.TemporaryDirectory() as d:
            f=make_file(d,count=4)
            with self.assertRaisesRegex(ValueError,"too few independent"):
                assist.load(f)


if __name__=="__main__":
    unittest.main()
