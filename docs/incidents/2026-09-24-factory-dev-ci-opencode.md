# Factory Development CI OpenCode Dependency

Date: 2026-09-24

Tracker: `edoworks/factory#69`

Status: corrected pending CI verification

## Evidence

Pull request #71 run `36083584263` passed router tests and the product doctor,
then failed `test_doctor_receipt_fields_and_stable_policy_digest` because the
hosted runner did not have the optional `opencode` executable installed.

## Why Chain

1. Why did the unit test fail? It invoked `bin/factory-dev doctor` against the
   live checkout, where doctor correctly reports OpenCode absence as not ready.
2. Why did the test require host state? The happy-path test used the production
   executable lookup instead of the existing controlled fake executable.
3. Why was that not seen locally? The development machine has OpenCode 1.18.19
   installed, so the hidden dependency was satisfied.
4. Why did CI not install OpenCode? OpenCode is a factory-development tool, not
   a product-runtime or CI build dependency, and installing it would weaken the
   runtime/development separation.

Root cause supported by the run log: a unit test for deterministic receipt
behavior accidentally asserted workstation provisioning rather than launcher
logic.

## Corrections

- The receipt stability test now uses the isolated fixture and version-reporting
  fake executable used by launch tests.
- CI remains free of an OpenCode runtime dependency.
- The production doctor still fails closed when OpenCode is unavailable.

The same test now mechanically guards against reintroducing ambient workstation
dependency into this receipt assertion.
