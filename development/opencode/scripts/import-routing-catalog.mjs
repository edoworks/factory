#!/usr/bin/env node
import { createHash, randomUUID } from "node:crypto";
import { constants } from "node:fs";
import { chmod, lstat, mkdir, open, rename, rm } from "node:fs/promises";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { DatabaseSync } from "node:sqlite";
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
  if (!Array.isArray(value) || value.some((item) => typeof item !== "string" || !item || item.length > 256 || /[\u0000-\u001f\u007f]/.test(item))) {
    fail(`${label} must be an array of bounded non-empty strings`);
  }
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
  if (typeof model.provider !== "string" || !model.provider || typeof model.model !== "string" || !model.model) {
    fail("catalog model provider and model must be non-empty strings");
  }
  const expected = `${model.provider}/${model.model}`;
  if (model.full_name !== expected) fail(`catalog model identity mismatch: ${model.full_name ?? "UNKNOWN"}`);
  if (!new Set(["active", "missing"]).has(model.status)) fail(`catalog model status is invalid: ${expected}`);
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
    if (route.variant !== null && route.variant !== undefined && (typeof route.variant !== "string" || !route.variant)) {
      fail(`${label} variant must be a non-empty string or null`);
    }
    references.set(name, {
      route,
      required: required || previous?.required === true,
      requirements: [...(previous?.requirements ?? []), { route, required, label }],
      variants: new Set([...(previous?.variants ?? []), ...(route.variant ? [route.variant] : [])]),
    });
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
  const policyProviders = Object.entries(object(policy.providers, "routing providers"));
  const enabledProviders = policyProviders
    .filter(([, value]) => object(value, "provider policy").enabled === true)
    .map(([name]) => name);
  const missingProviders = enabledProviders.filter((provider) => !sourceProviders.includes(provider));
  if (missingProviders.length) fail(`source catalog omitted enabled providers: ${missingProviders.join(", ")}`);
  if (!Array.isArray(source.failures) || source.failures.length) fail("source catalog contains provider failures");
  if (!Array.isArray(source.models) || !source.models.length) fail("source catalog contains no models");

  const available = new Map();
  const observed = new Set();
  for (const raw of source.models) {
    const model = sanitizedModel(raw);
    if (observed.has(model.full_name)) fail(`source catalog contains duplicate model: ${model.full_name}`);
    observed.add(model.full_name);
    if (model.status === "active") available.set(model.full_name, model);
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
    for (const requirement of reference.requirements.filter((item) => item.required)) {
      if (!supportsRoute(model, requirement.route)) fail(`source catalog model cannot serve required built-in route: ${name} (${requirement.label})`);
    }
    models.push({ ...model, variants: model.variants.filter((variant) => reference.variants.has(variant)) });
  }
  models.sort((left, right) => left.full_name < right.full_name ? -1 : left.full_name > right.full_name ? 1 : 0);
  return {
    snapshot: {
      schema_version: 1,
      generation: source.generation,
      refreshed_at: source.refreshed_at,
      providers: policyProviders.map(([name]) => name).filter((name) => sourceProviders.includes(name)),
      failures: [],
      models,
    },
    missing: missing.sort(),
  };
}

async function readRegularFile(path, label, { privateFile = false } = {}) {
  let handle;
  try {
    handle = await open(path, constants.O_RDONLY | constants.O_NOFOLLOW);
    const stats = await handle.stat();
    if (!stats.isFile()) fail(`${label} must be a regular non-symlink file`);
    if (privateFile && ((typeof process.getuid === "function" && stats.uid !== process.getuid()) || (stats.mode & 0o022))) {
      fail(`${label} must be owned by the current user and not group/world writable`);
    }
    return { text: await handle.readFile("utf8"), stats };
  } catch (error) {
    if (error?.code === "ELOOP") fail(`${label} must be a regular non-symlink file`);
    throw error;
  } finally {
    await handle?.close();
  }
}

async function syncDirectory(path) {
  const handle = await open(path, constants.O_RDONLY);
  try {
    await handle.sync();
  } finally {
    await handle.close();
  }
}

async function writeDurable(path, content, mode) {
  const handle = await open(path, constants.O_WRONLY | constants.O_CREAT | constants.O_EXCL, mode & 0o777);
  try {
    await handle.writeFile(content, "utf8");
    await handle.sync();
  } finally {
    await handle.close();
  }
}

async function replaceFile(path, temporary, content, mode) {
  try {
    await writeDurable(temporary, content, mode);
    await rename(temporary, path);
    await syncDirectory(dirname(path));
  } finally {
    await rm(temporary, { force: true });
  }
}

