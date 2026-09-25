---
name: model-routing
description: Verify or repair Factory model routes and fallbacks through tracked evidence without improvising promotions or changing budgets.
---

# Factory Model Routing

`model-routing/approved.json` is the route registry and `policy.json` is the
provider and tier policy. Preserve their current cost and fallback semantics.

1. Check catalog freshness, capabilities, route variants, and current benchmark
   evidence before proposing a route change.
2. Never promote routine, standard, or vision routes without current benchmark
   evidence for the exact suite digest.
3. Complex and trust-boundary routes additionally require owner approval.
4. Run the cost-router tests and a config-hook smoke check after changes.
5. Record contradictions rather than changing budgets, providers, evidence
   timestamps, or fallback policy to force readiness.

## Refreshing Tracked Catalog Evidence

1. Generate the user catalog through the approved global procedure:
   `npm --prefix ~/.config/opencode run models:refresh`.
2. Import its route-relevant, non-secret subset from a normal terminal with
   `bin/factory-dev refresh-catalog`. The command accepts no source override,
   requires valid repository policy integrity, and reads only
   `~/.config/opencode/model-routing/catalog.json`.
3. Treat missing non-built-in routes and fallbacks as unavailable catalog
   evidence. Never retain an older `active` claim or change `approved.json` to
   make the import pass.
4. Re-run `bin/factory-dev doctor`; do not launch unless it reports
   `launch_ready: true`.

No benchmark or paid model call is implied by invoking this skill.
