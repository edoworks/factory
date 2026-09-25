# Continuation Guard Cutover Failure

Date: 2026-09-24
Tracking: issue #69
Status: corrected with a versioned recurrence guard

## Impact

After the global continuation command moved from sf0.8 to factory, the existing
test failed because it required the predecessor filename. The active command was
correct, but the guard itself would have pushed future repair back toward the
retired authority.

## Evidence And Whys

1. Why did validation fail? The command directory contained
   `continue-factory.md` while the test required `continue-sf08.md`.
2. Why did the test require a predecessor? Its assertion encoded the old
   repository identity rather than the invariant of one canonical continuation.
3. Why was that stale assertion not migrated with the command? The guard lived
   only in unversioned global configuration and was absent from the initial
   factory development manifest.
4. Supported root cause: command migration and recurrence-guard migration were
   not one atomic, versioned contract.

No evidence supports a fifth causal layer.

Immediate correction: update the installed guard to require the factory
command. Root-cause correction: keep the guard in factory source, derive its
command root from the versioned environment, and run it in CI beside the router
tests.
