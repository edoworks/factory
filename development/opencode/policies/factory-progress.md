# Incremental Factory Progress

For every non-trivial task, split work into small, independently verifiable
chunks and keep `edoworks/factory` issue state and repository evidence current.

- `edoworks/factory` is the sole canonical factory and issue tracker.
- Use one issue per work chunk. Do not claim completion until implementation,
  verification, review, integration, and issue closeout are confirmed.
- Preserve unrelated worktree changes and never bypass repository protections.
- Record an evidence-based 5-Whys and a mechanical recurrence guard for a
  material defect, failed verification, trust gap, or recurring workflow error.
- Observe CI through bounded snapshots; a queued self-hosted job without steps
  for 60 seconds is a runner-readiness blocker.
- Completion notifications use
  `{env:FACTORY_DEV_OPENCODE_ROOT}/scripts/notify-completion.mjs`; notification
  delivery is not completion evidence.
- GitHub writes require the authorized identity and explicit applicable
  authority. Never use `--admin`, force-push, or permission workarounds.
- Clean merged feature branches only after merge, containment, worktree, and
  protection checks pass. Ambiguity requires retaining the branch.
- Keep the repository continuation command current when priorities, scope,
  authority boundaries, source-of-truth locations, or blockers change.
- Final responses state changed files, verification, and blockers concisely.
