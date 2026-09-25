# Factory Dev Path Fixture Failure

Date: 2026-09-24
Scope: issue #69 focused tests

## Evidence And Whys

1. The target-safety and launch tests failed because expected fixture paths used
   `/var/...` while `factory-dev` correctly emitted canonical `/private/var/...`.
2. The forms differed because macOS exposes `/var` through a system symlink.
3. The fixture retained `tempfile`'s lexical path instead of resolving it before
   constructing expected values and child targets.
4. The production launcher deliberately resolves paths before receipts and
   execution, so weakening it would have reduced the requested safety control.
5. Supported root cause: the test fixture did not share the launcher's canonical
   path invariant. No evidence indicates a production path-resolution defect.

Immediate and root-cause correction: canonicalize the temporary fixture root at
creation. Recurrence guard: the launch test compares the executed target with
that canonical root, while the separate symlink test must still fail closed.
