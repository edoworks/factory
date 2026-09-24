# Mews & Woofs UI Query Mismatch

Date: 2026-09-24
Issue: [#63](https://github.com/edoworks/factory/issues/63)
Status: correction verified locally; merged verification pending

## Observation

The app installed and all six model tests passed, but the first UI run failed
while waiting for identified canvas or thought-bubble elements. A broad semantic
query fixed the canvas states; the composed bubble remained represented through
its accessible label rather than its test-only identifier.

## Root-Cause Analysis

1. UI tests could not find some identified composed elements even though the app
   launched, actions were tappable, and screenshot evidence rendered them.
2. The tests queried those identifiers only as XCUI `Other` elements.
3. SwiftUI exposed the identified composed views under implementation-dependent
   accessibility element types rather than guaranteeing `Other`.
4. The tests coupled semantic identity to a framework representation detail.
5. The root cause was an unnecessarily narrow query contract rather than a
   missing product accessibility identifier.

## Corrections

- Immediate: resolve stable container identifiers across all XCUI element types
  and test bubble editing through its user-visible controls and preview result.
- Root cause: reserve typed queries for controls whose role is part of the
  product contract, such as buttons; query composed visual surfaces by stable
  identifier.
- Recurrence guard: UI tests launch the welcome, editor, and preview states and
  require their semantic identifiers before capturing visual evidence.

## Evidence

Fresh all-target replacements passed on 2026-09-24 with 11 of 11 tests on
iPhone 17 Pro and 11 of 11 tests on iPad Pro 13-inch (M5). Both UI suites
traversed the editor and preview states and retained screenshots in their result
bundles. CI now preserves equivalent result bundles as workflow artifacts.
