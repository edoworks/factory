# Outcome

Attribute hosted macOS verification storage drift to bounded external-owner directory classes without weakening the Factory storage policy or deleting global state.

# Scope

- Capture read-only before and after allocated-byte measurements for allowlisted hosted Xcode and CoreSimulator directory classes around template verification.
- Emit a machine-readable comparison artifact even when template verification fails.
- Record PR #92 run `36171964484`, where all product checks passed but `908771328` bytes of unknown persistent growth exceeded the unchanged `805306368`-byte tolerance.
- Add deterministic contract tests for exact roots, redacted path labels, comparison semantics, workflow ordering, and always-run artifact upload.

# Out of scope

- Increasing storage tolerance, deleting or modifying global Xcode or CoreSimulator state, changing product behavior, rerunning paid services, or claiming the measured directories fully explain aggregate APFS growth.

# Acceptance criteria

- Hosted template verification records before and after allocated bytes for an exact allowlist of external-owner directory classes.
- Public artifacts use fixed class identifiers and do not expose home paths, usernames, device data, or directory contents.
- The comparison reports signed per-class deltas and aggregate measured growth without converting measured external growth into automatically approved persistent bytes.
- Attribution capture and upload run after template verification even when that step fails.
- The 768 MiB hosted tolerance and local 64 MiB default remain unchanged.
- A hosted run either passes the existing policy or leaves actionable attribution evidence without cleanup or tolerance broadening.

# Verification

- Focused unit and workflow contract tests.
- Full Python and pinned Node policy suites.
- `git diff --check` and launch-ready Factory doctor.
- Independent read-only trust review of path privacy and fail-closed semantics.
- Hosted policy, iPhone, and iPad checks with attribution artifact evidence.

# Dependencies

- PR #92 run `36171964484` storage-policy failure.
- Existing recurrence contract in `docs/incidents/2026-09-24-ambiguous-simulator-destination.md`.

# Authority and privacy

- This issue authorizes reversible repository-local instrumentation and validation only.
- It does not authorize global state cleanup, tolerance increases, deletion, publication of directory contents, credential access, product release, or any preservation or cutover-state advancement.
- Unknown paths and contents remain private; public evidence contains fixed class identifiers and byte counts only.

# Source provenance

- `edoworks/factory` PR #92 and hosted run `36171964484`.
- Factory storage receipt reporting `908771328` unknown persistent bytes against `805306368` tolerated bytes.
- `docs/incidents/2026-09-24-ambiguous-simulator-destination.md` lines 137-157.

# Classification

Enhancement.

# Priority

P0.

# Triage review

- Duplicate review: issue #60 introduced storage governance and issue #81 recorded a separate timeout correction; neither provides the external-owner attribution required after this new exceedance.
- Reprioritization review: PR #92 cannot merge while its required policy check fails, and the existing recurrence contract prohibits another tolerance increase without this instrumentation.

# Intent Validation Failure 5-Whys

1. Why did the first intent validation fail? The `defect` classification was not included in the allowed labels.
2. Why did classification and labels differ? The intent used a human-facing defect category while assigning the repository's `bug` label.
3. Why was the repository category not used directly? The draft did not first bind classification to the validator's accepted label vocabulary.
4. Why did this not create a malformed remote issue? The frozen-intent validator runs before the separately authorized create operation and failed closed.
5. Root cause supported by the validation receipt: issue taxonomy was inferred instead of derived from the repository-owned intent schema.

The first correction aligned `bug` classification and label. The existing validate-before-create gate is the mechanical recurrence guard for structural taxonomy and remains mandatory.

# Remote Label Failure 5-Whys

1. Why did the first authorized create fail? GitHub reported that the `bug` label does not exist in `edoworks/factory`.
2. Why could the locally valid intent request an unavailable label? The local intent validator accepts a broader classification vocabulary than the repository's current hosted labels.
3. Why was availability not known before create? The frozen intent workflow validates structure and identity but does not preflight remote label existence.
4. Why was no malformed issue left behind? GitHub rejected the create request and remote title search returned no matching issue.
5. Root cause supported by local validation and remote rejection: structural classification validity and hosted label availability are not one synchronized contract.

The corrected frozen intent uses the repository's existing `enhancement` classification and label while retaining the defect evidence in Outcome, Source provenance, and Triage review. Remote readback remains mandatory after creation; unavailable labels fail closed without an untracked issue.
