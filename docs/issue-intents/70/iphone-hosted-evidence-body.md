# Outcome

Make hosted Mews & Woofs form-factor verification complete within an evidenced independent bound and upload immutable result evidence after success or timeout.

# Scope

- Record PR #98 run `36184422124`, where the iPhone verification reached its 15-minute step timeout while UI tests were still passing.
- Increase only the independent reference-app step and job bounds enough to contain the observed cold hosted run.
- Package each completed or interrupted `.xcresult` into an immutable archive before artifact upload.
- Add deterministic workflow contract tests for the new bounds, packaging order, fixed archive path, and fail-closed upload behavior.

# Out of scope

- Changing Mews & Woofs product behavior or tests, weakening required iPhone or iPad verification, introducing retries that hide test failures, changing Factory storage tolerances, or modifying global runner state.

# Acceptance criteria

- Each iPhone and iPad verification step has an independent finite timeout below its job timeout.
- The new bounds are tied to run `36184422124` rather than an unbounded increase.
- Evidence packaging runs after verification even when verification fails or times out.
- Artifact upload consumes only a completed immutable archive, not a live `.xcresult` directory.
- Missing or unpackageable evidence fails the job without exposing private runner paths in repository records.
- Focused and full local suites pass, hosted policy/iPhone/iPad checks pass, and the rendered workflow and issue records receive visual review.

# Verification

- Workflow contract tests for exact bounds, package-before-upload ordering, immutable archive naming, and `if: always()` behavior.
- Full Python and pinned Node policy suites.
- `git diff --check` and launch-ready Factory doctor.
- Independent read-only review of timeout and evidence semantics.
- Hosted policy, iPhone, and iPad checks on the corrected revision.

# Dependencies

- PR #98 run `36184422124`.
- Existing issue #70 and `docs/incidents/2026-09-25-mews-woofs-ci-timeout.md` independent form-factor contract.

# Authority and privacy

- This issue authorizes repository-local workflow, contract-test, incident, PRD/cutover evidence, and continuation updates only.
- It does not authorize product behavior changes, removal of test coverage, unlimited timeouts, global runner cleanup, storage tolerance changes, release-state advancement, or publication of private paths or artifact contents.

# Source provenance

- PR #98 hosted run `36184422124`, iPhone job `108234873235`.
- Rendered job evidence showing `Verify reference app` timed out after 15 minutes while UI tests were passing.
- Rendered upload evidence showing `actions/upload-artifact@v4` failed with `ENOENT` while zipping the live iPhone `.xcresult`.
- `.github/workflows/checks.yml` and `tests/test_factory_storage.py` at PR #98 head `f2c6c1d3625b9eaeda222d1d6d0f2df168fcb82b`.

# Classification

Enhancement.

# Priority

P0.

# Triage review

- Duplicate review: issue #70 introduced independent 15-minute form-factor steps, but it does not address the newly evidenced insufficiency of that bound or the live-result upload race. Issue #78 owns the portfolio index and does not own reference-app CI packaging.
- Reprioritization review: PR #98 cannot merge while a required hosted check fails, so this bounded verification correction precedes portfolio closeout.
