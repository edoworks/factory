# Issue Closeout Permission Gap

Date: 2026-09-25

Tracker: `edoworks/factory#87`

Status: corrected pending verification and integration

## Evidence

Issue #84 was remotely closed by PR #85 and its integration record merged in
PR #86, but the repository-mandated `issue-closeout.mjs verify` command was not
admitted by `development/opencode/opencode.jsonc`. Starting a fresh Factory
session would therefore preserve, not resolve, the blocker. The helper also
resolved `gh` through ambient `PATH` instead of `FACTORY_DEV_GH`.

The first authorized issue #87 creation attempt used the validator-supported
`bug` classification but GitHub rejected it because this repository has no
`bug` label. Remote search confirmed that no partial issue was created. The
intent was refrozen as the repository's existing `enhancement` classification,
validated again, created as issue #87, and matched by remote readback.

## Why Chain

1. Why could a closed issue not pass mandatory closeout? The deny-by-default
   shell policy had no exact permission for the repository closeout helper.
2. Why did a fresh session not solve it? The missing permission was in tracked
   source rather than stale loaded configuration.
3. Why was adding a broad GitHub read unsafe? The helper used ambient `gh`, and
   a broad allow could select a product-controlled executable or repository.
4. Why did existing contract tests miss the contradiction? They asserted issue
   intent preparation and mutation permissions but not the issue-tracking
   skill's required final verifier.
5. Why did completion reach this dead-end? The skill requirement, helper
   transport, and executable policy were reviewed as separate controls instead
   of one complete lifecycle.

Root cause: the mandatory issue lifecycle had no contract test binding its final
read-only verification step to the pinned runtime and deny-by-default policy.

## Corrections

- The verifier requires the absolute `FACTORY_DEV_GH` executable and fixes the
  repository to `github.com/edoworks/factory`.
- It removes inherited GitHub host, token, and proxy overrides and requests only
  issue number, title, and state, requires the `hellofoculoom` identity, and
  binds each returned issue number to its request.
- Its argument parser accepts one exact command shape and unique positive issue
  numbers; open or unreadable issues fail closed.
- OpenCode policy admits only that exact repository-owned verifier command and
  keeps direct issue mutation denied. Shell separators, substitution,
  redirection, background execution, and pipes remain denied.

## Mechanical Recurrence Guard

- Focused Node tests use a fake pinned GitHub CLI, a hostile environment, closed
  and open issue receipts, duplicate identifiers, malformed arguments, and
  missing or relative executable paths.
- The single-factory contract test requires the exact permission and exact
  tracked Node test list.
- Fresh-session verification must produce `CLOSED` for issue #84 before its
  closeout blocker is removed from continuation evidence.
