"""Standard-library tests for learner-disjoint causal validation."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.evaluate import (auc, bootstrap_auc, bucket, diagnostics, evaluate,
                              load_csv, metric, priors, replay, split_rows, wilson)


def make_rows(count=150, attempts=9, seed=0):
    from datetime import datetime, timedelta, timezone
    origin = datetime(2026, 1, 1, tzinfo=timezone.utc)
    rows = []
    for learner in range(count):
        for i in range(attempts):
            event = {
                "learner": "student-%03d" % learner, "concept": "skillA",
                "id": "q-%d" % i, "family": "f-%d" % i,
                "order": float(i + 1), "row": learner * attempts + i,
                "correct": int(((learner * 7 + i * 3 + seed) % 10) >= 3),
                "level": ("recall", "understand", "apply", "transfer")[i%4],
                "difficulty": 2, "type": "short", "hint_used": False,
                "confidence": "sure",
                "stamp": (origin + timedelta(days=i//3)).isoformat()
            }
            event["score"] = float(event["correct"])
            event["at"] = event["stamp"]
            rows.append(event)
    return rows


class TestMath(unittest.TestCase):
    def test_auc_matches_known_example(self):
        self.assertAlmostEqual(1.0, auc([(0.9, 1), (0.1, 0)]))
        self.assertAlmostEqual(0.5, auc([(0.5, 1), (0.5, 0)]))
        self.assertIsNone(auc([(0.5, 1), (0.9, 1)]))

    def test_wilson_finite_and_bounds(self):
        self.assertIsNone(wilson(0, 0))
        lo, hi = wilson(20, 100)
        self.assertTrue(0 <= lo < 0.2 < hi <= 1)

    def test_metrics_perfect(self):
        data = [{"learner": "a", "target": 1, "p": 1},
                {"learner": "b", "target": 0, "p": 0}]
        m = metric(data, "p")
        self.assertAlmostEqual(1.0, m["auc"])
        self.assertAlmostEqual(0.0, m["brier"])
        self.assertAlmostEqual(0.0, m["ece_10bin"])
        raw = metric(data, "p", probability=False)
        self.assertNotIn("brier", raw)


class TestProtocol(unittest.TestCase):
    def test_deterministic_learner_disjoint(self):
        records = make_rows()
        a = split_rows(records, seed=43)
        b = split_rows(records, seed=43)
        self.assertEqual({k: len(v) for k,v in a.items()},
                         {k: len(v) for k,v in b.items()})
        users = {k: {r["learner"] for r in v} for k,v in a.items()}
        self.assertFalse(users["train"] & users["test"])
        self.assertFalse(users["validation"] & users["test"])
        self.assertFalse(users["validation"] & users["train"])

    def test_prediction_does_not_see_future_target(self):
        rows = make_rows(count=1, attempts=7)
        prior, concepts = priors(make_rows(count=10, attempts=6))
        before = replay(rows, prior, concepts, min_history=2)
        self.assertTrue(before)
        modified = [dict(x) for x in rows]
        modified[-1]["correct"] = 1 - modified[-1]["correct"]
        modified[-1]["score"] = float(modified[-1]["correct"])
        after = replay(modified, prior, concepts, min_history=2)
        self.assertEqual(before[-1]["diagnostic_index"],
                         after[-1]["diagnostic_index"])
        self.assertEqual(before[-1]["local_history"], after[-1]["local_history"])
        self.assertNotEqual(before[-1]["target"], after[-1]["target"])

    def test_predictions_prior_only_on_current_skill(self):
        rows = make_rows(count=1, attempts=6)
        for i in range(3, 6):
            rows[i]["concept"] = "skillB"
        prior, concepts = priors(make_rows(count=5, attempts=4))
        out = replay(rows, prior, concepts, min_history=2)
        self.assertEqual(2, len(out))  # A's third event and B's third event

    def test_reproducible_metrics(self):
        a = evaluate(make_rows(), seed=2026, min_history=2, bootstraps=15)
        b = evaluate(make_rows(), seed=2026, min_history=2, bootstraps=15)
        self.assertEqual(a, b)
        self.assertGreater(a["test"]["eligible_predictions"], 0)
        self.assertEqual("do_not_add_yet", a["readiness"]["bkt_irt_decision"])

    def test_historical_selection_not_claimed_causal(self):
        report = evaluate(make_rows(), bootstraps=0)
        self.assertTrue(any("cannot estimate adaptive" in s for s in report["limitations"]))

    def test_no_identifiers_in_report(self):
        report = evaluate(make_rows(), bootstraps=0)
        raw = json.dumps(report)
        self.assertNotIn("student-001", raw)
        self.assertNotIn('"learner":', raw)
        self.assertNotIn('"concept":', raw)

    def test_strong_proxy_measures_next_error_not_mastery(self):
        rows = [{"diagnostic_label": "tentatively_strong", "target": 0,
                 "learner": "a"}, {"diagnostic_label": "tentatively_strong",
                 "target": 1, "learner": "b"}]
        d = diagnostics(rows)
        self.assertEqual(0.5, d["tentatively_strong"]["next_response_error_rate"])
        self.assertEqual(2, d["tentatively_strong"]["n"])

    def test_bootstrap_empty_or_missing_class(self):
        self.assertIsNone(bootstrap_auc([], "p", n_boot=2))
        x = [{"learner": "a", "target": 1, "p": 0.9},
             {"learner": "b", "target": 1, "p": 0.8}]
        self.assertIsNone(bootstrap_auc(x, "p", n_boot=5))

    def test_small_split_fails_loudly(self):
        with self.assertRaisesRegex(ValueError, "need learners"):
            evaluate(make_rows(count=1))

    def test_input_guard_coverage(self):
        with self.assertRaisesRegex(ValueError, "min-history"):
            evaluate(make_rows(), min_history=0)
        with self.assertRaisesRegex(ValueError, "bootstraps"):
            evaluate(make_rows(), bootstraps=-1)


class TestCSV(unittest.TestCase):
    def csvfile(self, path, fields, rows):
        with open(path, "w", encoding="utf-8", newline="") as out:
            writer = csv.DictWriter(out, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_generic_parses_time_and_flags(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "data.csv"
            self.csvfile(path, ["learner_id", "concept_id", "item_id", "correct",
                                "order", "answered_at", "level", "confidence",
                                "hint_used"], [
                {"learner_id": "u1", "concept_id": "s1", "item_id": "p1",
                 "correct": "1", "order": "1", "answered_at": "2026-11-20T08:00:00Z",
                 "level": "apply", "confidence": "guess", "hint_used": "true"}])
            rows, audit = load_csv(path)
            self.assertTrue(audit["has_calendar_dates"])
            self.assertTrue(rows[0]["hint_used"])
            self.assertEqual("apply", rows[0]["level"])

    def test_missing_mixed_dates_not_durable(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "data.csv"
            self.csvfile(path, ["learner_id", "concept_id", "item_id", "correct",
                                "answered_at"], [
                {"learner_id": "a", "concept_id": "x", "item_id": "1",
                 "correct": "1", "answered_at": "2026-01-01"},
                {"learner_id": "a", "concept_id": "x", "item_id": "2",
                 "correct": "0", "answered_at": ""}])
            with self.assertRaisesRegex(ValueError, "mixed missing"):
                load_csv(path)

    def test_duplicate_events_are_deduplicated(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "data.csv"
            self.csvfile(path, ["learner_id", "concept_id", "item_id", "correct",
                                "order"], [
                {"learner_id":"a","concept_id":"x","item_id":"p",
                 "correct":"1","order":"1"},
                {"learner_id":"a","concept_id":"x","item_id":"p",
                 "correct":"1","order":"1"}])
            rows, audit = load_csv(path)
            self.assertEqual(1, len(rows))
            self.assertEqual(1, audit["duplicates"])

    def test_conflicting_duplicates_raise(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "data.csv"
            self.csvfile(path, ["learner_id", "concept_id", "item_id", "correct",
                                "order"], [
                {"learner_id":"a","concept_id":"x","item_id":"p",
                 "correct":"1","order":"1"},
                {"learner_id":"a","concept_id":"x","item_id":"p",
                 "correct":"0","order":"1"}])
            with self.assertRaisesRegex(ValueError, "conflicting duplicate"):
                load_csv(path)

    def test_assistments_filters_scaffold_and_open_response(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "assist.csv"
            fields = ["user_id", "skill_id", "problem_id", "correct",
                      "order_id", "answer_type", "original"]
            self.csvfile(path, fields, [
                {"user_id":"a","skill_id":"1","problem_id":"1","correct":"1",
                 "order_id":"1","answer_type":"choose_1","original":"1"},
                {"user_id":"a","skill_id":"1","problem_id":"2","correct":"1",
                 "order_id":"2","answer_type":"open_response","original":"1"},
                {"user_id":"a","skill_id":"1","problem_id":"3","correct":"1",
                 "order_id":"3","answer_type":"algebra","original":"0"}])
            rows, audit = load_csv(path, schema="assistments09")
            self.assertEqual(1, len(rows))
            self.assertEqual(2, audit["skipped"])
            self.assertFalse(audit["has_calendar_dates"])

    def test_bad_correct_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "bad.csv"
            self.csvfile(path, ["learner_id", "concept_id", "item_id", "correct"],
                         [{"learner_id":"a","concept_id":"x","item_id":"1",
                           "correct":"yes"}])
            with self.assertRaisesRegex(ValueError, "0/1"):
                load_csv(path)


if __name__ == "__main__":
    unittest.main()
