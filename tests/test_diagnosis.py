"""Diagnosis evidence and session regression tests (stdlib only)."""
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from scripts.diagnosis import estimate, select_item
from scripts.qa import read_bank, validate_bank

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "examples" / "sample_bank.json"
SCRIPT = ROOT / "scripts" / "qa.py"
NOW = datetime(2026, 11, 20, tzinfo=timezone.utc)


def ev(item, concept="algebra", level="understand", score=1, day=0,
       family=None, confidence="sure", hint_used=False, kind="short"):
    return {"id": item, "family": family or item, "concept": concept,
            "level": level, "score": score, "type": kind,
            "confidence": confidence, "hint_used": hint_used,
            "difficulty": 2, "at": (NOW + timedelta(days=day)).isoformat()}


class TestEvidence(unittest.TestCase):
    def test_empty_untested(self):
        self.assertEqual("untested", estimate([])["label"])

    def test_same_family_same_day_repetition_not_independent(self):
        first = estimate([ev("a")])
        repeats = estimate([ev("a")] * 50)
        self.assertEqual(first["rate"], repeats["rate"])
        self.assertEqual(1, repeats["families"])
        self.assertEqual("insufficient_evidence", repeats["label"])

    def test_same_day_is_not_delayed_retention(self):
        s = estimate([ev("a", level="recall"), ev("b", level="understand"),
                      ev("c", level="apply"), ev("d", level="transfer")])
        self.assertEqual("developing", s["label"])
        self.assertIn("no_delayed_retrieval", s["gaps"])

    def test_provisionally_strong_requires_breadth_and_delay(self):
        s = estimate([ev("a", level="recall"), ev("b", level="understand"),
                      ev("c", level="apply", day=2),
                      ev("d", level="transfer", day=2)])
        self.assertEqual("tentatively_strong", s["label"])
        self.assertEqual(2, s["days"])

    def test_guess_does_not_equal_confident_independent_success(self):
        entries = [ev("a", level="recall"), ev("b", level="understand"),
                   ev("c", level="apply", day=2), ev("d", level="transfer", day=2)]
        good = estimate(entries)
        guess = estimate([dict(e, confidence="guess") for e in entries])
        self.assertLess(guess["effective_evidence"], good["effective_evidence"])
        self.assertIn("correct_but_guessed", guess["flags"])
        self.assertNotEqual("tentatively_strong", guess["label"])

    def test_confident_errors_highlight_review(self):
        s = estimate([ev("a", score=0), ev("b", score=0), ev("c", score=0)])
        self.assertIn("confident_error", s["flags"])
        self.assertEqual("needs_review", s["label"])

    def test_shared_variant_family_not_three_independent_items(self):
        entries = [ev("a", family="family-1", day=0),
                   ev("b", family="family-1", day=1),
                   ev("c", family="family-1", day=2),
                   ev("d", family="family-1", day=3)]
        self.assertEqual(1, estimate(entries)["families"])
        self.assertNotEqual("tentatively_strong", estimate(entries)["label"])

    def test_recent_miss_demotes_strong(self):
        entries = [ev("a", level="recall"), ev("b", level="understand"),
                   ev("c", level="apply", day=2), ev("d", level="transfer", day=2),
                   ev("e", level="transfer", day=3, score=0)]
        self.assertIn("recent_miss", estimate(entries)["flags"])
        self.assertNotEqual("tentatively_strong", estimate(entries)["label"])

    def test_hinted_correct_counts_less(self):
        self.assertLess(estimate([ev("a", hint_used=True)])["effective_evidence"],
                        estimate([ev("a")])["effective_evidence"])

    def test_wrong_answer_targets_repair(self):
        bank = [{"id":"x1","concept":"x","level":"understand","type":"single","difficulty":2},
                {"id":"x2","concept":"x","level":"apply","type":"short","difficulty":1},
                {"id":"y1","concept":"y","level":"recall","type":"single","difficulty":1}]
        wrong = ev("x1", concept="x", score=0)
        self.assertEqual("x2", select_item(bank, [wrong], session_history=[wrong])["id"])

    def test_guessed_correct_targets_verification(self):
        bank = [{"id":"x1","concept":"x","level":"understand","type":"single","difficulty":2},
                {"id":"x2","concept":"x","level":"apply","type":"short","difficulty":1},
                {"id":"y1","concept":"y","level":"recall","type":"single","difficulty":1}]
        unsure = ev("x1", concept="x", score=1, confidence="guess")
        self.assertEqual("x2", select_item(bank, [unsure], session_history=[unsure])["id"])

    def test_no_same_item_in_same_session(self):
        q = [{"id":"one","concept":"x","level":"recall","type":"short","difficulty":1}]
        a = ev("one", concept="x")
        self.assertIsNone(select_item(q, [a], session_history=[a]))

    def test_focus_boundaries(self):
        q = [{"id":"one","concept":"x","level":"recall","type":"short","difficulty":1},
             {"id":"two","concept":"y","level":"recall","type":"short","difficulty":1}]
        self.assertEqual("x", select_item(q, [], focus="x")["concept"])
        self.assertIsNone(select_item(q, [], focus="missing"))

    def test_reject_wrong_misconception_key(self):
        bank, _ = read_bank(BANK)
        bank["items"][0]["misconceptions"] = {"C": "cannot map correct option"}
        with self.assertRaisesRegex(ValueError, "misconceptions"):
            validate_bank(bank)

    def test_reject_unknown_prerequisite(self):
        bank, _ = read_bank(BANK)
        bank["items"][0]["prerequisites"] = ["not-in-bank"]
        with self.assertRaisesRegex(ValueError, "prerequisites"):
            validate_bank(bank)


