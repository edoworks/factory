# Product Lifecycle Admission Gap

Date: 2026-09-25

## Impact

Issue #70 selected Vorynce for active product-repository work and the canonical
continuation later prescribed unarchiving and integrating its local feature
commit. The owner subsequently clarified that Vorynce is paused. No Vorynce
remote mutation succeeded, but the workflow treated repository mutability as the
remaining gate when product lifecycle was the prior authority gate.

## Evidence-Based 5-Whys

1. Why did the workflow prescribe unarchiving Vorynce? The reviewed feature push
   failed because GitHub reported the repository as archived and read-only.
2. Why was archive status treated as the remaining blocker? The selected issue
   increment assumed Vorynce was active from earlier product-ownership context.
3. Why was that assumption not invalidated before implementation? Admission
   checked repository identity and later checked mutability, but did not require
   a current owner-backed lifecycle state.
4. Why could a transport failure become a repository-setting action? The
   continuation converted the observed write constraint into an unarchive step
   without first asking whether the archive reflected a paused product.
5. Root cause supported by the issue and repository evidence: product-repository
   work had no fail-closed lifecycle admission contract preceding implementation,
   repository-setting, and integration decisions.

## Correction

- Issue #70 now records the owner clarification that Vorynce is paused.
- `docs/product-lifecycle-admissions.json` records the current machine-readable
  allowed and denied action set.
- Commit `f47cab8` remains local, unintegrated paused-product work. It is not
  completion or cutover evidence.
- The continuation no longer directs unarchive, push, or merge actions for
  Vorynce.
- The Factory Development PRD requires a current lifecycle admission record and
  a separate owner reactivation decision before work on a paused product.

## Recurrence Guard

`tests/test_single_factory_contract.py` requires the canonical lifecycle record
to mark Vorynce `PAUSED`, limit allowed actions to local evidence preservation
and read-only audit, deny unarchive, push, merge, and release, and keep Vorynce
out of restart actions. The same contract requires deletion readiness to
classify lifecycle, Git divergence, local overlays, tested preservation, and
exact targets rather than infer safety from archive state or `git status`.
