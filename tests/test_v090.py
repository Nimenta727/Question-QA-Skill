"""v0.9 credential-gated corrections and HMAC-linked appeal audit."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import audit_ledger, reviewer_credentials, state_store

ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/"scripts"/"qa.py"
CREDENTIALS=ROOT/"scripts"/"reviewer_credentials.py"
BANK=ROOT/"examples"/"sample_bank.json"


def run(script,*args):
    return subprocess.run([sys.executable,str(script),*map(str,args)],
                          cwd=str(ROOT),capture_output=True,text=True)


class LocalReviewerCredentials(unittest.TestCase):
    def test_issue_authenticate_revoke_and_prohibit_token_reuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry=Path(tmp)/"reviewers.json"
            admin=Path(tmp)/"admin.token"
            teacher=Path(tmp)/"teacher.token"
            created=reviewer_credentials.initialize(registry,admin)
            self.assertFalse(created["identity_verified"])
            self.assertNotIn(admin.read_text().strip(),registry.read_text())
            enrolled=reviewer_credentials.enroll(registry,admin,"teacher-A",teacher)
            self.assertTrue(enrolled["enrolled"])
            self.assertTrue(reviewer_credentials.authenticate(registry,"teacher-A",teacher)
                            ["credential_verified"])
            self.assertNotIn(teacher.read_text().strip(),registry.read_text())
            with self.assertRaisesRegex(ValueError,"already enrolled"):
                reviewer_credentials.enroll(registry,admin,"teacher-A",Path(tmp)/"dup.token")
            wrong=Path(tmp)/"other.token"
            reviewer_credentials._new_file(wrong,(("x"*48)+"\n").encode())
            with self.assertRaisesRegex(ValueError,"authentication failed"):
                reviewer_credentials.authenticate(registry,"teacher-A",wrong)
            reviewer_credentials.revoke(registry,admin,"teacher-A")
            with self.assertRaisesRegex(ValueError,"not active"):
                reviewer_credentials.authenticate(registry,"teacher-A",teacher)
            with self.assertRaisesRegex(ValueError,"recycled|already enrolled"):
                reviewer_credentials.enroll(registry,admin,"teacher-A",Path(tmp)/"again.token")

    def test_admin_is_required_for_enrolment_and_registry_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            a=Path(tmp)/"a.json"
            admin=Path(tmp)/"admin.token"
            token=Path(tmp)/"teacher.token"
            reviewer_credentials.initialize(a,admin)
            bad=Path(tmp)/"bad.token"
            reviewer_credentials._new_file(bad,("z"*48+"\n").encode())
            with self.assertRaisesRegex(ValueError,"admin credential"):
                reviewer_credentials.enroll(a,bad,"teacher-A",token)
            reviewer_credentials.enroll(a,admin,"teacher-A",token)
            with self.assertRaisesRegex(ValueError,"registry does not match"):
                reviewer_credentials.authenticate(a,"teacher-A",token,"wrong-id")

    @unittest.skipIf(os.name=="nt","Windows ACL permissions require OS tooling")
    def test_private_token_permissions_are_enforced_on_posix(self):
        with tempfile.TemporaryDirectory() as tmp:
            a=Path(tmp)/"registry.json"
            admin=Path(tmp)/"admin.token"
            token=Path(tmp)/"teacher.token"
            reviewer_credentials.initialize(a,admin)
            reviewer_credentials.enroll(a,admin,"teacher-A",token)
            token.chmod(0o644)
            with self.assertRaisesRegex(ValueError,"readable"):
                reviewer_credentials.authenticate(a,"teacher-A",token)
            token.chmod(0o600)
            self.assertTrue(reviewer_credentials.authenticate(a,"teacher-A",token)
                            ["credential_verified"])


class SignedAppealAudit(unittest.TestCase):
    def prepare(self,tmp):
        state=Path(tmp)/"state.json"
        registry=Path(tmp)/"reviewers.json"
        admin=Path(tmp)/"admin.token"
        teacher=Path(tmp)/"teacher.token"
        key=Path(tmp)/"audit-key.hex"
        self.assertEqual(0,run(QA,"next",BANK,"--state",state).returncode)
        answer=run(QA,"answer",BANK,"--state",state,"--response","D")
        self.assertEqual(0,answer.returncode,answer.stderr)
        event_id=json.loads(answer.stdout)["event_id"]
        reviewer_credentials.initialize(registry,admin)
        reviewer_credentials.enroll(registry,admin,"teacher-A",teacher)
        started=run(QA,"audit-init","--state",state,"--registry",registry,
                    "--admin-token-file",admin,"--audit-key-output",key)
        self.assertEqual(0,started.returncode,started.stderr)
        self.assertTrue(state.exists())
        self.assertNotIn(teacher.read_text().strip(),state.read_text())
        self.assertNotIn(key.read_text().strip(),state.read_text())
        return state,registry,admin,teacher,key,event_id

    def open(self,state,key,event_id):
        opened=run(QA,"appeal-open","--state",state,"--event-id",event_id,
                   "--reason","possible_key_error","--audit-key-file",key)
        self.assertEqual(0,opened.returncode,opened.stderr)
        return json.loads(opened.stdout)["appeal_id"]

    def resolve(self,state,registry,teacher,key,appeal_id):
        return run(QA,"appeal-resolve","--state",state,"--appeal-id",appeal_id,
                   "--decision","correct","--reason","key_verified","--new-score","1",
                   "--audit-key-file",key,"--registry",registry,
                   "--reviewer-id","teacher-A","--reviewer-token-file",teacher)

    def test_secure_flow_requires_credentials_and_seals_corrected_grade(self):
        with tempfile.TemporaryDirectory() as tmp:
            state,registry,admin,teacher,key,event_id=self.prepare(tmp)
            without_key=run(QA,"appeal-open","--state",state,"--event-id",event_id,
                            "--reason","possible_key_error")
            self.assertEqual(2,without_key.returncode)
            appeal_id=self.open(state,key,event_id)
            no_auth=run(QA,"appeal-resolve","--state",state,"--appeal-id",appeal_id,
                        "--decision","correct","--reason","key_verified","--new-score","1",
                        "--reviewer-confirmed","--audit-key-file",key)
            self.assertEqual(2,no_auth.returncode)
            self.assertEqual(0,json.loads(state.read_text())["history"][0]["score"])
            done=self.resolve(state,registry,teacher,key,appeal_id)
            self.assertEqual(0,done.returncode,done.stderr)
            result=json.loads(done.stdout)
            self.assertEqual("local_credential",result["reviewer_auth_mode"])
            self.assertEqual("teacher-A",result["credential_reviewer_id"])
            self.assertEqual(2,result["audit_seq"])
            checked=run(QA,"audit-verify","--state",state,"--audit-key-file",key)
            self.assertEqual(0,checked.returncode,checked.stderr)
            self.assertEqual(2,json.loads(checked.stdout)["entries"])
            self.assertTrue(json.loads(checked.stdout)["valid"])
            self.assertNotIn(teacher.read_text().strip(),state.read_text())
            self.assertNotIn(key.read_text().strip(),state.read_text())

    def test_revoked_token_and_wrong_registry_cannot_resolve(self):
        with tempfile.TemporaryDirectory() as tmp:
            state,registry,admin,teacher,key,event_id=self.prepare(tmp)
            appeal_id=self.open(state,key,event_id)
            other_registry=Path(tmp)/"other.json"
            other_admin=Path(tmp)/"other-admin.token"
            other_teacher=Path(tmp)/"other-teacher.token"
            reviewer_credentials.initialize(other_registry,other_admin)
            reviewer_credentials.enroll(other_registry,other_admin,"teacher-A",other_teacher)
            wrong=self.resolve(state,other_registry,other_teacher,key,appeal_id)
            self.assertEqual(2,wrong.returncode)
            reviewer_credentials.revoke(registry,admin,"teacher-A")
            revoked=self.resolve(state,registry,teacher,key,appeal_id)
            self.assertEqual(2,revoked.returncode)
            self.assertEqual("open",json.loads(state.read_text())["appeals"][0]["status"])

    def test_tampered_appeal_and_score_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            state,registry,admin,teacher,key,event_id=self.prepare(tmp)
            aid=self.open(state,key,event_id)
            self.assertEqual(0,self.resolve(state,registry,teacher,key,aid).returncode)
            original=json.loads(state.read_text())
            corrupted=json.loads(state.read_text())
            corrupted["history"][0]["score"]=0
            state.write_text(json.dumps(corrupted))
            invalid=run(QA,"audit-verify","--state",state,"--audit-key-file",key)
            self.assertEqual(2,invalid.returncode)
            self.assertIn("grade changed",invalid.stderr)
            state.write_text(json.dumps(original))
            corrupted=json.loads(state.read_text())
            corrupted["audit"]["entries"][0]["appeal"]["score_before"]=1
            state.write_text(json.dumps(corrupted))
            invalid=run(QA,"audit-verify","--state",state,"--audit-key-file",key)
            self.assertEqual(2,invalid.returncode)
            self.assertIn("HMAC mismatch",invalid.stderr)

    def test_checkpoint_detects_snapshot_rollback_and_needs_explicit_ack(self):
        with tempfile.TemporaryDirectory() as tmp:
            state,registry,admin,teacher,key,event_id=self.prepare(tmp)
            aid=self.open(state,key,event_id)
            self.assertEqual(0,self.resolve(state,registry,teacher,key,aid).returncode)
            receipt=Path(tmp)/"receipt.json"
            created=run(QA,"audit-checkpoint","--state",state,
                        "--audit-key-file",key,"--output",receipt)
            self.assertEqual(0,created.returncode,created.stderr)
            self.assertEqual(0,run(QA,"audit-verify","--state",state,
                                   "--audit-key-file",key,
                                   "--checkpoint",receipt).returncode)
            snapshots=state_store.list_snapshots(state)
            old_snapshot=next(x["snapshot_id"] for x in snapshots
                              if x["valid"] and
                              # current last snapshot before secure resolution:
                              json.loads((state_store.snapshots_path(state)/
                                        (x["snapshot_id"]+".json")).read_text())
                                  .get("audit",{}).get("entries") and
                              len(json.loads((state_store.snapshots_path(state)/
                                             (x["snapshot_id"]+".json")).read_text())
                                  ["audit"]["entries"])==1)
            denied=run(QA,"state-recover","--state",state,
                       "--snapshot",old_snapshot,"--confirm")
            self.assertEqual(2,denied.returncode)
            allowed=run(QA,"state-recover","--state",state,
                        "--snapshot",old_snapshot,"--confirm",
                        "--acknowledge-audit-rollback","--audit-key-file",key)
            self.assertEqual(0,allowed.returncode,allowed.stderr)
            no_receipt=run(QA,"audit-verify","--state",state,"--audit-key-file",key)
            self.assertEqual(0,no_receipt.returncode,no_receipt.stderr)
            with_receipt=run(QA,"audit-verify","--state",state,
                             "--audit-key-file",key,"--checkpoint",receipt)
            self.assertEqual(2,with_receipt.returncode)
            self.assertIn("checkpoint",with_receipt.stderr)

    def test_stripping_signed_metadata_cannot_downgrade_authentication(self):
        with tempfile.TemporaryDirectory() as tmp:
            state,registry,admin,teacher,key,event_id=self.prepare(tmp)
            self.assertTrue(audit_ledger.policy_path(state).exists())
            original=json.loads(state.read_text())
            changed=dict(original)
            changed.pop("audit")
            state.write_text(json.dumps(changed))
            bypass=run(QA,"appeal-open","--state",state,"--event-id",event_id,
                       "--reason","other")
            self.assertEqual(2,bypass.returncode)
            self.assertIn("audit-key-file",bypass.stderr)
            check=run(QA,"state-check","--state",state)
            self.assertEqual(2,check.returncode)
            self.assertFalse(json.loads(check.stdout)["audit_metadata_consistent"])
            state.write_text(json.dumps(original))
            # A locally edited policy MAC cannot be used to sign false grades.
            policy=audit_ledger.policy_path(state)
            data=json.loads(policy.read_text())
            data["registry_id"]="attacker-registry"
            policy.write_text(json.dumps(data))
            broken=run(QA,"audit-verify","--state",state,"--audit-key-file",key)
            self.assertEqual(2,broken.returncode)
            self.assertIn("policy HMAC mismatch",broken.stderr)

    def test_pre_audit_snapshot_cannot_restore_into_protected_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            state,registry,admin,teacher,key,event_id=self.prepare(tmp)
            snapshots=state_store.list_snapshots(state)
            older=next(x["snapshot_id"] for x in snapshots if
                       "audit" not in json.loads(
                           (state_store.snapshots_path(state)/
                            (x["snapshot_id"]+".json")).read_text()))
            denied=run(QA,"state-recover","--state",state,"--snapshot",older,
                       "--confirm","--acknowledge-audit-rollback",
                       "--audit-key-file",key)
            self.assertEqual(2,denied.returncode)
            self.assertTrue(json.loads(state.read_text()).get("audit"))

    def test_wrong_key_and_protected_delete_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            state,registry,admin,teacher,key,event_id=self.prepare(tmp)
            another=Path(tmp)/"another.hex"
            audit_ledger.generate_key_file(another)
            bad=run(QA,"audit-verify","--state",state,"--audit-key-file",another)
            self.assertEqual(2,bad.returncode)
            denied=run(QA,"state-delete","--state",state,
                       "--confirm-delete","DELETE-LOCAL")
            self.assertEqual(2,denied.returncode)
            self.assertTrue(state.exists())
            done=run(QA,"state-delete","--state",state,
                     "--confirm-delete","DELETE-LOCAL",
                     "--acknowledge-audit-deletion")
            self.assertEqual(0,done.returncode,done.stderr)
            self.assertTrue(key.exists())
            self.assertFalse(state.exists())

    def test_old_unprotected_appeal_still_runs_and_is_labeled_unauthenticated(self):
        with tempfile.TemporaryDirectory() as tmp:
            state=Path(tmp)/"state.json"
            self.assertEqual(0,run(QA,"next",BANK,"--state",state).returncode)
            result=json.loads(run(QA,"answer",BANK,"--state",state,
                                  "--response","D").stdout)
            aid=json.loads(run(QA,"appeal-open","--state",state,
                               "--event-id",result["event_id"],
                               "--reason","scoring_error").stdout)["appeal_id"]
            response=run(QA,"appeal-resolve","--state",state,"--appeal-id",aid,
                         "--decision","correct","--reason","scoring_corrected",
                         "--new-score","1","--reviewer-confirmed")
            self.assertEqual(0,response.returncode,response.stderr)
            self.assertEqual("self_declared_not_authenticated",
                             json.loads(response.stdout)["reviewer_auth_mode"])


if __name__=="__main__":
    unittest.main()
