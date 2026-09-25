---
description: Resume active Edoworks Factory work
agent: explore
---

## Current State

- `edoworks/factory` is the sole canonical factory.
- Issue #69 and PR #71 completed the repository-owned OpenCode development
  environment and `CANONICAL_FOR_NEW_WORK` state.
- Issue #68 is the active consolidation map. PR #74 merged interactive Factory
  issue writes, bounded visual review, and GitHub authentication preservation at
  `1536ba6`; its local and hosted verification and rendered PRD review passed.
- PR #75 restores the fixed repository-owned issue-intent hash, validation, and
  remote-readback commands required before approved child issue creation. Its
  local 47 Python tests, 6 Node tests, Factory doctor, policy integrity,
  installed-policy comparison, and diff checks pass.
- The current OpenCode process predates PR #75's policy. A fresh
  `bin/factory-dev` session is required after integration before intent commands
  or child issue creation.
- Issue #70 tracks product and release-workflow decoupling.
- The Vorynce ownership chunk is implemented and verified locally at commit
  `f47cab8` on `feature/vorynce-prd-70` in the isolated worktree
  `/var/folders/m6/j69tcnk52059qvy0_6hnxk5r0000gq/T/opencode/vorynce-prd-70`.
- Integration is blocked because `foculoom/vorynce` is archived and the
  owner-authenticated push was rejected read-only. The blocker is recorded on
  issue #70.
- `OPERATIONALLY_CUT_OVER` and all later states remain unverified.
- Route readiness is blocked if tracked benchmark/catalog evidence is stale.

## Restart

1. Run `bin/factory-dev doctor` and read its JSON receipt.
2. Resolve integrity, predecessor-path, active-comparison, or routing blockers
   without changing provider budgets or fallback semantics without authority.
3. Open PR #75's rendered PRD in the bounded browser path, capture it with the
   pinned screenshot utility, and verify readability before integration.
4. Recheck PR #75's required checks at the current head. Merge only while they
   remain passed and the visual review has no unresolved findings.
5. Start a fresh `bin/factory-dev` session and use the repository-owned intent
   workflow to freeze, validate, create, and remotely read back only the
   owner-approved private-public, portfolio-index, and product-repository child
   issues.
6. Use an approved repository-setting path to unarchive exactly
   `foculoom/vorynce`; do not use an alternate remote or bypass policy.
7. Reassert the `hellofoculoom` GitHub identity, push the exact Vorynce feature
   ref, open and merge the reviewed PR, and safely clean the merged branch.
8. Continue the smallest independently verifiable issue #70 increment without
   modifying unrelated product branches.

## Boundaries

- Product runtime must not import or require development tooling.
- Do not delete predecessors, publish, release, or mutate external state without
  explicit applicable authority.
- Preserve unrelated worktree changes and all unverified state claims.
