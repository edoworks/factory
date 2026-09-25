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

No benchmark or paid model call is implied by invoking this skill.
