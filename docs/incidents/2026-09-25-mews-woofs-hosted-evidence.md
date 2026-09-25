# Mews & Woofs Hosted Evidence Timeout And Packaging Race

Date: 2026-09-25
Issue: [#99](https://github.com/edoworks/factory/issues/99)
Run: `36184422124`
Job: `108234873235`
Status: correction pending hosted verification

## Observation

PR #98's independent iPhone job reached the exact 15-minute `Verify reference
app` bound while UI tests were still passing. The always-run evidence upload then
enumerated the live `.xcresult`, but a diagnostics file disappeared before zip
creation completed, so `actions/upload-artifact@v4` failed with `ENOENT`. The
Factory policy and iPad jobs passed. No iPhone test assertion failure was shown.

## Evidence-Based 5-Whys

1. Why did the iPhone job fail? Verification reached its step timeout, and the
   subsequent evidence upload also failed.
2. Why did verification time out? Cold hosted simulator startup and execution
   consumed the complete 15-minute bound while passing UI tests were still in
   progress.
3. Why was that bound insufficient? The prior independent bound was established
   from a correction run that completed in 5 minutes 28 seconds, not from a
   demonstrated upper bound across recurring hosted startup variability.
4. Why did evidence upload fail after timeout? The uploader enumerated a live,
   interrupted `.xcresult` directory while Xcode-owned staging diagnostics were
   still changing, and one enumerated file disappeared before compression.
5. Why could one hosted variation produce both failures? The workflow had finite
   independent execution bounds but lacked evidenced headroom for a repeated cold
   run and uploaded a mutable result directory rather than a completed archive.

The evidence establishes workflow orchestration and packaging defects. It does
not establish an application test defect or explain the underlying hosted
simulator startup variability.

## Correction And Recurrence Guard

- Increase only the independent reference-app step from 15 to 20 minutes and its
  job from 20 to 30 minutes. The ten-minute bound difference contains setup plus
  packaging; the failed run's observed non-verification job time was under one
  minute, but corrected hosted execution remains required evidence.
- Preserve separate iPhone and iPad jobs and all existing tests.
- Run evidence packaging under `if: always()` after verification and create a
  completed `.xcresult.zip` with `ditto` before artifact upload.
- Upload only the immutable archive with `if-no-files-found: error`; packaging or
  missing evidence remains a hard job failure.
- Pin exact bounds, source-to-archive packaging, package-before-upload ordering,
  and fail-closed upload behavior in the workflow contract test.

## Verification

- Frozen issue #99 intent validates locally and remote readback matches exactly.
- PR #98, the Factory PRD portfolio section, the cutover portfolio section, and
  issue #78 received bounded rendered review before correction.
- Full local suites, independent review, corrected rendered records, and hosted
  policy/iPhone/iPad checks remain required before closeout.

## Local Timeout-Edit Failure 5-Whys

1. Why did the first corrected full Python run fail? The workflow still gave the
   reference job 25 minutes while the unrelated policy job had changed to 30.
2. Why were the values applied to the wrong jobs? A value-oriented patch matched
   the first `timeout-minutes: 25` occurrence instead of the named
   `reference-app` block.
3. Why did review not prevent the placement mistake? The correction was applied
   after review findings and was not yet re-read as a complete workflow.
4. Why did the mistake not reach hosted CI? The full local suite ran before commit
   or push and the policy/reference assertions disagreed with the edited file.
5. Root cause supported by the failing assertion: the mechanical edit lacked
   job-specific context, while the repository contract correctly treated each
   job timeout as an independent invariant.

The correction restores the policy job to 25 minutes and sets only the
reference-app job to 30. Exact named-job timeout assertions remain the mechanical
recurrence guard and must pass before publication.
