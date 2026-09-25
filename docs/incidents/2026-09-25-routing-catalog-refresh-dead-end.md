# Routing Catalog Refresh Dead-End

Date: 2026-09-25

Tracker: `edoworks/factory#84`

Status: integrated by PR #85; exact issue-closeout helper verification pending

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
- Catalog and manifest writes use exclusive temporary files, a persistent
  SQLite mutex whose kernel lock is released on process death, and a separate
  durable SQLite journal that rolls back an interrupted two-file transition
  before policy validation resumes.
- The exact mutation is interactive, while deterministic focused tests remain
  constrained to the pinned Node runtime and tracked test list.

Independent review of the first implementation found that its in-process
rollback could not recover an abrupt termination, pathname reads followed
metadata checks instead of reading the checked inode, model identity types were
under-validated, and the output retained arbitrary source provider and variant
names.

1. Why could a crash strand the importer? Catalog and manifest renames were
   separate, while rollback state existed only in process memory.
2. Why could a checked source still be replaced? Metadata and content were read
   through separate pathname operations.
3. Why could malformed identity fields pass? String interpolation occurred
   before provider and model types were asserted.
4. Why could private names enter tracked evidence? Provider and variant arrays
   were copied from the broad generated catalog rather than projected from
   tracked policy and route references.
5. Why did the first tests miss these defects? They covered validation failures
   and ordinary rollback but did not model process interruption, inode
   substitution, malformed scalar types, or excess source metadata.

Additional root cause: the first correction treated an ordinary exception as
representative of a process crash and treated a generated catalog as trusted as
a whole rather than as an untrusted source for a minimal projection.

Independent re-review then found that filesystem stale-lock takeover remained
racy even after owner records and recovery claims were added.

1. Why could two recoverers overlap? A stale claim was removed and recreated by
   pathname rather than transferred through an atomic ownership primitive.
2. Why could inode checks not close that race? They checked the lock directory,
   while a competing process could replace the claim within the same directory.
3. Why could ownerless cleanup delete active work? Recursive removal resolved
   the lock pathname after inspection and could therefore target a replacement
   generation.
4. Why did additional lock files not solve ownership? Portable Node filesystem
   APIs provide exclusive creation but no conditional unlink by observed inode.
5. Why was the design changed instead of adding another claim protocol? Kernel
   SQLite locking releases ownership on process death without stale path
   deletion, while a separate committed database preserves recovery state.

Additional root cause: a removable filesystem pathname was being used both as
the ownership primitive and as crash-recovery data, although those concerns
require different durability and lifecycle semantics.

## Mechanical Recurrence Guard

- Node tests reject stale, malformed, failed-provider, incomplete-provider,
  missing-built-in, incapable, and rollback source evidence and assert that
  rejected input does not change catalog or manifest files.
- The Factory launcher test imports a fresh generated fixture over a stale
  tracked catalog, validates the new manifest digest, and requires doctor to
  become launch-ready.
- General launcher fixtures refresh both benchmark and catalog times, preventing
  wall-clock expiry from obscuring the tested readiness condition.
- Import tests require file-descriptor reads of regular non-symlink sources,
  strict active-model identity types, and exact manifest digests for the
  registry, policy, and current catalog.
- Recovery tests interrupt the importer between catalog and manifest replacement
  and require the committed journal to restore the old pair. A second recoverer
  must fail while the first importer holds the SQLite write transaction, and the
  persistent coordination directory is never treated as removable lock state.
- Snapshot tests require provider names to come from tracked policy and variants
  to come from tracked route references, preventing generated private metadata
  from entering repository evidence.

No benchmark, route, provider, budget, credential, or fallback policy change is
authorized or made by this correction.
