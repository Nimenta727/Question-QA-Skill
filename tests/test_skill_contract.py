"""Skill's default learner experience and package contract."""
import unittest
from pathlib import Path

from scripts import build_release

ROOT=Path(__file__).resolve().parents[1]


class SkillContractTests(unittest.TestCase):
    def test_primary_skill_is_short_and_tutoring_first(self):
        text=(ROOT/"SKILL.md").read_text(encoding="utf-8")
        self.assertLess(len(text),7000,"The core Skill has grown into a platform manual")
        for expected in ("QUICK","DEEP","一次只问一个问题",
                         "references/tutoring.md","references/authoring.md",
                         "references/operations.md","tutor_next_move"):
            self.assertIn(expected,text)
        self.assertLess(text.index("## 2. QUICK"),text.index("references/operations.md"))

    def test_optional_advanced_tools_remain_available(self):
        for required in ("scripts/qa.py","scripts/tutor_core.py",
                         "scripts/assessment_engine.py",
                         "scripts/reviewer_credentials.py",
                         "scripts/audit_ledger.py",
                         "docs/TEACHING_EVALUATION.zh-CN.md",
                         "references/tutoring.md","references/operations.md"):
            self.assertTrue((ROOT/required).exists(),required)

    def test_release_selects_pedagogical_core_and_no_private_state(self):
        included={p.relative_to(ROOT).as_posix()
                  for p in build_release.selected_files()}
        for path in ("SKILL.md","scripts/tutor_core.py",
                     "references/tutoring.md","references/authoring.md",
                     "docs/TEACHING_EVALUATION.zh-CN.md"):
            self.assertIn(path,included)
        self.assertFalse(any(".qa-state" in p or p.endswith(".audit-policy")
                             or p.endswith(".token") for p in included))


if __name__=="__main__":
    unittest.main()
