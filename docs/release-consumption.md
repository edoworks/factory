# Proposed Release Consumption Contract

`scripts/check_release_consumption.py` performs a pure offline check of two
JSON files: an app lock and a bundled release manifest. The lock pins the
canonical repository `edoworks/factory`, an exact `vX.Y.Z` tag with an
optional semver prerelease, the 40-character source revision, the SHA-256 of
the exact manifest file bytes, one uploaded payload name and digest, and a
independently approved workflow path and commit. Workflow trust comes from human
approval of the app lock, not this validator. The manifest repeats those identities and
declares one inventory for all bundled skills.

Every inventoried file has a safe relative POSIX path, digest, declared
origin and license identifiers, and an inventoried notices reference. Origin
and license strings are declarations, not verified licensing clearance. Each skill names its
instructions, inventoried files, and bundled skill dependencies. Missing
resources (including notices), duplicate file/dependency declarations, missing or
cyclic dependencies, external skill references,
duplicate JSON keys, non-finite JSON constants, mutable selectors, and
unknown contract fields are rejected. Asset names are 1-128 ASCII characters,
beginning with a letter or digit and followed only by letters, digits, dots,
underscores or hyphens. Tags use SemVer syntax without build metadata; validating
their syntax does not establish that a GitHub release exists or is immutable.
Each input is limited to 1 MiB. Invalid-input receipts retain the total error
count and at most 64 messages of 512 characters each. JSON null, wrong schema
types, excessive JSON nesting and malformed resource types fail with receipts.

The command is a schema and identity check, not a downloader, archive
extractor, filesystem integrity verifier, attestation verifier, scheduler, or
package registry. A successful schema check never authorizes production:
receipts always report `release_verified: false` and
`consumption_authorized: false`. Inventory equality does not inspect actual
artifact bytes or prove closure; a later artifact verifier must validate the
downloaded payload, file tree, and complete dependency/license closure.

Separately acquired tools and explicit capability evidence dimensions are
deliberately deferred to a later contract rather than silently expanding this
small release identity contract.

## Development Use

```bash
python3 scripts/check_release_consumption.py factory.lock.json release.json
```

Schema version 1 uses the exact fields illustrated by `fixture()` in
`tests/test_release_consumption.py`. That fixture is invented test data, not a
published factory release or an app-adoptable lock. The command returns zero
only for declaration consistency; callers must still require independent release
verification and approval. No production workflow invokes this candidate yet.

The public `v0.1.0-rc3` release was inspected on 2026-09-30: it is a mutable
prerelease with no attached assets. Its generated source archive is not the
uploaded, attested skill bundle required by this proposed production contract.
Existing release tests and Quick Start remain unchanged to preserve the shipped
historical behavior; this candidate does not upgrade that release by declaration.

Next qualification needs the complete tool/configuration lock, actual payload
and inventory verification, disabled mutable instruction discovery, an independently
trusted bootstrap, and frozen candidate-to-benchmark-to-publication evidence.
Publishing and explicitly adopting those bytes remain separate human gates.
