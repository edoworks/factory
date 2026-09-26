# Workspace Bootstrap Deadlock

Date: 2026-09-26

Issue: #114

## Impact

After issue #109 merged, the quarantined primary checkout still contained the
older launcher. The merged launcher existed only in a closed linked worktree and
refused workspace creation because it was not the primary checkout. New issue
workspaces, including issue #113, could not start without bypassing the guard.

No primary file, branch, worktree, or registry entry was changed by the denied
loaded-session attempt. The owner later authorized one exact invocation of the
merged #109 module against the fixed primary path. It created and registered only
`feature/114-workspace-bootstrap` from fresh canonical `main`; the primary file
status remained unchanged.

## Five Whys

1. Why could issue #113 not start? No registered open-issue workspace existed.
2. Why could the primary checkout not create one? Its intentionally preserved
   source predated the merged workspace command.
3. Why could the merged #109 worktree not create one? Creation required the
   executable's own root to be the primary checkout.
4. Why was copying the launcher or using raw Git rejected? Either action would
   violate the read-only quarantine or bypass the repository-owned transport.
5. Why was there no safe handoff? The guard coupled reviewed code provenance and
   repository mutation authority to one physical checkout instead of the shared
   canonical Git repository identity.

## Recurrence Guard

`workspace create` now accepts no repository path and discovers the primary only
from a linked launcher's verified Git common directory. After a pinned canonical
fetch, the launcher's exact HEAD must be an ancestor of `origin/main`, and the
launcher must be registered, clean, and byte-identical to its committed blob.
Shared and per-worktree executable Git configuration, active hooks, replacement
objects, and grafts are rejected before status or checkout; replacement-object
interpretation is disabled in the sanitized environment. Created state must
remain clean at the exact canonical base. Rollback removes a branch only through
an atomic expected-OID update, so concurrent ownership changes are retained and
reported rather than deleted. Temporary-repository tests start with an older
dirty primary and prove that a merged linked launcher can create and register the
next workspace without changing primary files. Negative tests cover unregistered,
dirty, modified, and unmerged launchers, worktree config, hooks, replacement
refs, origin and branch mismatch, issue closure, registry failure, and rollback
ownership races.

## Verification Command Failure 5-Whys

1. Why did the first focused test command fail? `unittest` received an absolute
   file path where it expected an importable module name.
2. Why was that command proposed? The verification handoff used direct-module
   syntax without accounting for spaces and package discovery.
3. Why did quoting not help? Quoting preserved the path as one argument but did
   not change `unittest`'s module-name semantics.
4. Why was no test executed? Discovery never loaded the file, so the receipt was
   a runner-shape failure rather than a test result.
5. Root cause: the external handoff was not copied from the repository's proven
   discovery command shape.

The recurrence guard is to run repository suites from the workspace root, use
`python3 -m unittest discover -s PATH -p PATTERN` for path-based focused runs,
and require the receipt to report a non-zero test count before interpreting pass
or failure. This also prevents root-relative imports from being mistaken for
implementation failures when the terminal was left in a nested package.

## JavaScript Verification 5-Whys

1. Why did the first Node suite stop? The issue worktree had no installed
   `@opencode-ai/plugin`, so one test module could not load.
2. Why was the dependency absent? A new linked worktree does not contain ignored
   `node_modules`, and verification had not run the lockfile install first.
3. Why did the first type-check retry execute the wrong program? Bare
   `npm exec tsc` resolved the unrelated deprecated `tsc` package because the
   project did not declare TypeScript locally.
4. Why did the explicitly selected compiler still fail? The project also did
   not declare Node's type definitions, although both the plugin declarations
   and tool source require them.
5. Root cause: JavaScript verification relied on ambient or dynamically resolved
   tooling instead of a complete repository-pinned development toolchain.

The mechanical recurrence guard pins `typescript@5.8.2` and
`@types/node@22.18.6` in the package lock. Verification must run `npm ci` before
the Node suite, change into `development/opencode` for package-local type
discovery, and invoke `node_modules/.bin/tsc`, never bare `npm exec tsc`.

## Owner Handoff 5-Whys

1. Why was the owner repeatedly asked to run deterministic commands? The loaded
   session's Bash policy denies general commands and all unapproved test shapes.
2. Why were requests repeated rather than minimized? After the first denial, the
   session treated every external-worktree command as unavailable instead of
   attempting each materially different approved-looking operation once.
3. Why did some handoffs need correction? Their working-directory and package
   resolution assumptions were not validated before being sent.
4. Why did that create avoidable work? Each corrected command required another
   owner-terminal round trip even when the expected failure mode was knowable
   from repository metadata.
5. Root cause: execution-boundary handling lacked a mechanical distinction
   between confirmed policy denials, untried commands, and commands requiring a
   specific working directory.

The recurrence guard is to attempt a deterministic command once before handing
it off, retain the exact denial as evidence, derive cwd and dependency setup from
the repository first, batch only independently proven commands, and never ask
the owner to repeat output already captured. In this session, the package-local
type check remains an owner action because Bash explicitly denied it.

## Stale Push Wrapper 5-Whys

1. Why did the first guarded push reject the expected commit? The invoked wrapper
   resolved and inspected the quarantined primary checkout, whose HEAD differs
   from the issue #114 commit.
2. Why did it inspect the primary? The session permission map admitted only the
   wrapper path under `/Users/hello/factory`, and that older wrapper derives its
   repository root from its own source location.
3. Why was that wrapper attempted? Its command shape was allowed while the
   workspace-owned merged wrapper was denied.
4. Why was an allowed command not sufficient? Permission to execute a path does
   not establish that path's revision or repository binding is correct.
5. Root cause: executable provenance was inferred from the allowlist instead of
   verified against the target workspace before invocation.

No network mutation occurred because the stale wrapper failed its exact-HEAD
guard. The mechanical recurrence guard is to inspect a repository-owned wrapper's
root-binding behavior and revision before execution, and never substitute a
quarantined-primary wrapper for the workspace-owned wrapper merely to match a
permission pattern.
