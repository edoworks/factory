import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const command = await readFile(new URL("commands/rubberduck.md", new URL("../", import.meta.url)), "utf8");

test("rubberduck command uses canonical doctor receipts and deterministic ledger validation", () => {
  assert.match(command, /bin\/factory-dev doctor/);
  assert.match(command, /python3 \{env:FACTORY_DEV_OPENCODE_ROOT\}\/scripts\/validate-rubberduck\.py/);
  assert.match(command, /`INVESTIGATE NOW` requires PASS/);
  assert.match(command, /duplicate-key/);
  assert.doesNotMatch(command, /factory-dev hygiene/);
  for (const gate of ["ai_essential", "independent_demand", "two_week_test", "distribution", "recurrence", "economics", "defensibility", "risk", "validation_design"]) {
    assert.match(command, new RegExp(gate));
  }
});
