---
description: Resume active Edoworks Factory work
agent: explore
---

## Current State

- `edoworks/factory` is the sole canonical factory.
- Issue #69 and PR #71 completed the repository-owned OpenCode development
  environment and `CANONICAL_FOR_NEW_WORK` state.
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
3. Use an approved repository-setting path to unarchive exactly
   `foculoom/vorynce`; do not use an alternate remote or bypass policy.
4. Reassert the `hellofoculoom` GitHub identity, push the exact Vorynce feature
   ref, open and merge the reviewed PR, and safely clean the merged branch.
5. Continue the smallest independently verifiable issue #70 increment without
   modifying unrelated product branches.

## Boundaries

- Product runtime must not import or require development tooling.
- Do not delete predecessors, publish, release, or mutate external state without
  explicit applicable authority.
- Preserve unrelated worktree changes and all unverified state claims.
