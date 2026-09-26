# Open Issue Reconciliation

Date: 2026-09-26
Repository: `edoworks/factory`
Tracker: issue #116
Scope: 29 issues open before issue #116 was created

## Decision

Close exactly four issues without claiming their original acceptance criteria
completed:

| Issue | Disposition | Canonical successor or state |
|---|---|---|
| #15 | Superseded | Issue #68 replaced the Apple-dependent sf0.8 freeze sequence with immediate single-factory cutover and separately gated preservation and cleanup states. |
| #17 | Superseded | Issues #68 and #81 replaced archive-only retirement with exact-target inventory, private preservation, restore proof, dependency scans, and separate owner approvals. |
| #103 | Obsolete, unimplemented | PR #98 will be replaced through issue-isolated branches; issue #102 remains the bounded public-page review capability. No authenticated browser was accepted or installed. |
| #14 | Premature, not completed | Mews & Woofs remains an internal reference fixture. Issue #66 owns current qualification; any future Apple release requires a new lifecycle decision and owner-authorized release gate. |

The following 25 issues remain open after issue #116 closes:

- Factory and consolidation: #68, #70, #78, #79, #81, #99, #100, #108,
  #111, #112, and #113.
- Mews & Woofs: #12, #13, #64, #65, and #66.
- NowNest: #10, #28, #32, #42, #44, #45, and #54.
- Long-horizon Factory gates: #11 and #18.

Issues #12 and #13 retain stale `meow-capture` wording but remain active owner
and parent dependencies. Their wording requires later reconciliation; this audit
does not silently change or complete their gates.

## Non-Completion Boundaries

- No predecessor is preserved, archived, deleted, or locally cleaned by closing
  #15 or #17.
- No authenticated browser, dedicated profile, runtime, or screenshot boundary
  is implemented or accepted by closing #103.
- Issue #103's primary-checkout design files remain preserved and unclassified
  for deletion until a later hash-bound cleanup manifest is approved.
- No Mews & Woofs physical-device, household-media, public identity, Apple,
  release, or commercial gate is satisfied by closing #14.
- Closing one roadmap issue never advances another issue's acceptance state.

## Five Whys

1. Why did obsolete issues remain open? Later strategies added successor issues
   without reconciling the original issue state.
2. Why did successor links not trigger review? Issue creation and implementation
   were verified independently from the complete open queue.
3. Why was that unsafe? Open state continued to imply dependencies and approved
   future work that conflicted with current lifecycle and trust boundaries.
4. Why did prose not prevent recurrence? Several records described supersession,
   but no contract required the PRDs, continuation, and issue queue to agree.
5. Root cause: roadmap state lacked a mechanical cross-record assertion for
   superseded issue contracts.

## Recurrence Guard

`tests/test_single_factory_contract.py` binds this reconciliation record to the
Factory PRD, Mews & Woofs authority section, cutover record, and continuation.
It rejects restoration of #15 or #17 as active predecessor gates, #103 as an
implementation dependency, or #14 as the current Mews & Woofs release gate.
Future closures still require issue-specific evidence and remote closeout; this
guard does not infer completion from prose.

Historical frozen issue intents may still name the former dependencies. They
remain provenance records and are not current execution instructions.

## Verification

- Frozen issue #116 intent validates and remote readback matches.
- Local policy and contract suites, doctor, diff checks, independent review, and
  rendered review are required before integration.
- Hosted policy, iPhone, and iPad checks must pass on the exact PR head.
- After merge, each closure receives a revision-bound comment and the pinned
  closeout verifier must report `CLOSED` for #15, #17, #103, and #14.
