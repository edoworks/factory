# Factory Development PRD

Date: 2026-09-24
Status: ACTIVE, CUTOVER TRACKED BY ISSUES #68 AND #69
Authority: `edoworks/factory`

## Outcome

Provide one versioned development environment for improving Edoworks Factory
without making OpenCode, an AI provider, or agent policy a dependency of the
product runtime.

## Responsibilities

### Product Runtime

- Deterministic doctor, initialization, verification, and uninstall commands.
- Product templates, schemas, compatibility contracts, and release evidence.
- Provider-independent operation from an exact factory version and revision.

### Factory Development

- OpenCode planning, build, review, and continuation policy.
- Model/provider dispatch safeguards, cost controls, and bounded escalation.
- Issue tracking, evidence discipline, interruption recovery, and completion
  receipts.
- Installation receipts that identify factory version, source revision,
  OpenCode version, tracked policy digest, and local override state.

Development policy may invoke tools to improve the runtime. Runtime commands
and generated products must not import, download, or require that policy.

## Entry Contract

The supported development entry path is `bin/factory-dev`. It must:

1. Resolve the canonical factory checkout without following an untrusted
   project or target symlink.
2. Validate the tracked development configuration before startup.
3. Refuse a missing, stale, or mismatched installation rather than loading a
   predecessor fallback.
4. Print the factory version, source revision, policy digest, and dirty/override
   state before launching OpenCode.
5. Preserve the current working Build route and paid-fallback policy unless an
   independently verified change is explicitly authorized.

The versioned source is `development/opencode`. `bin/factory-dev` sets a
dedicated `XDG_CONFIG_HOME` for the fresh process, leaving credentials and data
untouched while isolating local user configuration. Before that isolation,
the launcher resolves and pins GitHub CLI's user configuration through
`GH_CONFIG_DIR`; it does not copy credentials into Factory source or receipts.
It removes inherited GitHub host and token overrides, selects GitHub CLI only
from a resolved `gh` package root, rejects a group/world-writable executable,
pins every allowed GitHub command to that executable and operations to `github.com`,
and requires the authenticated `hellofoculoom` identity before issue transport.
There is no control install or synchronization command: doctor compares active
user controls with the captured source baseline, while launch uses the
checksum-bound repository source. The bounded exception is
`bin/factory-dev refresh-catalog`, which imports only route-relevant non-secret
fields from the fixed approved generated user-catalog path. It first requires
valid repository integrity, accepts no non-catalog routing contradiction,
rejects older, stale, malformed, incomplete, or failed-provider evidence, and
updates the tracked catalog and its manifest digest together. Models absent from
the fresh generation remain unavailable rather than inheriting stale active
claims. The command does not refresh providers, run benchmarks, promote routes,
or change provider, budget, and fallback policy.

Launch removes every inherited `OPENCODE_*` variable, rejects project
configuration in the target or its ancestors, and rejects local managed
configuration that could override repository policy. Authenticated
organization `.well-known` policy is not suppressible by this launcher; any
future enrollment requires a separate effective-config review before readiness
may be claimed. The policy inventory is closed-world outside generated `node_modules`:
unlisted files and symlinked policy paths fail readiness. Broad GitHub issue
mutations remain denied. Issue creation is an interactive `ask` operation routed
through the environment-rooted repository script, which validates and transports
the frozen intent without accepting inline issue content. The launcher pins the
GitHub CLI to an absolute executable path before the script can transport or
read back that intent. Exact repository-first
comment and close commands for `edoworks/factory` are also interactive `ask` operations;
auto mode cannot supply that human authorization, and trailing
repository overrides are denied. Issue comments and closeout are routed through
the same pinned host, executable, and identity check. Repository-owned issue-intent hashing, local
validation, and remote readback commands are read-only allowed operations; their
fixed script path and argument validation prevent them from becoming alternate
mutation transports. Completion verification is a separate exact read-only
command: it accepts only unique positive issue numbers, fixes
`github.com/edoworks/factory`, invokes the pinned GitHub CLI with host, token, and
proxy overrides removed, requires the authenticated `hellofoculoom` identity,
binds each response number to its request, reads only issue number, title, and
state, and returns `CLOSED` only when every requested issue is closed. Shell
control, substitution, and redirection forms remain denied before the wildcard
issue-number argument can match.
Wildcard Python and Node test-runner commands are denied; only exact tracked
Factory suites anchored to `FACTORY_DEV_OPENCODE_ROOT` are allowed so a caller
cannot select a product-owned module or test file through an allowed runner.
Ordinary factory PR integration uses only explicitly allowed canonical command
forms, with trailing repository overrides denied. Rendered Factory
documentation review may interactively open one `edoworks/factory` GitHub page
with no additional target and may run
the screenshot utility at its fixed home-directory installation; neither
permission grants content mutation.
The launched process receives a fixed system/package-manager `PATH`, so a product
target cannot shadow allowed interpreters or tools. PR URL selectors and trailing
issue/PR repository overrides are denied. Git push has no shell allow exception.
An interactive repository-owned transport accepts one lowercase `feature/...`
branch and one full expected commit, verifies both `HEAD` and the GitHub identity,
pins Git and GitHub CLI, suppresses system/global configuration, rejects local
transport-affecting configuration, clears inherited Git and proxy overrides,
fixes the canonical HTTPS remote and no-follow-tags refspec to the expected
commit, and runs from the Factory root so repository hooks remain active.

