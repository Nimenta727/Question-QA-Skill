#!/usr/bin/env python3
"""Local credential-based reviewer capabilities (not verified human identity).

Reviewer and admin secrets are random high-entropy tokens, stored only in
user-controlled local files; registry contains salted PBKDF2 verifiers.
Neither token possession nor a self-supplied reviewer ID proves qualification,
real-world identity, independence, or consent.
"""
import argparse
import hashlib
import hmac
import json
import os
import re
import secrets
import sys
import uuid
from pathlib import Path

try:
    from . import state_store
except ImportError:
    import state_store

REVIEWER_ID = re.compile(r"^[A-Za-z0-9_.-]{3,64}$")
ROUNDS = 120000


def _read_token(filename):
    source = Path(filename)
    if source.is_symlink() or not source.is_file():
        raise ValueError("credential must be a regular, non-symlink local file")
    if os.name != "nt" and source.stat().st_mode & 0o077:
        raise ValueError("credential file must not be group/world readable")
    token = source.read_text(encoding="ascii").strip()
    if not 32 <= len(token) <= 128:
        raise ValueError("invalid high-entropy reviewer credential length")
    return token


def _verifier(token):
    salt = secrets.token_bytes(16)
    return {"salt": salt.hex(), "derived": hashlib.pbkdf2_hmac(
        "sha256", token.encode("ascii"), salt, ROUNDS).hex()}


def _check(stored, token):
    if not isinstance(stored, dict) or set(stored) != {"salt","derived"}:
        raise ValueError("invalid credential verifier")
    try:
        digest = hashlib.pbkdf2_hmac("sha256", token.encode("ascii"),
                                    bytes.fromhex(stored["salt"]), ROUNDS)
        expected = bytes.fromhex(stored["derived"])
    except (ValueError, TypeError):
        raise ValueError("invalid stored credential format")
    return hmac.compare_digest(digest, expected)


def _new_file(filename, content):
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        with os.fdopen(fd, "wb") as out:
            out.write(content)
            out.flush()
            os.fsync(out.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def read_registry(path):
    source=Path(path)
    if source.is_symlink():
        raise ValueError("registry cannot be a symlink")
    data=json.loads(source.read_text(encoding="utf-8"))
    if (not isinstance(data,dict) or data.get("version")!=1
            or not isinstance(data.get("registry_id"),str)
            or not isinstance(data.get("admin"),dict)
            or not isinstance(data.get("reviewers"),dict)):
        raise ValueError("invalid local reviewer registry")
    return data


def initialize(registry, admin_token_output):
    if Path(registry).resolve()==Path(admin_token_output).resolve():
        raise ValueError("registry and admin token paths must differ")
    if Path(registry).exists() or Path(admin_token_output).exists():
        raise FileExistsError("registry or admin secret already exists")
    token=secrets.token_urlsafe(32)
    data={"version":1,"registry_id":uuid.uuid4().hex,
          "admin":_verifier(token),"reviewers":{}}
    _new_file(admin_token_output,(token+"\n").encode("ascii"))
    try:
        _new_file(registry,(json.dumps(data,sort_keys=True,indent=2)+"\n").encode("utf-8"))
    except BaseException:
        Path(admin_token_output).unlink(missing_ok=True)
        raise
    return {"registry_id":data["registry_id"],"created":True,
            "secret_output":str(admin_token_output),
            "identity_verified":False}


def _require_admin(data, admin_token_file):
    if not _check(data["admin"],_read_token(admin_token_file)):
        raise ValueError("admin credential authentication failed")


def enroll(registry, admin_token_file, reviewer_id, token_output):
    if not REVIEWER_ID.fullmatch(reviewer_id):
        raise ValueError("reviewer ID must be 3..64 safe ASCII characters")
    if Path(token_output).resolve()==Path(registry).resolve():
        raise ValueError("token cannot replace registry")
    with state_store.locked_state(registry):
        data=read_registry(registry)
        _require_admin(data,admin_token_file)
        if reviewer_id in data["reviewers"]:
            raise ValueError("reviewer already enrolled or revoked; do not recycle ID")
        if Path(token_output).exists():
            raise FileExistsError("credential output already exists")
        token=secrets.token_urlsafe(32)
        entry={"role":"reviewer","status":"active","verifier":_verifier(token)}
        _new_file(token_output,(token+"\n").encode("ascii"))
        try:
            data["reviewers"][reviewer_id]=entry
            state_store._write_bytes(registry,(json.dumps(data,sort_keys=True,indent=2)+"\n").encode())
        except BaseException:
            Path(token_output).unlink(missing_ok=True)
            raise
    return {"reviewer_id":reviewer_id,"enrolled":True,"identity_verified":False}


def revoke(registry, admin_token_file, reviewer_id):
    with state_store.locked_state(registry):
        data=read_registry(registry)
        _require_admin(data,admin_token_file)
        entry=data["reviewers"].get(reviewer_id)
        if not entry or entry.get("status")!="active":
            raise ValueError("reviewer missing or already revoked")
        entry["status"]="revoked"
        state_store._write_bytes(registry,(json.dumps(data,sort_keys=True,indent=2)+"\n").encode())
    return {"reviewer_id":reviewer_id,"revoked":True}


def authenticate(registry, reviewer_id, reviewer_token_file, registry_id=None):
    data=read_registry(registry)
    if registry_id is not None and data["registry_id"]!=registry_id:
        raise ValueError("reviewer registry does not match protected state")
    entry=data["reviewers"].get(reviewer_id)
    if not entry or entry.get("status")!="active" or entry.get("role")!="reviewer":
        raise ValueError("reviewer is not active and authorized")
    if not _check(entry.get("verifier"),_read_token(reviewer_token_file)):
        raise ValueError("reviewer credential authentication failed")
    return {"reviewer_id":reviewer_id,"registry_id":data["registry_id"],
            "credential_verified":True,"real_identity_verified":False}


def main(argv=None):
    p=argparse.ArgumentParser(description="Local scoped reviewer credentials")
    subs=p.add_subparsers(dest="action",required=True)
    a=subs.add_parser("init")
    a.add_argument("--registry",required=True)
    a.add_argument("--admin-token-output",required=True)
    a=subs.add_parser("enroll")
    a.add_argument("--registry",required=True)
    a.add_argument("--admin-token-file",required=True)
    a.add_argument("--reviewer-id",required=True)
    a.add_argument("--token-output",required=True)
    a=subs.add_parser("revoke")
    a.add_argument("--registry",required=True)
    a.add_argument("--admin-token-file",required=True)
    a.add_argument("--reviewer-id",required=True)
    a=subs.add_parser("check")
    a.add_argument("--registry",required=True)
    a.add_argument("--reviewer-id",required=True)
    a.add_argument("--token-file",required=True)
    args=p.parse_args(argv)
    try:
        if args.action=="init":
            result=initialize(args.registry,args.admin_token_output)
        elif args.action=="enroll":
            result=enroll(args.registry,args.admin_token_file,args.reviewer_id,args.token_output)
        elif args.action=="revoke":
            result=revoke(args.registry,args.admin_token_file,args.reviewer_id)
        else:
            result=authenticate(args.registry,args.reviewer_id,args.token_file)
        print(json.dumps(result,ensure_ascii=True))
        return 0
    except (ValueError,OSError,TypeError,json.JSONDecodeError) as exc:
        print("error: "+str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    sys.exit(main())
