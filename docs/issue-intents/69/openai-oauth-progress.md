Issue #101 clean-branch update (2026-09-25): the launcher guard, deterministic
non-disclosure test, PRD contract, incident, and frozen intent were extracted
from the classified mixed source onto a clean branch based on canonical merge
`0e36c03`. The change removes inherited `OPENAI_API_KEY` from the OpenCode
version probe and final child process without reading or changing saved
credentials. The frozen intent validates, remote issue readback returns `MATCH`,
`git diff --check` passes, and independent trust review found no material issue.
After the invocation correction below, the full Python and pinned Node suites
passed from the isolated root. Factory doctor reports valid policy, matching
active installation, no routing contradiction, and `launch_ready: true`. Exact
rendered review of issue #101, PR #106, the exact-revision PRD paragraph, and
both incident Five-Whys sections passed at implementation head `2a914b9` without
clipping, unreadable wrapping, or exposed credential material. PR #106 merged
final head `61e0565` as `28edd62`, and hosted run `36219860937` passed all three
jobs. A fresh launch from that canonical merge reported `launch_ready: true` and
completed one owner-controlled OAuth-backed request without credential
disclosure. Repository closeout integration and issue-state verification remain
required; doctor alone is not the live-request evidence.

The first external clean-worktree verification attempt failed closed because
Python was launched from an unrelated checkout and the clean worktree's pinned
OpenCode dependency had not been restored before Node tests. The incident record
contains the evidence-based 5-Whys. Rerun from the isolated repository root with
lockfile-bound `npm ci` before the Node suite; partial passing output is not
completion evidence. The corrected rooted rerun passed both full suites.
