"""Deterministic release packaging, integrity and privacy checks."""
import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from scripts.build_release import build, verify, selected_files, PACKAGE_ROOT, ROOT


class PackageTests(unittest.TestCase):
    def test_only_allowlisted_files_are_packed(self):
        paths={p.relative_to(ROOT).as_posix() for p in selected_files()}
        self.assertIn("SKILL.md", paths)
        self.assertIn("scripts/dashboard.py", paths)
        self.assertIn("scripts/feedback.py", paths)
        self.assertFalse(any(p.endswith(".pyc") or ".qa-state" in p or
                             p.startswith(".github/") for p in paths))

    def test_reproducible_zip_and_manifest(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            a,b=build(first),build(second)
            bytes_a,bytes_b=a.read_bytes(),b.read_bytes()
            self.assertEqual(hashlib.sha256(bytes_a).hexdigest(),
                             hashlib.sha256(bytes_b).hexdigest())
            verified=verify(a)
            self.assertTrue(verified["valid"])
            with zipfile.ZipFile(a) as archive:
                names=archive.namelist()
                self.assertTrue(all(x.startswith(PACKAGE_ROOT+"/") for x in names))
                self.assertIn(PACKAGE_ROOT+"/manifest.json",names)

    def test_manifest_detects_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            base=build(directory)
            with zipfile.ZipFile(base) as arc:
                contents={i.filename:arc.read(i.filename) for i in arc.infolist()}
            contents[PACKAGE_ROOT+"/SKILL.md"]=b"modified without updating digest"
            evil=Path(directory)/"tampered.zip"
            with zipfile.ZipFile(evil,"w") as arc:
                for name,content in contents.items():
                    arc.writestr(name,content)
            with self.assertRaisesRegex(ValueError,"checksum"):
                verify(evil)

    def test_private_session_file_not_shipped(self):
        with tempfile.TemporaryDirectory() as directory:
            path=build(directory)
            with zipfile.ZipFile(path) as zipf:
                self.assertFalse(any(".qa-state" in name or "research-data/"
                                     in name or "learner-answers" in name
                                     for name in zipf.namelist()))


if __name__ == "__main__":
    unittest.main()
