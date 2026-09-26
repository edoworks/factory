import test from "node:test";
import assert from "node:assert/strict";
import { chmod, mkdir, mkdtemp, readFile, realpath, symlink, writeFile } from "node:fs/promises";
import { join, resolve } from "node:path";
import { tmpdir } from "node:os";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { pushFeature } from "./git-push.mjs";

test("feature push requires linked registered clean workspace and pins transport", async () => {
  const directory = await realpath(await mkdtemp(join(tmpdir(), "factory-push-")));
  const capture = join(directory, "capture.json");
  const gh = join(directory, "gh");
  const git = join(directory, "git");
  const commit = "a".repeat(40);
  const state = join(directory, "Library", "Application Support", "EdoworksFactory", "workspaces.json");
  await mkdir(join(directory, "Library", "Application Support", "EdoworksFactory"), { recursive: true });
  await writeFile(join(directory, ".git"), "gitdir: /tmp/fake-worktree\n");
  await writeFile(state, JSON.stringify({ schema_version: 2, workspaces: [{ path: directory, issue: "109", branch: "feature/109-transport-guard", base_revision: "b".repeat(40), head: commit }] }));
  await writeFile(gh, "#!/bin/sh\nif [ \"$1\" = issue ]; then printf '%s\\n' \"${ISSUE_STATE:-OPEN}\"; exit 0; fi\nif [ \"$1\" = api ]; then printf 'hellofoculoom\\n'; exit 0; fi\nexit 1\n");
  await writeFile(git, `#!/bin/sh
if [ "$1" = config ]; then if [ "$UNSAFE_CONFIG" = 1 ]; then printf 'url.bad.insteadOf https://github.com/\\n'; exit 0; fi; if [ "$HOOKS_CONFIG" = 1 ]; then printf 'core.hookspath /tmp/none\\n'; exit 0; fi; exit 1; fi
if [ "$1" = symbolic-ref ]; then printf 'feature/109-transport-guard\\n'; exit 0; fi
if [ "$1" = rev-parse ]; then if [ "$2" = --git-dir ]; then printf '.git/worktrees/x\\n'; elif [ "$2" = --git-common-dir ]; then printf '.git\\n'; else printf '%s\\n' "$EXPECTED_COMMIT"; fi; exit 0; fi
if [ "$1" = worktree ]; then printf 'worktree ${directory}\\n'; exit 0; fi
if [ "$1" = status ]; then exit \${DIRTY:-0}; fi
python3 -c 'import json, os, sys; open(os.environ["CAPTURE"], "w").write(json.dumps({"args": sys.argv[1:], "global": os.environ.get("GIT_CONFIG_GLOBAL", ""), "proxy": os.environ.get("HTTPS_PROXY", "")}))' "$@"
`);
  await chmod(gh, 0o755);
  await chmod(git, 0o755);
  const previous = process.cwd();
  process.chdir(directory);
  try {
    const environment = { ...process.env, HOME: directory, FACTORY_DEV_GH: gh, FACTORY_DEV_GIT: git, CAPTURE: capture, EXPECTED_COMMIT: commit, GIT_DIR: "/tmp/untrusted", HTTPS_PROXY: "http://untrusted.invalid" };
    pushFeature("feature/109-transport-guard", commit, environment);
    const direct = spawnSync(process.execPath, [fileURLToPath(new URL("./git-push.mjs", import.meta.url)), "feature/109-transport-guard", commit], { cwd: directory, encoding: "utf8", env: environment });
    assert.equal(direct.status, 0, direct.stderr);
    assert.doesNotThrow(() => pushFeature("feature/109-transport-guard", commit, { ...environment, FACTORY_WORKSPACE_ISSUE_STATE: "closed" }));
    const observed = JSON.parse(await readFile(capture, "utf8"));
    assert.equal(observed.global, "/dev/null");
    assert.equal(observed.proxy, "");
    assert.deepEqual(observed.args.slice(-4), ["push", "--no-follow-tags", "https://github.com/edoworks/factory.git", `${commit}:refs/heads/feature/109-transport-guard`]);
    assert.throws(() => pushFeature("feature/109-transport-guard", "b".repeat(40), environment), /HEAD does not match/);
    assert.throws(() => pushFeature("feature/109-transport-guard", commit, { ...environment, DIRTY: "1" }), /clean/);
    assert.throws(() => pushFeature("feature/109-transport-guard", commit, { ...environment, UNSAFE_CONFIG: "1" }), /transport-affecting/);
    assert.throws(() => pushFeature("feature/109-transport-guard", commit, { ...environment, HOOKS_CONFIG: "1" }), /transport-affecting/);
    assert.throws(() => pushFeature("feature/109-transport-guard", commit, { ...environment, ISSUE_STATE: "CLOSED" }), /open state/);
    assert.throws(() => pushFeature("feature/109-other", commit, environment), /current branch/);
    assert.throws(() => pushFeature("feature/109-transport-guard", commit, { ...environment, HOME: join(directory, "missing") }), /registry/);
    await symlink(directory, join(directory, "linked-home"));
    assert.throws(() => pushFeature("feature/109-transport-guard", commit, { ...environment, HOME: join(directory, "linked-home") }), /symlink/);
  } finally {
    process.chdir(previous);
  }
});
