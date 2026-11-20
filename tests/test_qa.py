"""Regression tests: run python3 -m unittest discover -s tests -v."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.qa import (due_date, estimate, grade, read_bank, select_item,
                        validate_bank)

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "examples" / "sample_bank.json"
SCRIPT = ROOT / "scripts" / "qa.py"


class BankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, _ = read_bank(BANK)

    def test_example_valid(self):
        self.assertEqual(9, len(validate_bank(self.data)))

    def test_duplicate_rejected(self):
        bank = copy.deepcopy(self.data)
        bank["items"][1]["id"] = bank["items"][0]["id"]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_bank(bank)

    def test_duplicated_choices_rejected(self):
        bank = copy.deepcopy(self.data)
        bank["items"][0]["options"][1] = bank["items"][0]["options"][0]
        with self.assertRaisesRegex(ValueError, "duplicate options"):
            validate_bank(bank)

    def test_one_at_a_time_and_objective_grading(self):
        q = self.data["items"][0]
        self.assertEqual((1.0, "exact_key"), grade(q, "C"))
        self.assertEqual((1.0, "exact_key"), grade(q, "5"))
        self.assertEqual((0.0, "exact_key"), grade(q, "B"))
        with self.assertRaises(ValueError):
            grade(q, "C", 1.0, "override")

    def test_short_exact_and_manual_review(self):
        short = next(q for q in self.data["items"] if q["id"] == "ALG-003")
        self.assertEqual(1.0, grade(short, "７")[0])
        self.assertEqual(0.0, grade(short, "seven")[0])
        manual = next(q for q in self.data["items"] if q["type"] == "manual")
        with self.assertRaises(ValueError):
            grade(manual, "anything")
        with self.assertRaises(ValueError):
            grade(manual, "anything", 0.5, "")
        self.assertEqual((0.5, "rubric_review"), grade(manual, "answer", 0.5, "one of three criteria"))

    def test_evidence_requires_three_and_two_unique_items(self):
        def e(item, score=1):
            return {"id": item, "score": score}
        self.assertEqual("insufficient_evidence", estimate([e("a"), e("a"), e("a")])["label"])
        self.assertEqual("tentatively_strong", estimate([e("a"), e("b"), e("b")])["label"])
        self.assertEqual("needs_review", estimate([e("a", 0), e("b", 0), e("b", 0)])["label"])

    def test_selection_prefers_unseen_concepts(self):
        history = [{"id": "ALG-001", "concept": "linear-equations", "level": "recall",
                    "score": 1, "at": datetime.now(timezone.utc).isoformat()}]
        chosen = select_item(self.data["items"], history, "quick")
        self.assertIn(chosen["concept"], {"functions", "proportions"})

    def test_due_date(self):
        old = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        events = [{"score": 1, "at": old} for _ in range(2)]
        self.assertLessEqual(due_date(events), datetime.now(timezone.utc).date().isoformat())


class CliTests(unittest.TestCase):
    def run_cli(self, *parts):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, parts)],
                              text=True, capture_output=True)

    def test_pending_does_not_leak_key_and_duplicate_grade_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "learning.json"
            first = self.run_cli("next", BANK, "--state", state)
            self.assertEqual(0, first.returncode, first.stderr)
            prompt = json.loads(first.stdout)
            self.assertNotIn("answer", prompt)
            self.assertNotIn("explanation", prompt)
            again = self.run_cli("next", BANK, "--state", state)
            self.assertEqual(prompt, json.loads(again.stdout))
            answered = self.run_cli("answer", BANK, "--state", state,
                                    "--response", "A")
            self.assertEqual(0, answered.returncode, answered.stderr)
            self.assertIn("score", json.loads(answered.stdout))
            duplicate = self.run_cli("answer", BANK, "--state", state,
                                     "--response", "A")
            self.assertNotEqual(0, duplicate.returncode)
            report = self.run_cli("report", "--state", state)
            self.assertEqual(1, json.loads(report.stdout)["total_answers"])

    def test_bank_change_during_pending_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            state, bank = Path(tmp) / "s.json", Path(tmp) / "bank.json"
            bank.write_bytes(BANK.read_bytes())
            self.assertEqual(0, self.run_cli("next", bank, "--state", state).returncode)
            data = json.loads(bank.read_text(encoding="utf-8"))
            data["subject"] += " modified"
            bank.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            blocked = self.run_cli("answer", bank, "--state", state, "--response", "A")
            self.assertNotEqual(0, blocked.returncode)
            self.assertIn("changed", blocked.stderr)

    def test_invalid_manual_without_reason_does_not_consume_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            state, bank = Path(tmp) / "s.json", Path(tmp) / "bank.json"
            example = next(x for x in read_bank(BANK)[0]["items"] if x["type"] == "manual")
            bank.write_text(json.dumps({"version": 1, "subject": "test", "items": [example]}),
                            encoding="utf-8")
            self.assertEqual(0, self.run_cli("next", bank, "--state", state).returncode)
            bad = self.run_cli("answer", bank, "--state", state,
                               "--response", "some answer", "--score", "1")
            self.assertNotEqual(0, bad.returncode)
            self.assertTrue(json.loads(state.read_text())["pending"])
            good = self.run_cli("answer", bank, "--state", state,
                                "--response", "some answer", "--score", "1",
                                "--reason", "meets all rubric criteria")
            self.assertEqual(0, good.returncode, good.stderr)


if __name__ == "__main__":
    unittest.main()
