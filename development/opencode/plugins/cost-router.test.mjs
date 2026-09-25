import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, readFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import costRouter from "./cost-router.mjs";
import { messageText, recordToolAttribution } from "./cost-router-lib.mjs";
import { assertTierCoherence, classifyTitle } from "../model-routing/routing-lib.mjs";

test("message text joins text parts only", () => assert.equal(messageText({ parts: [{ type: "text", text: "Crop" }, { type: "file", text: "ignored" }] }), "Crop"));
test("plugin exposes only its initializer", async () => assert.deepEqual(Object.keys(await import("./cost-router.mjs")), ["default"]));
test("routine work is rejected on standard routes", async () => {
  const hooks = await costRouter();
  await assert.rejects(() => hooks["chat.params"]({ agent: "build", model: { providerID: "openai", id: "gpt-5.6-luna" }, provider: { id: "openai" }, message: { parts: [{ type: "text", text: "Check status" }] } }), /must not dispatch/);
});
test("construction remains eligible for complex routing", () => assert.equal(assertTierCoherence(classifyTitle("Design the architecture", "frontier-build"), "complex", "route"), "complex"));
test("attribution excludes command text and raw session IDs", async () => {
  const path = join(await mkdtemp(join(tmpdir(), "factory-router-")), "log.jsonl");
  await recordToolAttribution({ sessionID: "secret-session", agent: "build", provider: "openai", model: "gpt-5.6-luna", tool: "bash", path });
  const record = JSON.parse(await readFile(path, "utf8"));
  assert.equal(record.tool, "bash");
  assert.notEqual(record.session, "secret-session");
  assert.equal("command" in record, false);
});