class TestCli(unittest.TestCase):
    def cmd(self, *parts):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, parts)],
                              text=True, capture_output=True)

    def test_budget_stop(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d) / "learning.json"
            self.assertEqual(0, self.cmd("start", BANK, "--state", state,
                                         "--limit", 1, "--focus", "functions").returncode)
            first = self.cmd("next", BANK, "--state", state)
            self.assertEqual(0, first.returncode, first.stderr)
            self.assertNotIn("answer", json.loads(first.stdout))
            self.assertEqual(0, self.cmd("answer", BANK, "--state", state,
                                         "--response", "A").returncode)
            done = json.loads(self.cmd("next", BANK, "--state", state).stdout)
            self.assertEqual("question_budget_reached", done["reason"])

    def test_bank_exhaustion_no_repeat(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d) / "s.json"
            self.cmd("start", BANK, "--state", state, "--limit", 20,
                     "--focus", "proportions")
            for _ in range(2):
                question = json.loads(self.cmd("next", BANK, "--state", state).stdout)
                self.assertIn("question", question)
                self.assertEqual(0, self.cmd("answer", BANK, "--state", state,
                                             "--response", "A").returncode)
            self.assertEqual("item_bank_exhausted",
                             json.loads(self.cmd("next", BANK, "--state", state).stdout)["reason"])

    def test_untested_concepts_are_visible(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d) / "s.json"
            out = self.cmd("report", "--state", state, "--bank", BANK)
            self.assertEqual(0, out.returncode, out.stderr)
            concepts = json.loads(out.stdout)["concepts"]
            self.assertTrue(concepts)
            self.assertTrue(all(c["label"] == "untested" for c in concepts))

    def test_no_raw_response_persisted(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d) / "s.json"
            self.cmd("next", BANK, "--state", state)
            out = self.cmd("answer", BANK, "--state", state,
                           "--response", "A", "--confidence", "guess", "--hint-used")
            self.assertEqual(0, out.returncode, out.stderr)
            raw = state.read_text(encoding="utf-8")
            ev0 = json.loads(raw)["history"][0]
            self.assertEqual("guess", ev0["confidence"])
            self.assertTrue(ev0["hint_used"])
            self.assertNotIn('"response"', raw)

    def test_start_does_not_drop_pending_without_consent(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d) / "s.json"
            self.cmd("next", BANK, "--state", state)
            self.assertNotEqual(0, self.cmd("start", BANK, "--state", state).returncode)
            self.assertEqual(0, self.cmd("start", BANK, "--state", state,
                                         "--discard-pending").returncode)


if __name__ == "__main__":
    unittest.main()
