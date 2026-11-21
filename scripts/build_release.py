#!/usr/bin/env python3
"""Create two deterministic, checksum-verified Question-QA-Skill distributions.

core: minimal Agent Skill instructions; no Python, tests, history or learner data.
full: backwards-compatible offline toolkit, current documentation, examples
and tests. Superseded prose is retrieved from immutable Git history/tags.
Neither package runs a model, proves question semantics, or guarantees lower
billable model tokens from smaller archive bytes.
"""
import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
PACKAGE_ROOT = "question-qa-skill-" + VERSION
CORE_PACKAGE_ROOT = "question-qa-skill-core-" + VERSION
TOP_LEVEL = ("SKILL.md", "README.md", "README.zh-CN.md",
             "LICENSE", "VERSION", "CHANGELOG.md")
FOLDERS = ("references", "scripts", "examples", "docs", "tests")
SUFFIXES = (".md", ".py", ".json", ".txt", ".yml", ".yaml", ".toml")
CORE_FILE_MAP = {
    "SKILL.md": "SKILL.md",
    "README.md": "docs/CORE_PACKAGE.md",
    "LICENSE": "LICENSE",
    "VERSION": "VERSION",
    "references/authoring.md": "references/authoring.md",
    "references/tutoring.md": "references/tutoring.md",
    "references/model_audit.md": "references/model_audit.md",
    "references/subjects.md": "references/subjects.md",
}
PRIVATE_EXAMPLE_MARKERS = (
    "private", "credential", "token", "secret", "audit-key",
    "checkpoint", "receipt", "registry", "independent-audit",
    "model-audit", "audit-packet", "course-extract", "source-extract",
    "course_source",
)
FULL_REQUIRED = {
    "SKILL.md", "LICENSE", "scripts/qa.py", "scripts/dashboard.py",
    "scripts/feedback.py", "scripts/math_equivalence.py",
    "scripts/state_store.py", "scripts/reviewer_study.py",
    "scripts/appeals.py", "scripts/reviewer_trial.py",
    "scripts/reviewer_pilot.py", "scripts/reviewer_credentials.py",
    "scripts/audit_ledger.py", "scripts/tutor_core.py",
    "scripts/model_audit.py", "scripts/skill_eval_report.py",
    "docs/SKILL_EVAL_REPORT.md", "docs/SKILL_EVAL_REPORT.zh-CN.md",
    "references/model_audit.md",
    "references/tutoring.md", "references/operations.md",
    "docs/MODEL_AUDIT.zh-CN.md", "docs/MODEL_AUDIT.md",
}


def sha256(payload):
    return hashlib.sha256(payload).hexdigest()


def selected_files(root=ROOT):
    """Existing complete, allowlisted distribution (kept backwards compatible)."""
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
            if (not file.is_file() or file.is_symlink()
                    or "__pycache__" in file.parts
                    or any(part.startswith(".")
                           for part in file.relative_to(root).parts)
                    or file.suffix not in SUFFIXES
                    or (folder == "examples"
                        and any(marker in file.name.lower()
                                for marker in PRIVATE_EXAMPLE_MARKERS))):
                continue
            paths.append(file)
    return sorted(paths, key=lambda path: path.relative_to(root).as_posix())


def core_files(root=ROOT):
    """Explicit core allowlist: no scripts, raw course materials or research files."""
    items = {}
    for destination, source in CORE_FILE_MAP.items():
        path = root / source
        if not path.is_file() or path.is_symlink():
            raise ValueError("required core file missing: " + source)
        items[destination] = path.read_bytes()
    return items


def archive_entry(archive, name, data):
    item = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
    item.create_system = 3
    item.external_attr = 0o100644 << 16
    item.compress_type = zipfile.ZIP_DEFLATED
    item.flag_bits = 0x800
    archive.writestr(item, data, compress_type=zipfile.ZIP_DEFLATED,
                     compresslevel=9)


def _root(profile):
    if profile == "core":
        return CORE_PACKAGE_ROOT
    if profile == "full":
        return PACKAGE_ROOT
    raise ValueError("unknown distribution profile")


