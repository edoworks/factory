# Open Issue Queue Audit

Date: 2026-09-22
Repository: `edoworks/factory`
Subject: open GitHub issues in `edoworks/factory`
Status: advisory, read-only audit

## Claim Under Review

The 17 open issues are mostly intentional roadmap work, qualification gates,
and owner-controlled decisions rather than 17 unresolved defects.

## Observations

- GitHub showed 17 open issues and 14 closed issues on 2026-09-22.
- Open issues fall into three visible groups: NowNest redesign (#28-#36),
  factory/reference-app roadmap and gates (#10-#18), and the human treatment
  decision (#32).
- The factory charter explicitly makes Apple submission, credential use,
  release publication, and customer engagement human-authorized actions.
- The open issue list and sampled issue metadata show no assignee or milestone
  for at least the newer NowNest items and issue #32.

## Classification

| Issues | Working classification | Evidence or next check |
|---|---|---|
| #29 | Completion candidate | Chunk A evidence records factory issue #29 and result commit `00357b4`; maintainer should verify closure. |
| #30, #34-#36 | Completion candidates | NowNest continuation records Chunk B and its B1-B3 PRs as merged; verify each child issue's evidence before closing. |
| #33 | Completion candidate with explicit downstream gate | Chunk C evidence records issue #33, result commit `c6c3194`, and 57/57 tests; physical VoiceOver/device checks are intentionally deferred to #32. |
| #28 | Active parent/map | Remains open while the redesign program and its human decision gate remain unresolved. |
| #32 | Active owner-only gate | Requires human comparison, physical accessibility observations, and an owner-approved decision; do not automate or infer completion. |
| #10 | Owner/external release gate | Reference App 1 Apple submission and acceptance. |
| #11 | Active qualification | 30-day factory qualification is time-bound and not equivalent to an implementation defect. |
| #12 | Owner gate for future app | Public identity and physical-device validation for Reference App 2. |
| #13 | Future implementation | Reference App 2 build using the future factory v0.2.0 path. |
| #14 | Owner/external release gate | Reference App 2 Apple submission and acceptance. |
| #15 | Owner-controlled administration | Freeze sf0.8 and publish successor notices. |
| #16 | Administrative disposition | Resolve open sf0.8 issues with successor links. |
| #17 | Owner-controlled administration | Archive predecessor repositories only after recovery proof. |
| #18 | Owner-only product gate | Assess paid-pilot readiness. |

This yields six likely completion candidates, two active NowNest items, and
nine roadmap, qualification, gate, or administrative items. The six are not
declared closed by this audit because GitHub issue state is maintainer-owned.

## Evidence, Inference, And Unknowns

The issue count, titles, labels, and open/closed totals are observations from
GitHub. The completion status of #29, #30, #33, and #34-#36 is an evidence-
backed inference from linked NowNest commits and retained evidence, not a live
GitHub closure decision. It remains unknown whether the owner intentionally
keeps completed child issues open until the parent map closes.

The queue therefore does not support the stronger claim that all 17 are active
work. It supports a narrower claim: the count combines real future gates with
at least six issues that warrant closure review.

## Disconfirming Test

For each open issue, record one of `active`, `blocked`, `owner-gated`,
`future`, `administrative`, or `completion-candidate`, together with an owner,
next action, evidence link, and review date. The roadmap explanation is
supported if every item has a valid category and next condition. It is
disconfirmed if completion candidates lack evidence, gates lack an owner or
decision condition, or future items have no target or dependency.

## Recommendation

Do not close or relabel issues automatically. A maintainer should first verify
the six completion candidates, close them or link their successor decision,
and add owner/next-action/review-date metadata to the remaining queue. Keep
Apple, productization, archival, and human-comparison gates open until their
human or external conditions are actually satisfied.

No issue mutation, publication, release action, or authority decision was
performed during this audit.
