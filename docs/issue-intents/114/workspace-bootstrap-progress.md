Issue #114 local progress (2026-09-26): the owner authorized one exact guarded
bootstrap using merged issue #109 code after the loaded pre-#109 permission map
denied it before execution. The resulting registered workspace starts at
canonical merge `b588844`; the quarantined primary path set remained unchanged.
The permanent correction discovers the primary through shared Git metadata,
requires a registered clean launcher already contained in fresh canonical
`origin/main`, verifies its bytes against the committed blob, rejects executable
shared or per-worktree Git configuration, active hooks, replacements, and
grafts, accepts no repository path, and atomically checks branch ownership during
rollback. Independent trust review rejected the first implementation and its
critical/high findings were corrected. Final trust re-review reports no remaining
critical, high, or medium findings. Approved catalog refresh generation
`1790421641508-3284` removed the local freshness mismatch without changing route
policy. Local verification passes: 86 Python tests, 16 Node tests, pinned
TypeScript 5.8.2 check, policy-valid doctor with no routing contradictions, and
`git diff --check`. The canonical issue body was rendered and visually verified
in Safari. PR #115 was rendered and visually verified at exact head
`a5dcb77769f5d3f0bf182354b27967ab059128a9`; its Factory policy, iPhone, and
iPad hosted checks all passed. Integration, fresh-session successor creation
proof, and closeout remain pending.
