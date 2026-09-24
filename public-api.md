# Public API — Edoworks Factory v0.1.0

The factory's public API is one opinionated journey:

```
download release → factory doctor → factory init → confirm PRD →
implement bounded increment → factory verify →
release evidence → human-authorized Apple submission
```

## Commands

### factory doctor

Verify toolchain readiness. Checks Xcode, Swift, Git, xcodegen, simulators,
and whether the default verification workload fits above the configured storage
recovery floor. Produces a JSON evidence receipt on stdout.

```
factory doctor
```

Exit codes:
- 0: All checks passed
- 1: One or more checks failed

### factory init

Scaffold a new iOS app from the factory template.

```
factory init <app-name> [--bundle-id com.example.app]
```

Creates a new directory with:
- SwiftUI universal app (iPhone + iPad)
- xcodegen project.yml
- PrivacyInfo.xcprivacy
- Unit and UI test targets

### factory verify

Run build, tests, static analysis, and archive on the current app.

```
factory verify [--retain-archive]
```

Must be run from the app root directory (where project.yml lives).

Steps:
1. Build on iPhone simulator
2. Unit tests
3. Build on iPad simulator
4. Static analysis
5. Archive (requires development team config)

Before Xcode starts, verification atomically reserves its maximum storage
budget. Build state and the unsigned archive use a run-scoped
`.factory/runs/<run-id>/` directory. Verification creates uniquely identified
run-owned simulators from installed device types and retires those devices
through `simctl`, avoiding mutation of a developer's existing simulator data.
A successful ordinary run removes its reproducible state; a failed or
interrupted run preserves and reports filesystem state for diagnosis while
still retiring run-owned simulator devices. `--retain-archive` promotes the successful archive to
`.factory/artifacts/archives/` instead of deleting it.

CoreSimulator and APFS may reclaim deleted state asynchronously. Verification
waits for a bounded period of free-space stability after cleanup before it
classifies persistent growth; it never converts a timeout into a cleanup claim.

Produces a JSON evidence receipt (`.factory-verify-result.json`) containing
starting, minimum, and ending free space; peak and persistent consumption;
reservation and recovery-floor bytes; reclaimed bytes; owned roots; and
retained artifacts.

The provisional defaults are an 8 GiB verification reservation and 10 GiB
recovery floor. They are based on an observed 2.4 GiB single-destination XCTest
peak plus build/archive margin and remain configurable while qualification
collects representative peaks:

```bash
FACTORY_VERIFY_MAX_GIB=8 FACTORY_RECOVERY_FLOOR_GIB=10 factory verify
```

APFS and Xcode may change shared host state while run-owned paths are removed.
The receipt therefore reports unknown growth separately and applies a
provisional 64 MiB measurement tolerance, configurable with
`FACTORY_STORAGE_GROWTH_TOLERANCE_MIB`. Growth above that bound fails the
verification storage policy instead of being hidden by cleanup.

The hosted-macOS policy gate declares a separate provisional 768 MiB tolerance
because aggregate APFS free-space observations across three clean runners varied
by 129, 664, and 227 MiB after factory-owned cleanup. This is an environment-
specific measurement allowance, not retained-artifact attribution or permission
to delete global state. If hosted drift exceeds that bound, qualification stops
and instruments external-owner directories instead of increasing it again.

The reservation ledger is local, contains no product content, and defaults to
`~/Library/Application Support/EdoworksFactory/storage`. Override its root with
`FACTORY_STORAGE_STATE` for isolated CI or testing.

### factory uninstall

Remove factory and residual local state.

```
factory uninstall [--purge]
```

Without --purge: cleans cached state only.
With --purge: removes the factory installation itself.

## Templates

### AppTemplate

A SwiftUI universal app template with:
- NavigationStack with list view
- Add/delete items
- ShareLink export
- ContentUnavailableView empty state
- Accessibility labels
- Unit tests (4 tests)
- UI tests (3 tests)
- PrivacyInfo.xcprivacy (no tracking, no collected data)

## Schemas

### schemas/apple-distribution/

- capabilities.json: Apple distribution capability registry
- submission-draft.schema.json: Non-submitting ASC draft schema
- rejection-feedback.schema.json: App Review feedback learning schema
- product-manifest.template.json: Product manifest shape template

## Versioning

This API is pre-1.0 and may change between minor versions. Pin to an exact
release tag for reproducible builds. The first stable API contract will be
v1.0.0.
