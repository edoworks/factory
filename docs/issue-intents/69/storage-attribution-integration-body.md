# Outcome

Record the completed hosted storage-attribution integration and restore the canonical continuation command to current merged state.

# Scope

- Replace the stale pre-merge PR #92 and issue #93 continuation wording with exact merge, hosted-run, artifact, and closeout evidence.
- Record PR #92 merge `5492a406fd78a2c073f907037c29ef03483fa7b5`, exact tested head `a8a0d565d0dad6ef84728864d5adbe4507bccec3`, and hosted run `36177899841`.
- Record the dedicated `external-storage-attribution` artifact digest `9ab0be06177043ba374ded6ea8c78958645a8b83b080d1eed5c3f1b616839f2d` and issue #93 closeout verification.
- Update the continuation policy digest and deterministic evidence.

# Out of scope

- Product behavior, storage tolerance, global state cleanup, release or publication, branch deletion, preservation-state advancement, and any new attribution implementation.

# Acceptance criteria

- The continuation command no longer states that PR #92 is open or that issue #93 is active.
- The continuation command identifies PR #92's merge commit, exact tested head, successful policy/iPhone/iPad run, attribution artifact digest, and issue #93 `CLOSED` receipt.
- Restart priorities return to issues #70, #78, #79, and blocked issue #81 without claiming later cutover state.
- Policy integrity and the active installation remain valid.
- No runtime, workflow, tolerance, cleanup, routing, or provider behavior changes.

# Verification

- Full Python and pinned Node policy suites.
- `git diff --check` and launch-ready Factory doctor.
- Frozen intent validation and exact remote readback.
- Exact continuation and policy-manifest review.
- Hosted policy, iPhone, and iPad checks before merge.

# Dependencies

- PR #92 merge `5492a406fd78a2c073f907037c29ef03483fa7b5`.
- Hosted run `36177899841` on head `a8a0d565d0dad6ef84728864d5adbe4507bccec3`.
- Closed issue #93 and its pinned `CLOSED` receipt.

# Authority and privacy

- This issue authorizes repository-local integration evidence and validation only.
- It does not authorize global state cleanup, tolerance changes, deletion, publication of private evidence, product release, or preservation and cutover-state advancement.
- Public evidence remains limited to repository identifiers, run identifiers, fixed artifact names, digests, and check conclusions.

# Source provenance

- `edoworks/factory` PR #92 and merge commit `5492a406fd78a2c073f907037c29ef03483fa7b5`.
- GitHub Actions run `36177899841` and its public artifact inventory.
- `edoworks/factory` issue #93 closeout receipt.

# Classification

Enhancement.

# Priority

P0.

# Triage review

- Duplicate review: issue #93 owns instrumentation and is closed; this bounded chunk owns only post-merge repository state accuracy.
- Reprioritization review: the canonical continuation command is currently stale after merge and must be corrected before other Factory work resumes.
