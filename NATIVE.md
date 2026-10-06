# Native prototype — packaging and qualification gates

This dependent increment adds original generic UIKit/WKWebView, XcodeGen project,
and XCTest templates to the existing spec compiler. No Couch source or former
factory implementation is used. Default web generation remains the default.

Generate source into an empty output:

```sh
python3 -B factory.py --spec specs/couch-clash.json --target ios \
  --out /private/tmp/factory-native-source --revision <exact-native-commit>
```

The manifest hashes every emitted source file and each native template. A supplied
revision is still unverified; committed-snapshot benchmark evidence is required
before claiming provenance. Xcode 27.0 (27A266a) and XcodeGen 2.44.1 were inspected;
the native toolchain file records the required versions, not a successful build.

The first native gate compiled and ran, but WKWebView rejected the app's nested
file-origin module imports with a CORS error. A standalone spec-module import,
Web Locks, and storage readback in a second WKWebView worked. The native target
now packs the same three source modules into one ordinary local native-app.js.
Web output remains modular. This is a closed, reviewed graph, not a general JS
bundler: exact engine/app hashes fail closed on unreviewed template changes;
spec data stays JSON; each module retains a separate scope; immutable imports
are bound in spec/engine/app order. No engine logic is duplicated. The manifest
records the packaging contract and hashes the generated bundle. Existing engine
tests execute against the actual packed engine via tests/native_bundle.mjs.

The host uses a persistent WKWebsiteDataStore, limits file reads and navigation
to the bundled Web directory, rejects new windows/downloads/external navigation,
and adds a content-security policy forbidding network connections and frames.
There is no local server, native storage bridge, private WebKit flag, or fallback
that removes the existing Web Locks requirement. ES module loading, Web Locks,
file-origin persistence and enforcement must pass the generated native tests for
each qualified revision. Compilation or source generation alone is not proof.
Navigation is restricted to the canonical bundled index.html (fragments allowed),
not arbitrary files within Web. Native boundary tests cover sibling paths, encoded
traversal, query-bearing URLs and a real escaping symlink. The generated test target
also has a product-specific bundle identifier so variants do not share its identity.
There is no script-message handler to validate or native network request to cancel.
The feasibility-test Web Lock acquisition has a three-second abort; WK JavaScript
evaluation itself and process-relaunch durability remain runtime verification gaps.

Resource gate: source-only work has a 2 MiB write budget and a 2 GiB free-space
floor. These are source-work limits, not sufficient capacity for native execution.
No XcodeGen, build, or simulator commands until the parent coordinates resources
with the Couch owner and confirms sufficient disk/build budget. Use dedicated
DerivedData and an explicitly allocated simulator; do not use another task's
candidate, DerivedData, or simulator. Install no tools or runtimes.

After resource coordination, the planned commands are:

```sh
xcodegen generate --spec project.json
xcodebuild test -project GeneratedApp.xcodeproj -scheme GeneratedApp \
  -destination 'platform=iOS Simulator,id=<allocated-UDID>' \
  -derivedDataPath <owned-derived-data> CODE_SIGNING_ALLOWED=NO
```

Then require a complete game, actual termination/relaunch persistence, blocked
outbound navigation/resource attempts and offline operation, corrupt-save/reset
coverage, changed-spec and boost-ID variants, deterministic regeneration, existing
web acceptance tests, and a pinned native receipt. Those broader native tests and
the native benchmark runner are not fully implemented by this prototype. Generated
tests now include the full spec-driven game, reload, and a UI test that terminates
and relaunches the real app after saving a synthetic match. Results must be reported
from executed tests; their presence is not a passing qualification claim.
Stop and report any file-origin/module/lock failure before changing architecture.

No Forecast/AI/legacy migration/backend, physical-device, signing, provisioning,
App Store, or full Couch parity claim. The owner's 100% assistant / 0% factory
accounting baseline remains unchanged; unmeasured effort stays unknown.
