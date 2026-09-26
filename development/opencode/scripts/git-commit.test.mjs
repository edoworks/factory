import test from "node:test";
import assert from "node:assert/strict";
import { chmod, mkdir, mkdtemp, realpath, symlink, unlink, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { commitFeature } from "./git-commit.mjs";

test("commit wrapper requires exact arguments, linked registration, open issue, and staged checks", async () => {
  const directory = await realpath(await mkdtemp(join(tmpdir(), "factory-commit-")));
  const git = join(directory, "git");
  const gh = join(directory, "gh");
  const state = join(directory, "Library", "Application Support", "EdoworksFactory", "workspaces.json");
  await mkdir(join(directory, "Library", "Application Support", "EdoworksFactory"), { recursive: true });
  await writeFile(join(directory, ".git"), "gitdir: /tmp/fake-worktree\n");
  await writeFile(state, JSON.stringify({ schema_version: 2, workspaces: [{ path: directory, issue: "109", branch: "feature/109-commit-guard", base_revision: "b".repeat(40), head: "a".repeat(40) }] }));
  await writeFile(gh, "#!/bin/sh\nif [ \"$1\" = issue ]; then printf '%s\\n' \"${ISSUE_STATE:-OPEN}\"; exit 0; fi\nif [ \"$1\" = api ]; then printf 'hellofoculoom\\n'; exit 0; fi\nexit 1\n");
  await writeFile(git, `#!/bin/sh
case "$1" in
  symbolic-ref) printf 'feature/109-commit-guard\n';;
  rev-parse) if [ "$2" = --git-dir ]; then printf '.git/worktrees/x\n'; elif [ "$2" = --git-common-dir ]; then printf '.git\n'; else printf '${"a".repeat(40)}\n'; fi;;
  merge-base) exit 0;;
  show) printf 'Factory Test\\0test@example.invalid\\0Factory Test\\0test@example.invalid\n';;
  worktree) printf 'worktree ${directory}\n';;
  config) if [ "$UNSAFE_CONFIG" = 1 ]; then printf 'url.bad.insteadOf https://github.com/\n'; exit 0; fi; if [ "$HOOKS_CONFIG" = 1 ]; then printf 'core.hookspath /tmp/none\n'; exit 0; fi; exit 1;;
  diff) if [ "$3" = --quiet ]; then exit 1; fi; exit 0;;
  commit) exit 0;;
  *) exit 1;;
esac
`);
  await chmod(git, 0o755);
  await chmod(gh, 0o755);
  const previous = process.cwd();
  process.chdir(directory);
  try {
    const env = { ...process.env, HOME: directory, FACTORY_DEV_GIT: git, FACTORY_DEV_GH: gh };
    assert.doesNotThrow(() => commitFeature("109", ["-m", "guard"], env));
    assert.doesNotThrow(() => commitFeature("109", ["-m", "guard"], { ...env, FACTORY_WORKSPACE_ISSUE_STATE: "closed" }));
    for (const args of [["-m", ""], ["-m", "line\nfeed"], ["--amend"], ["-m", "guard", "extra"]]) assert.throws(() => commitFeature("109", args, env));
    assert.throws(() => commitFeature("109", ["-m", "guard"], { ...env, HOME: join(directory, "missing") }), /unavailable/);
    assert.throws(() => commitFeature("109", ["-m", "guard"], { ...env, ISSUE_STATE: "CLOSED" }), /not open/);
    assert.throws(() => commitFeature("109", ["-m", "guard"], { ...env, UNSAFE_CONFIG: "1" }), /transport-affecting/);
    assert.throws(() => commitFeature("109", ["-m", "guard"], { ...env, HOOKS_CONFIG: "1" }), /transport-affecting/);
    await symlink(directory, join(directory, "linked-home"));
    assert.throws(() => commitFeature("109", ["-m", "guard"], { ...env, HOME: join(directory, "linked-home") }), /symlink/);
    await writeFile(`${state}.lock`, `${process.pid}\n`);
    assert.throws(() => commitFeature("109", ["-m", "guard"], env), /locked/);
    await unlink(`${state}.lock`);
  } finally {
    process.chdir(previous);
  }
});
