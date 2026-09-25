# Outcome

Make the mandatory Factory issue-closeout verification executable from a fresh policy-valid session through one exact read-only command with pinned GitHub transport.

# Scope

- Pin `issue-closeout.mjs` to Factory's trusted GitHub CLI instead of ambient `PATH` lookup.
- Admit only the exact `verify --repo edoworks/factory --issues NUMBER[,NUMBER...]` command through repository-owned OpenCode policy.
- Add focused tests for closed, open, malformed, duplicate, wrong-repository, hostile-path, and missing-pinned-CLI cases.
- Record the closeout permission dead-end 5-Whys and update the Factory development PRD and continuation evidence.

# Out of scope

- Creating, commenting on, closing, reopening, labeling, or otherwise mutating issues; changing repository settings; broad GitHub API access; changing credentials; or advancing unrelated consolidation state.

# Acceptance criteria

- A fresh Factory session can run the documented closeout verifier for issue #84 and receives exactly `CLOSED`.
- The verifier invokes only the pinned GitHub CLI, reads only `edoworks/factory`, accepts only unique positive numeric issue identifiers, and fails if any issue is not closed.
- Open, malformed, duplicate, wrong-repository, missing-runtime, or hostile-path inputs fail without external mutation.
- Direct unpinned GitHub issue mutations remain denied, and no broader shell or GitHub permission is added.
- The Factory development PRD, incident evidence, continuation source, policy manifest, and focused tests agree on the closeout workflow.

# Verification

- Focused Node tests for verifier parsing, pinned transport, closed/open states, and rejected inputs.
- Full Factory Python and pinned Node policy suites.
- Factory doctor before integration and from a fresh post-merge session.
- Exact issue #84 closeout receipt, independent trust-boundary review, hosted Factory checks, and bounded rendered review of changed human-facing documentation.

# Dependencies

- Parent canonical-development issue #69.
- Issue #84 and merged PRs #85 and #86, whose remote closure is readable but whose mandated closeout helper is blocked by current policy.

# Authority and privacy

- This issue authorizes repository-local development tooling, policy, tests, documentation, ordinary commits, reviewed PRs, and read-only issue-state verification for `edoworks/factory`.
- It does not authorize issue mutation, repository setting changes, credential broadening, publication, release, deletion, cleanup, paid model calls, or access to private issue payloads beyond number, title, and state.
- No credential value, token, private repository metadata, or issue body may be copied into tracked evidence.

# Source provenance

- `development/opencode/skills/issue-tracking/SKILL.md` requires exact closeout-helper verification before tracked completion.
- `development/opencode/opencode.jsonc` at Factory head `e3a789fe1b3a78cfc952f76a5fcc9d7454cbc66b` does not admit that helper command.
- PR #85 merged issue #84 implementation as `a1529c81cb46e3a585bb64676632a034c34beb52`; PR #86 merged its continuation record as `1ea85b227b6a151c65f8d39065d1732792f8588a`.

# Classification

Enhancement.

# Priority

P0.

# Triage review

- Duplicate review: issue #84 fixed routing-catalog refresh but did not authorize its mandatory closeout verifier; issue #69 established the development environment without this command. No open issue covers the contradiction.
- Reprioritization review: the contradiction blocks compliant completion of issue #84 and therefore precedes issue #77 and all preservation work.
