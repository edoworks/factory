# Outcome

Obtain a stable, path-safe external-owner storage measurement across transient CoreSimulator tree mutation without weakening the authoritative aggregate storage policy.

# Scope

- Record PR #98 run `36189352038`, where template verification passed but unknown persistent growth exceeded the unchanged tolerance and `coresimulator_system` was unavailable with `traversal_failed` in both snapshots.
- Retry a complete descriptor-bound traversal from a freshly opened allowlisted root a fixed number of times after transient traversal failure.
- Preserve `unavailable` when no stable full traversal succeeds; never convert a failed or partially observed traversal into zero bytes.
- Add deterministic tests for retry success, exhausted retries, root disappearance after failure, descriptor safety, and fixed path-free output.

# Out of scope

- Increasing storage tolerance, subtracting measured external growth from aggregate unknown growth, ignoring inaccessible subtrees, deleting or modifying global Xcode/CoreSimulator state, publishing paths or contents, or changing product behavior.

# Acceptance criteria

- Each retry begins from a newly opened exact allowlisted root and retains `O_NOFOLLOW` descriptor-relative traversal.
- A stable full traversal returns its allocated-byte count; no partial count is returned.
- Exhausted traversal attempts return fixed `unavailable` and `traversal_failed` values.
- A root that disappears after an earlier traversal failure remains unavailable rather than being reported as absent.
- Retry count is finite and pinned by tests.
- The 768 MiB hosted tolerance and 64 MiB local default remain unchanged.
- Local suites, independent trust review, rendered records, and hosted policy/iPhone/iPad checks pass before closeout.

# Verification

- Focused traversal retry, exhaustion, disappearance, descriptor, and privacy tests.
- Full Python and pinned Node policy suites.
- `git diff --check` and launch-ready Factory doctor.
- Independent read-only review of containment, partial-measurement, and privacy semantics.
- Hosted run with a complete attribution artifact and all required checks passing.

# Dependencies

- PR #98 run `36189352038` and policy job `108250432758`.
- Issue #93 external-owner attribution contract.
- `docs/incidents/2026-09-24-ambiguous-simulator-destination.md` storage recurrence rules.

# Authority and privacy

- This issue authorizes bounded read-only repository-local measurement, tests, incidents, cutover evidence, and continuation updates only.
- It does not authorize tolerance increases, automatic approval of measured growth, global cleanup, private path/content publication, product changes, release-state advancement, or preservation/deletion claims.

# Source provenance

- PR #98 hosted run `36189352038`, policy job `108250432758`.
- Factory receipt reporting `865488896` unknown persistent bytes against `805306368` tolerated bytes after all template checks passed.
- Attribution comparison reporting zero measured growth for available classes and `traversal_failed` for `coresimulator_system` before and after.
- `scripts/external_storage_attribution.py` and `tests/test_external_storage_attribution.py` at PR #98 head `e34236788525e2d04d99b5e6ce23473014535d79`.

# Classification

Enhancement.

# Priority

P0.

# Triage review

- Duplicate review: issue #93 introduced unavailable states but does not retry a transient concurrent traversal; issue #99 owns the separate reference-app timeout and immutable artifact correction.
- Reprioritization review: PR #98 cannot merge while the required policy gate fails and attribution remains incomplete, so this bounded trust repair precedes issue #78 and #99 closeout.
