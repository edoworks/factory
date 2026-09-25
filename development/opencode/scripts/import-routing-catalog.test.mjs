import test from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { chmod, mkdtemp, mkdir, readFile, symlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { buildRoutingSnapshot, importRoutingCatalog, recoverRoutingCatalog } from "./import-routing-catalog.mjs";

const now = Date.parse("2026-09-25T12:00:00Z");
const capable = (provider, model, overrides = {}) => ({
  full_name: `${provider}/${model}`,
  provider,
  model,
  status: "active",
  capabilities: { reasoning: true, attachment: true, toolcall: true, input: { text: true, image: true }, output: { text: true } },
  variants: ["low", "medium"],
  ...overrides,
});
const policy = {
  schema_version: 1,
  catalog_max_age_hours: 48,
  providers: { local: { enabled: true }, cloud: { enabled: true }, disabled: { enabled: false } },
};
const registry = {
  schema_version: 1,
  routes: {
    small: { provider: "local", model: "small", tier: "routine", variant: null, startup_fallback: { provider: "cloud", model: "gone", variant: null } },
    explore: { provider: "local", model: "small", tier: "routine", variant: null },
    general: { provider: "cloud", model: "standard", tier: "standard", variant: null },
    plan: { provider: "cloud", model: "standard", tier: "standard", variant: "low" },
    build: { provider: "cloud", model: "standard", tier: "standard", variant: null },
    optional: { provider: "cloud", model: "gone", tier: "routine", variant: null },
    disabled: { provider: "disabled", model: "ignored", tier: "routine", disabled: true },
  },
};
const source = (overrides = {}) => ({
  schema_version: 1,
  generation: "1790335243580-66796",
  refreshed_at: "2026-09-25T11:20:43.573Z",
  providers: ["local", "cloud", "disabled"],
  failures: [],
  models: [
    capable("local", "small", { capabilities: { reasoning: false, attachment: false, toolcall: true, input: { text: true, image: false }, output: { text: true } }, variants: [] }),
    capable("cloud", "standard"),
  ],
  ...overrides,
});
const current = { refreshed_at: "2026-09-23T11:20:00Z" };
const digest = (text) => createHash("sha256").update(text).digest("hex");

test("builds a route-only snapshot and marks absent optional routes missing", () => {
  const result = buildRoutingSnapshot(source(), registry, policy, current, now);
  assert.equal(result.snapshot.generation, source().generation);
  assert.deepEqual(result.snapshot.models.map((model) => model.full_name), ["cloud/gone", "cloud/standard", "local/small"]);
  assert.equal(result.snapshot.models[0].status, "missing");
  assert.deepEqual(result.snapshot.models[1].variants, ["low"]);
  assert.deepEqual(result.missing, ["cloud/gone"]);
  assert.equal("cost" in result.snapshot.models[1], false);
});

test("rejects stale, malformed, failed-provider, and incomplete sources", () => {
  assert.throws(() => buildRoutingSnapshot(source({ refreshed_at: "2026-09-20T00:00:00Z" }), registry, policy, current, now), /stale/);
  assert.throws(() => buildRoutingSnapshot(source({ generation: "manual" }), registry, policy, current, now), /generation/);
  assert.throws(() => buildRoutingSnapshot(source({ failures: [{ provider: "cloud" }] }), registry, policy, current, now), /provider failures/);
  assert.throws(() => buildRoutingSnapshot(source({ providers: ["local"] }), registry, policy, current, now), /omitted enabled providers/);
  assert.throws(() => buildRoutingSnapshot(source({ models: [source().models[0]] }), registry, policy, current, now), /required built-in/);
  assert.throws(() => buildRoutingSnapshot(source({ models: [source().models[0], capable(["cloud"], "standard")] }), registry, policy, current, now), /provider and model/);
  assert.throws(() => buildRoutingSnapshot(source({ models: [source().models[0], capable("cloud", "standard", { status: "unknown" })] }), registry, policy, current, now), /status is invalid/);
});

test("rejects incapable built-in models and catalog rollback", () => {
  const incapable = source({ models: [source().models[0], capable("cloud", "standard", { capabilities: { reasoning: false, attachment: false, toolcall: true, input: { text: true, image: false }, output: { text: true } } })] });
  assert.throws(() => buildRoutingSnapshot(incapable, registry, policy, current, now), /cannot serve/);
  assert.throws(() => buildRoutingSnapshot(source({ models: [source().models[0], capable("cloud", "standard", { variants: [] })] }), registry, policy, current, now), /route plan/);
  assert.throws(() => buildRoutingSnapshot(source(), registry, policy, { refreshed_at: "2026-09-25T11:30:00Z" }, now), /older/);
});

test("projects only policy providers and referenced variants", () => {
  const input = source({
    providers: ["local", "cloud", "disabled", "private-enterprise"],
    models: [source().models[0], capable("cloud", "standard", { variants: ["low", "medium", "private-experiment"] })],
  });
  const result = buildRoutingSnapshot(input, registry, policy, current, now);
  assert.deepEqual(result.snapshot.providers, ["local", "cloud", "disabled"]);
  assert.deepEqual(result.snapshot.models.find((model) => model.full_name === "cloud/standard").variants, ["low"]);
});

test("invalid import leaves the tracked catalog and manifest unchanged", async () => {
  const directory = await mkdtemp(join(tmpdir(), "factory-catalog-"));
  const root = join(directory, "opencode");
  const routing = join(root, "model-routing");
  await mkdir(routing, { recursive: true });
  const catalogText = `${JSON.stringify(current)}\n`;
  const registryText = `${JSON.stringify(registry)}\n`;
  const policyText = `${JSON.stringify(policy)}\n`;
  const manifestText = `${JSON.stringify({ schema_version: 1, files: {
    "model-routing/approved.json": digest(registryText),
    "model-routing/policy.json": digest(policyText),
    "model-routing/catalog.json": digest(catalogText),
  } }, null, 2)}\n`;
  await Promise.all([
    writeFile(join(routing, "catalog.json"), catalogText),
    writeFile(join(routing, "approved.json"), registryText),
    writeFile(join(routing, "policy.json"), policyText),
    writeFile(join(root, "policy-manifest.json"), manifestText),
    writeFile(join(directory, "source.json"), `${JSON.stringify(source({ failures: [{ provider: "cloud" }] }))}\n`),
  ]);
  await assert.rejects(() => importRoutingCatalog({ root, sourcePath: join(directory, "source.json"), now }), /provider failures/);
  assert.equal(await readFile(join(routing, "catalog.json"), "utf8"), catalogText);
  assert.equal(await readFile(join(root, "policy-manifest.json"), "utf8"), manifestText);

  await writeFile(join(directory, "source.json"), `${JSON.stringify(source())}\n`);
  await chmod(join(directory, "source.json"), 0o664);
  await assert.rejects(() => importRoutingCatalog({ root, sourcePath: join(directory, "source.json"), now }), /not group\/world writable/);
  assert.equal(await readFile(join(routing, "catalog.json"), "utf8"), catalogText);

  await chmod(join(directory, "source.json"), 0o600);
  await symlink(join(directory, "source.json"), join(directory, "source-link.json"));
  await assert.rejects(() => importRoutingCatalog({ root, sourcePath: join(directory, "source-link.json"), now }), /non-symlink/);
});

test("recovers interrupted pairs and excludes concurrent recovery", async () => {
  const directory = await mkdtemp(join(tmpdir(), "factory-catalog-recovery-"));
  const root = join(directory, "opencode");
  const routing = join(root, "model-routing");
  await mkdir(routing, { recursive: true });
  const catalogText = `${JSON.stringify(current)}\n`;
  const registryText = `${JSON.stringify(registry)}\n`;
  const policyText = `${JSON.stringify(policy)}\n`;
  const manifestText = `${JSON.stringify({ schema_version: 1, files: {
    "model-routing/approved.json": digest(registryText),
    "model-routing/policy.json": digest(policyText),
    "model-routing/catalog.json": digest(catalogText),
  } }, null, 2)}\n`;
  const sourcePath = join(directory, "source.json");
  await Promise.all([
    writeFile(join(routing, "catalog.json"), catalogText),
    writeFile(join(routing, "approved.json"), registryText),
    writeFile(join(routing, "policy.json"), policyText),
    writeFile(join(root, "policy-manifest.json"), manifestText),
    writeFile(sourcePath, `${JSON.stringify(source())}\n`, { mode: 0o600 }),
  ]);

  await assert.rejects(() => importRoutingCatalog({
    root,
    sourcePath,
    now,
    afterCatalogReplace: () => { throw new Error("simulated interruption"); },
  }), /simulated interruption/);
  const recovery = await recoverRoutingCatalog({ root });
  assert.equal(recovery.action, "rolled-back");
  assert.equal(await readFile(join(routing, "catalog.json"), "utf8"), catalogText);
  assert.equal(await readFile(join(root, "policy-manifest.json"), "utf8"), manifestText);

  let release;
  let started;
  const startedPromise = new Promise((resolve) => { started = resolve; });
  const releasePromise = new Promise((resolve) => { release = resolve; });
  const activeImport = importRoutingCatalog({ root, sourcePath, now, afterCatalogReplace: async () => {
    started();
    await releasePromise;
  } });
  await startedPromise;
  await assert.rejects(() => recoverRoutingCatalog({ root }), /locked|busy/i);
  release();
  await activeImport;
  assert.equal((await recoverRoutingCatalog({ root })).recovered, false);
});
