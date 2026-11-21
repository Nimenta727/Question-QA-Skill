"""Guard release identifiers and clearly unperformed real-model validation claims.

CI regression proves repository consistency, not item semantics or student outcomes.
"""
import re
import unittest
from pathlib import Path
from scripts import build_release as release

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
EXPECTED = "1.2.1"
CASES = tuple(f"RM-{i:02}" for i in range(1, 13))


class ReleaseContractTests(unittest.TestCase):
    def test_version_and_package_roots_agree(self):
        self.assertEqual(EXPECTED, VERSION)
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn(f'version: "{VERSION}"', skill)
        self.assertEqual(f"question-qa-skill-{VERSION}", release.PACKAGE_ROOT)
        self.assertEqual(f"question-qa-skill-core-{VERSION}", release.CORE_PACKAGE_ROOT)
        for path in ("README.md", "README.zh-CN.md",
                     "docs/INSTALL.md", "docs/INSTALL.zh-CN.md",
                     "docs/RELEASE.md", "docs/RELEASE.zh-CN.md",
                     "docs/CORE_PACKAGE.md"):
            text = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn(f"question-qa-skill-{VERSION}.zip", text, path)
            if path != "docs/CORE_PACKAGE.md":
                self.assertIn(f"question-qa-skill-core-{VERSION}.zip", text, path)

    def test_release_workflow_checks_and_links(self):
        release_yaml = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        test_yaml = (ROOT / ".github/workflows/tests.yml").read_text(encoding="utf-8")
        for yml in (release_yaml, test_yaml):
            for name in (f"question-qa-skill-{VERSION}.zip",
                         f"question-qa-skill-core-{VERSION}.zip"):
                self.assertIn(name, yml)
        for fragment in ("sha256sum --check SHA256SUMS.txt",
                         "gh release create",
                         "Branch changed since verification",
                         f"docs/RELEASE_NOTES_v{VERSION}.md",
                         "Run smoke tests inside a freshly extracted ZIP"):
            self.assertIn(fragment, release_yaml)
        self.assertTrue((ROOT / f"docs/RELEASE_NOTES_v{VERSION}.md").is_file())

    def test_empirical_cases_are_explicitly_not_run(self):
        zh = (ROOT / "docs/REAL_MODEL_TESTS.zh-CN.md").read_text(encoding="utf-8")
        en = (ROOT / "docs/REAL_MODEL_TESTS.md").read_text(encoding="utf-8")
        self.assertTrue(all(re.search(r"\b" + case + r"\b", zh) for case in CASES))
        self.assertTrue(all(re.search(r"\b" + case + r"\b", en) for case in CASES))
        self.assertGreaterEqual(zh.count("**未测试**"), 12)
        self.assertGreaterEqual(en.count("**NOT RUN**"), 12)
        for path in ("README.md", "README.zh-CN.md"):
            readme = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn("docs/REAL_MODEL_TESTS", readme)
            self.assertIn("docs/TEST_STATUS", readme)
            self.assertIn("docs/validation/REPORT_TEMPLATE.md", readme)
        self.assertTrue((ROOT / "docs/validation/REPORT_TEMPLATE.md").exists())
        self.assertFalse(any(p.relative_to(ROOT).as_posix().startswith("docs/")
                             for p in release.core_files()))


if __name__ == "__main__":
    unittest.main()
