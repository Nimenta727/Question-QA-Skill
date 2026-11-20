"""Real external-criterion evaluation tests, synthetic cases only."""
import csv
import tempfile
import unittest
from pathlib import Path
from scripts.evaluate_forget_se import (evaluate, examine, load,
                                        split_learners, baseline_priors)


def example():
    quiz, exam = {}, {}
    for n in range(150):
        u = "student_%03d" % n
        exam[u] = {}
        for c in range(1, 11):
            concept = str(c)
            exam[u][concept] = int((n*5+c*7) % 11 >= 4)
            quiz[(u, concept)] = [{
                "id": "q_%d_%d" % (c,i), "family": "q_%d_%d" % (c,i),
                "concept": concept, "score": float((n+c+i)%4 != 0),
                "level": "understand", "difficulty": 2, "type": "short",
                "confidence": "none", "hint_used": False,
                "at": "2020-01-01T00:00:00+00:00",
                "order": i, "row": i} for i in range(5)]
    return quiz, exam, {"matched_learners": 150}


class ExternalCriterionTests(unittest.TestCase):
    def test_disjoint_and_deterministic_splits(self):
        _, exam, _ = example()
        a, b = split_learners(exam, 2026), split_learners(exam, 2026)
        self.assertEqual(a, b)
        self.assertFalse(a["train"] & a["test"])
        self.assertFalse(a["validation"] & a["test"])

    def test_future_exam_label_does_not_enter_priors_or_features(self):
        quiz, exam, _ = example()
        splits = split_learners(exam, 2026)
        prior, skills = baseline_priors(exam, splits["train"])
        student = sorted(splits["test"])[0]
        changed = {u: dict(row) for u, row in exam.items()}
        changed[student]["1"] = 1 - changed[student]["1"]
        self.assertEqual((prior, skills), baseline_priors(changed, splits["train"]))
        x = examine(quiz, exam, {student}, prior, skills, 2)
        y = examine(quiz, changed, {student}, prior, skills, 2)
        a, b = next(r for r in x if r["concept"]=="1"), next(r for r in y if r["concept"]=="1")
        self.assertNotEqual(a["target"], b["target"])
        self.assertEqual(a["diagnostic_index"], b["diagnostic_index"])
        self.assertEqual(a["quiz_average"], b["quiz_average"])

    def test_aggregate_has_no_student_identifier(self):
        quiz, exam, audit = example()
        report = evaluate(quiz, exam, audit, bootstraps=0)
        self.assertNotIn("student_001", str(report))
        self.assertNotIn("student_002", str(report))
        self.assertFalse(report["decision"]["add_bkt_or_irt"])

    def test_no_invented_cognitive_level_or_delay(self):
        quiz, exam, audit = example()
        report = evaluate(quiz, exam, audit, bootstraps=0)
        self.assertEqual(0, report["test"]["diagnostic_labels"]["tentatively_strong"]["count"])
        self.assertFalse(report["decision"]["can_evaluate_provisional_strong"])

    def test_all_comparison_baselines_and_deterministic_bootstrap(self):
        quiz, exam, audit = example()
        r = evaluate(quiz, exam, audit, bootstraps=10)
        s = evaluate(quiz, exam, audit, bootstraps=10)
        self.assertEqual(r, s)
        self.assertGreater(r["test"]["n"], 0)
        self.assertTrue(all(k in r["test"]["models"] for k in (
            "global","concept_prior","quiz_average","quiz_recent3","diagnostic_index")))
        self.assertNotIn("brier", r["test"]["models"]["diagnostic_index"])

    def test_minimum_history_prevents_unobserved_predictions(self):
        quiz, exam, _ = example()
        splits = split_learners(exam, 2026)
        prior, skills = baseline_priors(exam, splits["train"])
        student = sorted(splits["test"])[0]
        quiz[(student, "1")] = quiz[(student,"1")][:1]
        rows = examine(quiz, exam, {student}, prior, skills, 2)
        self.assertFalse(any(x["concept"]=="1" for x in rows))

    def test_fractional_quiz_scores_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            p, e = Path(d)/"w.csv", Path(d)/"exam.csv"
            p.write_text("user_id,qid,sequence_id,log_id,correct\nu1,q1,1,100,0.6\n")
            e.write_text("user_id," + ",".join("KC%d" % k for k in range(1,11))
                         + "\nu1," + ",".join(["1"]*10) + "\n")
            quizzes, exams, audit = load(p,e)
            self.assertEqual(0.6, quizzes[("u1","1")][0]["score"])
            self.assertEqual(1, audit["partial_weekly_scores"])
            self.assertEqual(1, audit["matched_learners"])

    def test_nonbinary_exam_outcome_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p, e = Path(d)/"w.csv", Path(d)/"exam.csv"
            p.write_text("user_id,qid,sequence_id,log_id,correct\nu1,q1,1,100,0.5\n")
            e.write_text("user_id," + ",".join("KC%d" % k for k in range(1,11))
                         + "\nu1," + ",".join(["0.5"]+["1"]*9) + "\n")
            with self.assertRaisesRegex(ValueError, "binary"):
                load(p,e)


if __name__ == "__main__":
    unittest.main()
