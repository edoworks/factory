import test from "node:test";
import assert from "node:assert/strict";
import { readdir, readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const sourceRoot = process.env.FACTORY_DEV_OPENCODE_ROOT
  || join(dirname(fileURLToPath(import.meta.url)), "..");
const commandRoot = join(sourceRoot, "commands");

test("factory has one canonical continuation command", async () => {
  const commands = (await readdir(commandRoot))
    .filter((name) => name.startsWith("continue") && name.endsWith(".md"));
  assert.deepEqual(commands, ["continue-factory.md"]);
  const content = await readFile(join(commandRoot, commands[0]), "utf8");
  assert.match(content, /^agent: explore$/m);
  assert.match(content, /edoworks\/factory/);
  assert.doesNotMatch(content, /continue-(?:original|sf08-build|sf0\.8)/);
});
