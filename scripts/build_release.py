#!/usr/bin/env python3
"""Build and verify a reproducible, allowlisted, offline Agent Skill ZIP.

ZIP never bundles local .qa-state files, private learner responses, external
research data, git metadata, cached bytecode or CI credentials.
"""
import argparse
import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
PACKAGE_ROOT = "question-qa-skill-" + VERSION
TOP_LEVEL = ("SKILL.md", "README.md", "README.zh-CN.md",
             "LICENSE", "VERSION", "CHANGELOG.md")
FOLDERS = ("references", "scripts", "examples", "docs", "tests")
SUFFIXES = (".md", ".py", ".json", ".txt", ".yml", ".yaml", ".toml")


def sha256(payload):
    return hashlib.sha256(payload).hexdigest()


def selected_files(root=ROOT):
    paths = []
    for name in TOP_LEVEL:
        file = root / name
        if not file.is_file() or file.is_symlink():
            raise ValueError("required distribution file missing: " + name)
        paths.append(file)
    for folder in FOLDERS:
        base = root / folder
        if not base.is_dir():
            raise ValueError("required directory missing: " + folder)
        for file in sorted(base.rglob("*")):
            if (not file.is_file() or file.is_symlink() or
                    "__pycache__" in file.parts or
                    any(part.startswith(".") for part in file.relative_to(root).parts)
                    or file.suffix not in SUFFIXES):
                continue
            paths.append(file)
    return sorted(paths, key=lambda path: path.relative_to(root).as_posix())


def archive_entry(archive, name, data):
    item = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
    item.create_system = 3
    item.external_attr = 0o644 << 16
    item.compress_type = zipfile.ZIP_DEFLATED
    item.flag_bits = 0x800  # filename encoded with UTF-8
    archive.writestr(item, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def build(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    destination = output / (PACKAGE_ROOT + ".zip")
    data = {path.relative_to(ROOT).as_posix(): path.read_bytes()
            for path in selected_files()}
    manifest = {
        "package": "question-qa-skill",
        "version": VERSION,
        "format": 1,
        "offline": True,
        "files_sha256": {name: sha256(data[name]) for name in sorted(data)},
    }
    data["manifest.json"] = (json.dumps(manifest, indent=2, ensure_ascii=False,
                                       sort_keys=True) + "\n").encode("utf-8")
    with zipfile.ZipFile(destination, "w") as archive:
        for name in sorted(data):
            archive_entry(archive, PACKAGE_ROOT + "/" + name, data[name])
    verify(destination)
    return destination


def verify(path):
    with zipfile.ZipFile(path) as archive:
        entries = archive.namelist()
        if len(entries) != len(set(entries)):
            raise ValueError("duplicate ZIP entries")
        rootname = PACKAGE_ROOT + "/"
        if not entries or any(not entry.startswith(rootname) or
                              "/../" in entry or entry.endswith("/")
                              for entry in entries):
            raise ValueError("unsafe package root or paths")
        contents = {name[len(rootname):]: archive.read(name) for name in entries}
    if "manifest.json" not in contents:
        raise ValueError("missing checksum manifest")
    manifest = json.loads(contents["manifest.json"])
    if manifest.get("version") != VERSION or manifest.get("package") != "question-qa-skill":
        raise ValueError("package version mismatch")
    expected = manifest.get("files_sha256")
    if not isinstance(expected, dict) or set(expected) != (set(contents)-{"manifest.json"}):
        raise ValueError("manifest does not enumerate package files exactly")
    for name, expected_sha in expected.items():
        if sha256(contents[name]) != expected_sha:
            raise ValueError("checksum mismatch: " + name)
    if not {"SKILL.md", "LICENSE", "scripts/qa.py", "scripts/dashboard.py",
            "scripts/feedback.py", "scripts/math_equivalence.py",
            "scripts/state_store.py", "scripts/reviewer_study.py",
            "scripts/appeals.py", "scripts/reviewer_trial.py",
            "scripts/reviewer_pilot.py", "scripts/reviewer_credentials.py",
            "scripts/audit_ledger.py"}.issubset(contents):
        raise ValueError("required Skill modules missing")
    return {"valid": True, "version": VERSION, "files": len(contents),
            "archive_sha256": sha256(Path(path).read_bytes())}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build/verify offline skill release package")
    parser.add_argument("--output", default="dist")
    parser.add_argument("--verify", help="existing ZIP to inspect instead of building")
    args = parser.parse_args(argv)
    try:
        if args.verify:
            result = verify(args.verify)
        else:
            path = build(args.output)
            result = {"created": str(path), **verify(path)}
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, OSError, zipfile.BadZipFile, KeyError, json.JSONDecodeError) as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
