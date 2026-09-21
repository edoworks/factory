# Changelog

All notable changes to Edoworks Factory are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this
project adheres to [Semantic Versioning](https://semver.org/).

## [v0.1.0-rc2] - 2026-09-20

### Fixed

- Made doctor version checks safe under `pipefail` on hosted runners.
- Declared and installed xcodegen before clean-runner verification.
- Added lifecycle shell syntax and doctor receipt validation to CI.
- Corrected the uninstall shell option typo.
- Rejected invalid app names before template substitution.
- Produced unsigned CI archives without claiming distribution signing.
- Made XCUITests compatible with Swift 6 strict concurrency.

### Added

- FocusGate v0 PRD for Reference App 1.
- Clean-runner defect 5-Whys and recurrence guard.
- VERSION as the factory receipt's canonical release identity.

## [v0.1.0-rc1] — 2026-09-20

### Added

- CHARTER.md: Founding contract with product laws, paved road, CLI name,
  non-goals, success metrics, authority boundaries, versioning, stop rules,
  compatibility matrix, agent/provider dependencies, support promise, telemetry
  posture, trademark policy, brand reconciliation, meow-capture lane decision,
  and predecessor disposition
- LICENSE: MIT with brand notice reserving edoworks name/logo
- README.md: Quick start, what it does, requirements, status
- SECURITY.md: Vulnerability reporting and security posture
- CONTRIBUTING.md: How to contribute, code style, testing
- .gitignore: Xcode, Swift, Python, secrets
- bin/factory-doctor: Toolchain readiness verification
- bin/factory-init: App scaffolding from template
- bin/factory-verify: Build, test, analyze, and archive
- bin/factory-uninstall: Local state cleanup
- bin/find-simulators.py: Simulator discovery helper
- templates/AppTemplate: SwiftUI universal app template (iPhone + iPad)
- schemas/apple-distribution/: Capability registry, submission draft schema,
  rejection feedback schema, product manifest template
- scripts/apple-quality.py: Apple experience quality validator
- templates/PrivacyInfo.xcprivacy: Privacy manifest template
- tests/test_apple_quality.py: 4 unit tests for apple-quality validator
- PROVENANCE.json: Provenance manifest for ported components
- compatibility-matrix.md: Supported macOS/Xcode/Swift versions
- public-api.md: Paved road contract and command reference
- .github/workflows/checks.yml: CI policy gate

### Decisions

- CLI/package name: `factory`
- Brand reconciliation: Edoworks is primary brand
- Support: No telemetry, best-effort community support
- Trademark: Code MIT, edoworks brand reserved
- Meow-capture: Preserved as second reference app
- Compatibility: macOS 26.x + Xcode 26.x
