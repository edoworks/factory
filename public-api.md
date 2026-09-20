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
and disk space. Produces a JSON evidence receipt on stdout.

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
factory verify
```

Must be run from the app root directory (where project.yml lives).

Steps:
1. Build on iPhone simulator
2. Unit tests
3. Build on iPad simulator
4. Static analysis
5. Archive (requires development team config)

Produces a JSON evidence receipt (.factory-verify-result.json).

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