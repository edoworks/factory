# Mews & Woofs CI Form-Factor Timeout

Date: 2026-09-25
Issue: [#70](https://github.com/edoworks/factory/issues/70)
Run: `36092353434`
Status: correction pending hosted verification

## Observation

PR #73's Factory policy gate timed out while verifying the Mews & Woofs
reference app. The iPhone unit and UI suites had already passed all 11 tests;
the iPad build began but did not reach test execution before the shared step's
12-minute timeout.

## Root-Cause Analysis

1. The gate failed because the reference-app step reached its 12-minute timeout.
2. It reached the timeout because two full simulator test runs executed serially
   within that single budget.
3. The first run consumed 588.637 seconds, leaving less than two minutes for the
   second build and test run.
4. The first run was slow because its tests did not begin until more than nine
   minutes after `xcodebuild` started on the cold hosted simulator; once running,
   all 11 tests passed in under one minute.
5. The workflow coupled two independent form-factor checks to one serial timeout
   instead of bounding and reporting them independently. Prior passing evidence
   established correctness but did not establish a safe cold-run serial bound.

The evidenced root cause is CI orchestration, not an application test failure.
Hosted simulator startup variability is a contributing factor. The evidence
does not identify why this particular hosted simulator took nine minutes to
start, so no deeper infrastructure cause is claimed.

## Corrections

- Immediate: run iPhone and iPad verification as separate matrix jobs so one
  cold simulator cannot consume the other form factor's execution budget.
- Root cause: give each form factor its own 15-minute step timeout and 20-minute
  job timeout while retaining fail-closed results for both jobs.
- Recurrence guard: preserve and upload a distinct result bundle for each matrix
  job; either form factor failing or exceeding its independent bound fails CI.

## Evidence

- Run `36092353434`: the iPhone `xcodebuild` reported 588.637 seconds elapsed.
- Six unit tests and five UI tests passed with zero failures on iPhone.
- The iPad invocation began at 04:11:00 UTC; the shared step timed out at
  04:12:52 UTC while still building its test runner.
