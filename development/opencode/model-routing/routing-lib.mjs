export function isCatalogFresh(catalog, maxAgeHours, now = Date.now()) {
  const refreshedAt = Date.parse(catalog?.refreshed_at);
  const age = now - refreshedAt;
  return Number.isFinite(refreshedAt) && age >= -300000 && age <= maxAgeHours * 3600000;
}

export function isBenchmarkCurrent(result, policy, expectedDigest, now = Date.now()) {
  const measuredAt = Date.parse(result?.measured_at);
  const age = now - measuredAt;
  return result?.status === "passed"
    && result.suite_version === policy.benchmark_suite_version
    && result.fixture_set_sha256 === expectedDigest
    && Number.isFinite(measuredAt)
    && age >= -300000
    && age <= policy.benchmark_max_age_days * 86400000;
}

export function supportsRoute(model, route) {
  if (!model || model.status !== "active") return false;
  const capabilities = model.capabilities ?? {};
  if (!capabilities.toolcall || !capabilities.input?.text || !capabilities.output?.text) return false;
  if (route.tier === "vision" && !(capabilities.input?.image && capabilities.attachment)) return false;
  if (["standard", "complex", "trust_boundary"].includes(route.tier) && !capabilities.reasoning) return false;
  return !route.variant || model.variants?.includes(route.variant);
}

export function classifyTitle(title, agent) {
  const normalized = title.toLowerCase();
  if (agent === "explore" || /\b(explore|map|locate|search)\b/.test(normalized)) return "routine_exploration";
  if (/\b(commit|bookkeeping|format|state edit|screenshot|crop|resize|ocr|rename|notify|notification|status check|status|doctor|verify|ledger|baseline|restart|cleanup|run command|run shell|shell command|bash|terminal|execute|log tail|issue (close|comment|update)|close issue)s?\b/.test(normalized)) return "deterministic_or_mechanical";
  if (/\b(review|rubberduck|recheck|audit|confirm|clearance)\b/.test(normalized)) return "review";
  return "construction_or_other";
}

export function assertTierCoherence(classification, tier, routeLabel) {
  if (["routine_exploration", "deterministic_or_mechanical"].includes(classification) && ["standard", "complex"].includes(tier)) {
    throw new Error(`routine-class task (${classification}) must not dispatch to a ${tier} route ${routeLabel}; use small, explore, or an approved routine route`);
  }
  return tier;
}
