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
properties. Follow-up review applied the same override denial to allowed PR
commands and denied extra arguments or targets on the browser-open command.

The first follow-up test edit failed discovery with an indentation error because
an assertion intended for the issue-command loop landed after the new PR/open
assertions. It landed there because the patch context crossed the loop boundary;
that was not noticed because visual diff inspection preceded execution; execution
then failed because Python could not import the module; the failure could not be
mistaken for a product failure because discovery named the exact syntax location;
the root cause was an unverified structural edit. The correction moved the
assertion back into the loop, and full Python test discovery remains the
mechanical recurrence guard required before commit.

## Fresh-Session Authentication Gap

Pre-merge execution found that the restored issue commands still could not use
GitHub CLI authentication inside `bin/factory-dev`, even though the same
credential helper could push the feature branch.

1. `gh issue` could not authenticate because it found no host configuration.
2. GitHub CLI resolved its configuration beneath the launcher's isolated
   `XDG_CONFIG_HOME`.
3. The launcher replaced `XDG_CONFIG_HOME` for OpenCode without first preserving
   GitHub CLI's user configuration root.
4. Launch tests asserted removal of OpenCode overrides but did not observe any
   credential-bearing tool's configuration path.
5. The root cause was process-wide configuration isolation modeled only as an
   OpenCode concern, leaving allowed external tools without an explicit
   configuration-preservation contract.

The correction resolves `GH_CONFIG_DIR` from the pre-isolation environment and
passes that path to the launched process while continuing to isolate OpenCode.
The launcher test records both paths and requires GitHub CLI to retain the user
configuration root. No credential value is copied, logged, or committed.

## Issue-Intent Preparation Gap

After PR #74 merged, child issue creation remained noncompliant because the
required issue-intent preparation commands were not executable under the same
policy.

1. A child issue could not be frozen and validated because the shell allowlist
   admitted issue transport commands but not `issue-intent.mjs`.
2. The correction focused on interactive GitHub mutations and omitted the
   read-only preparation and remote-readback stages that make those mutations
   trustworthy.
3. The permission contract test asserted create, comment, and close patterns but
   not the complete issue lifecycle.
4. The issue-tracking skill and runtime permission policy were reviewed as
   separate artifacts rather than one executable workflow.
5. The root cause was an incomplete end-to-end trust model: transport authority
   was restored without mechanically proving that intent freezing and readback
   remained possible.

The correction adds a deterministic body-hash operation to the repository-owned
script and allows only its fixed `hash`, `validate`, and `verify-remote` command
forms. Script argument checks reject extra operands, the shell policy still
denies compound commands, and contract tests require the complete read-only
preparation surface.

## Intent-Binding Review Gap

Independent review of PR #75 found that the initial correction still trusted a
working-directory-relative script path and left raw issue creation separately
approvable from the validated intent.

1. A product target could shadow the relative script path because permission
   matching constrained the typed command but not the resolved executable file.
2. The allowlist described the script as repository-owned without anchoring it
   to the launcher's trusted `FACTORY_DEV_OPENCODE_ROOT`.
3. Raw `gh issue create` remained an interactive operation, so approval did not
   prove that its title and body came from the validated intent.
4. Contract tests checked the presence of command patterns but did not exercise
   a non-repository target or the complete validate-create-readback data flow.
5. The root cause was treating human authorization and content integrity as one
   gate rather than independent gates that must both pass.

The correction anchors all intent commands to `FACTORY_DEV_OPENCODE_ROOT`,
removes direct issue creation from the interactive surface, and adds an
interactive script command that validates the intent before passing the exact
validated title, body bytes, and labels to GitHub. Tests reject the relative
shadowable pattern and exercise valid, hash-mismatched, created, and remote
readback states through a fake GitHub transport.

## Boundaries

This change does not auto-approve a write, permit another repository, weaken the
identity check, allow compound shell commands, or authorize issue content. Each
mutation still requires a separate identity check, frozen validated intent, and
an interactive approval. The bounded browser and screenshot permissions are
read-only visual-review tools and do not grant GitHub mutation authority.
