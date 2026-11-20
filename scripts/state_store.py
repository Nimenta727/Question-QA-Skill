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
        _write_bytes(backup_path(path), old)
    _write_bytes(target, payload)


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
    return {"current": primary, "last_good_backup": previous,
            "can_restore": previous["valid"],
            "caution": ("Backup contains the prior committed state, so restoring "
                        "may lose the most recent completed action. No files "
                        "are uploaded, and backups require the same privacy protection.")}


def recover(path):
    """Caller holds lock and explicitly confirmed rollback. Preserve backup."""
    previous = backup_path(path)
    if not previous.exists():
        raise ValueError("no state backup available")
    data = previous.read_bytes()
    _validate_raw(data)
    _write_bytes(path, data)
    return _validate_raw(data)
