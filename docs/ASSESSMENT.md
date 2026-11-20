# v0.6.0 independent student-answer review and arbitration

The CLI validates structured judgments by human or separately hosted Agent reviewers; it does NOT autonomously understand arbitrary responses, verify logical correctness or prove actual reviewer independence.

For a pending manual question, two reviewers independently submit the criteria scores, one judgment per rubric criterion. The combined JSON object has exactly the field reviews, an array of two entries. Each entry has reviewer_id, independent:true, and judgments. Each judgment has score (0, 0.5, 1), quote (verbatim substring in the student's real answer), evidence (why the quote supports the score), and feedback (actionable recommendation). See examples/sample_dual_review.json.

If the reviewers' scores disagree, the answer is NOT recorded or consumed without a separate adjudication object containing adjudicator_id different from both reviewer IDs and decisions for exactly the disputed indices. Each decision contains criterion_index (zero based), score, reason, quote. See examples/sample_adjudication.json.

CLI pattern:

    python scripts/qa.py answer BANK.json --state .qa-state.json --response-file PRIVATE_ANSWER.txt --independent-reviews @reviews.json --adjudication @adjudication.json

Omit adjudication when all scores already agree. Sample data is synthetic and must never be copied as evidence about an actual student's grade. The pending question must correspond to the same rubric and original answer as the review.

Privacy: --response-file avoids writing the student's answer to command-line arguments but leaves an ordinary local file that the caller must protect and eventually remove if appropriate. Only the final numeric rubric scores, agreement rate and count of disputed criteria are written to the state JSON. Detailed assessment output containing quotations remains temporary, but console logs also need private handling.

Limitations: verbatim matching verifies presence, not semantic validity or relevance. Reviewer identities/independence are self-declared and not independently verified. Matching wrong judgments may agree. Neither agreement nor score is an independently calibrated measure of latent mastery. High-stakes grading requires qualified review and an appeal process.


## v0.8.0 correction pathway
A recorded answer can be appealed through the new event_id and appeal-open/list/resolve commands, with reason codes and explicit reviewer-confirmed corrections. If a manual item already has criterion_scores, the revised rubric vector must match its original dimensions and mean; an arbitrary total score override is rejected. See docs/APPEALS.md. Reviewers' credentials and real-world independence are not authenticated by the CLI.
