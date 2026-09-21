# Clean-Runner Lifecycle Verification Defect

Date: 2026-09-20
Tracking: https://github.com/edoworks/factory/issues/25
Trigger: https://github.com/edoworks/factory/actions/runs/35549122335

## Impact

The first public factory pull request failed in `factory-doctor` before it
emitted evidence. This invalidated the earlier clean-runner and release-readiness
claims until corrected and reverified.

## Root Cause

1. CI stopped because `factory-doctor` exited before emitting its receipt.
2. Version commands used early-closing pipelines under `set -o pipefail`, so a
   producer could terminate non-zero instead of becoming evidence.
3. The workflow had not exercised this path on a clean hosted runner before the
   release candidate was described as ready.
4. The workflow also assumed xcodegen was installed even though it is a declared
   dependency rather than part of Xcode.
5. Verification relied on a configured founder workstation instead of the
   declared public environment.

The failed log does not identify which version process returned exit 134. The
pipeline design and absent clean-runner proof are evidenced; a more specific
process-level cause would be speculation.

## Corrections

- Remove early-closing version pipelines from doctor.
- Install xcodegen explicitly in CI before doctor.
- Syntax-check every lifecycle shell script.
- Validate the doctor JSON receipt mechanically.
- Fix the invalid `pipeflag` option in `factory-uninstall`.
- Produce an unsigned archive in CI; distribution signing remains a separate
  human-authorized gate.
- Reject app names containing spaces or path separators before template
  substitution; callers choose the destination through their working directory.
- Mark XCUITest classes `@MainActor` so the template compiles under Swift 6
  strict concurrency on hosted runners as well as the founder workstation.

## Recurrence Guard

The public workflow must pass on the hosted macOS runner before future
clean-install or release-readiness claims. Local success is insufficient.
