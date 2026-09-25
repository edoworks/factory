# Outcome

Classify consolidation evidence and preservation material as private or safe for public disclosure before any preservation or retirement state advances.

# Scope

- Define a field-level private/public classification contract for repository history, hosted metadata, local overlays, obligations, checksums, and recovery receipts.
- Inventory the evidence required by issue #68 and assign an owner-controlled storage class without exposing protected values.
- Add fail-closed checks that reject public evidence containing credentials, personal information, private metadata, or backup routing.

# Out of scope

- Publishing private artifacts, changing repository visibility, deleting repositories or local paths, broadening credentials, or claiming preservation and deletion-readiness states.

# Acceptance criteria

- Every required consolidation evidence class has an explicit private or public-safe disposition.
- Public records contain only safe provenance, inventory, checksum, and recovery references.
- Unknown or sensitive material defaults to private, and a mechanical guard rejects prohibited public fields.
- The result is referenced by issue #68 without embedding secrets or private payloads.

# Verification

- Focused classification and redaction contract tests.
- Secret and privacy scan of tracked public evidence.
- Independent read-only review of the classification boundary and state claims.
- `git diff --check` and the applicable Factory policy suite.

# Dependencies

- Parent consolidation map issue #68.
- An owner-controlled private preservation destination remains required before `PRESERVATION_VERIFIED` can be claimed.

# Authority and privacy

- This issue authorizes reversible repository-local classification and validation work only.
- It does not authorize publication, visibility changes, credential access or broadening, remote deletion, local cleanup, purchases, or release actions.
- Sensitive and ambiguous material must remain private.

# Source provenance

- `edoworks/factory` issue #68 and `docs/single-factory-cutover.md`.
- Factory development PRD cutover-state and privacy controls at feature head `97e17b0883c6fdacd6ab2fd85ad3dfc70a7f8719`, merged by PR #76 as `cf1ac7ade3b2e488e6c454cf3e3bca427891a2aa`.

# Classification

Enhancement.

# Priority

P0.

# Triage review

- Duplicate review: issue #17 covers predecessor archiving after recovery proof, while this chunk defines the private/public evidence boundary required before that proof; it does not perform archival or deletion.
- Reprioritization review: this boundary precedes preservation and retirement work because misclassified evidence could disclose protected material or create unverifiable state claims.
