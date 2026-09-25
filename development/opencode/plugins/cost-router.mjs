import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { benchmarkSuiteDigest } from "../model-routing/benchmark-suite.mjs";
import { assertTierCoherence, classifyTitle, isBenchmarkCurrent, isCatalogFresh, supportsRoute } from "../model-routing/routing-lib.mjs";
import { messageText, recordToolAttribution } from "./cost-router-lib.mjs";

const routingRoot = join(dirname(fileURLToPath(import.meta.url)), "..", "model-routing");
const agentTiers = Object.freeze({ small: "routine", title: "routine", summary: "routine", compaction: "routine", explore: "routine", "openai-routine": "routine", "ollama-cloud-routine": "routine", general: "standard", plan: "standard", build: "standard", "openai-standard": "standard", "frontier-build": "complex", "trust-review": "trust_boundary", vision: "vision", "ollama-cloud-vision": "vision" });
const sessions = new Map();

function modelName(route) { return `${route.provider}/${route.model}`; }

function availableRoute(route, catalogByName, qualified, policy) {
  if (supportsRoute(catalogByName.get(modelName(route)), route) && qualified(route)) return route;
  for (const item of route.fallbacks || []) {
    const fallback = Array.isArray(item) ? item[1] : item;
    if (fallback && supportsRoute(catalogByName.get(modelName(fallback)), fallback) && qualified(fallback)) return fallback;
  }
  const startup = route.startup_fallback && !(route.tier === "routine" && !policy.allow_routine_cloud_fallback) ? { ...route, ...route.startup_fallback } : null;
  return startup && supportsRoute(catalogByName.get(modelName(startup)), startup) && qualified(startup) ? startup : null;
}

function applyRoute(config, name, route, description, mode = "subagent") {
  config.agent ??= {};
  const existing = config.agent[name] ?? {};
  config.agent[name] = { ...existing, description: existing.description ?? description, mode: existing.mode ?? mode, model: modelName(route), ...(route.variant ? { variant: route.variant } : {}) };
}

export default async () => ({
  config: async (config) => {
    const [registry, catalog, policy, benchmarks] = await Promise.all(["approved.json", "catalog.json", "policy.json", "benchmarks.json"].map((name) => readFile(join(routingRoot, name), "utf8").then(JSON.parse)));
    if (!isCatalogFresh(catalog, policy.catalog_max_age_hours)) throw new Error("cost-router catalog is missing or stale; update repository routing evidence through the approved model-routing procedure");
    const catalogByName = new Map((catalog.models ?? []).map((model) => [model.full_name, model]));
    const evidence = new Map((benchmarks.results ?? []).map((result) => [`${result.provider}/${result.model}/${result.tier}`, result]));
    const qualified = (route) => !policy.auto_promotion_tiers.includes(route.tier) || isBenchmarkCurrent(evidence.get(`${route.provider}/${route.model}/${route.tier}`), policy, benchmarkSuiteDigest(route.tier, policy.tiers[route.tier].minimum_quality, policy.benchmark_suite_version));
    const routes = Object.fromEntries(Object.entries(registry.routes).map(([name, route]) => [name, availableRoute(route, catalogByName, qualified, policy)]));
    if (!routes.small || !routes.explore || !routes.general || !routes.plan || !routes.build) throw new Error("cost-router has no available primary or fallback route for a built-in agent");
    config.small_model = modelName(routes.small);
    config.agent ??= {};
    for (const name of ["title", "summary", "compaction"]) config.agent[name] = { ...(config.agent[name] ?? {}), model: modelName(routes.small) };
    applyRoute(config, "explore", routes.explore, "Fast, low-cost repository exploration.");
    applyRoute(config, "general", routes.general, "Cost-effective general-purpose subagent.");
    applyRoute(config, "plan", routes.plan, "Cost-effective planning agent.", "primary");
    applyRoute(config, "build", routes.build, "Cost-effective implementation agent.", "primary");
    const descriptions = { "trust-review": "High-risk trust-boundary reviewer.", "frontier-build": "Frontier construction escalation.", vision: "Visual verification agent.", "openai-routine": "OpenAI routine task agent.", "openai-standard": "OpenAI standard task agent.", "zen-routine": "OpenCode Zen routine task agent.", "zen-standard": "OpenCode Zen standard task agent.", "zen-frontier": "OpenCode Zen frontier agent.", "go-routine": "OpenCode Go routine agent.", "ollama-cloud-routine": "Ollama Cloud routine agent.", "ollama-cloud-vision": "Ollama Cloud vision agent.", "copilot-routine": "Copilot routine agent.", "copilot-standard": "Copilot standard agent.", "copilot-code": "Copilot code agent." };
    for (const [name, description] of Object.entries(descriptions)) if (routes[name]) applyRoute(config, name, routes[name], description);
  },
  "chat.params": async (input) => {
    const provider = input.model.providerID ?? input.provider.id;
    const tier = agentTiers[input.agent] ?? "standard";
    const classification = classifyTitle(messageText(input.message), input.agent);
    sessions.set(input.sessionID, { agent: input.agent, provider, model: input.model.id });
    if (sessions.size > 1000) sessions.delete(sessions.keys().next().value);
    assertTierCoherence(classification, tier, `${provider}/${input.model.id}`);
    if (classification !== "construction_or_other" && tier !== "routine") {
      throw new Error(`routine-class task (${classification}) must use a routine agent; refusing ${provider}/${input.model.id}`);
    }
  },
  "tool.execute.before": async (input) => {
    const session = sessions.get(input.sessionID);
    if (session) await recordToolAttribution({ sessionID: input.sessionID, ...session, tool: input.tool });
  }
});
