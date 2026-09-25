# Ambiguous simulator destination

## Impact

The first storage-governed verification probe reserved capacity correctly but
failed its iPhone build and unit-test steps. Two available simulators had the
same `iPhone 17 Pro` name, so Xcode rejected the name-based destination. The
failed run retained 130,351,104 bytes of scoped diagnostic state and released
its storage lease as designed.

## Five Whys

1. The iPhone build failed because Xcode found multiple matching destinations.
2. Multiple destinations matched because two available devices shared the same
   model name and runtime.
3. The verifier passed only the selected device name to Xcode.
4. The selector parsed human-readable `simctl` output even though each device
   already had a unique UDID.
5. The lifecycle tests covered simulator availability but not duplicate names.

The evidence stops at the missing duplicate-name case; no cause is asserted for
why the host has duplicate devices.

## Corrections And Guard

- Immediate correction: select an available device by UDID and pass
  `platform=iOS Simulator,id=<UDID>` to Xcode.
- Root-cause correction: consume `simctl --json` as structured data rather than
  reparsing display output.
- Recurrence guard: unit tests provide duplicate names and require the booted
  device's unique UDID; unavailable devices must not be selected.

## Receipt Finalization Follow-Up

The next probe passed every Xcode stage but failed while finalizing its receipt:
macOS Bash with `set -u` treated expansion of an empty optional retained-artifact
array as an unbound variable. The interruption trap still released the lease,
so no capacity remained reserved.

1. Finalization failed because an empty array was expanded under nounset mode.
2. The array was empty because a successful ordinary run retained no artifact.
3. Optional CLI arguments and required CLI arguments were assembled separately.
4. The shell contract was syntax-checked but the successful no-retention path
   had not yet completed end to end.

The correction uses one always-populated finish-argument array and appends
retention arguments only when present. The static test rejects the former empty
array pattern, and the clean end-to-end verification probe is the behavioral
recurrence guard.

## Asynchronous Simulator Reclamation Follow-Up

A later probe created and retired unique run-owned simulator devices, but the
receipt finalized before CoreSimulator returned their backing storage. It
reported 1,231,265,792 bytes of persistent growth; a subsequent filesystem
measurement showed that approximately 1.2 GB had already been reclaimed.

1. The storage policy failed because ending free space was sampled immediately
   after `simctl delete`.
2. `simctl delete` removed the device identity before background filesystem
   reclamation completed.
3. The governor modeled cleanup as synchronous.
4. The first integration tests checked deletion success and lease release but
   not delayed free-space recovery.

The correction keeps the strict growth policy and adds a bounded stabilization
phase after all run-owned cleanup. It samples until free space remains within a
small delta for three observations or the timeout expires. A unit test simulates
delayed reclamation and requires the minimum-space measurement to remain intact.

## Final Review Follow-Up

Final diff review found that exceptional exits finalized only the storage lease,
not the public verification receipt; finalization retries could not recover the
first receipt; and failed simulator deletion erased the device identifier.

1. Failure-path evidence was incomplete because normal result assembly occurred
   only after all lifecycle stages returned.
2. Finalization was not retry-safe because the active lease was deleted without
   retaining its immutable completion receipt.
3. Simulator recovery data was lost because cleanup cleared identifiers
   regardless of the delete result.
4. Static contract tests checked command presence but did not exercise these
   failure transitions.

The corrections route normal and exceptional exits through the same result
writer, atomically retain completed receipts for idempotent reads, and keep a
failed simulator identifier as an attributed retained resource. Regression tests
require retry-safe finalization and failure-path result assembly. Review also
found that boot state had been used to choose a source simulator even though the
verifier creates a fresh device; selection now prefers the newest installed iOS
runtime, with a multi-runtime test.

## CI Reclamation Plateau Follow-Up

The first pull-request run completed all Xcode work and deleted its run-owned
state, but failed the 64 MiB unknown-growth policy with 129,748,992 bytes still
pending reclamation.

1. The receipt finalized while shared filesystem free space was on a short
   stable plateau after simulator deletion.
2. Settlement treated three samples within 4 MiB as sufficient regardless of
   elapsed time.
3. That rule detected momentary stability, not completion of delayed
   CoreSimulator reclamation.
4. The delayed-reclamation test modeled changing samples but not an early stable
   plateau.

The correction requires both stable samples and a 15-second minimum observation
window while retaining the 60-second hard timeout and strict 64 MiB policy. A
deterministic test holds free space stable for the first three samples and proves
that settlement continues until the minimum window is reached.

## Post-Merge Recovery-Target Follow-Up

The pull-request check passed with the minimum observation window, but the
merged-main check later failed with 664,276,992 bytes of unknown persistent
growth after the same 15-second window.

1. Main failed because settlement finalized while free space remained well below
   the successful-run policy envelope.
2. It finalized because the samples were stable after the minimum wait.
3. Stability only proves that free space is not changing at that moment; it does
   not prove that asynchronous reclamation has reached the required target.
