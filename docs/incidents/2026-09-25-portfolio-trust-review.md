# Portfolio Index Trust Review Gaps

Date: 2026-09-25
Tracker: issue #78

## Impact

The first independent review found that the draft index exposed raw hosted
repository metadata beyond issue #77's opaque public projection and allowed
syntactically valid but unsupported ownership, lifecycle, tracker, source, and
PRD substitutions. Two Factory evidence references also used one remote revision
that was not present in the local repository graph. No draft was committed or
published.

## Evidence-Based 5-Whys

1. Why could unsupported claims pass? The validator checked independent sets and
   value shapes instead of binding each product ID to one approved complete
   record.
2. Why did independent set checks look sufficient? The design treated the index
   as a generic self-describing registry rather than a public trust boundary.
3. Why did that also expose hosted metadata? The draft copied repository archive,
   branch, and push observations into the public file to support contradiction
   checks instead of retaining issue #77's opaque evidence reference.
4. Why were two evidence references unverifiable locally? The draft used one
   remote merge commit as general evidence rather than the exact local commits
   introducing the cited PRD and lifecycle record.
5. Root cause supported by the review: completeness, privacy, and lifecycle
   authority were modeled as flexible schema properties rather than one closed
   approved mapping per portfolio record.

## Correction And Recurrence Guards

- Raw hosted observations were removed; both public and private hosted inventory
  use the fixed `EVIDENCE-HOSTED-METADATA` reference.
- Every record ID now maps to an exact approved repository reference, visibility,
  lifecycle, tracker, evidence revision and source, PRD disposition, and public
  claim in the validator.
- Mews & Woofs and Vorynce cite the exact local commits that introduced their
  source records.
- PRD references must bind the exact evidence revision and a non-empty path.
- Privacy scanning covers local and Windows paths, email, tokens, private keys,
  credential URLs, backup routes, and SSH repository identities.
- Malformed validation errors are converted to a fixed path-free CLI failure.

Deterministic tests mutate repository ownership, lifecycle, tracker, revision,
private identities, malformed field types, and freshness so each guard fails
closed before publication.
