# Edoworks Factory

**Current direction (2026-10-07):** [PRIORITIES.md](PRIORITIES.md) is the
entrypoint for new work. Deliver differentiated software with verified customer
revenue and prove product value before expanding factory infrastructure. The
current Couch Clash benchmark has no demonstrated product-fit go-ahead; see
[the bounded review](https://github.com/edoworks/factory/pull/136). Older
factory repositories are historical, not work queues.

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
The benchmark archives the exact committed Git HEAD into a fresh private directory,
records its commit/tree and file hashes, and runs tests and generation from those
committed bytes. It checks snapshot hashes before and after the run and compares
generated source hashes with the snapshot. It then runs generator tests, generates twice from an isolated source closure,
compares every output byte, changes branding/question/scoring data and regenerates,
then executes engine and headless browser tests for those products and a valid
question-ID `boost` regression spec. Every browser run checks two real pages sharing
one origin/store: the first lock must survive a stale second-page write. It emits
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
for hostile Python. The standalone compiler labels `--revision` as
`caller_supplied_unverified`; supplying a hex string does not verify Git identity.
The benchmark separately binds generated source hashes to its committed snapshot.
The generator reads no Git blobs and its manifest records actual source/spec hashes.

All generated save/reset operations take the same origin-scoped Web Lock and compare
the saved value while holding it. A stale tab stops with a visible reload action;
browsers without Web Locks fail closed. This coordinates cooperating app pages,
not malicious scripts or other software writing storage outside the protocol.

The owner-selected accounting baseline is **100% assistant / 0% factory** in
`autonomy-baseline.json`. Benchmark wall time is a separate execution observation;
development, setup, debugging, review, active labor, tokens and dollars remain
unmeasured. Prior 8.5565-second evidence receives no retroactive automation credit.
Future comparisons must preserve scope/coverage; the next manual handoff to encode
is the source-and-receipt package for independent review.

- [PRD](PRD.md): measurable scope, limits, acceptance and parity gaps.
- [Lessons](LESSONS.md): evidence to retain without importing old architecture.
- [Charter](CHARTER.md): authority and product boundaries.
- [Transition](TRANSITION.md): backup, issue treatment and workflow impact.

MIT licensed; the existing license, trademark and security-reporting policies
remain in force. Old implementation is recoverable through the verified
[backup](https://github.com/edoworks/factory/tree/backup/pre-clean-slate-20261006T140606Z-dab21a8a).
