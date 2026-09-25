# Factory Development Review Gaps

Date: 2026-09-24

Tracker: `edoworks/factory#69`

Status: corrected pending final review

## Evidence

Independent review found that the first development-environment draft allowed
unmatched shell commands, inherited OpenCode overrides, loaded an unpinned
auto-approval plugin, accepted unlisted policy files, and implemented a weaker
routing readiness check than the router itself.

## Why Chain

1. Why could a checksum-valid launch execute unreviewed behavior? The manifest
   checked listed files but did not reject additional files or inherited
   configuration sources.
2. Why were inherited sources possible? The launcher changed
   `XDG_CONFIG_HOME` but preserved higher-precedence OpenCode override variables
   and did not inspect target ancestors.
3. Why could shell mutations bypass intended gates? Permission rules named
   known command prefixes but had no deny-by-default rule, and `ask` was treated
   as an authority control despite auto-mode behavior.
4. Why could plugin behavior change without a policy digest change? The config
   loaded an unversioned third-party auto-approval plugin outside the manifest.
5. Why did tests pass? Fixtures asserted selected positive paths rather than
   adversarial configuration composition and closed-world inventory behavior.

Root cause supported by the review: the entry contract modeled repository files
as the complete policy boundary, while OpenCode composes policy from files,
environment variables, discovered project configuration, managed settings,
plugins, and permissive unmatched commands.

## Corrections

- The shell policy is deny-by-default, has no `ask` outcomes, denies issue
  mutations, and allows only explicit read, test, commit, canonical push, and
  factory PR command forms.
- The auto-approval plugin was removed from repository and active global config.
- Launch strips every `OPENCODE_*` variable and rejects target-ancestor and
  local managed configuration. Authenticated organization policy remains an
  explicit future review boundary rather than an isolation claim.
- Launch restores repository-owned no-autoupdate and no-model-catalog-fetch
  safety flags after removing ambient OpenCode variables.
- Doctor rejects unlisted files and symlinked paths outside generated
  `node_modules`, including a symlinked policy-source root.
- Doctor invokes the same cost-router configuration hook used at startup rather
  than approximating route readiness, but only after all integrity checks pass.
- Regression tests cover inherited overrides, ancestor config, unlisted files,
  symlinked policy directories, router digest failure, deny-by-default policy,
  and unclaimed later cutover states.

No remote mutation or deletion authority is inferred from these corrections.
