# Template Verification CI Timeout

Date: 2026-09-25
Issue: [#81](https://github.com/edoworks/factory/issues/81)
Run: `36117730389`
Status: correction pending hosted verification

## Observation

PR #82's Factory policy gate passed syntax, cost-router, doctor, receipt, and all
53 Python tests. The `Verify template builds` step then reached its 8-minute
timeout while the first cold hosted `xcodebuild` invocation was still running.
The independent Mews & Woofs iPhone and iPad jobs passed. No template build or
test failure was reported before timeout.

## Evidence-Based 5-Whys

1. Why did the Factory policy gate fail? The template verification step reached
   its configured 8-minute action timeout.
2. Why did it reach the bound? The full `factory-verify` workflow had entered its
   first hosted `xcodebuild` but had not completed it before the action stopped
   the step at 8 minutes 13 seconds.
3. Why did one cold build consume the entire budget? Hosted simulator startup
   and Xcode build latency vary; the log showed destination discovery but no
   product error before termination. No deeper infrastructure cause is claimed.
4. Why was the budget fixed at 8 minutes? Issue #60 added a bounded duration and
   a test that pinned the literal, but no recorded cold hosted template run
   established that 8 minutes covered this serial build, unit-test, iPad-build,
   analysis, archive, cleanup, and settlement workflow.
5. Root cause supported by the workflow and run evidence: the duration contract
   guarded the presence of a timeout, not the sufficiency of that timeout for
   the declared hosted workload.

## Correction

- Increase only `Verify template builds` from 8 to 15 minutes, retaining the
  existing 25-minute Factory policy job bound.
- Keep the workflow fail closed. A product failure or a run exceeding the new
  bound still fails the required check.
- Update the contract test to pin the evidenced 15-minute step and 25-minute job
  relationship.

The change does not alter storage tolerance, product behavior, deletion state,
or release authority.
