# Superseded-contract whitespace assertion

## Impact

PR #117's first hosted Factory policy run failed even though the required issue
#103 containment sentence was present. The failure blocked integration and, by
ending the policy job before its storage baseline, also prevented creation of
the external-storage attribution artifact.

## Five Whys

1. Why did the policy job fail? The superseded-issue contract test did not find
   `Until then every #103 file remains preserved` in the restart section.
2. Why did it not find the sentence? Markdown line wrapping split `remains` and
   `preserved` with indentation and a newline.
3. Why did wrapping change the result? The assertion searched raw Markdown even
   though the contract concerns rendered prose.
4. Why was that inconsistency missed locally? The new test ran only in the clean
   issue workspace; the earlier broad local receipt came from the quarantined
   primary checkout, whose older test suite did not contain this assertion.
5. Why could the evidence be confused? The verification note identified the
   test count but did not bind that count to the exact worktree path and head.

## Recurrence Guard

The test now normalizes whitespace in the bounded restart section before
checking both successor and containment sentences. Verification and issue
comments must identify the exact workspace and revision whose suite ran; a pass
from another checkout is not evidence for the feature head.

## Bounded iPhone Failure Analysis

The same hosted run's iPhone job independently failed while launching the app
with `Failed to get background assertion ... No failure details provided`.
The iPad job passed the same reference-app suite, and PR #117 changes no product
runtime or UI test source. That evidence is consistent with a hosted
simulator-launch failure but does not prove one or waive the required iPhone
gate.

1. Why did the iPhone job fail? XCTest could not acquire a background assertion
   for the target application during launch.
2. Why was no product assertion available? The launch failed before the test
   reached its first product interaction.
3. Why did target launch fail? The hosted log does not say; it supplied no detail
   beyond the background-assertion error.
4. Why can the analysis not continue causally? No retained evidence attributes
   the launch-service rejection to runner or product state.
5. Why does that uncertainty remain blocking? One occurrence cannot distinguish
   a transient hosted launch failure from a reproducible form-factor defect.

The mechanical guard remains fail closed: the corrected exact head must pass the
iPhone, iPad, and Factory policy jobs. If the launch failure repeats, stop and
track its exact job evidence as a separate defect before changing product or
workflow behavior; do not use retries to hide a reproducible failure.

## Workspace Commit Guard Failure

The first correction commits advanced the linked branch from registered head
`cf76348` to local head `dc8e1df` through raw Git. The workspace registry
therefore remained at `cf76348`. Editing the hash-bound continuation also left
its policy-manifest digest stale. The issue-workspace launcher rejected both
conditions before opening a write-capable session; no push occurred.

1. Why did the workspace registry become stale? The correction used raw Git
   commits instead of `git-commit.mjs`.
2. Why was raw Git available? The loaded session came from the quarantined
   primary checkout's older policy rather than the issue workspace policy.
3. Why did that session write into the linked workspace? The target worktree was
   treated as a working directory without first proving that the loaded policy
   belonged to the same repository revision and workspace admission record.
4. Why did the policy digest also fail? The continuation was edited without
   updating its entry in `policy-manifest.json` in the same staged change.
5. Why did the error reach owner handoff? Verification stopped at the primary
   policy's command boundary instead of running the target workspace launcher
   receipt before claiming the branch was ready for a fresh session.

The owner authorized exact guarded recommit recovery on 2026-09-26. Recovery
returned only the local branch pointer to registered head `cf76348` with a soft
reset without discarding the correction, refreshed the exact continuation
digest, and preserved the complete diff for `git-commit.mjs`, which atomically
advances the registry with the resulting commit.

The existing mechanical containment is the registry-bound launcher and guarded
push: a raw commit leaves the registered head stale, so neither a write-capable
launch nor a push can proceed. The operational recurrence rule is to use no raw
commit in a linked workspace, verify the launcher source and target are the same
admitted root, and run that root's doctor receipt after every hash-bound policy
edit before handoff.

## Exact-Head Catalog Freshness Blocker

Exact-head verification at `b12b195f2c49921139196933b6a696f2abe0e909`
passed all 21 pinned Node tests and 86 of 87 Python tests. The remaining Python
test compared the tracked route-only catalog generation
`1790421641508-3284` with approved generated user catalog generation
`1790693125869-34347` and failed. Factory doctor independently reported the
tracked catalog stale and kept `launch_ready` false.

1. Why did the Python suite fail? The tracked catalog no longer matched the
   available approved generated user evidence.
2. Why did the files differ? The user catalog was refreshed on 2026-09-29,
   while the issue branch retained the tracked snapshot from 2026-09-26.
3. Why did the branch not remain launch-ready? Routing policy permits tracked
   catalog evidence for at most 48 hours.
4. Why was this discovered only after the recovery commit? The commit helper
   validates the staged diff and workspace registry but does not claim that
   time-dependent routing evidence is current.
5. Why must the branch stop before push? Issue #116 requires the complete local
   suite and launch-ready doctor on the exact head; a known stale-evidence
   failure cannot be replaced by hosted or older-head results.

The mechanical guard is unchanged: the catalog-equality test rejects drift,
doctor rejects stale tracked evidence, and `bin/factory-dev refresh-catalog`
imports only the approved route-relevant subset while updating its manifest
digest atomically. After that import, the corrected files and this incident
record require a guarded issue #116 commit and a fresh exact-head rerun before
push.