4. The first correction delayed evaluation but retained stability as the success
   criterion.
5. Tests covered an early stable plateau but did not require the plateau to be
   within the permitted persistent-growth envelope.

The correction derives a minimum available-space target from starting capacity,
attributed retained bytes, and the declared growth tolerance. Settlement can
complete before its timeout only when samples are stable, the minimum observation
window has elapsed, and that target is met. A deterministic test proves that a
stable plateau below target does not finalize. Timeout remains fail-closed through
the unchanged finish policy.

The target-based pull-request run exhausted the full 60-second settlement period
and still reported 227,233,792 bytes of aggregate growth. Together with prior
hosted observations of 129,748,992 and 664,276,992 bytes, this disproved delayed
reclamation as the complete explanation.

1. Hosted verification remained red because aggregate APFS free space did not
   return within the local 64 MiB measurement tolerance.
2. The aggregate includes runner-wide Xcode, CoreSimulator, and filesystem state
   outside the exact factory-owned roots.
3. The governor intentionally does not delete or claim ownership of those global
   stores, and aggregate free space cannot assign their changes to one owner.
4. The same provisional tolerance was applied to local and clean hosted-macOS
   environments before hosted variability had been measured.
5. Qualification initially had no repeated hosted observations from which to set
   an environment-specific measurement bound.

The hosted policy gate now declares a provisional 768 MiB tolerance, covering
the observed 664 MiB maximum with bounded margin while preserving the local
64 MiB default. The receipt continues to expose all unknown growth. A workflow
test pins the bound and its stopping rule: another exceedance requires external-
owner directory instrumentation, not another tolerance increase.

## 2026-09-25 Hosted Storage Recurrence

PR #92 run `36171964484` passed public-evidence validation, 68 Python tests,
build, unit tests, iPad build, analysis, archive, and run-owned simulator cleanup.
The Factory policy gate then failed closed because `908771328` bytes of unknown
persistent growth exceeded the unchanged `805306368`-byte hosted tolerance. The
independent iPhone and iPad jobs passed.

1. Why did the policy gate fail? Aggregate filesystem free space remained
   `908771328` bytes below its starting value after cleanup and bounded
   settlement.
2. Why was the growth classified unknown? The receipt attributes only exact
   factory-owned retained artifacts; this successful run retained none.
3. Why could the prior 768 MiB bound not accept it? The new observation exceeded
   the bound by `103464960` bytes, and the existing recurrence contract forbids
   another increase without attribution.
4. Why was attribution unavailable in the failed run? CI retained the aggregate
   receipt but did not capture before and after allocated bytes for external
   Xcode and CoreSimulator directory classes.
5. Root cause supported by runs `36171964484` and the earlier observations:
   aggregate APFS drift can exceed the provisional hosted measurement bound, but
   the policy job lacked bounded external-owner measurements needed to separate
   known directory-class growth from unexplained filesystem change.

Issue #93 adds read-only before and after measurements for fixed user Xcode,
user CoreSimulator, and system CoreSimulator classes. Public artifacts contain
only fixed identifiers, state, and byte counts. The comparison reports signed
and positive deltas but does not convert them into approved persistent bytes,
delete global state, or change either storage tolerance.

### Attribution Trust Review Correction

1. Why could the first instrumentation draft measure outside its fixed class?
   It rejected a symlink only at the final root component.
2. Why was that insufficient? A parent component could be a symlink, and a root
   could be replaced between the check and `du` traversal.
3. Why did initial tests not detect this? They mocked measurement and asserted
   output redaction without exercising component containment.
4. Why is a byte count still a trust concern? Publishing it under a fixed class
   would falsely claim that an unallowlisted target belonged to that class, even
   though no names or contents were emitted.
5. Root cause supported by the independent review: output redaction was treated
   as sufficient without binding traversal to stable, non-symlinked components.

The correction opens every path component relative to the previously bound
directory descriptor with `O_NOFOLLOW`, then counts allocated blocks through
descriptor-relative traversal. Child identity must match the entry inspected
before traversal; symlinks are counted but never followed. Tests cover exact
roots, ancestor symlinks, descriptor traversal, schema typing, and redacted OS
and parse failures. Attribution has a dedicated artifact upload that fails closed
when the comparison file is missing.

### Attribution Boundedness Review Correction

1. Why could the first descriptor-relative traversal fail on a wide tree? It
   opened every discovered child before processing the traversal frontier.
2. Why did that threaten the evidence artifact? Open descriptors scaled with
   sibling count and could reach the process limit before comparison completed.
3. Why did initial containment tests not detect it? They exercised a small tree
   and checked containment rather than descriptor pressure.
4. Why was cleanup alone insufficient? Closing the frontier after failure avoids
   a leak but still leaves the required attribution unavailable.
5. Root cause supported by the independent review: descriptor binding solved the
   path race without initially preserving the bounded-resource behavior of a
   depth-first filesystem walk.

