# Edoworks Factory Charter

Date: 2026-09-20
Status: ACTIVE
Owner: founder (customer zero)
Reference: [PRD](https://github.com/edoworks/sf0.8/blob/main/docs/PRD-edoworks-factory.md)

## Founding Statement

Edoworks Factory is a public, versioned, MIT-licensed software factory that
produces offline-first iOS/iPadOS apps through a deterministic paved road. The
founder is customer zero. The factory is downloaded from the generated source
archive for an exact release tag, used to scaffold and verify an app, and
produces human-gated release candidates for Apple App Store submission.

The factory does not autonomously publish. It does not promise Apple approval
dates. It does not manage multiple tenants until v1.0.0.

## Product Laws

### Human Authority Law

No credential use, upload, submission, release, or repository visibility
change happens without explicit human authorization. The factory produces
evidence and candidates; the human decides.

### Clean-Checkout Law

Every build must reproduce from the factory release artifact and the app
repository. No hidden local state, ambient credentials, or founder-only
knowledge may be required.

### Verified-Candidate Law

The factory's daily service level is a verified release candidate: clean build,
tests pass, archive produced, evidence recorded. Public App Store availability
is an external Apple process, not a factory promise.

### Differentiation Law

Every app produced through the factory must be materially differentiated.
Template-generated fleets of near-identical apps violate Apple Guideline 4.2.6
and are explicitly out of scope.

### Recovery Law

Every failure must have a machine-readable classification and a documented
recovery path. If the factory cannot recover, it must fail safely and report.

### Storage Envelope Law

Disk-expensive work declares and reserves its maximum peak above a recovery
floor before execution. Successful routine work retains no unexplained bytes:
persistent growth must belong to a named artifact with an owner and retention
policy. Automatic cleanup is limited to exact factory-owned reproducible paths;
source, uncommitted work, promoted artifacts, pinned resources, and global
developer state are never inferred to be disposable.

## Paved Road

The factory's public API is one opinionated journey:

```
download release → factory doctor → factory init → confirm PRD →
implement bounded increment → factory verify →
release evidence → human-authorized Apple submission
```

### CLI

Package name: `factory`

Commands:
- `factory doctor` — verify Xcode, simulators, storage admission, and dependencies
- `factory init` — scaffold a new iOS app from the factory template
- `factory verify` — reserve storage, run build, tests, analysis, and archive in
  factory-scoped paths, then emit a storage receipt
- `factory uninstall` — remove factory and residual local state

## Non-Goals

- Autonomous App Store publishing
- Multi-tenant SaaS platform
- macOS, watchOS, tvOS, visionOS targets (added as independently qualified
  capabilities after v1.0.0)
- Template app fleet generation
- Customer self-service without human gates
- General-purpose CI/CD platform
- Dashboards, learned routing, transcript stores
- General portfolio automation
- Self-modifying policy

## Success Metrics

Track these, not app count:

| Metric | Target |
|---|---|
| Clean-checkout build success | 100% from released artifact |
| Unattended run success (30-day qualification) | ≥95% without manual repair |
| Lead time (change to verified candidate) | Measured, trending down |
| Operator effort (human minutes per increment) | Measured, trending down |
| Escaped defects per release | 0 critical, measured minor |
| Apple review outcomes | No template/spam/privacy/metadata rejection |
| Recovery from deliberate failure | Documented and rehearsed |
| Second-operator execution | Succeeds without oral help |
| Successful-run persistent disk growth | Zero except named retained artifacts |

## Authority Boundaries

| Action | Authority |
|---|---|
| Code changes in factory repo | Founder |
| Factory release publication | Founder |
| App code changes in app repo | Founder |
| Credential use | Human only |
| TestFlight upload | Human only |
| App Store submission | Human only |
| Repository visibility change | Human only |
| License or trademark decision | Human only |
| Customer engagement | Human only |

## Versioning

- `v0.1.0` — Initial release: paved road, lifecycle scripts, simpler utility
  template
- `v0.1.x` — Corrections discovered during Reference App 1 qualification
- `v0.2.0` — Post-qualification hardened release (after 30-day test passes)
- `v0.3.0` — Meow-capture capability (microphone, SoundAnalysis, audio clip
  management)
- `v1.0.0` — Stable public compatibility contract (only after second
  independent consumer and paid pilot)

Every factory correction is a new tagged version. The reference app records the
exact tag and source revision and upgrades explicitly. Release records must
state whether they are prereleases, immutable, and accompanied by attached
assets rather than implying those properties from the tag alone.

## Stop Rules

Stop or re-scope if:

- Work remains founder-dependent after 30-day qualification
- Customers only want bespoke development, not the factory
- Apps converge toward templates despite differentiation efforts
- Apple repeatedly objects on template, spam, privacy, or minimum-functionality
  grounds
- Support costs exceed customer willingness to pay
- Factory governance output consistently exceeds shipped app value

## Compatibility Matrix

| Component | Supported versions |
|---|---|
| macOS | 26.x (current and previous major) |
| Xcode | 26.x (current and previous major) |
| iOS (deployment target) | 18.0+ |
| iPadOS (deployment target) | 18.0+ |
| Swift | 6.x |

The factory is tested against the current and previous major macOS/Xcode
versions. Older versions may work but are not guaranteed.

## Agent and Provider Dependencies

The factory artifact is **provider-agnostic**. It requires only:

- Apple Xcode (per compatibility matrix)
- Swift Package Manager (bundled with Xcode)
- A Git client

The factory has **no runtime dependency** on any AI agent, cloud provider, or
external service. AI agents may be used during development of the factory
itself, but the released artifact does not require or invoke them.

Developers using the factory may use any AI coding assistant they prefer; the
factory's lifecycle scripts (`factory doctor`, `factory init`, `factory verify`)
are plain shell scripts that work independently of any agent.

## Support Promise

- **License:** MIT (see LICENSE)
- **Support:** Best-effort community support via GitHub issues. No SLA. No
  guaranteed response time.
- **Contributions:** Welcome via pull requests (see CONTRIBUTING.md)

## Telemetry Posture

The factory collects **no telemetry**. It does not phone home, report usage,
or transmit any data to any server. `factory doctor` checks local toolchain
state only; it never sends data externally.

## Trademark Policy

The MIT license covers the code. The "edoworks" name and logo are brand
trademarks of the owner under [TRADEMARKS.md](TRADEMARKS.md). Others may use,
modify, and distribute the code under the MIT license but may not use the
"edoworks" name, logo, or brand for their own products or services without
written permission from the owner.

## Brand Reconciliation

Edoworks is the canonical brand for the factory. The constitution invariant is
updated from "Foculoom compounds engineering knowledge" to "Edoworks compounds
engineering knowledge." Foculoom remains a separate entity and brand.

This charter supersedes the sf0.8 constitution's branding reference for all
Edoworks Factory purposes. The sf0.8 constitution is preserved as historical
evidence and is not modified.

## Meow-Capture Lane Decision

Meow-capture is explicitly preserved as the **second reference app** (Phase 4)
for the factory. It is not abandoned. The first reference app (Phase 2) is a
simpler offline utility with no special permissions, used to prove the factory's
paved road with the lowest App Review friction.

The meow-capture reference app requires owner-authorized public name,
physical-device validation, and first real-meow fixture before it can proceed.
These are tracked in [Issue #12](https://github.com/edoworks/factory/issues/12).

## Predecessor Disposition

sf0.8 is frozen and superseded — not archived — until the new factory proves:

1. Two Apple-accepted reference apps
2. Recovery from factory failure rehearsed
3. Every open sf0.8 issue dispositioned with successor links
4. All obligations tracked to a successor

Only then are sf0.8 and predecessors archived (read-only, never deleted).

## Customer Zero

The founder is customer zero. Two reference apps qualify the factory in
sequence:

1. **Reference App 1 (simpler offline utility):** A minimal offline
   iOS/iPadOS utility with no special permissions. Proves the factory's paved
   road with the lowest App Review friction.

2. **Reference App 2 (meow-capture):** A local cat-meow audio
   capture/replay/delete app with microphone permission and on-device
   SoundAnalysis classification. Proves the factory handles a harder
   real-world product with permission complexity and App Review scrutiny.
