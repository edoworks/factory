# Mews & Woofs Missing Bundle Identity

Date: 2026-09-24
Issue: [#63](https://github.com/edoworks/factory/issues/63)
Status: correction verified locally; merged verification pending

## Observation

After all targets compiled, the iOS Simulator refused to install the app because
the processed `Info.plist` had no `CFBundleIdentifier`.

## Root-Cause Analysis

1. The simulator could not install the test host because its bundle identifier
   was absent.
2. The built app lacked that value because the source plist omitted
   `CFBundleIdentifier` and the standard bundle metadata keys.
3. The source plist was written as a new minimal file instead of starting from
   the factory template's proven plist.
4. The omission was not caught at project generation or compile time because
   those stages do not require an installable application identity.
5. The root cause was bypassing an existing paved-road artifact for a standard
   application concern.

## Corrections

- Immediate: restore the factory template's standard bundle metadata while
  retaining the Mews & Woofs display name and orientation policy.
- Root cause: derive reference-app infrastructure files from the template and
  customize only product-specific values.
- Recurrence guard: the canonical all-target test command installs and launches
  the app; source-only compilation is insufficient completion evidence.

## Evidence

Fresh all-target replacements passed on 2026-09-24 with 11 of 11 tests on
iPhone 17 Pro and 11 of 11 tests on iPad Pro 13-inch (M5). Both UI suites
installed and launched the app. CI now preserves equivalent result bundles as
workflow artifacts.
