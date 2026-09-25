import test from "node:test";
import assert from "node:assert/strict";
import { chmod, mkdtemp, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { pushFeature } from "./git-push.mjs";

test("feature push pins identity remote and refspec", async () => {
  const directory = await mkdtemp(join(tmpdir(), "factory-push-"));
  const capture = join(directory, "capture.json");
  const gh = join(directory, "gh");
  const git = join(directory, "git");
  const commit = "a".repeat(40);
  await writeFile(gh, "#!/bin/sh\nif [ -n \"$HTTP_PROXY$HTTPS_PROXY$ALL_PROXY$http_proxy$https_proxy$all_proxy\" ]; then exit 98; fi\nif [ \"$1 $2 $3 $4 $5 $6\" != \"api --hostname github.com user --jq .login\" ]; then exit 99; fi\nprintf 'hellofoculoom\\n'\n");
  await writeFile(git, "#!/bin/sh\nif [ \"$1\" = config ]; then if [ \"$UNSAFE_CONFIG\" = 1 ]; then printf 'url.bad.insteadOf https://github.com/\\n'; exit 0; fi; exit 1; fi\nif [ \"$1\" = rev-parse ]; then printf '%s\\n' \"$EXPECTED_COMMIT\"; exit 0; fi\npython3 -c 'import json, os, sys; open(os.environ[\"CAPTURE\"], \"w\").write(json.dumps({\"args\": sys.argv[1:], \"cwd\": os.getcwd(), \"git_dir\": os.environ.get(\"GIT_DIR\", \"\"), \"global\": os.environ.get(\"GIT_CONFIG_GLOBAL\", \"\"), \"proxy\": os.environ.get(\"HTTPS_PROXY\", \"\")}))' \"$@\"\n");
  await chmod(gh, 0o755);
  await chmod(git, 0o755);
  const environment = { ...process.env, FACTORY_DEV_GH: gh, FACTORY_DEV_GIT: git, CAPTURE: capture, EXPECTED_COMMIT: commit, GIT_DIR: "/tmp/untrusted", HTTPS_PROXY: "http://untrusted.invalid" };
  pushFeature("feature/transport-guard", commit, environment);
  const observed = JSON.parse(await readFile(capture, "utf8"));
  assert.equal(observed.git_dir, "");
  assert.equal(observed.global, "/dev/null");
  assert.equal(observed.proxy, "");
  assert.match(observed.cwd, /\/factory$/);
  assert.deepEqual(observed.args.slice(-4), ["push", "--no-follow-tags", "https://github.com/edoworks/factory.git", `${commit}:refs/heads/feature/transport-guard`]);
  assert.match(observed.args[3], /^credential\.helper=!.*\/gh auth git-credential$/);
  assert.throws(() => pushFeature("main", commit, environment), /lowercase feature name/);
  assert.throws(() => pushFeature("feature/good --force", commit, environment), /lowercase feature name/);
  assert.throws(() => pushFeature("feature/transport-guard", "HEAD", environment), /full lowercase SHA-1/);

  const wrongHead = { ...environment, EXPECTED_COMMIT: "b".repeat(40) };
  assert.throws(() => pushFeature("feature/transport-guard", commit, wrongHead), /HEAD does not match expected commit/);
  assert.throws(() => pushFeature("feature/transport-guard", commit, { ...environment, UNSAFE_CONFIG: "1" }), /transport-affecting settings/);
});
