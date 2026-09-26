# Outcome

Make the canonical Factory checkout read-only and require every write-capable Factory session, commit, and push to use one clean linked worktree bound to one open Factory issue.

# Scope

- Add a guarded issue-worktree create, audit, and retire lifecycle rooted outside the canonical checkout.
- Refuse write-capable `factory-dev` launch in the primary checkout, local `main`, unregistered worktrees, mismatched branches, stale issue bindings, or unsafe paths.
- Replace broad raw commit permission with a repository-owned guarded commit transport.
- Require `git-push.mjs` to prove the current local branch exactly matches the requested remote feature branch and the registered issue workspace.
- Add deterministic temporary-repository tests, CI contract checks, PRD updates, an evidence-based 5-Whys, continuation state, and rendered visual validation.
- Bootstrap clean containment and later recovery of the currently quarantined mixed checkout without resetting, cleaning, or losing unrelated work.

# Out of scope

- Deleting or rewriting the current mixed checkout, force-pushing, bypassing branch protection, publishing releases, changing provider routes, or cleaning Factory build artifacts; artifact retention is a separate bounded issue.

# Acceptance criteria

- The primary Factory checkout supports read-only doctor and hygiene audit operations but cannot launch a write-capable session.
- A write-capable Factory session requires a clean linked worktree created from freshly verified canonical `main`, an open issue, and a matching `feature/ISSUE-SLUG` branch.
- Raw direct commit and push paths are denied; guarded transports fail closed on primary checkout, branch mismatch, dirty post-commit state, stale issue state, unsafe Git configuration, or path escape.
- The open PR #98 head, merged issue #101/#102 material, open issue #103 WIP, and issue #108 WIP remain preserved and independently classified throughout containment.
- Local `main` is not repaired until every uncommitted hunk is integrated, superseded with evidence, or preserved in an issue worktree and an exact cleanup manifest receives owner approval.
- CI and local tests cover the admission and negative paths, and the updated PRD and issue evidence pass rendered visual validation.

# Verification

- Focused temporary-Git-repository workspace, commit, push, path-containment, and retirement tests.
- Full Python and pinned Node suites, `git diff --check`, and launch-ready doctor from the isolated worktree.
- Independent trust review of local mutation, containment, and cleanup boundaries.
- Rendered visual validation of the PRD, issue, incident, continuation, and final PR surfaces.
- Hosted Factory policy, iPhone, and iPad checks on the exact feature head.

# Dependencies

- Canonical GitHub `main` revision verified immediately before bootstrap.
- Existing mixed-WIP containment ledger under issue #69.
- Open PR #98 and issues #78, #99, #100, #103, and #108.

# Authority and privacy

- The owner authorizes reversible repository-local worktree creation, guarded local commits, ordinary reviewed PR integration, issue tracking, and validation for this chunk.
- No force push, reset-hard, broad clean, tag, release, deletion of uncontained work, credential export, or global cache cleanup is authorized.
- Local paths and WIP content remain outside public evidence except the already public canonical checkout path and opaque containment classifications.

# Source provenance

- Current `/Users/hello/factory` status, branch graph, mixed-WIP containment ledger, and Factory development policy.
- Canonical GitHub `main` and open PR #98 metadata inspected on 2026-09-26.
- `bin/factory-dev`, `development/opencode/scripts/git-push.mjs`, and their tests.

# Classification

Enhancement correcting a local-workspace governance defect.

# Priority

P0.

# Triage review

- Duplicate review: issue #108 owns source-version freshness, issue #103 owns authenticated browser review, and issue #69 owns the broader development environment; none enforces issue-isolated local workspaces or protects local `main` from feature commits.
- Reprioritization review: this guard precedes issue #108 integration and any further write-capable Factory work because the current checkout is explicitly quarantined and local `main` is divergent.
