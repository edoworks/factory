# Release Consumption Validation

Tracking: edoworks/factory#124. Date: 2026-09-30.
Status: locally tested source candidate; not integrated, released or adopted.

## Observed Preflight

- macOS 26.6.2, build 25G83; Xcode 26.6, build 17F113.
- The runtime inventory lists iOS 26.5 build 23F77 as available. Availability is
  not a boot, app-behavior, minimum-OS or physical-device test.
- The observed available capacity was below the documented 8 GiB reservation
  plus 10 GiB recovery floor, even before other active reservations. No Apple
  build, VM provisioning, tool installation or cleanup was attempted.
- The inspected public release v0.1.0-rc3 reports immutable=false, prerelease=true,
  and an empty attached asset list. No source archive was executed.
- A clean issue workspace was admitted from canonical revision
  0ff8117a75882a656aa20451e5c21244a3910b28; unrelated dirty work was preserved.
- Frozen issue intent validation returned VALID. The issue was created after
  separate authorized identity inspection. The pinned readback helper could not
  run because FACTORY_DEV_GH was absent; direct read-only issue inspection was
  performed, but no helper MATCH receipt or closeout is claimed.

## Defect And Five Whys

The first implementation passed seven narrow test methods. Independent review
found that parsed JSON null could report contract_valid=true and malformed
resource fields could raise exceptions before a JSON failure receipt.

1. Why did null pass? The entrypoint skipped validation when a parsed document
   was None, then interpreted an empty error list as success.
2. Why was None skipped? The same value represented both JSON null and a failed
   load, rather than using the recorded parse errors to control validation.
3. Why did malformed fields crash? String/path checks recorded errors but later
   dictionary and graph operations still consumed the invalid values.
4. Why did the first suite miss this? It covered a valid fixture and selected
   helper-level failures, not a command-level malformed-input matrix.
5. Why could some negatives appear reassuring? Several tests supplied an
   unrelated manifest-hash mismatch that could mask a missing semantic check.

## Mechanical Guards

- New command-entrypoint tests construct correctly hashed malformed documents
  and require a nonzero result plus parseable false-authorization receipts.
- Regression tests were run before correction: 13 methods produced 15 failures
  and 6 errors, reproducing the review findings.
- Schema versions now require integer type, notices reference bundled inventory,
  resource/dependency duplicates fail, and malformed graph inputs are not used.
- Input documents are limited to 1 MiB; excessive parser nesting fails with a
  receipt. Error output retains total count and bounds individual messages.
- A nonrecursive standard-library topological check validates declared cycles.
- Tags validate syntax only; workflow approval and actual artifact provenance
  remain explicit independent prerequisites.

## Verification

- Corrected release-consumption suite: 16 test methods passed.
- Existing pure storage admission suite: 3 test methods passed.
- Existing canonical continuation contract: 1 Node test passed; the modified
  continuation's recorded SHA-256 was updated in its tracked policy manifest.
- Independent re-review found no remaining material offline-validation defect.
  Its documentation wording correction was applied: origins/licenses are declared,
  not verified licensing clearance.
- git diff --check passed for tracked changes. Full factory suites, hosted CI,
  rendered product review, release verification and app rebuilding were not run.
- Receipts always say release_verified=false and consumption_authorized=false.

## Continuation

Keep issue #124 open. Finish actual content/tool/configuration closure and bootstrap
qualification before proposing a release. Issue #112 separately owns storage
retention and cleanup; issue #123 owns protected maintenance entrypoint admission.
Do not lower the storage floor, change model routes, load this candidate as live
policy, or grant signing/publication authority to unblock qualification.

No commit, push, integration, publication, signing, device test or Apple submission
was performed. This is a development validation chunk, not the first delivery
milestone or a demonstrated autonomy report.

Skill currency: no new skill is extracted from this unfinished qualification
procedure. Its evolving contract and tests remain factory-owned source; a future
production procedure must be covered by a published release before adoption.
