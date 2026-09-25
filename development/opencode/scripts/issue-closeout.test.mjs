import test from "node:test";
import assert from "node:assert/strict";
import { chmod, mkdtemp, readFile, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { parseArguments, parseIssueNumbers, verifyIssueCloseout } from "./issue-closeout.mjs";

test("parses only the exact canonical closeout command", () => {
  assert.deepEqual(parseArguments(["verify", "--repo", "edoworks/factory", "--issues", "84,87"]), ["84", "87"]);
  assert.throws(() => parseArguments(["verify", "--repo", "other/repo", "--issues", "84"]), /usage/);
  assert.throws(() => parseArguments(["verify", "--issues", "84", "--repo", "edoworks/factory"]), /usage/);
  assert.throws(() => parseArguments(["verify", "--repo", "edoworks/factory", "--issues", "84", "--state", "closed"]), /usage/);
  assert.throws(() => parseIssueNumbers("84,84"), /duplicates/);
  assert.throws(() => parseIssueNumbers("84,nope"), /canonical positive numeric/);
  assert.throws(() => parseIssueNumbers("084"), /canonical positive numeric/);
});

test("uses only pinned read-only GitHub transport and rejects open issues", async () => {
  const directory = await mkdtemp(join(tmpdir(), "factory-closeout-"));
  const capture = join(directory, "capture.jsonl");
  const gh = join(directory, "gh");
  const hostile = join(directory, "hostile-gh");
  await writeFile(gh, "#!/bin/sh\nif [ -n \"$GH_HOST$GH_TOKEN$GITHUB_TOKEN$HTTP_PROXY$HTTPS_PROXY$ALL_PROXY$http_proxy$https_proxy$all_proxy\" ]; then exit 98; fi\npython3 -c 'import json, os, sys; open(os.environ[\"CAPTURE\"], \"a\").write(json.dumps(sys.argv[1:]) + \"\\n\")' \"$@\"\nif [ \"$1\" = api ]; then printf '%s\\n' \"${FAKE_LOGIN:-hellofoculoom}\"; exit 0; fi\nif [ \"$5\" = 87 ]; then printf '{\"number\":87,\"title\":\"Open\",\"state\":\"OPEN\"}\\n'; elif [ \"$5\" = 88 ]; then printf '{\"title\":\"Missing number\",\"state\":\"CLOSED\"}\\n'; elif [ \"$5\" = 89 ]; then printf '{\"number\":1,\"title\":\"Wrong number\",\"state\":\"CLOSED\"}\\n'; else printf '{\"number\":%s,\"title\":\"Closed\",\"state\":\"CLOSED\"}\\n' \"$5\"; fi\n");
  await writeFile(hostile, "#!/bin/sh\nexit 99\n");
  await chmod(gh, 0o755);
  await chmod(hostile, 0o755);
  const environment = { ...process.env, FACTORY_DEV_GH: gh, CAPTURE: capture, PATH: `${directory}:${process.env.PATH}`, GH_HOST: "evil.invalid", GH_TOKEN: "secret", HTTPS_PROXY: "http://evil.invalid" };

  assert.equal(verifyIssueCloseout(["84", "85"], environment), true);
  const calls = (await readFile(capture, "utf8")).trim().split("\n").map(JSON.parse);
  assert.deepEqual(calls[0], ["api", "--hostname", "github.com", "user", "--jq", ".login"]);
  assert.deepEqual(calls[1], ["issue", "view", "--repo", "github.com/edoworks/factory", "84", "--json", "number,title,state"]);
  assert.deepEqual(calls[2], ["issue", "view", "--repo", "github.com/edoworks/factory", "85", "--json", "number,title,state"]);
  assert.throws(() => verifyIssueCloseout(["87"], environment), /87:OPEN/);
  assert.throws(() => verifyIssueCloseout(["88"], environment), /invalid issue receipt/);
  assert.throws(() => verifyIssueCloseout(["89"], environment), /invalid issue receipt/);
  assert.throws(() => verifyIssueCloseout(["84"], { ...environment, FAKE_LOGIN: "wrong-user" }), /must be hellofoculoom/);
  assert.throws(() => verifyIssueCloseout(["84"], { ...environment, FACTORY_DEV_GH: "gh" }), /pinned GitHub CLI/);
  assert.throws(() => verifyIssueCloseout(["84"], { ...environment, FACTORY_DEV_GH: undefined }), /pinned GitHub CLI/);
});
