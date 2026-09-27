# Unsupported Rubberduck Promotion

Date: 2026-09-26
Status: contained by issue #113; no product decision is authorized

## Evidence-Based 5-Whys

1. Why could a candidate appear ready for investigation? The report used a
   disposition without a machine-checked gate ledger.
2. Why was the disposition not mechanically constrained? Research prose and
   decision state had no closed schema or duplicate-key rejection.
3. Why could missing demand and economics be overlooked? Mandatory gates were
   described conceptually but not required per candidate with dated evidence.
4. Why was completion easy to overstate? Doctor evidence and research evidence
   were not bound to pre/post receipts in one validator-owned record.
5. Root cause supported by the preserved intent and progress record: research
   qualification lacked a repository-owned, fail-closed evidence boundary.

## Recurrence Guard

`python3 development/opencode/scripts/validate-rubberduck.py` is invoked
directly in CI before the
full Python suite. It rejects duplicate JSON keys, unknown schema fields,
unbound or empty evidence, PASS records without an exact candidate/gate and
complete source/assertion set in the validator-owned approval map, unlabeled or unknown-source report
bullets, candidate/section drift, unsupported dispositions, missing
non-rejected unit economics, absent no-candidate language, and pre/post
`bin/factory-dev doctor` summaries that differ from the validator-owned approval
record. CI additionally recomputes the complete policy-source inventory and
every policy-manifest digest, so current policy integrity cannot be replaced by
a ledger boolean. A future promotion or receipt claim therefore requires a
reviewable validator change and cannot pass by editing only report or ledger
prose.

## Verification-State Test Failure 5-Whys

1. Why did the first full local suite fail? The command contract regex omitted
   Markdown backticks, and two validator tests still expected the deliberately
   pending post receipt after the real receipt had been approved.
2. Why were those assertions stale? Verification-state changes updated the
   command and canonical ledger without updating tests that encoded their prior
   textual and pending-state representations.
3. Why did implementation behavior remain intact? The command contained the
   required gate text, and the validator correctly accepted the newly approved
   receipt; the failures were expectation drift rather than a bypass.
4. Why is expectation drift material? A failing pinned Node test also fails the
   full Python suite that invokes it, obscuring any later implementation defect.
5. Root cause: state-transition edits and their exact contract assertions were
   not treated as one atomic verification update.

The recurrence guard is to update pending/success receipt tests in the same
patch as the validator-owned approval record, assert the exact Markdown token
shape, and rerun both the focused Node test and full Python suite before
interpreting any other result.

## Development-Boundary Verification 5-Whys

1. Why did the corrected full suite still fail? The validator was placed under
   the root `scripts` directory, which the runtime-boundary test treats as a
   product surface.
2. Why was that placement wrong? The validator imports and verifies
   repository-owned OpenCode policy, so it is Factory development tooling.
3. Why was the boundary missed? CI invocation convenience was prioritized over
   the PRD rule that product runtime must not require development tooling.
4. Why did a permission test also fail? Its exact pinned Node command still
   encoded the suite before the Rubberduck contract test was added.
5. Root cause: new development verification was wired by command path without
   first classifying its ownership boundary and updating every exact permission
   assertion.

The mechanical guard is the existing runtime-dependency scan plus exact policy
permission assertions. The validator now lives under
`development/opencode/scripts`, and both its direct permission and the complete
pinned Node command are asserted.

## Policy-Bytecode Verification 5-Whys

1. Why did the next full suite invalidate several doctor fixtures? Importing the
   validator created a Python bytecode cache inside the closed policy tree.
2. Why did that cache affect unrelated doctor tests? Fixtures copied the policy
   source after the unlisted generated file appeared.
3. Why was the generated file unlisted? Policy intentionally excludes mutable
   runtime artifacts; adding a cache hash would make integrity interpreter-
   specific and nondeterministic.
4. Why did the focused validator appear valid first? Direct script execution did
   not create the import cache; the later unittest import did.
5. Root cause: the new test imported a module from a closed-world source tree
   without disabling Python bytecode emission.

The mechanical guard sets `sys.dont_write_bytecode` before loading the validator,
retains the closed-world policy inventory, removes only the observed generated
cache, and reruns the full suite from a cache-free tree.