function transactionEntry(value, label) {
  object(value, label);
  if (typeof value.old !== "string" || typeof value.next !== "string" || !Number.isInteger(value.mode)) fail(`${label} is invalid`);
  if (value.old_sha256 !== sha256(value.old) || value.next_sha256 !== sha256(value.next)) fail(`${label} digest is invalid`);
  return value;
}

async function coordinationDatabase(path) {
  let existed = true;
  try {
    const stats = await lstat(path);
    if (!stats.isFile() || stats.isSymbolicLink() || (typeof process.getuid === "function" && stats.uid !== process.getuid()) || (stats.mode & 0o077)) {
      fail("catalog coordination database is unsafe");
    }
  } catch (error) {
    if (error?.code !== "ENOENT") throw error;
    existed = false;
  }
  const database = new DatabaseSync(path);
  if (!existed) {
    await chmod(path, 0o600);
    await syncDirectory(dirname(path));
  }
  database.exec("PRAGMA journal_mode = DELETE; PRAGMA synchronous = FULL; PRAGMA busy_timeout = 0");
  return database;
}

async function coordinationRoot(root) {
  const legacy = join(dirname(root), ".opencode-catalog-import.lock");
  try {
    await lstat(legacy);
    fail("legacy catalog import lock requires verified process quiescence");
  } catch (error) {
    if (error?.code !== "ENOENT") throw error;
  }
  const path = join(dirname(root), ".opencode-catalog-import-v2");
  try {
    await mkdir(path, { mode: 0o700 });
    await syncDirectory(dirname(path));
  } catch (error) {
    if (error?.code !== "EEXIST") throw error;
  }
  const stats = await lstat(path);
  if (!stats.isDirectory() || stats.isSymbolicLink() || (typeof process.getuid === "function" && stats.uid !== process.getuid()) || (stats.mode & 0o077)) {
    fail("catalog coordination directory is unsafe");
  }
  return path;
}

function journalRow(database) {
  return database.prepare("SELECT generation, journal_json FROM routing_import WHERE singleton = 1").get();
}

function persistJournal(database, generation, journal) {
  database.exec("BEGIN IMMEDIATE");
  try {
    database.prepare("INSERT OR REPLACE INTO routing_import (singleton, generation, journal_json) VALUES (1, ?, ?)").run(generation, JSON.stringify(journal));
    database.exec("COMMIT");
  } catch (error) {
    database.exec("ROLLBACK");
    throw error;
  }
}

function clearJournal(database, generation) {
  database.exec("BEGIN IMMEDIATE");
  try {
    database.prepare("DELETE FROM routing_import WHERE singleton = 1 AND generation = ?").run(generation);
    database.exec("COMMIT");
  } catch (error) {
    database.exec("ROLLBACK");
    throw error;
  }
}

async function recoverLocked(root, coordination, database) {
  const row = journalRow(database);
  if (!row) return { recovered: false };
  const journal = object(JSON.parse(row.journal_json), "catalog import transaction");
  if (journal.schema_version !== 1) fail("catalog import transaction schema is invalid");
  const catalog = transactionEntry(journal.catalog, "catalog import transaction catalog");
  const manifest = transactionEntry(journal.manifest, "catalog import transaction manifest");
  const catalogPath = join(root, "model-routing", "catalog.json");
  const manifestPath = join(root, "policy-manifest.json");
  const currentCatalog = (await readRegularFile(catalogPath, "tracked catalog")).text;
  const currentManifest = (await readRegularFile(manifestPath, "policy manifest")).text;
  const catalogState = currentCatalog === catalog.old ? "old" : currentCatalog === catalog.next ? "next" : "unknown";
  const manifestState = currentManifest === manifest.old ? "old" : currentManifest === manifest.next ? "next" : "unknown";
  if (catalogState === "unknown" || manifestState === "unknown") fail("catalog import transaction does not match tracked files");
  if (catalogState !== manifestState) {
    await replaceFile(catalogPath, join(coordination, `catalog.${randomUUID()}.rollback`), catalog.old, catalog.mode);
    await replaceFile(manifestPath, join(coordination, `manifest.${randomUUID()}.rollback`), manifest.old, manifest.mode);
  }
  clearJournal(database, row.generation);
  return { recovered: true, action: catalogState === manifestState ? `accepted-${catalogState}` : "rolled-back" };
}

