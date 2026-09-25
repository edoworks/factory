# Outcome

Create one evidence-backed portfolio index that identifies current products, canonical repositories, lifecycle state, and owning issue without recreating a predecessor control plane.

# Scope

- Inventory active, parked, archived, and historical products across the inspected Edoworks and Foculoom repository surface.
- Record each product's canonical repository, visibility class, lifecycle state, owning tracker, and evidence revision.
- Add a freshness and uniqueness guard that rejects duplicate canonical ownership and unsupported active-state claims.

# Out of scope

- Rebuilding predecessor dashboards or orchestration, changing repository visibility, publishing product claims, moving product code into Factory, deleting repositories, or changing product qualification and release state.

# Acceptance criteria

- The index has exactly one canonical repository and owning tracker for each in-scope current product.
- Historical and unknown entries are distinguished from active products rather than silently omitted or promoted.
- Lifecycle and public-state claims cite current evidence and fail closed when stale or contradictory.
- Factory remains the software-factory authority without becoming the owner of product-specific PRDs or release evidence.

# Verification

- Repository inventory and duplicate-ownership contract tests.
- Freshness and contradiction checks against the inspected hosted state.
- Independent read-only review of lifecycle claims and exclusions.
- Rendered review if a public or human-facing index surface changes.

# Dependencies

- Parent consolidation map issue #68.
- The private/public classification chunk must define which hosted and local metadata may appear in public evidence.

# Authority and privacy

- This issue authorizes reversible repository-local inventory and validation work only.
- It does not authorize publication, visibility changes, repository transfer, product release, remote deletion, local cleanup, or disclosure of private repository metadata.
- Unknown visibility or lifecycle state must remain non-public and unclaimed.

# Source provenance

- `edoworks/factory` issue #68 and `docs/single-factory-cutover.md`.
- Current canonical Factory state at PR #76 feature head `97e17b0883c6fdacd6ab2fd85ad3dfc70a7f8719`, merged as `cf1ac7ade3b2e488e6c454cf3e3bca427891a2aa`.
- Hosted organization and repository observations must be revision- or timestamp-bound when collected.

# Classification

Enhancement.

# Priority

P0.

# Triage review

- Duplicate review: issue #48 reconciled organization repository and public state at an earlier snapshot; this chunk creates the continuing canonical portfolio ownership index required by the new single-factory strategy.
- Reprioritization review: the index is required before repository retirement decisions because missing or duplicate ownership can hide active obligations.