Doctor emits one JSON object containing `factory_version`, `git_revision`,
`dirty`, `opencode_version`, `policy_digest`, `active_installation`,
`config_override`, `canonical_repo`, target, and readiness fields. Missing,
changed, escaping, symlinked, predecessor-bound, or project-config-overridden
policy/targets fail closed.

Product work may use a compatible version-pinned installation of this same
configuration. Such an installation is a receipt-bound deployment, not a new
factory or an editable policy source.

## Cutover States

| State | Evidence required |
|---|---|
| `CANONICAL_FOR_NEW_WORK` | Charter, PRD, and sole factory issue tracker point to `edoworks/factory` |
| `OPERATIONALLY_CUT_OVER` | Fresh development startup and representative runtime workflow complete with predecessors unavailable |
| `PRESERVATION_VERIFIED` | Required Git, local overlays, hosted metadata, and obligations restore from tested private preservation |
| `READY_FOR_OWNER_DELETION_APPROVAL` | Exact allowlists pass dependency, recovery, privacy, and target-safety gates |
| `REMOTE_DELETION_COMPLETED` | Authenticated results confirm only approved remotes were deleted |
| `LOCAL_CLEANUP_COMPLETED` | Only approved resolved paths were removed and factory operation was reverified |

No later state is inferred from an earlier one. Product qualification and
release status remain separate.

Deletion readiness requires a revision-bound manifest of exact remote identities
and resolved local paths. For each proposed target it records lifecycle state,
ownership, Git divergence, local overlays, hosted metadata, obligations,
preservation and restore receipts, dependency-scan results, and an explicit
include or exclude disposition. A clean or dirty `git status` is evidence to
classify, not a deletion decision. Product repositories, paused products,
secrets, preservation artifacts, runner definitions needed for recovery, and
targets with unknown ownership or lifecycle state are excluded.

## Required Controls

- Routine work uses the lowest-cost qualified route; premium escalation is
  bounded and explicit.
- A budget or no-progress stop preserves progress and never triggers an
  unapproved paid fallback or retry loop.
- Issue state, implementation evidence, and release state are independently
  verified.
- Product-repository work requires a current lifecycle admission record. A
  paused product is ineligible for implementation, unarchive, push, merge, or
  release until a separate owner reactivation decision is recorded. Current
  machine-readable admissions are tracked in
  `docs/product-lifecycle-admissions.json`.
- Configuration changes require a fresh process because OpenCode does not
  hot-reload startup policy.
- Secrets remain in approved external secret storage and never enter receipts,
  source, issue bodies, or public evidence.
- Route readiness requires current evidence. The inherited local routine
  benchmark expired during cutover and was rerun only for
  `ollama/granite4.1:3b` on the local zero-marginal-cost provider. It passed the
  unchanged suite on 2026-09-25. No paid benchmark, provider, Build route,
  budget, or fallback policy changed.
- Catalog expiry has a pre-launch recovery path: generate user evidence through
  the approved model-routing procedure, run `bin/factory-dev refresh-catalog`
  from a normal terminal, then require a launch-ready doctor receipt.

## Non-Goals

- Recreating sf0.8's portfolio control plane, dashboards, learned dispatcher,
  transcript store, or general-purpose migration machinery.
- Migrating every predecessor experiment, command, skill, or evidence graph.
- Centralizing product-specific PRDs, data, or release evidence in factory.
- Changing subscriptions, billing, credentials, product qualification, or
  release authority.

## Acceptance

- `bin/factory-dev doctor` reports the loaded version, revision, policy digest,
  OpenCode version, and override state.
- A fresh bounded session starts from tracked factory policy with no `sf0.*`
  path or repository fallback.
- Factory runtime tests pass when development tooling is unavailable.
- A targeted guard rejects predecessor operational references outside an
  explicit historical/provenance allowlist.
- A deletion-readiness record fails closed until exact targets, local divergence,
  tested off-machine preservation, hosted metadata, current dependency scans,
  and separate owner approvals are verified.
- A clean-room check performs doctor, init, verify, checkpoint, and safe failure
  without predecessor access.
