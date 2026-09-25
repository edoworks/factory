# Outcome

Produce evidence sufficient to decide, but not perform, exact predecessor remote deletion and local cleanup without losing history, local-only work, hosted metadata, obligations, or active dependencies.

# Scope

- Inventory exact predecessor remote identities, resolved local roots, related runners and service definitions, and explicit exclusions.
- Classify every modified, untracked, unpushed, remote-only, unborn, generated, sensitive, and intentionally disposable state before cleanup eligibility.
- Preserve required Git refs, local overlays, hosted metadata, and obligations outside both the deletion targets and this machine's failure boundary.
- Run isolated restore drills and current operational-reference, process, service, runner, privacy, and target-safety scans.
- Prepare separate exact remote and local allowlists for later owner approval.

# Out of scope

- Deleting, archiving, transferring, unarchiving, or changing visibility of any repository; removing local paths; publishing preservation artifacts; changing credentials; or claiming a later cutover state before its evidence passes.

# Acceptance criteria

- Every proposed remote and local target has an exact identity, lifecycle disposition, ownership record, and explicit inclusion or exclusion reason.
- Every non-clean local or divergent Git state is preserved or explicitly approved as disposable, with no inference from `git status` alone.
- Required Git, local overlays, hosted metadata, and obligations restore successfully from integrity-checked owner-controlled preservation outside the deletion and machine-failure boundary.
- A fresh scan finds zero unexplained critical predecessor execution, service, runner, configuration, product, release, or validation dependencies.
- Remote and local allowlists pass dependency, recovery, privacy, retention, and resolved-target safety checks and remain unexecuted pending separate exact owner approvals.

# Verification

- Exact-target inventory and lifecycle-state contract tests.
- Git divergence and local-overlay classification receipts for every local predecessor root.
- Serialized archive integrity checks and isolated restore drills.
- Current process, service, runner, configuration, and operational-reference scans.
- Independent read-only review and rendered review of the human-facing readiness record.

# Dependencies

- Parent consolidation map issue #68.
- Active dependency removal and classification issues #70, #77, #78, and #79.
- An approved owner-controlled preservation destination outside this machine's failure boundary.

# Authority and privacy

- This issue authorizes reversible inventory, preservation, validation, and repository-local documentation only.
- It does not authorize remote deletion, local cleanup, publication, repository setting changes, credential broadening, product release, or treating issue closure as deletion approval.
- Sensitive inventories, private metadata, backup routing, credentials, and preservation payloads must remain outside public evidence.

# Source provenance

- `edoworks/factory` issue #68 and `docs/single-factory-cutover.md`.
- Local read-only predecessor inspection on 2026-09-25 at Factory feature head `20fd8c1fa65872921479e55031161f273b14b901`.
- Owner clarification on 2026-09-25 that Vorynce is paused, so it is not an active integration or unarchive target.

# Classification

Enhancement.

# Priority

P0.

# Triage review

- Duplicate review: issue #17 retains an older archive-only contract; this issue implements issue #68's superseding exact-target, tested-preservation, and separately approved deletion-readiness gates without deleting anything.
- Reprioritization review: no predecessor deletion or cleanup can be considered until this evidence and its dependencies pass.