async function withImportMutex(root, action) {
  const coordination = await coordinationRoot(root);
  const mutex = await coordinationDatabase(join(coordination, "mutex.sqlite"));
  let locked = false;
  try {
    mutex.exec("BEGIN IMMEDIATE");
    locked = true;
    const journal = await coordinationDatabase(join(coordination, "journal.sqlite"));
    try {
      journal.exec("CREATE TABLE IF NOT EXISTS routing_import (singleton INTEGER PRIMARY KEY CHECK (singleton = 1), generation TEXT NOT NULL, journal_json TEXT NOT NULL)");
      return await action(coordination, journal);
    } finally {
      journal.close();
    }
  } finally {
    if (locked) mutex.exec("COMMIT");
    mutex.close();
  }
}

export async function recoverRoutingCatalog({ root = defaultRoot } = {}) {
  return withImportMutex(root, (coordination, journal) => recoverLocked(root, coordination, journal));
}

export async function importRoutingCatalog({ root = defaultRoot, sourcePath = join(homedir(), ".config", "opencode", "model-routing", "catalog.json"), now = Date.now(), afterCatalogReplace } = {}) {
  const routingRoot = join(root, "model-routing");
  const catalogPath = join(routingRoot, "catalog.json");
  const registryPath = join(routingRoot, "approved.json");
  const policyPath = join(routingRoot, "policy.json");
  const manifestPath = join(root, "policy-manifest.json");
  return withImportMutex(root, async (coordination, journalDatabase) => {
    await recoverLocked(root, coordination, journalDatabase);
    const [sourceFile, registryFile, policyFile, catalogFile, manifestFile] = await Promise.all([
      readRegularFile(sourcePath, "source catalog", { privateFile: true }),
      readRegularFile(registryPath, "approved registry"),
      readRegularFile(policyPath, "routing policy"),
      readRegularFile(catalogPath, "tracked catalog"),
      readRegularFile(manifestPath, "policy manifest"),
    ]);
    const manifest = JSON.parse(manifestFile.text);
    for (const [relative, text] of [
      ["model-routing/approved.json", registryFile.text],
      ["model-routing/policy.json", policyFile.text],
      ["model-routing/catalog.json", catalogFile.text],
    ]) {
      if (manifest?.files?.[relative] !== sha256(text)) fail(`${relative} does not match the policy manifest`);
    }
    const { snapshot, missing } = buildRoutingSnapshot(
      JSON.parse(sourceFile.text),
      JSON.parse(registryFile.text),
      JSON.parse(policyFile.text),
      JSON.parse(catalogFile.text),
      now,
    );
    const nextCatalog = `${JSON.stringify(snapshot, null, 2)}\n`;
    const nextManifest = {
      ...manifest,
      files: { ...manifest.files, "model-routing/catalog.json": sha256(nextCatalog) },
    };
    const nextManifestText = `${JSON.stringify(nextManifest, null, 2)}\n`;
    const journal = {
      schema_version: 1,
      catalog: { old: catalogFile.text, next: nextCatalog, old_sha256: sha256(catalogFile.text), next_sha256: sha256(nextCatalog), mode: catalogFile.stats.mode & 0o777 },
      manifest: { old: manifestFile.text, next: nextManifestText, old_sha256: sha256(manifestFile.text), next_sha256: sha256(nextManifestText), mode: manifestFile.stats.mode & 0o777 },
    };
    const generation = randomUUID();
    persistJournal(journalDatabase, generation, journal);

    const unchanged = await Promise.all([
      readRegularFile(registryPath, "approved registry"),
      readRegularFile(policyPath, "routing policy"),
      readRegularFile(catalogPath, "tracked catalog"),
      readRegularFile(manifestPath, "policy manifest"),
    ]);
    if ([registryFile.text, policyFile.text, catalogFile.text, manifestFile.text].some((text, index) => text !== unchanged[index].text)) {
      fail("routing policy inputs changed during catalog import");
    }
    await replaceFile(catalogPath, join(coordination, `catalog.${generation}.next`), nextCatalog, catalogFile.stats.mode);
    await afterCatalogReplace?.();
    await replaceFile(manifestPath, join(coordination, `manifest.${generation}.next`), nextManifestText, manifestFile.stats.mode);
    clearJournal(journalDatabase, generation);
    return { generation: snapshot.generation, refreshed_at: snapshot.refreshed_at, models: snapshot.models.length, missing };
  });
}

if (process.argv[1] === scriptPath) {
  try {
    const recoverOnly = process.argv[2] === "--recover";
    if (process.argv.length > (recoverOnly ? 3 : 2)) fail("usage: import-routing-catalog.mjs [--recover]");
    const receipt = recoverOnly ? await recoverRoutingCatalog() : await importRoutingCatalog();
    process.stdout.write(`${JSON.stringify(receipt)}\n`);
  } catch (error) {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exitCode = 1;
  }
}
