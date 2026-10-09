# Contributing

Use a separate branch and reviewable change in edoworks/factory. Preserve existing
worktrees. Follow the PRD and change one product capability at a time. Add executable
failure cases where they protect real behavior. Before merging, run the documented
new acceptance commands and review the transition's compatibility breaks.

Do not use the removed predecessor development launcher as a prerequisite. The
owner's clean-slate instruction supersedes the old open-issue bootstrap dependency.
New work can be tracked after the old backlog reset; this local authorized candidate
does not claim an old issue was implemented. No default-branch merge is authorized.

MIT license and trademark policy remain unchanged. Report vulnerabilities privately
using SECURITY.md. No credentials, private paths, customer records or private
snapshot exports belong in commits or public issue comments.

## Active product evidence

Before implementing or expanding an active product, include one `## Factory reuse
and contribution` section in its PRD, with a fenced JSON declaration accepted by
`requirements.py`. Inspect the current factory, established platform APIs and the
existing Edoworks artifact catalog before proposing a general component. Record
verified existing capabilities, required gaps and the smallest testable contribution;
record an explicit stop disposition when no recurring consumer need is demonstrated.
Use the current PRD section as the compact format. Do not bulk rewrite historical,
held or archived PRDs; this check applies to the explicitly selected active PRD.
Existing product/account holds and ownership remain authoritative.

Run `python3 -B requirements.py path/to/active/PRD.md` before a handoff. The factory
benchmark runs this gate against its committed PRD and includes the declaration
result in its receipt. Run `python3 -B -m unittest discover -s tests -p 'test_*.py' -v`
for the existing regression suite. Generation-only commands remain generation-only;
this gate does not change version-1 product specs or confer verification on them.

Each capability declares source reference/revision/license/attribution, artifact
SHA-256, narrow scope, limitations, consumer/interface, evidence, gap disposition,
and a contribution with a behavior test. Use JSON `null` for unknown facts.
Statuses mean:

- `unknown`: insufficient evidence; missing facts are explicit.
- `candidate`: inspected or proposed within the stated limits, not adopted.
- `verified`: a passing local receipt supports only the exact artifact and scope.
- `reused`: additionally, that receipt identifies a real consumer and interface,
  with license and attribution recorded.

An evidence reference is a PRD-relative path plus SHA-256. Its JSON receipt has
exact fields `result` (`passed`, `failed`, `not_run`), `source` (matching `reference`
and `revision`), `recorded_at` (ISO timestamp with timezone), `artifact_sha256`, `scope`,
`command`, `environment`, `consumer`, and `interface`. Commands are descriptive
text, never executed by the validator. Promoted claims require a matching passing
receipt; reused claims also require matching consumer/interface evidence. Candidate
and unknown declarations may omit receipts. Do not promote a status solely to pass
this gate: a hash verifies bytes, not truth. Review the underlying execution,
source/version, license and actual consumer; a fabricated but consistent receipt
can pass structural checks. `declarations_valid` is not an authenticity, security,
product-fit, licensing or release verdict. Keep private evidence private; use a
candidate/unknown public declaration when its support cannot be shared safely.

The clean-slate/no-old-code constraint applies to the original benchmark's source
provenance, not a permanent ban on reviewed, licensed future reuse. Its existing
`product_source_reuse: false` manifest remains accurate and unchanged. No native
runner, PDF platform, dependency adoption or historical product revival follows
from this workflow requirement. The Safe Share example in
`tests/fixtures/safe-share-prd.md` illustrates a candidate with recorded synthetic
results and unresolved gaps; it is not an active product approval.