def _payload(profile):
    if profile == "core":
        return core_files()
    if profile == "full":
        return {p.relative_to(ROOT).as_posix(): p.read_bytes()
                for p in selected_files()}
    raise ValueError("unknown distribution profile")


def build(output, profile="full"):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    root = _root(profile)
    destination = output / (root + ".zip")
    data = _payload(profile)
    manifest = {
        "package": "question-qa-skill-core" if profile == "core"
                   else "question-qa-skill",
        "profile": profile,
        "version": VERSION,
        "format": 1,
        "offline": True,
        "files_sha256": {name: sha256(data[name]) for name in sorted(data)},
    }
    data["manifest.json"] = (json.dumps(
        manifest, indent=2, ensure_ascii=False, sort_keys=True
    ) + "\n").encode("utf-8")
    with zipfile.ZipFile(destination, "w") as archive:
        for name in sorted(data):
            archive_entry(archive, root + "/" + name, data[name])
    verify(destination, profile)
    return destination


def verify(path, profile=None):
    with zipfile.ZipFile(path) as archive:
        entries = archive.namelist()
        if not entries or len(entries) != len(set(entries)):
            raise ValueError("empty or duplicate ZIP entries")
        names = {entry.split("/", 1)[0] for entry in entries}
        if len(names) != 1:
            raise ValueError("multiple archive roots")
        root = next(iter(names))
        detected = ("core" if root == CORE_PACKAGE_ROOT else
                    "full" if root == PACKAGE_ROOT else None)
        if detected is None or (profile is not None and profile != detected):
            raise ValueError("unexpected archive root or distribution profile")
        prefix = root + "/"
        for entry in entries:
            if (not entry.startswith(prefix) or entry.endswith("/")
                    or "\\" in entry or "\0" in entry
                    or any(part in ("", ".", "..")
                           for part in entry[len(prefix):].split("/"))):
                raise ValueError("unsafe package entry")
        contents = {name[len(prefix):]: archive.read(name)
                    for name in entries}
    if "manifest.json" not in contents:
        raise ValueError("missing checksum manifest")
    manifest = json.loads(contents["manifest.json"])
    if (manifest.get("version") != VERSION
            or manifest.get("profile") != detected
            or manifest.get("package") != (
                "question-qa-skill-core" if detected == "core"
                else "question-qa-skill")):
        raise ValueError("package or version mismatch")
    expected = manifest.get("files_sha256")
    if (not isinstance(expected, dict)
            or set(expected) != set(contents) - {"manifest.json"}):
        raise ValueError("manifest does not enumerate files exactly")
    for name, expected_sha in expected.items():
        if sha256(contents[name]) != expected_sha:
            raise ValueError("checksum mismatch: " + name)
    if detected == "core":
        if set(contents) != set(CORE_FILE_MAP) | {"manifest.json"}:
            raise ValueError("core archive is not strictly allowlisted")
        if len(contents["SKILL.md"].decode("utf-8")) > 3500:
            raise ValueError("core SKILL.md exceeded context budget")
    elif not FULL_REQUIRED.issubset(contents):
        raise ValueError("required full Skill modules missing")
    return {
        "valid": True, "version": VERSION, "profile": detected,
        "files": len(contents),
        "archive_sha256": sha256(Path(path).read_bytes()),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Build/verify lean core and full offline Skill ZIPs")
    parser.add_argument("--output", default="dist")
    parser.add_argument("--profile", choices=("core", "full"))
    parser.add_argument("--all", action="store_true",
                        help="build both immutable release ZIP profiles")
    parser.add_argument("--verify", help="inspect a previously generated ZIP")
    args = parser.parse_args(argv)
    try:
        if args.all and args.verify:
            raise ValueError("--all cannot be combined with --verify")
        if args.verify:
            result = verify(args.verify, args.profile)
        elif args.all:
            result = {"created": [
                {"path": str(build(args.output, profile)),
                 **verify(Path(args.output) / (_root(profile) + ".zip"), profile)}
                for profile in ("core", "full")
            ]}
        else:
            profile = args.profile or "full"
            path = build(args.output, profile)
            result = {"created": str(path), **verify(path, profile)}
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, OSError, UnicodeError, zipfile.BadZipFile, KeyError,
            json.JSONDecodeError) as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
