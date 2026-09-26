Local issue #102 update (2026-09-25): the first Bash-carried URL design was
rejected by independent trust review because shell expansion could precede URL
validation. The corrected implementation is a structured OpenCode custom tool
with one URL field, no Bash browser permission, fixed Chrome Guest argv, strict
public Factory path/query/fragment validation, and a requested isolated browser
session. Follow-up review corrected the OpenCode 1.18.19 discovery extension and
duplicate tool-shaped export risk; final independent review found no material
implementation defect. Isolated review then identified a material authority
inconsistency between the later Safari-only issue comment and the Chrome Guest
privacy correction. The owner explicitly authorized Chrome Guest on 2026-09-25,
superseding that Safari-only comment while retaining all other authority and
privacy boundaries. The corrected head passes 82 Python tests and 20 pinned Node tests,
`git diff --check`, and launch-ready Factory doctor with valid policy and no
routing contradiction. The opener receipt now distinguishes LaunchServices
acceptance from observed Guest mode. Fresh autonomous opening of issue #102, PR
#76, and PR #76's exact PRD revision required no Bash command or approval prompt.
Temporary captures confirmed Chrome Guest, signed-out GitHub rendering, no
normal-profile account chrome, and no private content. The bounded post-merge
review of PR #76's 159-line exact PRD found no overlap, clipping, unreadable
wrapping, or later-state overclaim. PR #104's first Factory policy job failed in
a clean checkout because the workflow did not install the already pinned
OpenCode tool dependency before importing the tool in its Node suite. The local
correction adds a lockfile-bound `npm ci` step and a mechanical order assertion.
Corrected hosted run `36214255479` passed all three jobs. PR #104 merged exact
head `5780f09f8fd1e6150f69f05a740e923268984a51` as
`58f2406795309af0608d7138c7d9e60bab1f406d`; remote issue #102 is closed and the
pinned verifier returns `CLOSED`. The current OpenCode process loaded policy
before merge, so it cannot prove the required post-integration fresh launch.
Completion and notification remain blocked until a newly launched Factory
session verifies the merged opener.
