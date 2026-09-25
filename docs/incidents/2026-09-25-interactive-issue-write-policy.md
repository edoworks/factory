# Interactive Factory Issue Write Deadlock

Date: 2026-09-25
Tracker: `edoworks/factory#68`
Status: post-merge correction pending verification

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

Rereview found that the trusted script still spawned `gh` by name:

1. Validated intent could reach a substituted executable because child-process
   transport resolved `gh` from inherited `PATH`.
2. Anchoring the script protected its own code but did not anchor its external
   transport dependency.
3. The launcher preserved the user environment without resolving the allowed
   GitHub CLI before entering a product target.
4. The transport test intentionally injected a fake `gh` through `PATH` to
   observe arguments, so it proved construction while normalizing substitution.
5. The root cause was applying executable provenance to the validator but not
   recursively to the validator's privileged child process.

The launcher now resolves `gh` once, passes its absolute real path as
`FACTORY_DEV_GH`, and refuses readiness when GitHub CLI is unavailable. The
script requires that pinned absolute path for creation and readback. A regression
test prepends a hostile executable after pinning and proves it is not selected.

## Post-Merge Transport Trust Gap

Independent post-merge review found that initial executable selection, inherited
GitHub overrides, and wildcard test runners still weakened the issue-write
boundary.

1. An unapproved write could run indirectly because allowed wildcard test
   runners could select arbitrary workspace code.
2. A substituted transport could be pinned because the launcher selected the
   first `gh` from inherited `PATH` before resolving it.
3. A different host or credential could be selected because inherited
   `GH_HOST`, `GH_TOKEN`, and related overrides remained in the launched process.
4. Tests covered post-launch `PATH` substitution and direct command strings, but
   not initial executable provenance, exact runner operands, host pinning, or
   authenticated identity.
5. The root cause was treating an absolute path, a repository argument, and a
   top-level permission match as complete provenance without binding where the
   executable came from, which host received the operation, which identity
   authenticated it, and what code an allowed runner could select.

The correction denies wildcard Python and Node runner forms while allowing only
the two exact tracked suite commands anchored to `FACTORY_DEV_OPENCODE_ROOT`.
The launcher resolves GitHub CLI once from explicit package-manager paths,
requires its target to remain within a `gh` package root and rejects a
group/world-writable executable, strips inherited `GH_*` and `GITHUB_*`
overrides, and the issue workflow
pins `github.com/edoworks/factory` and verifies
`hellofoculoom` before creation or readback. Regression tests inject a repository
`gh`, hostile host and token variables, an incorrect authenticated identity, and
non-exact runner forms. All allowed GitHub commands now use the pinned executable,
comment and close use the identity-checking repository script, and doctor is
anchored to the environment root. These checks are the mechanical recurrence
guard.

Final command-surface review found that inherited `PATH` could still shadow the
anchored commands' interpreters, PR URL selectors could override the canonical
repository, and the Git credential-helper push exception was malformed. The
launcher now supplies a fixed system/package-manager `PATH`; policy denies PR URL
selectors and trailing issue-read repository overrides; and the unsafe push
exception is removed rather than repaired without a dedicated transport design.
Tests require each guard. Vorynce integration therefore remains blocked pending
a separately reviewed push path.

The follow-up push transport is repository-owned and interactive. It accepts one
validated lowercase `feature/...` branch and one full expected commit, verifies
that commit as `HEAD` plus the `hellofoculoom` identity, uses the pinned GitHub
CLI and `/usr/bin/git`, suppresses system/global Git configuration, rejects local
URL, HTTP, and include settings, removes inherited `GIT_*` and proxy overrides,
fixes the canonical HTTPS remote and no-follow-tags refspec to that commit, and
executes from the Factory root without bypassing hooks. Its test rejects
non-feature, option-bearing, mutable, and mismatched commit inputs and captures
the exact child-process arguments.

The first full verification of that correction failed two assertions:

1. The provenance fixture was rejected because its executable resolved beneath
   `/private/var` while its approved package root retained the `/var` spelling.
2. The comment assertion differed for the same reason: production canonicalized
   the body file while the expected fixture path did not.
3. The tests used macOS temporary paths, where `/var` is a symlink to
   `/private/var`.
4. The implementation canonicalized leaf files but not both sides of containment
   and equality checks.
5. The root cause was inconsistent path canonicalization at a trust boundary.

The correction resolves approved roots and expected body paths before comparison.
The full Python suite, rather than a platform-specific skip or relaxed string
comparison, remains the mechanical recurrence guard.

## Boundaries

This change does not auto-approve a write, permit another repository, weaken the
identity check, allow compound shell commands, or authorize issue content. Each
mutation still requires a separate identity check, frozen validated intent, and
an interactive approval. The bounded browser and screenshot permissions are
read-only visual-review tools and do not grant GitHub mutation authority.
