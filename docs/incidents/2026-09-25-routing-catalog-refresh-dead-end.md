# Routing Catalog Refresh Dead-End

Date: 2026-09-25

Tracker: `edoworks/factory#84`

Status: corrected pending integration and fresh-session verification

## Evidence

Factory doctor at revision `2f1a5ecd04344957f794b949f5e215b5d37e4b44`
reported the tracked catalog stale and refused launch. The approved user catalog
had been refreshed as generation `1790335243580-66796` at
`2026-09-25T11:20:43.573Z`, but Factory had no repository-owned import command.
The global refresh command was not admitted by the already-loaded shell policy.

The fresh catalog also omitted `opencode/x-preview-f-free`, which remained an
approved startup fallback and specialty route. Carrying its old `active` record
forward under the new generation would have created false availability evidence.

## Why Chain

1. Why could a healthy generated catalog not restore launch readiness? Factory
   consumed an expiring tracked snapshot but exposed no command to import a new
   generated snapshot.
2. Why was the global refresh procedure insufficient? Factory launch isolates
   user configuration, and its deny-by-default shell policy did not admit the
   global package command.
3. Why could a new Factory session not perform the repair? Doctor requires route
   readiness before launch, while the only documented refresh procedure assumed
   an already running configured session.
4. Why was manually advancing `refreshed_at` unsafe? The newer source changed
   observed route availability; a timestamp-only edit would preserve a stale
   active fallback claim.
5. Why did verification not prevent the dead-end? Tests refreshed benchmark
   fixture time but inherited the tracked catalog time, so they covered stale
   rejection without a tested recovery transition.

Root cause: catalog expiry was enforced as a launch prerequisite without a
pre-launch, repository-owned, provenance-checking transition for generated
catalog evidence.

## Corrections

- `bin/factory-dev refresh-catalog` first validates repository integrity and
  permits no routing contradiction other than stale catalog evidence.
- The importer reads only the fixed approved user-catalog path, rejects stale,
  older, malformed, incomplete-provider, or failed-provider input, and requires
  every built-in primary route to remain capable.
- The tracked snapshot copies only non-secret route fields. Referenced optional
  models absent from the generation are recorded as `missing`, never inherited
  as active.
- Catalog and manifest writes use exclusive temporary files, rollback ordinary
  write failures, and leave crash interruption fail-closed on digest mismatch.
- The exact mutation is interactive, while deterministic focused tests remain
  constrained to the pinned Node runtime and tracked test list.

## Mechanical Recurrence Guard

- Node tests reject stale, malformed, failed-provider, incomplete-provider,
  missing-built-in, incapable, and rollback source evidence and assert that
  rejected input does not change catalog or manifest files.
- The Factory launcher test imports a fresh generated fixture over a stale
  tracked catalog, validates the new manifest digest, and requires doctor to
  become launch-ready.
- General launcher fixtures refresh both benchmark and catalog times, preventing
  wall-clock expiry from obscuring the tested readiness condition.

No benchmark, route, provider, budget, credential, or fallback policy change is
authorized or made by this correction.
