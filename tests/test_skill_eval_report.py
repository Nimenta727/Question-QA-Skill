"""Guard factual/provenance gates for the compact post-run Skill report."""
import copy
import html
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import skill_eval_report as report

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples/synthetic_skill_eval.json"


class CompactEvalReportTests(unittest.TestCase):
    def setUp(self):
        self.data = report.read_report(FIXTURE)

    def test_synthetic_fixture_counts_are_exact_and_never_real(self):
        s = report.summarize(self.data)
        self.assertEqual("synthetic_demo", s["evidence"])
        self.assertEqual(19, s["cases"])
        self.assertEqual(13, s["audited"])
        self.assertEqual(6, s["tutored"])
        self.assertEqual((5, 7),
                         (s["scores"]["defect_detection"]["numerator"],
                          s["scores"]["defect_detection"]["denominator"]))
        self.assertEqual((5, 6),
                         (s["scores"]["sound_acceptance"]["numerator"],
                          s["scores"]["sound_acceptance"]["denominator"]))
        self.assertEqual((4, 5),
                         (s["scores"]["tutoring_match"]["numerator"],
                          s["scores"]["tutoring_match"]["denominator"]))
        self.assertEqual(2, s["unresolved"])
        self.assertEqual(1, s["failure_types"]["missed_defect"])
        self.assertEqual(1, s["failure_types"]["false_alarm"])

    def test_wilson_intervals_are_bounded(self):
        for numerator, denominator in ((0, 6), (6, 6), (5, 7), (1, 20)):
            lo, hi = report.wilson(numerator, denominator)
            self.assertLessEqual(0, lo)
            self.assertLessEqual(lo, numerator / denominator)
            self.assertLessEqual(numerator / denominator, hi)
            self.assertLessEqual(hi, 1)
        with self.assertRaises(ValueError):
            report.wilson(2, 1)

    def test_synthetic_html_is_static_local_accessible_and_disclosed(self):
        s = report.summarize(self.data)
        zh = report.render(self.data, s)
        en = report.render(self.data, s, "en")
        for page, banner in ((zh, "合成演示"), (en, "Synthetic demo")):
            self.assertIn(banner, page)
            self.assertIn("<details>", page)
            self.assertIn("5/7", page)
            self.assertIn("5/6", page)
            self.assertNotIn("<script", page.lower())
            self.assertNotIn("https://", page.lower())
            self.assertIn("Content-Security-Policy", page)
            self.assertIn("style=\"width:", page)
        self.assertIn("缺陷类别", zh)

    def test_no_labels_means_no_semantic_rate_or_fake_risk(self):
        d = copy.deepcopy(self.data)
        d["run"]["mode"] = "actual_model"
        d["run"]["reference"] = "model_only"
        s = report.summarize(d)
        self.assertEqual("unverified", s["evidence"])
        for v in s["scores"].values():
            self.assertIsNone(v["rate"])
            self.assertIsNone(v["numerator"])
        page = report.render(d, s)
        self.assertIn("缺少独立效标", page)
        self.assertNotIn("错误题被放行 / Defective accepted", page)

    def test_n_less_than_five_and_repeated_family_suppress_false_precision(self):
        d = copy.deepcopy(self.data)
        d["cases"] = d["cases"][:2]
        s = report.summarize(d)
        self.assertIsNone(s["scores"]["defect_detection"]["rate"])
        self.assertIn("样本不足", report.render(d, s))
        d = copy.deepcopy(self.data)
        d["cases"][1]["family"] = d["cases"][0]["family"]
        s = report.summarize(d)
        self.assertFalse(s["scores"]["defect_detection"]["independent_families"])
        self.assertIsNone(s["scores"]["defect_detection"]["wilson_95"])

    def test_empty_dataset_does_not_invent_zero_percent(self):
        d = copy.deepcopy(self.data)
        d["cases"] = []
        s = report.summarize(d)
        page = report.render(d, s)
        self.assertNotIn("0.0%", page)
        self.assertIn("未测量", page)

    def test_unknown_personal_or_raw_text_fields_fail_closed(self):
        for malicious in ("student_text", "raw_prompt", "student_name", "source_excerpt"):
            d = copy.deepcopy(self.data)
            d["cases"][0][malicious] = "PRIVATE"
            with tempfile.TemporaryDirectory() as directory:
                p = Path(directory) / "input.json"
                p.write_text(json.dumps(d), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "unexpected"):
                    report.read_report(p)

    def test_bad_data_rejected_without_partial_report(self):
        for field, val in (
            ("id", "A02"), ("input_tokens", -1), ("latency_ms", float("nan")),
            ("test_id", "RM-42"), ("decision", "pass"),
        ):
            d = copy.deepcopy(self.data)
            d["cases"][0][field] = val
            with tempfile.TemporaryDirectory() as directory:
                p = Path(directory) / "input.json"
                p.write_text(json.dumps(d), encoding="utf-8")
                with self.assertRaises(ValueError):
                    report.read_report(p)

    def test_html_escape_prevents_injection(self):
        d = copy.deepcopy(self.data)
        d["cases"][0]["id"] = "<img src=x onerror=alert(1)>"
        s = report.summarize(d)
        page = report.render(d, s)
        self.assertNotIn("<img src=x", page)
        self.assertIn(html.escape("<img src=x onerror=alert(1)>"), page)

    def test_block_without_matching_real_defect_is_not_detected(self):
        d = copy.deepcopy(self.data)
        d["cases"][0]["caught_actual_defect"] = False
        s = report.summarize(d)
        self.assertEqual(4, s["scores"]["defect_detection"]["numerator"])
        self.assertEqual(1, s["failure_types"]["unmatched_block"])

    def test_blocked_defect_requires_explicit_expert_match(self):
        d = copy.deepcopy(self.data)
        d["cases"][0].pop("caught_actual_defect")
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "input.json"
            p.write_text(json.dumps(d), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "requires independently adjudicated"):
                report.read_report(p)

    def test_real_model_requires_non_synthetic_reference(self):
        d = copy.deepcopy(self.data)
        d["run"]["mode"] = "actual_model"
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "input.json"
            p.write_text(json.dumps(d), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "synthetic references"):
                report.read_report(p)

    def test_cli_renders_and_writes_public_aggregate(self):
        with tempfile.TemporaryDirectory() as directory:
            html_path = Path(directory) / "compact.html"
            json_path = Path(directory) / "summary.json"
            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts/skill_eval_report.py"),
                 str(FIXTURE), "--output", str(html_path),
                 "--summary", str(json_path)],
                capture_output=True, text=True, check=False)
            self.assertEqual(0, proc.returncode, proc.stderr)
            self.assertIn("合成演示", html_path.read_text(encoding="utf-8"))
            data = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertNotIn("failures", data)
            self.assertEqual("synthetic_demo", data["evidence"])
            self.assertEqual(19, data["cases"])


if __name__ == "__main__":
    unittest.main()
