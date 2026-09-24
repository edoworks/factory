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
