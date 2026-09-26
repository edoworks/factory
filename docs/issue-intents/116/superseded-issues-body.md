# Outcome

Reconcile the Factory roadmap with current canonical strategy by recording and closing only issues whose original contracts are explicitly superseded, obsolete, or premature, without claiming their former acceptance criteria completed.

# Scope

- Record evidence-backed dispositions for issues #15, #17, #103, and #14.
- Update the Factory Development PRD, Mews & Woofs PRD, single-factory cutover record, and continuation state so successor ownership and retained gates are explicit.
- Preserve issue #68 and #81 as the canonical predecessor-retirement path, issue #66 as the current Mews & Woofs qualification path, and issue #102 as the bounded public review capability.
- Add a reviewed issue-queue reconciliation record and validate that retained open issues remain open.
- Render and visually validate the changed human-facing records before integration and closure.

# Out of scope

- Claiming predecessor preservation, archive, deletion, local cleanup, authenticated-browser acceptance, Mews & Woofs qualification, Apple upload, submission, release, or public identity.
- Closing issues other than #15, #17, #103, and #14.
- Deleting #103 source evidence before the quarantined-primary containment ledger classifies it as intentionally superseded.
- Changing product behavior, provider routes, budgets, credentials, repository visibility, or branch protection.

# Acceptance criteria

- Issue #15 is linked to issue #68's immediate single-factory cutover strategy and is closed as superseded, not completed.
- Issue #17 is linked to issues #68 and #81's exact preservation, restore, target-safety, and separately approved deletion-readiness contract and is closed as superseded, not completed.
- Issue #103 is closed as an unimplemented obsolete diagnostic path after PR #98 is assigned to issue-isolated replacement work; no authenticated-browser acceptance is claimed.
- Issue #14 is closed as premature while Mews & Woofs remains an internal reference fixture; issue #66 retains qualification and any future release requires a new owner-authorized lifecycle and Apple gate.
- Repository records contain no instruction that depends on any of the four closed issues and retain all unresolved safety and owner gates.
- Local verification, independent review, rendered visual validation, hosted checks, merge, remote issue comments, closure, and closeout verification complete before completion is claimed.

# Verification

- Open-issue inventory and targeted remote readback for all four disposition candidates and their successors.
- Full Python and pinned Node suites, `git diff --check`, and launch-ready Factory doctor.
- Independent read-only review of supersession evidence and non-completion language.
- Rendered review of the issue, PRDs, cutover record, reconciliation record, continuation, and final PR.
- Hosted Factory policy, iPhone, and iPad checks on the exact feature head.
- Pinned closeout verification reports `CLOSED` for issues #15, #17, #103, and #14.

# Dependencies

- Merged single-factory cutover and workspace isolation through issue #114.
- Open issues #68, #81, #66, and the PR #98 replacement plan.
- Preserved quarantined-primary containment ledger for issue #103 source evidence.

# Authority and privacy

- The owner's instruction authorizes repository-local records, ordinary reviewed integration, rendered review, comments, and closure of exactly issues #15, #17, #103, and #14.
- It does not authorize predecessor archive or deletion, local cleanup, browser installation, authenticated interaction, Apple actions, product release, public identity, or closure of any other issue.
- Public evidence may cite public issue and revision numbers but must not disclose private repository identities, local evidence payloads, credentials, or browser profile state.

# Source provenance

- Issues #15, #17, #103, and #14 and the complete 2026-09-26 open-issue review.
- Issue #68, issue #81, `docs/single-factory-cutover.md`, `docs/FactoryDevelopment-PRD.md`, and `docs/MewsAndWoofs-PRD.md`.
- Owner-selected aggressive evidence-based closure threshold on 2026-09-26.

# Classification

Documentation and roadmap-state reconciliation.

# Priority

P0.

# Triage review

- Duplicate review: issues #68 and #81 own predecessor consolidation and readiness, issue #66 owns Mews & Woofs qualification, and issue #102 owns bounded public review; none records the cross-issue supersession closeout requested here.
- Reprioritization review: stale open contracts create incorrect dependencies for PR #98 reconciliation, worktree cleanup, predecessor readiness, and product release planning, so this record precedes those operations.
