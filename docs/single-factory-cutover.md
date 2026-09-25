# Single-Factory Cutover Record

Date: 2026-09-24
Tracker: `edoworks/factory` issues #68 and #69
Inspected factory revision: `7ff54762c7c853055202a2d048b62a02714b6933`
Status: `CANONICAL_FOR_NEW_WORK` in progress; later states not claimed

## Verified Current State

- `edoworks/factory` is the sole tracker and destination for new reusable
  factory work.
- The predecessor-bound services below were unloaded and disabled on
  2026-09-24. Their definitions remain intact under
  `/Users/hello/Library/LaunchAgents`, outside proposed predecessor checkout
  cleanup targets.
- Direct Ollama remained available on `127.0.0.1:11434`; the unused sf0.1 proxy
  on `127.0.0.1:11435` was stopped.
- Active global OpenCode startup now loads the factory-owned progress policy,
  model-routing instructions, and cost-router plugin. Its sole continuation
  command is `continue-factory.md`; predecessor issue and PR mutation rules were
  removed from the global command policy.
- `bin/factory-dev doctor` reports valid policy, a matching active bootstrap,
  OpenCode `1.18.19`, and no routing contradiction. A fresh process loaded the
  local-config-isolated factory configuration and returned `FACTORY_CANONICAL`. The observed
  effective default Build route was `openai/gpt-5.6-luna` with no variant; no
  route was changed during consolidation.
- The expired local `ollama/granite4.1:3b` routine benchmark was rerun against
  the unchanged suite and passed on 2026-09-25. No paid benchmark or cloud
  fallback was used.
- No predecessor remote repository, local checkout, service definition, runner
  registration, backup, release, visibility, or credential was deleted or
  changed beyond the reversible local service disablement.

### Service Evidence

- `com.foculoom.factory-operator`: source `/Users/hello/sf0.5`; definition
  SHA-256 <code>b21dec0ca191ccfea5d5dd271054aea0<wbr>7b5daacd10b531a6a9f4838a214c669b</code>;
  unloaded and disabled.
- `com.foculoom.factory-worker-poller`: source `/Users/hello/sf0.5`;
  definition SHA-256
  <code>17eae791aad16dbda90cc741f39c4db7<wbr>8db1b33f6dcad4e7b003145ad0a780e8</code>;
  unloaded and disabled.
- `com.foculoom.sf07.device-watcher`: source `/Users/hello/sf0.7`;
  definition SHA-256
  <code>717a3105bf45aa7b562a71b1496c3c1<wbr>e0761cc847d1416eb3b035541913fb5c8</code>;
  unloaded and disabled.
- `actions.runner.edoworks-sf0.8.sf08-mac`: source
  `/Users/hello/actions-runner-sf08`; definition SHA-256
  <code>b6501e1ba20a9d1cd4871ecd87a6c55c<wbr>4b81e593919ad0d30db38e2108b7f6d3</code>;
  unloaded and disabled.
- `com.foculoom.ollama-nothink-proxy`: source `/Users/hello/sf0.1`;
  definition SHA-256
  <code>d17ebc511ce88c70b6b9ee2fcb4ece65<wbr>f34691df0f25308e35bdc5273487bf7b</code>;
  unloaded and disabled.

Runner registration checksum:
<code>531437682c16e9c85fdf3e79adbb540b<wbr>9db84d64da9ea9038c3f3985a3d71db9</code>.

## Trust-Gap 5-Whys

1. Why was predecessor disposition reported complete while predecessors still
   executed? Completion followed issue/document state rather than a process,
   configuration, and dependency rescan.
2. Why did issue state win over contradictory evidence? The closeout contract
   checked whether the issue was closed, not whether the cited manifest was
   current and internally complete.
3. Why was the manifest stale? It bound a 23-issue snapshot while later sf0.8
   work and issues continued, and no freshness guard invalidated the claim.
4. Why could later work continue? The former Charter delayed freeze until
   unrelated Apple milestones and retained predecessor CI and local automation.
5. Root cause supported by inspected evidence: repository strategy, issue
   closeout, and runtime/process state had no shared mechanical cutover gate.

Immediate correction: stop predecessor execution and move all new work to
factory issues. Root-cause correction in this increment: version development
policy in factory and mechanically prevent later cutover states from being
claimed in the record. Operational references, active services, preservation,
and issue freshness still require evidence before that state guard may advance.
The independent development-policy review and corrections are recorded in
`docs/incidents/2026-09-24-factory-dev-review-gaps.md`.

## Unknown Or Blocking

- Versioned OpenCode development source, local-config-isolated launcher, matching
  global bootstrap, and fresh-session policy load are verified. A bounded tool
  workflow from the fresh session remains part of final clean-room validation.
- Several active products still reference sf0.1 validators or policy.
- Predecessor Git/local overlays and hosted metadata are not yet fully
  preserved or recovery-tested.
- No approved durable preservation destination outside this machine's failure
  boundary has been verified.
- No remote or local predecessor target is ready for deletion approval.

## State Claims

| State | Result |
|---|---|
| `CANONICAL_FOR_NEW_WORK` | IN PROGRESS until this governance change is merged and continuation is installed |
| `OPERATIONALLY_CUT_OVER` | NOT VERIFIED |
| `PRESERVATION_VERIFIED` | NOT VERIFIED |
| `READY_FOR_OWNER_DELETION_APPROVAL` | NOT VERIFIED |
| `REMOTE_DELETION_COMPLETED` | NOT PERFORMED |
| `LOCAL_CLEANUP_COMPLETED` | NOT PERFORMED |
