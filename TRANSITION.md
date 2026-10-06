# Owner-directed clean slate — 2026-10-06

Old main: `dab21a8a3a3859366639768ea1f42e2d1d7b15aa`.
Verified backup:
[`backup/pre-clean-slate-20261006T140606Z-dab21a8a`](https://github.com/edoworks/factory/tree/backup/pre-clean-slate-20261006T140606Z-dab21a8a),
at that exact SHA. Independent remote readback, local fetch, equal-tree comparison
and Git object integrity check passed before replacing local code.

The initial fully paginated inventory contained 38 open issues. Their bodies and
comments were preserved privately; public issue discussions remain in place.
They are superseded, not implemented. Open PR #120 and all preexisting branches
and worktrees are preserved. Closing its associated issue does not close its PR.

This branch is a normal descendant of old main, not orphaned or force-pushed.
The first transition commit intentionally retains only governance and compact
requirements/lessons. It removes the old implementation and old CI workflow from
this candidate. A following commit starts an original bounded generator.

Workflow impact: old factory CLI commands, Swift template, OpenCode development
environment, reference apps, compatibility promises and CI gate are unavailable
in this candidate. Historical consumers must continue pinning old revisions;
there is no drop-in compatibility claim or automatic migration. A new lightweight
check does not replace Apple/native qualification. Review this explicit break
before merging to main. Main remains unchanged; no PR, merge, release or deployment
is performed by this task.
