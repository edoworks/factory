#!/usr/bin/env node
import { createHash } from "node:crypto";
import { lstat, mkdir, readFile, rename, rm, writeFile } from "node:fs/promises";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { isCatalogFresh, supportsRoute } from "../model-routing/routing-lib.mjs";

const scriptPath = fileURLToPath(import.meta.url);
const defaultRoot = join(dirname(scriptPath), "..");
const requiredAgents = new Set(["small", "explore", "general", "plan", "build"]);

function fail(message) {
  throw new Error(message);
}

function object(value, label) {
  if (!value || typeof value !== "object" || Array.isArray(value)) fail(`${label} must be an object`);
  return value;
}

function strings(value, label) {
  if (!Array.isArray(value) || value.some((item) => typeof item !== "string" || !item)) fail(`${label} must be an array of non-empty strings`);
  return value;
}

function sha256(text) {
  return createHash("sha256").update(text).digest("hex");
}

function modelName(route) {
  if (typeof route?.provider !== "string" || typeof route?.model !== "string") fail("route provider and model must be strings");
  return `${route.provider}/${route.model}`;
}

function sanitizedModel(model) {
  object(model, "catalog model");
  const expected = `${model.provider}/${model.model}`;
  if (model.full_name !== expected) fail(`catalog model identity mismatch: ${model.full_name ?? "UNKNOWN"}`);
  if (typeof model.status !== "string" || !model.status) fail(`catalog model status missing: ${expected}`);
  const capabilities = object(model.capabilities, `catalog capabilities for ${expected}`);
  const input = object(capabilities.input, `catalog input capabilities for ${expected}`);
  const output = object(capabilities.output, `catalog output capabilities for ${expected}`);
  const variants = strings(model.variants, `catalog variants for ${expected}`);
  return {
    full_name: expected,
    provider: model.provider,
    model: model.model,
    status: model.status,
    capabilities: {
      reasoning: capabilities.reasoning === true,
      attachment: capabilities.attachment === true,
      toolcall: capabilities.toolcall === true,
      input: { text: input.text === true, image: input.image === true },
      output: { text: output.text === true },
    },
    variants: [...variants],
  };
}

function missingModel(route) {
  return {
    full_name: modelName(route),
    provider: route.provider,
    model: route.model,
    status: "missing",
    capabilities: {
      reasoning: false,
      attachment: false,
      toolcall: false,
      input: { text: false, image: false },
      output: { text: false },
    },
    variants: [],
  };
}

function routeReferences(registry) {
  const references = new Map();
  const add = (route, required, label) => {
    object(route, label);
    const name = modelName(route);
    const previous = references.get(name);
    references.set(name, { route, required: required || previous?.required === true, labels: [...(previous?.labels ?? []), label] });
  };
  for (const [name, route] of Object.entries(object(registry.routes, "approved routes"))) {
    if (route.disabled === true) continue;
    add(route, requiredAgents.has(name), `route ${name}`);
    for (const [index, item] of (route.fallbacks ?? []).entries()) {
      const fallback = Array.isArray(item) ? item[1] : item;
      if (fallback) add({ ...route, ...fallback }, false, `route ${name} fallback ${index}`);
    }
    if (route.startup_fallback) add({ ...route, ...route.startup_fallback }, false, `route ${name} startup fallback`);
  }
  return references;
}

export function buildRoutingSnapshot(source, registry, policy, current, now = Date.now()) {
  object(source, "source catalog");
  object(registry, "approved registry");
  object(policy, "routing policy");
  object(current, "current catalog");
  if (source.schema_version !== 1 || registry.schema_version !== 1 || policy.schema_version !== 1) fail("unsupported routing schema version");
  if (typeof source.generation !== "string" || !/^\d+-\d+$/.test(source.generation)) fail("source catalog generation is invalid");
  if (!isCatalogFresh(source, policy.catalog_max_age_hours, now)) fail("source catalog is missing or stale");
  const sourceTime = Date.parse(source.refreshed_at);
  const currentTime = Date.parse(current.refreshed_at);
  if (Number.isFinite(currentTime) && sourceTime < currentTime) fail("source catalog is older than the tracked catalog");

  const sourceProviders = strings(source.providers, "source catalog providers");
  if (new Set(sourceProviders).size !== sourceProviders.length) fail("source catalog providers contain duplicates");
  const enabledProviders = Object.entries(object(policy.providers, "routing providers"))
    .filter(([, value]) => object(value, "provider policy").enabled === true)
    .map(([name]) => name);
  const missingProviders = enabledProviders.filter((provider) => !sourceProviders.includes(provider));
  if (missingProviders.length) fail(`source catalog omitted enabled providers: ${missingProviders.join(", ")}`);
  if (!Array.isArray(source.failures) || source.failures.length) fail("source catalog contains provider failures");
  if (!Array.isArray(source.models) || !source.models.length) fail("source catalog contains no models");

  const available = new Map();
  for (const raw of source.models) {
    const model = sanitizedModel(raw);
    if (available.has(model.full_name)) fail(`source catalog contains duplicate model: ${model.full_name}`);
    available.set(model.full_name, model);
  }

  const models = [];
  const missing = [];
  for (const [name, reference] of routeReferences(registry)) {
    const model = available.get(name);
    if (!model) {
      if (reference.required) fail(`source catalog omitted required built-in route model: ${name}`);
      models.push(missingModel(reference.route));
      missing.push(name);
      continue;
    }
    if (reference.required && !supportsRoute(model, reference.route)) fail(`source catalog model cannot serve required built-in route: ${name}`);
    models.push(model);
  }
  models.sort((left, right) => left.full_name < right.full_name ? -1 : left.full_name > right.full_name ? 1 : 0);
  return {
    snapshot: {
      schema_version: 1,
      generation: source.generation,
      refreshed_at: source.refreshed_at,
      providers: [...sourceProviders],
      failures: [],
      models,
    },
    missing: missing.sort(),
  };
}

