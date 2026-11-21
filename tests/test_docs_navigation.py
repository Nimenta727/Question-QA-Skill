"""Check high-value user-facing documentation and release links."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAVIGATION = (
    "README.md", "README.zh-CN.md",
    "docs/INDEX.md", "docs/INDEX.zh-CN.md",
    "docs/INSTALL.md", "docs/INSTALL.zh-CN.md",
    "docs/RELEASE.md",
)
LINKS = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


class DocumentationNavigationTests(unittest.TestCase):
    def test_local_markdown_targets_exist(self):
        missing = []
        for name in NAVIGATION:
            base = ROOT / name
            for url in LINKS.findall(base.read_text(encoding="utf-8")):
                target = url.split("#", 1)[0].strip()
                if not target or "://" in target or target.startswith("mailto:"):
                    continue
                # Only static local documentation paths are part of this test.
                if not (base.parent / target).exists():
                    missing.append("%s -> %s" % (name, target))
        self.assertEqual([], missing)

    def test_core_and_full_are_unambiguously_described(self):
        for name in ("README.md", "README.zh-CN.md",
                     "docs/INSTALL.md", "docs/INSTALL.zh-CN.md"):
            content = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn("question-qa-skill-core-1.2.0.zip", content)
            self.assertIn("question-qa-skill-1.2.0.zip", content)
        self.assertTrue((ROOT / "docs/archive/RELEASE_PRE_V1_2.md").exists())

    def test_no_unsupported_automatic_independent_audit_claim(self):
        for name in ("README.md", "README.zh-CN.md"):
            content = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn("model_audit.py", content)
            # Only an actual separate reviewer run can be called independent.
            self.assertTrue(("不" in content and "独立" in content)
                            or "not independent review" in content
                            or "not independent" in content)


if __name__ == "__main__":
    unittest.main()
