# Changelog

All notable changes to Edoworks Factory are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this
project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Single Factory Law, explicit cutover and deletion states, and a factory-
  development PRD that keeps OpenCode orchestration separate from product
  runtime (issues #68 and #69).
- Checksum-bound `development/opencode` policy source and `bin/factory-dev`
  doctor/launcher with local-config isolation, active-control comparison, target
  safety, predecessor rejection, and runtime-independence tests (issue #69).
- Evidence-backed predecessor service freeze and a recurrence guard that keeps
  later operational, preservation, and deletion-readiness states unclaimed
  until their separate evidence exists.
- Workload-aware storage admission, atomic reservations, lease reconciliation,
  scoped Xcode build state, and storage lifecycle receipts (issue #60).

### Changed

- Replaced the former Apple-acceptance-gated, never-delete predecessor policy
  with exact-target, preservation-verified, owner-authorized retirement while
  leaving product qualification gates unchanged.
- Successful ordinary verification now removes only its run-owned build state
  and unsigned archive; `--retain-archive` explicitly promotes an archive.

## [v0.1.0-rc3] - 2026-09-22

### Fixed

- Pinned README quick start to exact tag archive URL (from PR #38).
- Strengthened release-contract test to verify live URL resolves and release
  record matches README version (from PR #40).

### Added

- Release-contract CI test now checks HTTP 200 on documented download URL and
  verifies GitHub release API returns matching tag with prerelease flag.
- Obligation disposition manifest for cutover gate #16 (sf0.8 issues
  classified: 5 migrated, 1 completed, 9 superseded, 6 retained-evidence).
- Cutover evidence contracts and blocker rubberduck review in sf0.8 PRD.

### Changed

- Bumped VERSION to 0.1.0-rc3.
- Factory issues #29, #30, #33, #34, #35, #36 closed with evidence after
  maintainer-reviewed closeout verification.

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
