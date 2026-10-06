# Edoworks Factory

One canonical factory: `edoworks/factory`. This is a fresh, unproven experiment
combining Factory004's shipping-first direction with recorded predecessor lessons.
The owner selected a clean implementation on 2026-10-06; historical repository
retirement instructions no longer select the destination for new work.

The first transition commit (`653e833f1cbedd6fa2147ad15a78980c438b2ef3`) contains
requirements and governance only: **zero implementation code**. This subsequent
checkpoint adds an original spec-to-web-game compiler and bounded acceptance tests.
It is not a release, full Couch parity, or a replacement deployed on main.

## Run the clean-generation benchmark

Use a clean checkout of an exact commit. `toolchain.json` pins the installed Python,
Node and browser versions; no installation or paid service is performed. Explicitly
set `FACTORY_NODE` and `FACTORY_CHROME` to those existing executables, then run:

```sh
python3 -B benchmark.py --out /absolute/canonical/new-benchmark-directory
```

The output parent must exist; use its real path, not a symlink such as macOS `/tmp`.
The benchmark runs generator tests, generates twice from an isolated source closure,
compares every output byte, changes branding/question/scoring data and regenerates,
then executes engine and headless browser tests for both products. It emits
`receipt.json`, individual logs and apps. It refuses dirty source and missing tools.
Loopback serving/headless Chrome require executor permission where sandboxed.

For generation alone (not a verification claim):

```sh
python3 -B factory.py --spec specs/couch-clash.json \
  --revision EXACT_40_CHARACTER_FACTORY_COMMIT --out /absolute/canonical/empty-app
python3 -m http.server 8000 --bind 127.0.0.1 --directory /absolute/canonical/empty-app
```

Open the local server in a browser. Static ES modules need HTTP; no bundler is
required. This checkpoint does not install a PWA cache or provide offline reload.
Generation uses no Couch source or old factory implementation. Python audit hooks
in the benchmark reject undeclared file reads, network and subprocess access by
the trusted generator. This is measured closure evidence, not a security sandbox
for hostile Python. Git supplies the pinned revision to the benchmark; the
generator reads no Git blobs and its manifest records actual source/spec hashes.

- [PRD](PRD.md): measurable scope, limits, acceptance and parity gaps.
- [Lessons](LESSONS.md): evidence to retain without importing old architecture.
- [Charter](CHARTER.md): authority and product boundaries.
- [Transition](TRANSITION.md): backup, issue treatment and workflow impact.

MIT licensed; the existing license, trademark and security-reporting policies
remain in force. Old implementation is recoverable through the verified
[backup](https://github.com/edoworks/factory/tree/backup/pre-clean-slate-20261006T140606Z-dab21a8a).
