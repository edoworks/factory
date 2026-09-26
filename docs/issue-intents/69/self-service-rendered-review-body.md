# Outcome

Allow a fresh Factory OpenCode session to open exact rendered `edoworks/factory`
GitHub pages in Safari and capture screenshots without requiring the owner to
open each link manually.

# Scope

- Add a repository-owned helper that accepts exactly one validated public
  Factory GitHub review URL and opens it with the pinned system `open` command
  and Safari bundle identifier.
- Admit only the pinned helper command in Factory OpenCode policy and retain
  fail-closed shell, additional-target, host, repository, and path boundaries.
- Add deterministic URL, argument, permission-order, and launch-argv tests plus
  matching Factory Development PRD, incident, and continuation evidence.

# Out of scope

- Arbitrary browsing, browser automation, authentication, clicks, form
  submission, JavaScript execution, downloads, saved-credential access, GitHub
  mutation, other repositories, or non-GitHub hosts.

# Acceptance criteria

- A fresh `bin/factory-dev launch` can open one approved issue, PR, commit,
  action, or revision-bound document page under `https://github.com/edoworks/factory`
  without an approval prompt and can capture Safari with the existing screenshot
  utility.
- The helper rejects HTTP, alternate hosts, user information, ports, sibling or
  prefix-lookalike repositories, settings paths, branch-relative document URLs,
  encoded boundary escapes, controls, whitespace, browser flags, and additional
  arguments before invoking `/usr/bin/open`.
- The direct wildcard `open` permission is removed; issue and PR writes retain
  their existing interactive identity and authority checks.
- No provider, route, fallback, budget, product, release, storage tolerance, or
  deletion authority changes.

# Verification

- Pinned Node tests for accepted and rejected URLs, exact Safari launch argv,
  and fail-closed additional arguments.
- Python policy tests for effective last-match permissions and the exact pinned
  Node suite.
- Full Python and pinned Node suites, `git diff --check`, launch-ready Factory
  doctor, and independent trust review.
- Fresh-session autonomous opening and bounded Safari captures of the exact
  issue, PR, and PR #76 final PRD revision without owner-opened links.

# Dependencies

- Factory development environment issue #69 and its checksum-bound policy
  source.
- Existing fixed macOS screenshot utility permission and installed Safari.

# Authority and privacy

- This issue authorizes repository-local helper, policy, tests, documentation,
  fresh-session navigation to approved public Factory pages, and temporary
  screenshots only.
- It does not authorize credentials, authenticated browser actions, arbitrary
  URLs, GitHub writes, screenshot publication, or retention of private browser
  state. Captures remain temporary and are not committed.

# Source provenance

- `development/opencode/opencode.jsonc` currently marks the bounded Factory page
  opener as `ask` while allowing the fixed screenshot utility.
- `tests/test_single_factory_contract.py` currently requires that opener to be
  interactive and checks only static permission entries.
- OpenCode permission documentation states that the last matching wildcard rule
  wins and configuration changes require a fresh session.
- Owner direction on 2026-09-25 selected autonomous Factory-GitHub-only review
  through Chrome or Safari.

# Classification

Enhancement.

# Priority

P0.

# Triage review

- Duplicate review: issue #101 isolates OpenAI credentials and does not change
  browser navigation; issue #87 pins read-only issue closeout but does not render
  pages. No open issue owns self-service rendered review.
- Reprioritization review: rendered review is a recurring acceptance gate for
  Factory integration and predecessor deletion-readiness evidence, while manual
  page opening creates an avoidable owner dependency.
