# OpenAI OAuth API-Key Collision

Date: 2026-09-25
Tracker: `edoworks/factory#101`
Status: correction integrated; closeout evidence pending integration

## Evidence

A user-provided OpenCode screenshot showed OpenAI rejecting a submitted,
masked API-key-shaped credential as an incorrect API key. The user confirmed
OpenCode was connected through the browser and explicitly chose OAuth-only
behavior for the Factory launcher. The screenshot does not establish whether the
key came from the inherited environment or saved OpenCode credentials; neither
secret source was inspected or published. `bin/factory-dev` stripped inherited
`OPENCODE_*`, GitHub, and Node overrides, but passed `OPENAI_API_KEY` through to
the OpenCode child. Doctor validated route and policy readiness, not credential
selection or a successful OAuth request.

## Five Whys

1. Why did the request fail? OpenAI rejected a submitted API-key-shaped
   credential rather than processing an OAuth-backed request.
2. Why was that credential eligible for a Factory launch? The launcher passed
   inherited `OPENAI_API_KEY` through to OpenCode.
3. Why did an OpenCode browser connection not rule it out? The launcher did not
   isolate the OpenAI provider credential environment, and the screenshot cannot
   distinguish environment input from a saved API-key connection.
4. Why did doctor not catch the mismatch? Its readiness checks cover tracked
   policy, routing evidence, and installation, but do not exercise credential
   selection or call OpenAI.
5. Why did this boundary go untested? Launch contract tests pinned GitHub,
   OpenCode, and Node overrides but not the inherited OpenAI API-key variable.

The evidenced trust gap is that an API-key-shaped credential can reach a
Factory OpenAI route without a launcher guard. It is not evidence that the
particular rejected key originated in the inherited environment.

## Guard And Limits

The Factory launcher drops inherited `OPENAI_API_KEY` before both its OpenCode
version probe and the final child execution. The fake-OpenCode launch test
asserts only that the variable is absent and never prints its value. This change
does not read, clear, or replace saved credentials, change route choice, modify
provider budgets, or promise OAuth success. If the error persists in a fresh
launch, inspect only credential type through approved OpenCode controls and
reconnect with `/connect` -> OpenAI -> ChatGPT Plus/Pro interactively; never
paste a key or token into repository evidence.

## Verification State

The guard has been extracted onto a clean branch from canonical merge `0e36c03`.
The frozen intent validates, remote issue readback returns `MATCH`, `git diff
--check` passes, and independent trust review found no material issue. After the
invocation correction below, the full Python and pinned Node suites passed from
the isolated repository root. Factory doctor reports valid policy, matching
active installation, no routing contradiction, and `launch_ready: true`. Exact
rendered review of issue #101, PR #106, the PRD paragraph, and both incident
Five-Whys sections passed at implementation head `2a914b9` without clipping,
unreadable wrapping, or exposed credential material. PR #106 merged final head
`61e0565` as `28edd62`; hosted run `36219860937` passed the Factory policy,
iPhone, and iPad jobs. A fresh launch from merged canonical `main` reported
revision `28edd62` and `launch_ready: true`, and the owner completed one
OAuth-backed request without exposing credential material. This proves the
accepted request path in that fresh launch, not the stored credential's internals
or every future request. Repository closeout integration and issue-state
verification remain required before completion.

## Clean-Worktree Verification Invocation 5-Whys

1. Why did the first isolated Python run report one import error after 64 passing
   tests? It was launched from the unrelated `sf0.8` directory, so the Factory
   repository root was absent from Python's module search path.
2. Why did an absolute test-suite path not prevent that? Unittest discovery
   selected the tests but did not change the process working directory used by
   repository-root imports.
3. Why did the first isolated Node run report one missing package after 15
   passing tests? The clean worktree correctly excluded generated `node_modules`
   and had not restored its lockfile-bound development dependencies.
4. Why were both prerequisites omitted? The external verification instruction
   listed test executables but did not reproduce the hosted workflow's repository
   root and dependency-install order.
5. Why is this not accepted as product evidence? Partial passing output does not
   satisfy either full suite; both commands failed closed before integration.

The correction is to run verification from the isolated repository root and run
`npm ci --prefix development/opencode` before the pinned Node suite. The
mechanical recurrence guard is the hosted workflow and its contract test, which
require that exact lockfile-bound install before the Node command while CI runs
Python from the checkout root. Local acceptance must reproduce the same order;
the failed receipts are retained and no pass is claimed from them. The corrected
rooted rerun passed both full suites.
