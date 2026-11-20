"""Auditable, privacy-minimal score appeals on locally stored learner state.

Caller MUST hold state_store.locked_state through read/modification/save.
This is not independent authentication of a real reviewer.
"""
import math
import uuid
from datetime import datetime, timezone

OPEN_REASONS={"possible_key_error","equivalent_answer","rubric_dispute","scoring_error","other"}
RESOLVE_REASONS={"key_verified","equivalence_reviewed","rubric_rechecked","scoring_corrected","appeal_upheld"}


def now():
    return datetime.now(timezone.utc).isoformat()


def _event(state,event_id=None,index=None):
    history=state["history"]
    if (event_id is None)==(index is None):
        raise ValueError("provide exactly one of event-id or event-index")
    if index is not None:
        if type(index) is not int or not 0<=index<len(history):
            raise ValueError("event-index is out of range")
        event=history[index]
    else:
        matched=[e for e in history if e.get("event_id")==event_id]
        if len(matched)!=1:
            raise ValueError("event-id not found or ambiguous")
        event=matched[0]
    if "event_id" not in event:
        event["event_id"]=uuid.uuid4().hex
    return event


def open_appeal(state,reason,event_id=None,index=None):
    if reason not in OPEN_REASONS:
        raise ValueError("unknown appeal reason")
    event=_event(state,event_id,index)
    appeals=state.setdefault("appeals",[])
    if any(a["event_id"]==event["event_id"] and a["status"]=="open" for a in appeals):
        raise ValueError("open appeal already exists for this answer")
    appeal={"appeal_id":uuid.uuid4().hex,"event_id":event["event_id"],
            "item_id":event["id"],"opened_at":now(),"reason_code":reason,
            "status":"open","score_before":event["score"]}
    appeals.append(appeal)
    return dict(appeal)


def _score(value):
    if type(value) not in (int,float) or not math.isfinite(value) or not 0<=value<=1:
        raise ValueError("corrected score must be a finite number in [0,1]")
    return float(value)


def resolve_appeal(state,appeal_id,decision,reason,reviewer_confirmed=False,
                   new_score=None,criterion_scores=None):
    if not reviewer_confirmed:
        raise ValueError("independent reviewer confirmation is required (self-declared)")
    if reason not in RESOLVE_REASONS:
        raise ValueError("unknown resolution reason")
    if decision not in ("uphold","correct"):
        raise ValueError("decision must be uphold or correct")
    found=[a for a in state.get("appeals",[]) if a.get("appeal_id")==appeal_id]
    if len(found)!=1 or found[0]["status"]!="open":
        raise ValueError("appeal is missing or already resolved")
    appeal=found[0]
    event=next((e for e in state["history"] if e.get("event_id")==appeal["event_id"]),None)
    if event is None:
        raise ValueError("appealed answer missing: no change made")
    if appeal["item_id"]!=event["id"]:
        raise ValueError("appeal item and event mismatch")
    original=_score(event["score"])
    if decision=="uphold":
        if new_score is not None or criterion_scores is not None or reason!="appeal_upheld":
            raise ValueError("uphold requires appeal_upheld and no changed scores")
        target=original
    else:
        if reason=="appeal_upheld":
            raise ValueError("correction needs a concrete resolution reason")
        if criterion_scores is not None:
            old=event.get("criterion_scores")
            if (not isinstance(old,list) or not isinstance(criterion_scores,list)
                    or len(old)!=len(criterion_scores) or len(old)==0):
                raise ValueError("criterion scores must match existing rubric evidence")
            revised=[_score(x) for x in criterion_scores]
            if any(x not in (0,.5,1) for x in revised):
                raise ValueError("rubric scores must be 0, 0.5 or 1")
            target=sum(revised)/len(revised)
            if new_score is not None and abs(_score(new_score)-target)>1e-9:
                raise ValueError("corrected score disagrees with revised rubric")
        else:
            if "criterion_scores" in event:
                raise ValueError("rubric-reviewed answer requires corrected criterion-scores")
            if new_score is None:
                raise ValueError("new-score required for correction")
            target=_score(new_score)
            if event.get("type") != "manual" and target not in (0.,1.):
                raise ValueError("objective answer corrections must be 0 or 1")
        if abs(target-original)<1e-9:
            raise ValueError("corrected score must differ from prior score")
        event["score"]=target
        event["method"]="appeal_correction"
        if criterion_scores is not None:
            event["criterion_scores"]=revised
        if target==1:
            # A previously assigned misconception must not linger after
            # a validated score correction to full credit.
            event.pop("misconception",None)
    appeal.update({"status":"resolved","decision":decision,
                   "resolved_at":now(),"resolution_code":reason,
                   "score_after":target,
                   "reviewer_confirmation_self_declared":True})
    return dict(appeal)


def view(state):
    appeals=state.get("appeals",[])
    if not isinstance(appeals,list):
        raise ValueError("invalid appeal history")
    return {"appeals":[dict(x) for x in appeals],
            "open_count":sum(a.get("status")=="open" for a in appeals),
            "resolved_count":sum(a.get("status")=="resolved" for a in appeals),
            "caution":("Reviewer identity and adjudication expertise are not authenticated. "
                       "Only reason codes, score changes and timestamps are persisted; "
                       "no answer text or private comments.") }
