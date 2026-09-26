# Local Workspace Hygiene Failure

Date: 2026-09-26
Status: correction in issue #109; quarantine cleanup not authorized

## Evidence

- Local branch `main` resolved to open PR #98 head `d4d1068`, while canonical
  GitHub `main` resolved to `3762758`.
- The primary checkout was ahead by four commits, behind canonical history, and
  contained mixed uncommitted work for issues #101, #102, #103, and #108.
- `git-push.mjs` verified `HEAD` and a remote feature destination but did not
  require the current local branch to equal that destination.
- `factory-dev doctor` reported dirty state without using it or workspace
  identity as write-admission gates.
- The issue #69 containment ledger already required the primary checkout to
  remain untouched, but the launcher had no mechanical enforcement.

## 5-Whys

1. Why was issue #108 implemented in a quarantined mixed checkout? The session
   observed unrelated changes but still had a write-capable launch and raw local
   commit path in that checkout.
2. Why was the checkout write-capable? Doctor treated dirty and divergent Git
   state as informational rather than binding launch to an isolated workspace.
3. Why did local `main` hold feature commits? The push transport could send any
   exact `HEAD` to a remote `feature/...` ref without requiring a matching local
   feature branch.
4. Why was no clean workspace created first? Direct fetch, branch, switch, and
   worktree commands were denied, but no guarded repository-owned workspace
   lifecycle existed.
5. Root cause supported by the branch graph, launcher, and transport source:
   remote mutation was tightly guarded while local workspace identity and
   lifecycle were not part of the same admission contract.

## Correction

- The primary checkout is read-only for Factory launch and remains available
  only for doctor and workspace audit/create operations.
- One registered linked worktree, one open issue, and one matching
  `feature/ISSUE-SLUG` branch are required for write launch, commit, and push.
- Raw commit, push, fetch, branch, switch, and worktree commands remain denied;
  exact repository-owned transports perform the admitted operations.
- Registry records bind the issue, resolved path, branch, canonical base, and
  current head. Guarded commit advances the recorded head atomically.
- Retirement requires a closed issue, clean exact worktree, freshly fetched
  canonical main, and merged branch containment. It removes no branch and uses
  no broad filesystem cleanup.

## Verification Failure And Guard

The first isolated local suites correctly rejected non-canonical macOS `/var`
fixture paths and found an unescaped shell expansion in a JavaScript template
fixture. Tests now canonicalize temporary roots before exercising symlink
rejection, and the tracked Node suite parses and directly invokes both guarded
transports. Hosted verification then found that missing-registry validation ran
after lock acquisition; the transport now proves registry presence before any
mutation lock is created, preserving the intended fail-closed diagnostic. The
same correction validates and carries forward registered commit identity so
suppressed global Git configuration cannot make the guarded commit unusable. The
independent exact-head review then found partial-mutation gaps. Guarded commit
now soft-resets to the prior registered head if registry persistence fails, and
workspace creation preflights branch absence and removes only the exact branch
or linked worktree created by a failed attempt. The
remaining missing-package result was an environment prerequisite:
the pinned `npm ci --prefix development/opencode` step must run before the Node
suite, as already enforced by hosted checks.

## Quarantine

No current mixed-checkout file is deleted or rewritten by this correction. PR
#98's exact remote head, merged issue #101/#102 state, issue #103 WIP, and issue
#108 WIP must be independently classified and contained. Repairing local `main`
requires a later exact cleanup manifest and owner approval after that evidence.
