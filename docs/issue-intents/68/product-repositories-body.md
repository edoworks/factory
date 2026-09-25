# Outcome

Reconcile canonical ownership, tracker, policy boundaries, and retirement eligibility for each in-scope product repository without coupling product runtime to Factory development tooling.

# Scope

- Bind each product repository to its product-local PRD, evidence, release authority, and canonical issue tracker.
- Classify predecessor references as active dependency, narrow shared Factory contract, or historical provenance.
- Record archived, transferred, duplicate, and unknown repository states with exact identities and conservative retirement eligibility.
- Add guards that prevent product runtime from importing or requiring Factory development policy.

# Out of scope

- Removing the active predecessor-path dependencies already tracked by issue #70, changing product behavior, moving products into Factory, unarchiving or transferring repositories, publishing releases, or deleting remote or local repositories.

# Acceptance criteria

- Every in-scope product repository has one evidence-backed owner, tracker, PRD location, and release-authority disposition.
- Active product code and runtime do not import or require `development/opencode` or another development-tooling path.
- Unknown, archived, and historical repositories remain explicitly classified and are not inferred to be safe for deletion.
- Any overlap with issue #70 is linked rather than duplicated, and reusable Factory changes remain minimal and versioned.

# Verification

- Product-repository ownership and policy-boundary contract tests.
- Operational-reference scan with explicit historical/provenance allowances.
- Independent read-only cross-repository review.
- Product-specific tests only in repositories whose contracts change.

# Dependencies

- Parent consolidation map issue #68.
- Coordinate with issue #70 for active predecessor dependency removal.
- Consume the canonical portfolio index and private/public classification when those chunks are available.

# Authority and privacy

- This issue authorizes reversible inventory, repository-local documentation, and validation work only.
- It does not authorize repository setting changes, transfer, unarchive, publication, release, remote deletion, local cleanup, or credential broadening.
- Private repository metadata and product evidence must remain private unless separately approved.

# Source provenance

- `edoworks/factory` issues #68 and #70 and `docs/single-factory-cutover.md`.
- Current canonical Factory state at PR #76 feature head `97e17b0883c6fdacd6ab2fd85ad3dfc70a7f8719`, merged as `cf1ac7ade3b2e488e6c454cf3e3bca427891a2aa`.
- Product repository observations must record exact repository identity and inspected revision.

# Classification

Enhancement.

# Priority

P0.

# Triage review

- Duplicate review: issue #70 removes verified active predecessor dependencies; this chunk establishes repository ownership and authority dispositions and explicitly delegates dependency remediation to #70.
- Reprioritization review: ownership and authority must be explicit before preservation, repository-setting, or retirement decisions can be evaluated safely.
