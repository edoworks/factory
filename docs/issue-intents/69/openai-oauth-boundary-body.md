# Outcome

Ensure Factory OpenCode's OpenAI route does not inherit an API key when the user chooses ChatGPT browser OAuth, without reading or changing saved credentials.

# Scope

- Record the user-provided incorrect-API-key OpenCode screenshot as redacted evidence, without publishing its credential fingerprint.
- Remove inherited `OPENAI_API_KEY` from the Factory launcher child environment only.
- Add a fake-OpenCode launch test for key absence and no value leakage; document the doctor/OAuth evidence boundary in the Factory Development PRD and incident.

# Out of scope

- Reading, overwriting, or exporting saved OpenCode credentials; changing model routes, provider budgets, fallbacks, subscriptions, or other applications' environments; treating this as a fix for PR #98's hosted storage failure.

# Acceptance criteria

- A fresh `bin/factory-dev launch` never passes inherited `OPENAI_API_KEY` to OpenCode and never prints the value in receipts or tests.
- Browser OAuth remains an interactive user-owned OpenCode connection; a stored API-key credential, if present, is handled separately through `/connect`.
- Full local suites, Factory doctor, independent review, and rendered human-facing records pass before integration; hosted checks must pass before issue closeout.
- No route, provider, fallback, budget, product, release, or storage-tolerance behavior changes.

# Verification

- Fake-OpenCode launch test with a test-only sentinel and no credential-value output.
- Python and pinned Node policy suites, `git diff --check`, and launch-ready Factory doctor.
- Independent read-only review of the OAuth boundary and visual review of the rendered PRD, incident, issue, and PR.
- Hosted Factory policy, iPhone, and iPad checks on the integrated revision; one user-controlled OAuth-backed request from a fresh launch to establish live credential behavior.

# Dependencies

- Factory Development PRD entry contract and existing repository-owned issue workflow.
- OpenCode's documented OpenAI ChatGPT Plus/Pro `/connect` browser authentication.
- PR #98 and issues #78/#99/#100 are separately blocked by their hosted policy evidence.

# Authority and privacy

- This issue authorizes the repository-local launcher guard, deterministic tests, documentation, and issue evidence. It does not authorize credential access or mutation, model calls on the user's behalf, paid route changes, GitHub bypasses, or product/release changes.
- Do not publish any API-key prefix/suffix, token, screenshot pixels containing credential material, or private user state.

# Source provenance

- User-provided OpenCode error screenshot inspected 2026-09-25; only the generic incorrect-API-key classification is retained.
- `bin/factory-dev`, `tests/test_factory_dev.py`, and `docs/FactoryDevelopment-PRD.md` at local parent `d4d1068`.
- `https://opencode.ai/docs/providers/#openai` documents ChatGPT Plus/Pro browser OAuth.

# Classification

Enhancement.

# Priority

P0.

# Triage review

- Duplicate review: issue #87 addressed GitHub closeout identity and permission, not OpenAI provider credential precedence; issues #99/#100 own unrelated hosted evidence and storage failures.
- Reprioritization review: an untrusted API key in an OAuth-only Factory development session is an immediate credential-boundary defect, independent of blocked PR #98.
