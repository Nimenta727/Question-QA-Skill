"""Core vs full distributions: deterministic builds and bounded prompt context."""
import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts import build_release as pkg

ROOT = Path(__file__).resolve().parents[1]


class CoreDistributionTests(unittest.TestCase):
    def test_core_is_only_instruction_files_and_has_no_optional_code(self):
        with tempfile.TemporaryDirectory() as temp:
            core = pkg.build(temp, "core")
            self.assertTrue(pkg.verify(core, "core")["valid"])
            with zipfile.ZipFile(core) as z:
                names = [p[len(pkg.CORE_PACKAGE_ROOT)+1:]
                         for p in z.namelist()]
            self.assertEqual(set(names), set(pkg.CORE_FILE_MAP) | {"manifest.json"})
            self.assertFalse(any(name.startswith(("scripts/", "tests/", "docs/",
                                                  "examples/"))
                                 for name in names))

    def test_core_is_reproducible_and_small(self):
        with tempfile.TemporaryDirectory() as x, tempfile.TemporaryDirectory() as y:
            first, second = pkg.build(x, "core"), pkg.build(y, "core")
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertLess(first.stat().st_size, 30000,
                            "core package should be compact; read only SKILL by default")
            with zipfile.ZipFile(first) as z:
                skill = z.read(pkg.CORE_PACKAGE_ROOT+"/SKILL.md")
                self.assertLess(len(skill.decode("utf-8")), 3501)
                self.assertIn(b"references/model_audit.md", skill)

    def test_core_manifest_detects_tamper_and_profile_confusion(self):
        with tempfile.TemporaryDirectory() as temp:
            core = pkg.build(temp, "core")
            with self.assertRaisesRegex(ValueError, "profile"):
                pkg.verify(core, "full")
            with zipfile.ZipFile(core) as z:
                contents = {name: z.read(name) for name in z.namelist()}
            contents[pkg.CORE_PACKAGE_ROOT+"/SKILL.md"] = b"altered"
            tampered = Path(temp)/"tampered.zip"
            with zipfile.ZipFile(tampered, "w") as z:
                for name, data in contents.items():
                    z.writestr(name, data)
            with self.assertRaisesRegex(ValueError, "checksum"):
                pkg.verify(tampered)

    def test_full_retains_advanced_tools_and_backward_compatibility(self):
        with tempfile.TemporaryDirectory() as temp:
            full = pkg.build(temp)
            report = pkg.verify(full)
            self.assertEqual("full", report["profile"])
            with zipfile.ZipFile(full) as z:
                names = z.namelist()
            self.assertTrue(any(x.endswith("/scripts/model_audit.py")
                                for x in names))
            self.assertTrue(any("/docs/routine/" in x for x in names))
            self.assertTrue(any("/tests/" in x for x in names))

    def test_manifest_paths_resolve_without_unsafe_extractions(self):
        with tempfile.TemporaryDirectory() as temp:
            core = pkg.build(temp, "core")
            with zipfile.ZipFile(core) as z:
                z.extractall(temp)
            root = Path(temp) / pkg.CORE_PACKAGE_ROOT
            for f in pkg.CORE_FILE_MAP:
                self.assertTrue((root/f).is_file(), f)
            guide = (root/"README.md").read_text(encoding="utf-8")
            self.assertIn("references/tutoring.md", guide)
            self.assertNotIn("docs/MODEL_AUDIT.md", guide)


if __name__ == "__main__":
    unittest.main()
