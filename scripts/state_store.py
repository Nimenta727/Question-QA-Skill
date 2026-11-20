"""Portable, process-safe local JSON state transactions and last-good backups.

Use advisory native OS file locks: flock on POSIX, msvcrt.locking on Windows.
Lock sidecar remains on disk: unlinking it could create two independent locks.
The caller MUST hold locked_state around every read-modify-write transaction.
Only intended for local filesystems, not distributed/NFS coordination.
"""
import contextlib
import hashlib
import json
import os
import tempfile
import time
import re
import uuid
from collections import defaultdict
from pathlib import Path

try:
    import fcntl
except ImportError:
    fcntl = None
try:
    import msvcrt
except ImportError:
    msvcrt = None


def _validate_raw(payload):
    data = json.loads(payload.decode("utf-8"))
    if (not isinstance(data, dict) or data.get("version") != 1
            or not isinstance(data.get("history"), list)
            or ("pending" in data and data["pending"] is not None
                and not isinstance(data["pending"], dict))):
        raise ValueError("invalid or unsupported local state")
    return data


@contextlib.contextmanager
def locked_state(path, timeout=8.0):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    lockpath = Path(str(target) + ".lock")
    with lockpath.open("a+b") as handle:
        if os.name != "nt":
            os.chmod(lockpath, 0o600)
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        acquired = False
        deadline = time.monotonic() + timeout
        while not acquired:
            try:
                handle.seek(0)
                if os.name == "nt":
                    if msvcrt is None:
                        raise ValueError("Windows file locking unavailable")
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
            except (BlockingIOError, OSError) as exc:
                if os.name == "nt":
                    if getattr(exc, "winerror", None) not in (33, 36) and getattr(exc, "errno", None) not in (13, 11):
                        raise
                elif not isinstance(exc, BlockingIOError) and getattr(exc,"errno",None) not in (11, 35):
                    raise
                if time.monotonic() >= deadline:
                    raise TimeoutError("state busy: another process owns the lock; retry later")
                time.sleep(0.05)
        try:
            yield
        finally:
            if acquired:
                handle.seek(0)
                if os.name == "nt":
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _write_bytes(path, payload):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".qa-transaction-", suffix=".tmp",
                                dir=str(target.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, target)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def backup_path(path):
    return Path(str(path) + ".bak")


MAX_SNAPSHOTS = 5
SNAPSHOT_PATTERN = re.compile(r"^\d{20}-[a-f0-9]{8}\.json$")


def snapshots_path(path):
    return Path(str(path) + ".snapshots")


def _safe_snapshots(path):
    folder = snapshots_path(path)
    if not folder.exists():
        return []
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError("unsafe snapshot directory")
    return sorted(p for p in folder.iterdir()
                  if SNAPSHOT_PATTERN.fullmatch(p.name) and p.is_file()
                  and not p.is_symlink())


def _snapshot(path, raw):
    _validate_raw(raw)
    folder = snapshots_path(path)
    if folder.is_symlink():
        raise ValueError("snapshot path must not be a symlink")
    folder.mkdir(mode=0o700, exist_ok=True)
    ident = "%020d-%s" % (time.time_ns(), uuid.uuid4().hex[:8])
    target = folder / (ident + ".json")
    _write_bytes(target, raw)
    return ident


def _prune(path, limit=MAX_SNAPSHOTS):
    existing = _safe_snapshots(path)
    for item in existing[:-limit]:
        item.unlink()


def list_snapshots(path):
    summaries = []
    for item in _safe_snapshots(path):
        try:
            raw = item.read_bytes()
            state = _validate_raw(raw)
            summaries.append({"snapshot_id": item.stem, "valid": True,
                              "answers": len(state["history"]),
                              "sha256": hashlib.sha256(raw).hexdigest()})
        except (OSError, ValueError, UnicodeError, TypeError):
            summaries.append({"snapshot_id": item.stem, "valid": False})
    return summaries




def save(path, state):
    """Caller must hold locked_state; validate before writing anything."""
    payload = (json.dumps(state, ensure_ascii=False, indent=2, allow_nan=False)
               + "\n").encode("utf-8")
    _validate_raw(payload)
    target = Path(path)
    if target.exists():
        old = target.read_bytes()
        _validate_raw(old)
        # Backup is exactly the prior committed state. No unvalidated file
        # can replace last-good backup through save().
        _snapshot(path, old)
        _write_bytes(backup_path(path), old)
    _write_bytes(target, payload)
    _prune(path)


