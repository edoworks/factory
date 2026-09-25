# Consolidation Public-Evidence Boundary Gaps

Date: 2026-09-25

Tracker: `edoworks/factory#77`

## Impact

The first issue #77 validator draft did not provide a complete fail-closed
boundary. Its policy document could authorize additional public fields, ordinary
JSON parsing hid duplicate keys, value scanning covered only selected secret and
privacy patterns, and CI did not directly validate a declared set of tracked
public evidence. No credential or private preservation payload was found in the
draft, and no preservation destination was provisioned.

## Evidence-Based 5-Whys

1. Why could protected material evade the draft guard? Public records accepted
   allowlisted but otherwise free-form string values, and JSON duplicate keys
   were collapsed before validation.
2. Why were those forms accepted? The first validator relied on prohibited-field
   names and selected regular expressions rather than a fixed record schema and
   constrained reference formats.
3. Why could the policy itself weaken that boundary? Contract validation checked
   only required-field inclusion and disjoint lists, not exact policy values and
   exact nested schemas.
4. Why would CI miss an unlisted public evidence file? The CLI validated only
   paths supplied by its caller, while the test used a temporary fixture rather
   than a contract-owned public-record manifest.
5. Root cause supported by the reviewed draft: public classification policy,
   canonical public-record enumeration, and CI enforcement were separate
   conventions instead of one exact fail-closed contract.

## Correction

- The contract records a validator-pinned public-record manifest and exact
  public, private, and prohibited field sets.
- The parser rejects duplicate JSON keys before validation.
- Public records allow no free-form fields. Provenance and inventory references
  use fixed public or opaque values; checksums and recovery receipt references
  require constrained typed formats and validator-owned approval bound to the
  exact evidence class.
- The CLI always validates the complete canonical public inventory, and the CI
  policy job runs it directly.
- The first verification after tightening the schema found a stale test fixture
  with an independently copied inventory ID. The fixture now derives that ID
  from the validator's fixed mapping.

## Recurrence Guard

`tests/test_consolidation_privacy.py` mutates the contract at each nested level,
attempts policy self-authorization, exercises duplicate keys and protected value
forms, requires all six evidence classes in the canonical public inventory, and
requires the direct CI invocation. The validator and tests pin the canonical
public inventory filename independently of contract content.
`scripts/check_consolidation_evidence.py` returns nonzero before accepting any
malformed contract or public record.

## PRD Contract-Test Failure Follow-Up

1. Why did the first PRD-boundary verification fail? The test searched raw
   Markdown for a phrase split across a formatting line break.
2. Why did formatting affect a semantic contract assertion? The test compared
   presentation whitespace instead of normalized prose.
3. Why was raw text used? The initial recurrence guard copied the expected phrase
   directly from the rendered paragraph without accounting for Markdown wraps.
4. Why did the defect reach the full suite? The PRD assertion was added in the
   same increment and had not yet run against the final wrapped text.
5. Root cause supported by the failure output: the semantic assertion lacked the
   repository's existing whitespace-normalization pattern; the PRD contract was
   present and the failure exposed no privacy-boundary defect.

The first correction normalized only the PRD input, so the rerun exposed the
same raw-whitespace assumption in the cutover input. The recurrence guard now
normalizes both human-facing Markdown documents before checking the
class-versus-instance boundary. The full suite is required again before
integration.

## Feature-Push Receipt Mismatch

1. Why did the first documentation-head push fail? The supplied expected commit
   did not match `HEAD`.
2. Why was the value wrong? A full commit ID was inferred from the abbreviated
   commit receipt instead of read from Git.
3. Why was inference used? The push step was started before mechanically
   resolving the new documentation commit.
4. Why did this not alter the remote branch? The pinned push helper compares the
   exact expected commit with `HEAD` before invoking Git transport.
5. Root cause supported by the helper receipt: operator input bypassed the
   mechanical SHA-resolution step, while the existing transport guard failed
   closed as designed.

The retry used `git show --no-patch --format=%H HEAD` and pushed only the returned
commit. Future pinned pushes must derive the full expected commit from Git rather
than expand an abbreviated receipt manually.