The correction processes one child subtree at a time, so open descriptors scale
with depth rather than width. A deterministic 100-sibling test tracks opens and
closes, requires zero retained descriptors, and caps concurrent descriptors at
two for that one-level tree.

### Hosted Attribution Capture Failure

Run `36176741252` failed both external-storage snapshot steps before template
verification. The dedicated upload then failed because no comparison artifact
existed; the separate device jobs were unaffected.

1. Why was no attribution artifact produced? Baseline and after-snapshot commands
   each exited when at least one allowlisted external class could not be measured.
2. Why did one class prevent the whole receipt? Measurement access and live-tree
   traversal errors were treated as command-fatal rather than class state.
3. Why was that too strict for external-owner roots? The Factory intentionally
   has no authority to normalize permissions or stop concurrent Xcode and
   CoreSimulator mutation in those directories.
4. Why must the job not silently accept those errors? Missing measurements are
   actionable evidence and must not be converted into zero growth or approved
   persistent bytes.
5. Root cause supported by the two failed capture steps and missing-file upload
   annotation: expected external-root unavailability was conflated with a
   malformed attribution receipt.

The correction emits `unavailable` with one of two fixed, path-free reasons and
`null` allocated bytes for that class. Comparison reports a `null` delta and
excludes the class from aggregate measured growth. Unknown schema, identifiers,
states, reasons, and values still fail closed, while the existing aggregate
storage policy remains unchanged and authoritative.

### Unavailable-State Test Correction

1. Why did the first local suite after this correction fail? The ancestor-
   symlink test still expected measurement to raise an exception.
2. Why was that assertion stale? Symlink rejection now maps to the same explicit
   unavailable class state as other unsafe root-open failures.
3. Why was the stale assertion not updated with the implementation? The initial
   edit updated generic open/traversal error coverage but missed the earlier
   dedicated ancestor-symlink case.
4. Why did this not reach another hosted run? The full local suite failed before
   commit and push.
5. Root cause supported by the single failed assertion: the contract migration
   from command-fatal to class-unavailable was not applied to every existing
   test case in one edit.

The ancestor-symlink test now requires the exact fixed `root_open_failed` state,
`null` bytes, and no path-bearing value. The full-suite gate remains the
mechanical recurrence guard before publication.

### Malformed-Type Review Correction

1. Why could a malformed receipt print a source-bearing traceback? Array or
   object `state` and `reason` values reached set membership before type checks.
2. Why did that bypass fixed validation errors? Python raises `TypeError` for an
   unhashable membership operand, while the CLI catches only expected parse,
   validation, and filesystem errors.
3. Why did existing malformed tests not detect it? They covered unknown strings,
   duplicate keys, and boolean schema versions but not unhashable field types.
4. Why is this relevant when CI creates the snapshots? Comparison accepts files
   as inputs, so malformed or replaced evidence must remain privacy-safe.
5. Root cause supported by the review: value-domain validation was performed
   before primitive-type validation for two enum fields.

The validator now requires string enum values before membership checks. Tests
cover unhashable state and reason values and an all-unavailable comparison whose
zero aggregates remain qualified by `measured_class_count: 0` and null deltas.

### Hosted Concurrent-Traversal Recurrence

PR #98 run `36189352038` passed portfolio validation, Python tests, all template
build/test/archive steps, and independent iPhone and iPad jobs. The policy gate
failed closed on `865488896` unknown persistent bytes against the unchanged
`805306368`-byte tolerance. Its attribution receipt measured zero growth in the
available classes, but `coresimulator_system` was unavailable with
`traversal_failed` before and after.

1. Why did the policy gate fail? Unknown persistent growth exceeded the unchanged
   hosted tolerance after successful run-owned cleanup and settlement.
2. Why did attribution not classify the excess? The system CoreSimulator class
   did not produce a complete before or after measurement.
3. Why was that class unavailable? A descriptor-bound traversal raised an
   `OSError` and failed the entire class safely; the path-free receipt does not
   distinguish concurrent mutation, permissions, I/O, or another traversal cause.
4. Why could a potentially transient traversal error blind the full class?
   Measurement attempted one complete traversal and had no bounded fresh-root
   retry.
5. Root cause supported by run `36189352038`: fail-closed unavailable-state
   handling preserved trust, but the read-only measurement contract had no
   bounded way to recover from a potentially transient error while still
   requiring a complete stable sample.

Issue #100 retries the complete traversal at most three times, reopening the
exact allowlisted root for each attempt and retaining all descriptor and
`O_NOFOLLOW` containment. A failed partial traversal is never counted. Exhausted
attempts, or disappearance after a failed traversal, remain path-free
`traversal_failed` evidence. Tests pin retry success, exhaustion, disappearance,
and the unchanged unavailable-state semantics. Storage tolerances, global state,
and automatic approval of measured bytes remain unchanged.
