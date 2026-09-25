#!/usr/bin/env node
import { realpathSync } from "node:fs";
import { dirname, isAbsolute, resolve } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const GITHUB_HOST = "github.com";
const GITHUB_IDENTITY = "hellofoculoom";
const REMOTE = "https://github.com/edoworks/factory.git";
const fail = (message) => { throw new Error(message); };

const pinnedExecutable = (name, environment) => {
  const configured = environment[name];
  if (!configured || !isAbsolute(configured) || /\s/.test(configured)) fail(`${name} must identify a pinned executable without whitespace`);
  return realpathSync(configured);
};

export function pushFeature(branch, expectedCommit, environment = process.env) {
  if (!/^feature\/[a-z0-9]+(?:-[a-z0-9]+)*$/.test(branch ?? "")) fail("branch must be a lowercase feature name");
  if (!/^[0-9a-f]{40}$/.test(expectedCommit ?? "")) fail("expected commit must be a full lowercase SHA-1");
  const gh = pinnedExecutable("FACTORY_DEV_GH", environment);
  const git = pinnedExecutable("FACTORY_DEV_GIT", environment);
  const cleanEnvironment = { ...environment, GIT_CONFIG_NOSYSTEM: "1", GIT_CONFIG_GLOBAL: "/dev/null" };
  for (const name of Object.keys(cleanEnvironment)) {
    if (name.startsWith("GIT_") && !["GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL"].includes(name)) delete cleanEnvironment[name];
    if (["ALL_PROXY", "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "all_proxy", "http_proxy", "https_proxy", "no_proxy"].includes(name)) delete cleanEnvironment[name];
  }
  const root = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
  const unsafeConfig = spawnSync(git, ["config", "--local", "--get-regexp", "^(url\\.|http\\.|include\\.|includeIf\\.)"], { cwd: root, encoding: "utf8", env: cleanEnvironment });
  if (unsafeConfig.status === 0) fail("repository Git config contains transport-affecting settings");
  if (unsafeConfig.status !== 1) fail(unsafeConfig.stderr.trim() || "repository Git config inspection failed");
  const head = spawnSync(git, ["rev-parse", "--verify", "HEAD^{commit}"], { cwd: root, encoding: "utf8", env: cleanEnvironment });
  if (head.status !== 0) fail(head.stderr.trim() || "HEAD commit resolution failed");
  if (head.stdout.trim() !== expectedCommit) fail("HEAD does not match expected commit");
  const identity = spawnSync(gh, ["api", "--hostname", GITHUB_HOST, "user", "--jq", ".login"], { encoding: "utf8", env: cleanEnvironment });
  if (identity.status !== 0) fail(identity.stderr.trim() || "GitHub identity check failed");
  if (identity.stdout.trim() !== GITHUB_IDENTITY) fail(`GitHub identity must be ${GITHUB_IDENTITY}`);
  const args = ["-c", "credential.helper=", "-c", `credential.helper=!${gh} auth git-credential`, "push", "--no-follow-tags", REMOTE, `${expectedCommit}:refs/heads/${branch}`];
  const result = spawnSync(git, args, { cwd: root, encoding: "utf8", env: cleanEnvironment });
  if (result.status !== 0) fail(result.stderr.trim() || "git push failed");
  return result.stdout;
}

function main(argv) {
  if (argv.length !== 2) fail("usage: git-push.mjs feature/NAME EXPECTED_COMMIT");
  process.stdout.write(pushFeature(argv[0], argv[1]));
}

if (process.argv[1] && fileURLToPath(import.meta.url) === realpathSync(process.argv[1])) {
  try { main(process.argv.slice(2)); } catch (error) { process.stderr.write(`ERROR: ${error.message}\n`); process.exitCode = 1; }
}
