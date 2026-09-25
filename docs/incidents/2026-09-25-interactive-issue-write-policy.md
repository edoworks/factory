# Interactive Factory Issue Write Deadlock

Date: 2026-09-25
Tracker: `edoworks/factory#68`
Status: correction pending merged verification

## Observation

The owner explicitly approved a dedicated issue-write session for a new Factory
governance map, but the effective Factory development policy denied issue
creation, comments, and closeout unconditionally. It also denied the deterministic
hash command needed by the repository's issue-intent workflow. The required map
and child issue bodies could be prepared but not transported.

## Root-Cause Analysis

1. The issue write could not proceed because every `gh issue create`, comment,
   and close command was denied.
2. The deny was unconditional because the cutover treated auto-mode inability to
   prove human authorization as a reason to remove all issue mutation paths.
3. Interactive and autonomous sessions were conflated even though OpenCode's
   `ask` action exists to require visible human authorization for an exact call.
4. The closeout policy still required one canonical issue per chunk, so the
   mutation deny and tracking requirement formed a governance deadlock.
5. The root cause was an asymmetric guard: policy tested that autonomous writes
   were impossible but did not test that explicitly approved repository-first
   writes remained possible.

## Corrections

- Immediate: retain broad issue mutation denies and add only exact
  repository-first `edoworks/factory` create, comment, and close forms as
  interactive `ask` operations.
- Root cause: document that auto mode cannot satisfy the prompt while an
  interactive owner may approve each exact mutation.
- Recurrence guard: the Factory contract test requires exactly those three
  issue `ask` patterns, the bounded Factory GitHub-page open pattern, and the
  screenshot utility permission; it requires broad issue denies and rejects any
  additional interactive shell permission.

## Pre-Merge Review Gap

Independent review found that the first correction used a suffix-matched
screenshot path, allowed a second repository flag after the approved Factory
repository, and skipped active-policy comparison when only part of the policy
was installed.

1. Those defects survived because tests asserted the intended positive forms
   but not adversarial path, argument, or partial-install forms.
2. The adversarial forms were absent because "exact" was treated as a readable
   command prefix rather than the command's effective destination and binary.
3. That interpretation persisted because policy matching was reviewed as text,
   not as a last-match-wins authorization surface.
4. The partial-install skip shared the same flaw: absence and inconsistency were
   treated as one state instead of separate trust states.
5. The root cause was incomplete negative modeling at the policy boundary.

The correction pins the screenshot command to its home-directory installation,
denies trailing long and short repository overrides, and skips baseline checks
only when no baseline files are installed. Regression tests require all three
properties.

## Boundaries

This change does not auto-approve a write, permit another repository, weaken the
identity check, allow compound shell commands, or authorize issue content. Each
mutation still requires a separate identity check, frozen validated intent, and
an interactive approval. The bounded browser and screenshot permissions are
read-only visual-review tools and do not grant GitHub mutation authority.
