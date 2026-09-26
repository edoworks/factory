# Outcome

Provide a fail-closed bootstrap path for creating the next registered issue workspace after the canonical primary checkout has been quarantined read-only and the workspace guard has merged remotely.

# Scope

- Reproduce and document the post-issue-#109 bootstrap deadlock without modifying the quarantined primary checkout.
- Add one repository-owned path that executes merged workspace policy while binding creation to the existing canonical repository's discovered primary checkout and fresh `origin/main`.
- Require an open issue, exact `feature/ISSUE-SLUG` branch, pinned origin and GitHub identity, clean destination, safe Git configuration, path containment, and registry consistency.
- Reject caller-selected repositories, raw Git worktree creation, source checkout writes, stale or unmerged launcher code, branch reuse, and partial unregistered state.
- Add deterministic temporary-repository tests, Factory Development PRD and continuation updates, a 5-Whys, independent trust review, and rendered validation.

# Out of scope

- Cleaning, resetting, updating, or deleting the quarantined primary checkout; rewriting existing worktrees; force operations; branch-protection bypass; release publication; provider changes; or implementing issue #113 research corrections in this issue.

# Acceptance criteria

- A policy-valid session using code already contained in canonical `origin/main` can create a new registered issue workspace even when the primary checkout's tracked files intentionally remain older and dirty.
- The bootstrap discovers and verifies the primary checkout through Git common-directory facts; callers cannot supply or redirect the repository root.
- The operation changes only allowlisted Git worktree metadata, the new worktree/branch, the fetched canonical-main ref, and the workspace registry; primary checkout files remain byte-for-byte untouched.
- Every failure before registration rolls back only the newly created branch/worktree and reports bounded evidence; ambiguity fails closed without cleaning existing state.
- Raw Git worktree, fetch, branch, switch, commit, and push commands remain denied.
- Local tests, independent trust review, rendered documentation review, and hosted policy, iPhone, and iPad checks pass on the exact feature head before integration.

# Verification

- Temporary-repository tests covering dirty divergent primary state, linked launcher state, stale launcher rejection, common-directory escape, origin mismatch, issue closure races, branch collisions, rollback failure, and registry failure.
- Full Python and pinned Node suites, `git diff --check`, and Factory doctor from the isolated correction workspace.
- Independent trust review of repository discovery, mutation containment, rollback, and authority boundaries.
- Rendered review of the PRD, incident, issue, continuation, and final PR.
- Hosted Factory policy, iPhone, and iPad checks on the exact feature head.

# Dependencies

- Merged issue #109 workspace registry and guarded lifecycle.
- Preserved quarantined primary checkout and clean merged #109 linked worktree.
- Open issue #113 as the first observed blocked successor.

# Authority and privacy

- The owner's instruction to proceed authorizes reversible repository-local implementation, ordinary issue tracking, tests, review, and one guarded bootstrap acceptance test.
- It does not authorize raw manual Git worktree creation, primary-checkout file changes, cleanup, deletion, force operations, release publication, credential disclosure, or provider changes.
- Public evidence may identify issue and revision numbers but must not publish private registry contents or unrelated worktree material.

# Source provenance

- Merged issue #109 implementation and PR #110 hosted evidence.
- Workspace registry receipt showing only the closed #109 workspace.
- Quarantined primary status and issue #113 bootstrap blocker receipt from 2026-09-26.

# Classification

Enhancement correcting a workspace-admission bootstrap defect.

# Priority

P0.

# Triage review

- Duplicate review: issue #109 introduced workspace isolation, issue #111 owns verification inside an admitted workspace, and issue #113 owns research-gate correction; none provides a successor-workspace bootstrap when the primary executable cannot be updated.
- Reprioritization review: this correction blocks every new write-capable issue workspace, including #113, so it precedes all further repository implementation.

# Bootstrap Failure 5-Whys

1. Why can issue #113 not start? No registered open-issue workspace exists, and creation requires the primary checkout's executable.
2. Why can the primary executable not create it? The quarantined primary checkout intentionally remains on older mixed source that predates the merged workspace command.
3. Why not run the merged executable from issue #109? It derives repository authority from its own linked-worktree path and correctly rejects creation because that path is not the primary checkout.
4. Why not copy code or use raw Git commands? Both would bypass the read-only primary and repository-owned transport guarantees introduced by issue #109.
5. Root cause: issue #109 bound policy provenance and repository mutation authority to one executable path without a contained handoff from a merged linked worktree to its same repository's quarantined primary metadata.

The recurrence guard is a temporary-repository acceptance test that starts with an older dirty primary checkout and a clean linked worktree whose exact launcher revision is contained in fresh canonical `origin/main`; only the guarded transport may create and register the next issue workspace while proving the primary worktree files are unchanged.
