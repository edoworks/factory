---
description: Audit an opportunity without promoting unsupported evidence
agent: plan
---

# Rubberduck Opportunity Gate

Use this command to challenge a repository-owned opportunity report. It is a
research and evidence command, not product approval.

1. Read `docs/rubberduck-research-2026-09-26.md` and its adjacent
   `docs/rubberduck-research-2026-09-26.json` ledger. Preserve the report's
   FACT, INFERENCE, HYPOTHESIS, and UNKNOWN labels.
2. Capture a JSON receipt from the canonical command before editing:
   `bin/factory-dev doctor > /tmp/rubberduck-doctor-pre.json`.
3. Research only public, direct, dated sources. Bind every material claim to a
   source or mark it UNKNOWN. Do not infer buyer spending from general market
   interest, legal exposure, or vendor marketing.
4. Audit every candidate against every fixed mandatory gate in the ledger:
   `ai_essential`, `independent_demand`, `two_week_test`, `distribution`,
   `recurrence`, `economics`, `defensibility`, `risk`, and `validation_design`.
   `INVESTIGATE NOW` requires PASS for every gate. `WATCH` requires at least one
   MISSING gate and no FAIL. `REJECT` requires at least one FAIL. No disposition
   may be promoted by prose alone.
5. For every non-rejected candidate, record workload assumptions, model and
   infrastructure calls, human-review exposure, cost range, pricing
   hypothesis, gross-margin risk, and a cheaper fallback architecture.
6. Write the machine-readable ledger with a duplicate-key-rejecting JSON
   writer. Keep its candidate IDs and report section IDs exactly aligned.
7. Run deterministic validation directly:
   `python3 {env:FACTORY_DEV_OPENCODE_ROOT}/scripts/validate-rubberduck.py`
8. Capture the post-change receipt only after the report and ledger are
   complete:
   `bin/factory-dev doctor > /tmp/rubberduck-doctor-post.json`.
   Summarize both receipts in the ledger. A post receipt may be dirty and may
   have false write/launch readiness before commit; it must still be doctor
   ready, policy-valid, and free of errors and routing contradictions. A
   missing, malformed, or failed receipt is a blocker, not a pass.
9. Run the exact validator again, `git diff --check`, the focused Python tests, the
   pinned Node suite, and the full Python suite. Never claim completion from a
   report that has not passed the validator.

The validator is deliberately fail-closed. This command must not create a
product, contact buyers, purchase services, make compliance claims, or change
provider routes, budgets, credentials, issue state, or release state.