async function regularFile(path, label) {
  const stats = await lstat(path);
  if (!stats.isFile() || stats.isSymbolicLink()) fail(`${label} must be a regular non-symlink file`);
  return stats;
}

async function replaceFile(path, temporary, content, mode) {
  await writeFile(temporary, content, { flag: "wx", mode: mode & 0o777 });
  await rename(temporary, path);
}

export async function importRoutingCatalog({ root = defaultRoot, sourcePath = join(homedir(), ".config", "opencode", "model-routing", "catalog.json"), now = Date.now() } = {}) {
  const routingRoot = join(root, "model-routing");
  const catalogPath = join(routingRoot, "catalog.json");
  const registryPath = join(routingRoot, "approved.json");
  const policyPath = join(routingRoot, "policy.json");
  const manifestPath = join(root, "policy-manifest.json");
  const lockPath = join(root, ".catalog-import.lock");
  const catalogTemporary = join(routingRoot, `.catalog.json.${process.pid}.tmp`);
  const manifestTemporary = join(root, `.policy-manifest.json.${process.pid}.tmp`);
  const rollbackTemporary = join(routingRoot, `.catalog.json.${process.pid}.rollback`);

  const [sourceStats, catalogStats, manifestStats] = await Promise.all([
    regularFile(sourcePath, "source catalog"),
    regularFile(catalogPath, "tracked catalog"),
    regularFile(manifestPath, "policy manifest"),
  ]);
  if ((typeof process.getuid === "function" && sourceStats.uid !== process.getuid()) || (sourceStats.mode & 0o022)) {
    fail("source catalog must be owned by the current user and not group/world writable");
  }
  const [sourceText, registryText, policyText, catalogText, manifestText] = await Promise.all([
    readFile(sourcePath, "utf8"),
    readFile(registryPath, "utf8"),
    readFile(policyPath, "utf8"),
    readFile(catalogPath, "utf8"),
    readFile(manifestPath, "utf8"),
  ]);
  const manifest = JSON.parse(manifestText);
  if (manifest?.files?.["model-routing/catalog.json"] !== sha256(catalogText)) fail("tracked catalog does not match the policy manifest");
  const { snapshot, missing } = buildRoutingSnapshot(
    JSON.parse(sourceText),
    JSON.parse(registryText),
    JSON.parse(policyText),
    JSON.parse(catalogText),
    now,
  );
  const nextCatalog = `${JSON.stringify(snapshot, null, 2)}\n`;
  const nextManifest = {
    ...manifest,
    files: { ...manifest.files, "model-routing/catalog.json": sha256(nextCatalog) },
  };
  const nextManifestText = `${JSON.stringify(nextManifest, null, 2)}\n`;

  await mkdir(lockPath);
  let catalogReplaced = false;
  try {
    await replaceFile(catalogPath, catalogTemporary, nextCatalog, catalogStats.mode);
    catalogReplaced = true;
    await replaceFile(manifestPath, manifestTemporary, nextManifestText, manifestStats.mode);
  } catch (error) {
    if (catalogReplaced) await replaceFile(catalogPath, rollbackTemporary, catalogText, catalogStats.mode);
    throw error;
  } finally {
    await Promise.all([
      rm(catalogTemporary, { force: true }),
      rm(manifestTemporary, { force: true }),
      rm(rollbackTemporary, { force: true }),
      rm(lockPath, { recursive: true, force: true }),
    ]);
  }
  return { generation: snapshot.generation, refreshed_at: snapshot.refreshed_at, models: snapshot.models.length, missing };
}

if (process.argv[1] === scriptPath) {
  try {
    process.stdout.write(`${JSON.stringify(await importRoutingCatalog())}\n`);
  } catch (error) {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exitCode = 1;
  }
}
