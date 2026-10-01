# Analyzer Outcome Correction

Tracker: `edoworks/factory#121`
State: locally implemented and focused-verified; integration and closeout pending.
Baseline: `0ff8117a75882a656aa20451e5c21244a3910b28`.
Authority: owner requested the analyzer correction first, implementation, and
validation; canonical progress writes were explicitly authorized.

## Implementation And Evidence

The baseline suppresses analyzer failure with `|| true`, then records a pass in
both warning branches. The correction tests the actual analyzer exit status,
preserves successful warnings as advisory, and writes combined raw diagnostics
to `static-analysis.log` under the existing run-owned root. Failed analysis
increments the existing failure count and therefore retains the root and exits
nonzero. A log-creation failure also fails rather than asserting a successful
analysis or a retained log that was never created. No timeout mechanism or
signing/distribution behavior was added.

The executable regression fixture copies the actual verifier into a private
temporary factory and supplies controlled storage, simulator selection, xcrun,
and xcodebuild tools. Apple-tool doubles reject unknown first operations. A
preexisting fixture project avoids generation. The child environment has a
private HOME and a fixed PATH; no credentials or provider calls are needed.
Storage calls and their final outcome/retained root are checked independently.
Only the fixture's own temporary state is cleaned.

- The construction agent's first reported before-run was not reliable: a missing
  iPad fixture produced a skip counted as failure, masking analyzer attribution.
  That report is not used as the definitive reproduction evidence.
- Historical replay reads the exact retained baseline Git object and uses the
  same corrected tools as the current test. Analyzer exits 65, 124, 137, and 143
  incorrectly produce a zero overall exit, a static_analysis pass, and PASSED
  storage outcome in that unchanged baseline.
- The corrected matrix covers successful clean output, successful warnings,
  nonzero errors, nonzero warnings, empty failure output, and timeout-/signal-
  style statuses. It checks nonzero overall failure, retained raw stdout/stderr,
  successful cleanup, and exact storage outcome.
- An additional case makes the log path a directory, proving that the analyzer
  is not invoked and log-creation failure cannot become a pass.
- Focused command: `python3 -m unittest discover -s tests -p test_factory_verify.py -v`.
  Three test methods passed, covering 13 scenarios; historical replay was not
  skipped. All Apple operations were doubles, not actual compilation or devices.

Historical replay is supplemental: it explicitly skips when the baseline Git
object is unavailable, while all current-verifier cases still run. Existing CI
checks out full history. No network fetch is performed by that test.

## Broader Validation And Limits

- Registered issue-121 workspace creation succeeded and initial status was
  clean. Doctor reported valid policy, no integrity errors, and admitted
  workspace binding. Stale routing evidence blocks development launcher
  readiness; the launcher was not started and routing was not changed.
- Full Python run: 101 tests, 99 passed, two failed. The failures are installed
  user-profile versus captured baseline, and generated user catalog versus
  tracked catalog. Both assertions remain intact; no baseline/catalog was
  rewritten to force a pass.
- Full Node run: 17 passed and one test-file load failed because the fresh
  workspace lacks declared `@opencode-ai/plugin`. No package installation,
  source-copy workaround, or dependency stub was used to force that suite green.
- `git diff --check` passed. Independent review found no scoped implementation
  defect; it initially noted the missing redirection-failure case, subsequently
  added and passed.
- Final follow-up checks passed: 18 storage/lifecycle tests, 11 single-factory
  contract tests, policy-manifest consistency, and the Node continuation test.
  Independent follow-up confirmed the new failure case and found no substantive
  finding. These focused checks do not turn the broad-suite failures green.
- Real Apple compilation, physical-device behavior, runtime autonomy, hosted
  checks, integration, a published factory correction, and issue closeout are
  not demonstrated. Published releases and app locks were not modified.
- Completion notification remains unadmitted by the loaded user-only policy;
  no alternate wrapper or delivery claim is made. This belongs to complete
  startup admission, not an analyzer permission expansion.

## Evidence-Bounded 5-Whys

1. Why could verification pass after analyzer failure? Nonzero status was
   discarded and both output-classification branches recorded a pass.
2. Why was warning text treated as success evidence? The gate classified output
   instead of requiring successful execution before interpreting diagnostics.
3. Why did the existing failure counter not catch it? Only recorded failures
   contribute to the final nonzero verifier outcome.
4. Why did tests not detect it? The prior lifecycle tests checked storage and
   simulator failures but did not exercise analyzer exit statuses end to end.
5. Supported root cause: execution success and advisory diagnostics had no
   separate mechanically tested contract. Earlier author intent is unknown.

Recurrence guard: execute the actual verifier with controlled tools, require all
non-analysis operations to succeed, inspect analyzer and overall outcomes, and
check storage retention and unmodified raw diagnostics. Exit 124 is tested as a
failure status, not proof of a real timed-out Xcode process.

## Verification-Failure Causes And Guards

The first harness failure came from treating an absent iPad as harmless, while
the verifier counts skip as non-pass. The corrected fixture supplies both form
factors and asserts exact tool operations, failure count, and storage outcome;
historical and corrected runs now share that fixture. The before-run count was
corrected instead of promoted into proof.

The broad-suite failures depend on ambient installation state and missing
development dependencies, not analyzer case selection. Their recurrence guard
belongs to the existing self-service verification work: separate fixture-based
tests from installation qualification and preflight declared dependencies.
Do not refresh provider evidence or grant arbitrary package-manager execution
inside this analyzer correction.

Keep issue #121 open until required validation, independent review, applicable
integration/hosted checks, and canonical closeout are confirmed. No user terminal
repair is prescribed. Issue #111 and user-only issue #122 remain separate scopes.

## Diagnostics-Read Follow-Up

The next read-only review found a smaller false-clean case: suppressing grep
errors conflated a readable log with no matches and an unreadable/missing log.
A new controlled case removes only the fixture-owned log after the analyzer
returns zero. Before correction, that case returned zero overall instead of the
expected failure. The correction accepts grep statuses 0 and 1 as successful
diagnostic classification, and records a failure for operational errors above 1.
It explicitly reports that analysis succeeded but diagnostics could not be read.

The focused suite now passes four methods covering 14 scenarios: ten current
cases and four historical reproductions. Missing diagnostics retain the failed
run root without falsely claiming the missing file was retained. Independent
review found no finding in the follow-up code.

Recurrence analysis: an execution-status fix was followed by an output-reader
whose status was still discarded. The missing-log case was not in the original
matrix. The mechanical guard now tests analyzer execution, log creation, and log
reading independently; none can be promoted into a clean result from absent data.

The separate issue-111 candidate now has fixture-based profile/catalog tests;
its green suites do not imply that those changes are integrated into this
issue-121 worktree. No cross-worktree source or dependency copy was performed.

Integration preflight invoked the registered commit script with no arguments,
which cannot commit even if admitted. Loaded user-only command policy denied the
invocation before execution. Raw Git is not substituted because it would not
perform the registered workflow's atomic HEAD update. No staging, commit, push,
PR, merge, release, or closeout occurred.
