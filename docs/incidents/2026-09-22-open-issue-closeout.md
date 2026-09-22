# Open Issue Closeout Recurrence

Date: 2026-09-22
Tracking: `docs/open-issue-queue-audit-2026-09-22.md` and factory PR #39
Subject: completed factory-tracked chunks left as open GitHub issues
Status: process correction prepared; existing issue state intentionally unchanged

## Impact

At least six NowNest chunk issues remained open after implementation evidence
and merged app pull requests existed: #29, #30, #33, #34, #35, and #36. This
inflated the active queue and caused later sessions to re-audit work that had
already passed its implementation checks.

## Evidence

- Chunk A evidence names `edoworks/factory#29` and result commit `00357b4`.
- Chunk C evidence names `edoworks/factory#33`, result commit `c6c3194`, and
  57/57 passing tests.
- The NowNest continuation record identifies Chunk B and B1-B3 as merged and
  links child issues #34-#36.
- The live factory queue showed those issues still open on 2026-09-22.

## 5-Whys

1. Why did completed chunks remain open? Sessions recorded code, test, and
   evidence completion but did not perform the corresponding issue-close
   mutation and readback.
2. Why was the close mutation omitted? The issue-tracking skill stated that an
   issue should close after verification but did not make closure a required
   final checklist step with a concrete command.
3. Why did review not catch the omission? Completion review checked commits,
   tests, and evidence paths, but not the live state of every canonical
   tracking issue.
4. Why was there no mechanical detection? No read-only guard failed when an
   issue remained `OPEN`, so a clean worktree and merged PR could be mistaken
   for an integrated tracker state.
5. Root cause: the workflow treated GitHub issues as narrative references
   instead of a release-gated source of work status; closure had no enforced
   owner, command, or machine-checkable completion condition.

The evidence supports the workflow root cause. It does not establish whether
the owner intentionally kept any specific child issue open for parent-map
bookkeeping; that remains a maintainer decision.

## Corrections

- Immediate correction: add a closeout gate to the `issue-tracking` skill that
  requires issue closure and a `CLOSED` readback before completion is reported.
- Root-cause correction: add the read-only
  `~/.config/opencode/scripts/issue-closeout.mjs` guard and unit tests for
  duplicate, invalid, open, and closed issue states.
- Existing issues: do not close them automatically from inferred evidence;
  perform a separate maintainer-reviewed cleanup using the new guard.

## Recurrence Guard

The guard fails on `OPEN`, missing, malformed, or unknown issue state and emits
`CLOSED` only when every requested issue is closed. Auto-mode sessions must
leave an explicit closure follow-up rather than claiming completion.

No issue was closed, relabeled, or otherwise mutated while preparing this
correction.
