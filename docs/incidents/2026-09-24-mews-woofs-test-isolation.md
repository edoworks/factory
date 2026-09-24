# Mews & Woofs Test Isolation Build Failure

Date: 2026-09-24
Issue: [#63](https://github.com/edoworks/factory/issues/63)
Status: correction verified locally; merged verification pending

## Observation

The first `xcodebuild test` for the Mews & Woofs reference app failed while
compiling both XCTest targets. XCTest initializers and `setUp()` inherited main
actor isolation that did not match XCTest's nonisolated declarations.

## Root-Cause Analysis

1. The tests did not compile because XCTest overrides had incompatible actor
   isolation.
2. They became main actor-isolated because the project initially set
   `SWIFT_DEFAULT_ACTOR_ISOLATION: MainActor` globally.
3. Moving that setting to the app target fixed XCTest declarations but still
   isolated imported domain models, so ordinary deterministic unit tests could
   not call them.
4. Both failures reached verification because the generated project had not yet
   completed its first all-target compile.
5. The root cause was using broad default isolation where framework isolation
   and narrow explicit annotations already provide the required UI safety.

## Corrections

- Immediate: remove project-wide and app-target default actor isolation.
- Root cause: keep domain models and XCTest declarations nonisolated by default;
  use framework isolation and explicit `@MainActor` only where UI-test calls
  require it.
- Recurrence guard: repository verification must compile and run all three
  Mews & Woofs targets from the generated project; a source-only or app-only
  build is insufficient.

## Evidence

Fresh all-target replacements passed on 2026-09-24 with 11 of 11 tests on
iPhone 17 Pro and 11 of 11 tests on iPad Pro 13-inch (M5). The canonical
factory verification also passed build, unit tests, iPad build, static analysis,
unsigned archive, simulator cleanup, and storage policy. CI now runs all three
targets on both form factors and uploads both result bundles.