def inspect(path):
    target = Path(path)
    backup = backup_path(path)
    def check(item):
        if not item.exists():
            return {"exists": False, "valid": False}
        try:
            raw = item.read_bytes()
            state = _validate_raw(raw)
            return {"exists": True, "valid": True, "answers": len(state["history"]),
                    "pending": bool(state.get("pending")),
                    "sha256": hashlib.sha256(raw).hexdigest()}
        except (UnicodeError, OSError, ValueError, TypeError):
            return {"exists": True, "valid": False}
    primary = check(target)
    previous = check(backup)
    snapshots = list_snapshots(path)
    return {"current": primary, "last_good_backup": previous,
            "snapshots": snapshots,
            "can_restore": previous["valid"] or any(x["valid"] for x in snapshots),
            "caution": ("Backup contains the prior committed state, so restoring "
                        "may lose the most recent completed action. No files "
                        "are uploaded, and backups require the same privacy protection.")}


def recover(path, snapshot_id=None):
    """Explicit, locked rollback. Invalid source state is never restored."""
    if snapshot_id is None:
        source = backup_path(path)
    else:
        valid = {x["snapshot_id"]: x for x in list_snapshots(path)}
        if snapshot_id not in valid or not valid[snapshot_id]["valid"]:
            raise ValueError("snapshot not found or invalid")
        source = snapshots_path(path) / (snapshot_id + ".json")
    if not source.exists():
        raise ValueError("requested recovery snapshot not found")
    raw = source.read_bytes()
    restored = _validate_raw(raw)
    current = Path(path)
    if current.exists():
        old = current.read_bytes()
        try:
            _validate_raw(old)
        except (ValueError, UnicodeError, TypeError):
            pass
        else:
            _snapshot(path, old)
    # Recover without modifying last-good .bak, which may be our source.
    _write_bytes(current, raw)
    _prune(path)
    return restored


def export(path, destination, include_private=False):
    """Never overwrite; caller locks and confirms private export separately."""
    target = Path(path)
    output = Path(destination)
    forbidden = {target.resolve(), backup_path(path).resolve(),
                 Path(str(path)+".lock").resolve()}
    if output.resolve() in forbidden or output.resolve().is_relative_to(
            snapshots_path(path).resolve()):
        raise ValueError("export cannot overwrite state or its recovery files")
    state = _validate_raw(target.read_bytes())
    if include_private:
        data = {"type":"private_full_state", "state":state,
                "warning":"Private learner data: guard file access and delete copies deliberately."}
    else:
        grouped = defaultdict(list)
        for event in state["history"]:
            if type(event.get("score")) in (int,float) and isinstance(event.get("concept"),str):
                grouped[event["concept"]].append(event["score"])
        appeals = state.get("appeals",[])
        data = {"type":"aggregate_only", "total_answers":len(state["history"]),
                "concepts":[{"concept":key, "count":len(scores),
                             "mean_observed_score":round(sum(scores)/len(scores),4)}
                            for key,scores in sorted(grouped.items())],
                "appeal_counts":{"open":sum(a.get("status")=="open" for a in appeals),
                                 "resolved":sum(a.get("status")=="resolved" for a in appeals)},
                "caution":"Even aggregate course data can be sensitive in small groups."}
    payload = (json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+"\n").encode("utf-8")
    output.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(str(output),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        with os.fdopen(fd,"wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        output.unlink(missing_ok=True)
        raise
    return {"exported":True,"private":include_private,"bytes":len(payload),
            "destination":str(output)}


def delete_local(path):
    """Irreversibly unlink only managed local files; caller holds lock."""
    target = Path(path)
    children = [target,backup_path(path)] + _safe_snapshots(path)
    removed = 0
    for item in children:
        if item.exists() or item.is_symlink():
            item.unlink()
            removed += 1
    folder = snapshots_path(path)
    if folder.exists() and not any(folder.iterdir()):
        folder.rmdir()
    return {"deleted_managed_files":removed,
            "remaining_lock_file":True,
            "caution":"OS/cloud backups, log copies and filesystem remnants are not securely erased."}
