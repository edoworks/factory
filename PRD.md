# Fresh factory product requirements

## Authority and provenance

The owner's 2026-10-06 decision selects edoworks/factory, a backup branch, closure
of the old issue backlog as superseded, and a fresh implementation from zero
code. Factory004 direction is sourced from published issue
[#130](https://github.com/edoworks/factory/issues/130), including its October 1
checkpoint. Restricted local Factory004 files were not accessed during this reset.
Exact original numeric budgets are unavailable; the limits below are new proposed
experiment limits, not quotations or silently inherited approvals.

## First product checkpoint

Generate a local pass-and-play prediction game for 2–6 people. The versioned JSON
spec supplies product identity, questions, options, points, phases and rules.
One command starts with a clean, pinned factory checkout and empty output and
emits runnable HTML/CSS/JavaScript, executable tests and a provenance manifest.
The generator must not read a Couch checkout, archive, Git blobs or network.
Original templates are allowed and explicitly listed; no old implementation is
copied. Product-specific question/rule data belongs in the spec.

Players pick or explicitly skip every question, may boost one pregame call,
and irreversibly lock before the host confirms outcomes. Courtesy handoff privacy
conceals picks until results are confirmed. Host previews results before confirming;
unlocked rounds cannot score. Misses/skips/voids score zero. Ties share ranks.
Reload preserves valid progress, invalid/corrupt saves visibly fail closed,
storage failure warns, reset removes only the generated product's key.

Acceptance: happy/failure/reload browser flows; engine rules and persistence
invariants; generated executable tests; deterministic regeneration into a second
empty directory; meaningful changed-question/scoring/branding spec changes behavior
without editing the generator. Reject unknown spec versions, unknown fields,
nonempty destinations, symlink/traversal/unsafe output paths. Fix the factory or
spec and regenerate rather than patching generated output.

## Parity ledger

| Capability | Existing Couch scope supplied as oracle | Fresh checkpoint target |
|---|---|---|
| Social game | Pregame/halftime calls, locks, boost, manual results, recap | Local generated core, bounded tests |
| Web persistence | Reload, recovery, history, offline installation | Reload only; history/PWA remain gaps |
| Native | Bundled iOS WKWebView, signing and distribution | Not implemented or qualified |
| Forecast Reviews | Separate local journal, Brier score, eligible optional on-device AI | Not implemented; no AI needed for social game |
| Legacy compatibility | Existing versioned saves, native wrappers | No migration claim; separate namespace |
| Own-phone/shared backend | Planned authenticated multi-device rooms | Planned, not existing parity |
| Physical device/release | Distinct evidence and owner gates | Not tested/released by this benchmark |

## Operating limits and stop rules

For this implementation checkpoint: local deterministic tooling only; zero paid
API calls/provisioning; no Xcode/simulator work; generation target under 10 seconds
and 5 MiB per app, verification target under 120 seconds and 100 MiB output
(browser scratch excluded and separately temporary). Measure durations and tool
versions, not guessed engineering cost. Owner intervention count must be reported;
this checkpoint requires no manual output patching.

Proposed shipping experiment gates, pending owner scheduling: Day 3 playable
generation; Day 7 observed useful on-device loop; Day 14 verified release candidate;
Day 21 owner-authorized submission target; Day 30 accepted available app or an
explicit outcome review. Dates are relative to an owner-selected experiment start,
not a promise of Apple processing. Before spending or distribution, agree human
time/cost/intervention caps and a specific submission date.

Kill or rescope if clean generation cannot be reproduced, core losses/corruption
remain, product work is displaced by framework work, or costs exceed agreed caps.
No Factory005 or multi-app generalization before a recorded outcome and distinct
replacement hypothesis. No claim of demand, retention, revenue or paid readiness
without direct evidence. Proposed quality thresholds: zero observed critical data
loss/authorization defects, all bounded acceptance tests pass, deterministic files
match, and no unsupported qualification claims.
