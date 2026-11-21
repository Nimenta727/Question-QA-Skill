"""Test current bilingual documentation links and Git-only retirement policy."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTIVE_PAGES = (
    "README.md", "README.zh-CN.md", "CHANGELOG.md",
    "docs/INDEX.md", "docs/INDEX.zh-CN.md",
    "docs/INSTALL.md", "docs/INSTALL.zh-CN.md",
    "docs/RELEASE.md", "docs/RELEASE.zh-CN.md",
    "docs/ARCHITECTURE.md", "docs/ROADMAP.md", "docs/DIAGNOSIS.md",
    "docs/MODEL_AUDIT.md", "docs/MODEL_AUDIT.zh-CN.md",
    "docs/QUALITY_VALIDATION.md", "docs/QUALITY_VALIDATION.zh-CN.md",
    "docs/REAL_MODEL_TESTS.md", "docs/REAL_MODEL_TESTS.zh-CN.md",
    "docs/TEST_STATUS.md", "docs/TEST_STATUS.zh-CN.md",
    "docs/RELEASE_NOTES_v1.2.1.md", "docs/validation/REPORT_TEMPLATE.md",
)
LINKS = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
OBSOLETE_NOTES = (
    "docs/RELEASE_NOTES_v0.4.0.md",
    "docs/RELEASE_NOTES_v0.5.0.md",
    "docs/RELEASE_NOTES_v0.6.0.md",
    "docs/RELEASE_NOTES_v0.7.0.md",
    "docs/RELEASE_NOTES_v0.8.0.md",
    "docs/RELEASE_NOTES_v0.9.0.md",
    "docs/RELEASE_NOTES_v1.0.0.md",
    "docs/RELEASE_NOTES_v1.1.0.md",
)


class DocumentationNavigationTests(unittest.TestCase):
    def test_all_current_local_markdown_links_resolve(self):
        missing = []
        for name in ACTIVE_PAGES:
            base = ROOT / name
            self.assertTrue(base.is_file(), name)
            for url in LINKS.findall(base.read_text(encoding="utf-8")):
                target = url.split("#", 1)[0].strip()
                if not target or "://" in target or target.startswith("mailto:"):
                    continue
                if not (base.parent / target).exists():
                    missing.append(f"{name} -> {target}")
        self.assertEqual([], missing)

    def test_core_and_full_are_explicit(self):
        for name in ("README.md", "README.zh-CN.md",
                     "docs/INSTALL.md", "docs/INSTALL.zh-CN.md"):
            content = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn("question-qa-skill-core-1.2.1.zip", content)
            self.assertIn("question-qa-skill-1.2.1.zip", content)

    def test_superseded_guides_are_only_in_git_history(self):
        self.assertFalse((ROOT / "docs/archive").exists())
        for old in OBSOLETE_NOTES:
            self.assertFalse((ROOT / old).exists(), old)
        self.assertTrue((ROOT / "docs/RELEASE_NOTES_v1.2.1.md").exists())
        self.assertTrue((ROOT / "docs/routine").is_dir())

    def test_verified_limits_are_explained_in_both_languages(self):
        for name, marker in (
            ("README.md", "does not call an LLM"),
            ("README.zh-CN.md", "不会自行调用大模型"),
        ):
            content = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn("model_audit.py", content)
            self.assertIn(marker, content)
        for name in ("docs/QUALITY_VALIDATION.md",
                     "docs/QUALITY_VALIDATION.zh-CN.md"):
            text = (ROOT / name).read_text(encoding="utf-8").lower()
            self.assertIn("protocol only" if name.endswith("VALIDATION.md")
                          else "尚未", text)


if __name__ == "__main__":
    unittest.main()
