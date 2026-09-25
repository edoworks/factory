# Edoworks Factory

A public, versioned, MIT-licensed software factory for producing offline-first
iOS/iPadOS apps through a deterministic paved road.

## Quick Start

```bash
# Download the generated source archive for the exact verified prerelease tag
FACTORY_VERSION=0.1.0-rc3
FACTORY_REVISION=a627c88ff9382b4a24887b0a4a5418e8f6c6de7e
curl -fsSL "https://github.com/edoworks/factory/archive/refs/tags/v${FACTORY_VERSION}.tar.gz" | tar xz
mv "factory-${FACTORY_VERSION}" factory

# Verify your toolchain
./factory/bin/factory-doctor

# Scaffold a new app
./factory/bin/factory-init my-app

# Verify your app
cd my-app && ../factory/bin/factory-verify
```

## What It Does

The factory provides one opinionated journey:

```
download release → factory doctor → factory init → confirm PRD →
implement bounded increment → factory verify →
release evidence → human-authorized Apple submission
```

The factory produces verified release candidates. It does not autonomously
publish to the App Store. All credential use, uploads, and submissions require
explicit human authorization.

## What's Included

- SwiftUI universal app template (iPhone + iPad)
- Lifecycle scripts: `factory doctor`, `factory init`, `factory verify`, `factory uninstall`
- Storage admission, reservations, scoped build state, and per-run receipts
- Apple distribution capability registry and validator
- Privacy manifest template (`PrivacyInfo.xcprivacy`)
- Release-criteria schema and evidence generator
- Recovery knowledge boundary and failure classifier
- CI policy gate (deterministic verification)

## One Factory, Two Responsibilities

`edoworks/factory` is the sole canonical factory. Its product runtime remains
provider-independent; its separately versioned development environment contains
the OpenCode policy and safeguards used to improve the factory. Predecessor
repositories are preservation sources, not execution fallbacks.

Run `bin/factory-dev doctor` before starting development, then use
`bin/factory-dev [PRODUCT_PATH]` to print the receipt and start a fresh,
local-config-isolated OpenCode process. The tracked source is under
`development/opencode`; it does not install or modify global OpenCode config.
See the [Factory Development PRD](docs/FactoryDevelopment-PRD.md).
Product repositories remain separate and should pin a supported factory version
and revision rather than copy or independently maintain factory policy.

## Requirements

- macOS 26.x (current or previous major)
- Xcode 26.x (current or previous major)
- Swift 6.x
- Git

No AI agent, cloud provider, or external service is required at runtime.

`factory doctor` and `factory verify` preserve a configurable recovery floor
and reserve capacity for the verification workload before Xcode starts. An
ordinary successful verification removes only its own reproducible build state
and unsigned archive. Use `factory verify --retain-archive` only when that
archive is an intentional retained artifact.

## Documentation

- [CHARTER.md](CHARTER.md) — Founding contract, product laws, authority boundaries
- [CONTRIBUTING.md](CONTRIBUTING.md) — How to contribute
- [Mews & Woofs MVP PRD](docs/MewsAndWoofs-PRD.md) — Reference App 2 product contract
- [Factory Development PRD](docs/FactoryDevelopment-PRD.md) — versioned development environment and cutover contract
- [Single-factory cutover](docs/single-factory-cutover.md) — current state, evidence, and retirement gates
- [SECURITY.md](SECURITY.md) — Security policy

## License

MIT — see [LICENSE](LICENSE). The "edoworks" name and logo are trademarks of
the owner and are not covered by the MIT license; see
[TRADEMARKS.md](TRADEMARKS.md).

## Status

Pre-v1.0. The factory is being qualified by its founder (customer zero) through
two reference apps before any general usability claim is made.

The documented `v0.1.0-rc3` GitHub release is a mutable prerelease with no
attached assets. Quick Start uses GitHub's generated archive for that exact tag,
not a separately uploaded release artifact. `FACTORY_REVISION` records the
source commit expected at the tag so movement is detectable.
