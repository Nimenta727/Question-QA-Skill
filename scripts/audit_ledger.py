"""HMAC-linked appeal audit records with optional independently retained receipt.

The HMAC key belongs in a separate protected secret file, never in learner
state, backups or the repository. This detects edits/reordering without the
key. Without an externally retained receipt it CANNOT detect replacement of
the whole state with an older valid snapshot, or an attacker holding the key.
"""
import hashlib
import hmac
import json
import re
import secrets
from copy import deepcopy
from pathlib import Path

try:
    from . import reviewer_credentials
except ImportError:
    import reviewer_credentials


def _canonical(data):
    return json.dumps(data,ensure_ascii=True,sort_keys=True,
                      separators=(",",":"),allow_nan=False).encode("ascii")


def key_from_file(filename):
    token=reviewer_credentials._read_token(filename)
    if not re.fullmatch(r"[a-f0-9]{64}",token):
        raise ValueError("audit key must be a 32-byte lowercase hex secret file")
    return bytes.fromhex(token)


def generate_key_file(filename):
    if Path(filename).is_symlink():
        raise ValueError("audit key path cannot be a symlink")
    key=secrets.token_bytes(32)
    reviewer_credentials._new_file(filename,(key.hex()+"\n").encode("ascii"))
    return key


def _key_id(key):
    return hashlib.sha256(b"question-qa-audit-key\0"+key).hexdigest()[:24]


def initialize(state,key,registry_id):
    if state.get("audit") is not None or state.get("appeals"):
        raise ValueError("cannot retroactively certify existing appeals; use a fresh state")
    if not isinstance(registry_id,str) or not registry_id.strip():
        raise ValueError("reviewer registry ID required")
    state["audit"]={"format":1,"key_id":_key_id(key),
                    "registry_id":registry_id,"entries":[]}
    return {"enabled":True,"key_id":_key_id(key),"registry_id":registry_id,
            "past_appeals_certified":False}


def _audit(state,key):
    obj=state.get("audit")
    if (not isinstance(obj,dict) or set(obj)!={"format","key_id","registry_id","entries"}
            or obj["format"]!=1 or not isinstance(obj["entries"],list)):
        raise ValueError("audit is not enabled or its metadata was altered")
    if obj["key_id"]!=_key_id(key):
        raise ValueError("wrong HMAC key for this learning state")
    return obj


def append(state,key,action,appeal):
    if action not in ("open","resolve"):
        raise ValueError("unsupported audit action")
    obj=_audit(state,key)
    entries=obj["entries"]
    event=next((e for e in state["history"]
                if e.get("event_id")==appeal["event_id"]),None)
    if event is None:
        raise ValueError("appeal event not found in learner history")
    data={"seq":len(entries)+1,"prev":entries[-1]["mac"] if entries else "0"*64,
          "action":action,"appeal":deepcopy(appeal),
          "effective_score":event["score"]}
    mac=hmac.new(key,b"question-qa-appeal/v1\0"+_canonical(data),
                 hashlib.sha256).hexdigest()
    entries.append({**data,"mac":mac})
    return {"audit_seq":data["seq"],"audit_head":mac}


def verify(state,key,receipt=None):
    obj=_audit(state,key)
    entries=obj["entries"]
    prev="0"*64
    seen={}
    effective={}
    for position,record in enumerate(entries,1):
        if not isinstance(record,dict) or set(record)!={
                "seq","prev","action","appeal","effective_score","mac"}:
            raise ValueError("audit record structure altered")
        if type(record["seq"]) is not int or record["seq"]!=position or record["prev"]!=prev:
            raise ValueError("audit chain order or link invalid")
        payload={k:v for k,v in record.items() if k!="mac"}
        actual=hmac.new(key,b"question-qa-appeal/v1\0"+_canonical(payload),
                        hashlib.sha256).hexdigest()
        if not isinstance(record["mac"],str) or not hmac.compare_digest(actual,record["mac"]):
            raise ValueError("appeal audit HMAC mismatch: possible tampering")
        appeal=record["appeal"]
        if not isinstance(appeal,dict) or not isinstance(appeal.get("appeal_id"),str):
            raise ValueError("invalid audit appeal snapshot")
        identifier=appeal["appeal_id"]
        if record["action"]=="open":
            if identifier in seen or appeal.get("status")!="open":
                raise ValueError("unexpected duplicate or closed appeal open")
        elif record["action"]=="resolve":
            if identifier not in seen or seen[identifier].get("status")!="open":
                raise ValueError("appeal resolution without corresponding open")
            if appeal.get("status")!="resolved":
                raise ValueError("inconsistent resolved appeal status")
        else:
            raise ValueError("unknown audit action")
        seen[identifier]=appeal
        effective[appeal["event_id"]]=record["effective_score"]
        prev=record["mac"]
    recorded=state.get("appeals",[])
    if not isinstance(recorded,list) or len(recorded)!=len(seen):
        raise ValueError("appeal audit and current appeal registry differ")
    current={a.get("appeal_id"):a for a in recorded if isinstance(a,dict)}
    if current!=seen:
        raise ValueError("appeal metadata changed outside authenticated audit")
    events={e.get("event_id"):e for e in state.get("history",[])
            if isinstance(e,dict) and e.get("event_id")}
    for event_id,value in effective.items():
        if event_id not in events or events[event_id].get("score")!=value:
            raise ValueError("grade changed without authenticated appeal record")
    if receipt is not None:
        check_receipt(state,key,receipt)
    return {"valid":True,"entries":len(entries),"head":prev,
            "key_id":obj["key_id"],"receipt_checked":receipt is not None,
            "warning":("HMAC checks detect edits without the separately kept key. "
                       "Truncation/rollback is only detectable when an older "
                       "receipt is retained OUTSIDE the state and compared.")}


def receipt_for(state,key):
    valid=verify(state,key)
    body={"format":1,"key_id":valid["key_id"],
          "entries":valid["entries"],"head":valid["head"]}
    signature=hmac.new(key,b"question-qa-checkpoint/v1\0"+_canonical(body),
                       hashlib.sha256).hexdigest()
    return {**body,"signature":signature}


def check_receipt(state,key,receipt):
    if not isinstance(receipt,dict) or set(receipt)!={
            "format","key_id","entries","head","signature"}:
        raise ValueError("invalid audit checkpoint receipt")
    body={k:v for k,v in receipt.items() if k!="signature"}
    expected=hmac.new(key,b"question-qa-checkpoint/v1\0"+_canonical(body),
                      hashlib.sha256).hexdigest()
    if not isinstance(receipt["signature"],str) or not hmac.compare_digest(
            expected,receipt["signature"]):
        raise ValueError("audit checkpoint receipt authentication failed")
    obj=_audit(state,key)
    head=obj["entries"][-1]["mac"] if obj["entries"] else "0"*64
    if (receipt["key_id"]!=obj["key_id"] or
            receipt["entries"]!=len(obj["entries"]) or receipt["head"]!=head):
        raise ValueError("audit does not match independently retained checkpoint")
    return True
