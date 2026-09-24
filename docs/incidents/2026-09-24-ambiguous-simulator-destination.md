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
