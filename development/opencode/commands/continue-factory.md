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
- PR #75 merged the repository-owned issue-intent workflow at `dfbc416` after
  its three hosted checks passed. Its bounded rendered PRD review at the final
  feature head found no overlap, clipping, or readability defect.
- Post-merge independent review found that wildcard test runners, initial `gh`
  selection from inherited `PATH`, and inherited GitHub host/token overrides
  still weakened the issue-write trust boundary. The correction is committed
  locally at `a3bb760`; 49 Python tests, 6 Node tests, Factory doctor, diff checks,
  and independent rereview pass with no finding. Hosted integration is blocked
  because the unsafe Git credential-helper push exception was removed. The pinned
  repository-owned push transport is committed at `150decd`; 49 Python tests,
  7 Node tests, Factory doctor, diff checks, and independent review pass. A fresh
  session is required before using it. No child issue creation is permitted until
  the correction is pushed, merged, freshly launched, and verified.
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
3. Start a fresh Factory session, obtain the full current commit with
   `git log -1 --format=%H`, and run the interactive pinned push transport for
   branch `feature/issue-transport-trust-68` and that exact expected commit.
4. Run hosted checks and bounded rendered PRD review before integration.
5. Start a fresh `bin/factory-dev` session after that integration and use the repository-owned intent
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
