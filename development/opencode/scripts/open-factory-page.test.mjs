import test from "node:test";
import assert from "node:assert/strict";

import factoryPageTool, * as factoryPageModule from "../tools/open_factory_page.js";

const { openFactoryPage, validateFactoryPageUrl } = factoryPageModule;

const revision = "97e17b0883c6fdacd6ab2fd85ad3dfc70a7f8719";

test("accepts bounded public Factory review pages", () => {
  const accepted = [
    "https://github.com/edoworks/factory",
    "https://github.com/edoworks/factory/issues/102#verification",
    "https://github.com/edoworks/factory/pull/76/files#diff-abc",
    `https://github.com/edoworks/factory/commit/${revision}`,
    `https://github.com/edoworks/factory/blob/${revision}/docs/FactoryDevelopment-PRD.md?plain=1#L100`,
    "https://github.com/edoworks/factory/actions/runs/36192085292/job/108259338225",
  ];
  for (const url of accepted) assert.equal(validateFactoryPageUrl(url), new URL(url).href);
});

test("rejects unapproved authorities, repositories, paths, and encodings", () => {
  const rejected = [
    "http://github.com/edoworks/factory/issues/102",
    "https://github.com.evil.example/edoworks/factory/issues/102",
    "https://attacker@github.com/edoworks/factory/issues/102",
    "https://github.com:443/edoworks/factory/issues/102",
    "https://github.com/edoworks/other/issues/102",
    "https://github.com/edoworks/factory-other/issues/102",
    "https://github.com/edoworks/factory/settings",
    "https://github.com/edoworks/factory/blob/main/docs/FactoryDevelopment-PRD.md",
    "https://github.com/edoworks/factory/commit/97e17b0",
    "https://github.com/edoworks/factory/blob/97e17b0/docs/FactoryDevelopment-PRD.md",
    "https://github.com/edoworks/factory/%2e%2e/other",
    `https://github.com/edoworks/factory/blob/${revision}/docs/%2e%2e/README.md`,
    "https://github.com/edoworks/factory/issues%2f102",
    `https://github.com/edoworks/factory/blob/${revision}/docs/%252e%252e%252fsettings`,
    `https://github.com/edoworks/factory/blob/${revision}/docs/%zz`,
    "https://github.com/edoworks/factory/issues/102\\extra",
    "https://github.com/edoworks/factory/issues/102 extra",
    "https://github.com/edoworks/factory/issues/102?private=value",
    "https://github.com/edoworks/factory/issues/102#bad%20fragment",
    "--args",
  ];
  for (const url of rejected) assert.throws(() => validateFactoryPageUrl(url));
});

test("opens Chrome Guest with fixed argv and no shell", () => {
  const calls = [];
  const url = "https://github.com/edoworks/factory/issues/102#verification";
  const receipt = openFactoryPage(url, (...args) => {
    calls.push(args);
    return { status: 0 };
  });
  assert.deepEqual(calls, [[
    "/usr/bin/open",
    ["-n", "-b", "com.google.Chrome", "--args", "--guest", url],
    { encoding: "utf8", shell: false, timeout: 10000 },
  ]]);
  assert.deepEqual(receipt, {
    launchAccepted: true,
    requestedBrowser: "com.google.Chrome",
    requestedMode: "guest",
    url,
  });
});

test("exposes one structured URL argument", () => {
  assert.deepEqual(Object.keys(factoryPageTool.args), ["url"]);
  assert.deepEqual(
    Object.keys(factoryPageModule).sort(),
    ["default", "openFactoryPage", "validateFactoryPageUrl"],
  );
});

test("fails closed when Chrome Guest launch fails", () => {
  assert.throws(
    () => openFactoryPage(
      "https://github.com/edoworks/factory/issues/102",
      () => ({ status: 1 }),
    ),
    /failed/,
  );
});
