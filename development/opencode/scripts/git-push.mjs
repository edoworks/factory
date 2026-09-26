#!/usr/bin/env node
import { realpathSync, readFileSync, lstatSync } from "node:fs";
import { isAbsolute, resolve } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const GITHUB_HOST = "github.com";
const GITHUB_IDENTITY = "hellofoculoom";
const REMOTE = "https://github.com/edoworks/factory.git";
const fail = (message) => { throw new Error(message); };

const workspaceState = (environment) => `${environment.HOME || process.env.HOME}/Library/Application Support/EdoworksFactory/workspaces.json`;
const safeStatePath = (value) => {
  const absolute = isAbsolute(value) ? value : resolve(value);
  let current = "/";
  for (const part of absolute.split("/").filter(Boolean)) {
    current = resolve(current, part);
    if (lstatSync(current, { throwIfNoEntry: false })?.isSymbolicLink()) fail("workspace registry path must not contain symlinks");
  }
  return resolve(absolute);
};
const validRecord = (item) => item && typeof item === "object" && !Array.isArray(item)
  && Object.keys(item).sort().join(",") === "base_revision,branch,head,issue,path"
  && /^\d+$/.test(String(item.issue))
  && typeof item.branch === "string" && new RegExp(`^feature/${item.issue}-[a-z0-9]+(?:-[a-z0-9]+)*$`).test(item.branch)
  && typeof item.path === "string" && isAbsolute(item.path) && resolve(item.path) === item.path
  && /^[0-9a-f]{40}$/.test(item.base_revision)
  && /^[0-9a-f]{40}$/.test(item.head);
const registeredWorkspace = (cwd, issue, environment) => {
  const statePath = safeStatePath(workspaceState(environment));
  try {
    if (lstatSync(statePath).isSymbolicLink()) fail("workspace registry must not be a symlink");
    const state = JSON.parse(readFileSync(statePath, "utf8"));
    if (state.schema_version !== 2 || !Array.isArray(state.workspaces)) fail("workspace registry schema is invalid");
    if (state.workspaces.some((item) => !validRecord(item))) fail("workspace registry record is invalid");
    for (const field of ["issue", "branch", "path"]) {
      if (new Set(state.workspaces.map((item) => String(item[field]))).size !== state.workspaces.length) fail(`workspace registry contains duplicate ${field}`);
    }
    const record = state.workspaces?.find((item) => resolve(item.path) === resolve(cwd));
    if (!record || String(record.issue) !== String(issue) || record.branch !== environment.FACTORY_WORKSPACE_BRANCH) fail("workspace is not registered for the requested issue and branch");
    return record;
  } catch (error) {
    if (error.code === "ENOENT") fail("workspace registry is unavailable");
    throw error;
  }
};

const pinnedExecutable = (name, environment) => {
  const configured = environment[name];
  if (!configured || !isAbsolute(configured) || /\s/.test(configured)) fail(`${name} must identify a pinned executable without whitespace`);
  return realpathSync(configured);
};

export function pushFeature(branch, expectedCommit, environment = process.env) {
  if (!/^feature\/[0-9]+-[a-z0-9]+(?:-[a-z0-9]+)*$/.test(branch ?? "")) fail("branch must be feature/ISSUE-SLUG");
  if (!/^[0-9a-f]{40}$/.test(expectedCommit ?? "")) fail("expected commit must be a full lowercase SHA-1");
  const gh = pinnedExecutable("FACTORY_DEV_GH", environment);
  const git = pinnedExecutable("FACTORY_DEV_GIT", environment);
  const cwd = process.cwd();
  const cleanEnvironment = { ...environment, GIT_CONFIG_NOSYSTEM: "1", GIT_CONFIG_GLOBAL: "/dev/null" };
  for (const name of Object.keys(cleanEnvironment)) {
    if (name.startsWith("GIT_") && !["GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL"].includes(name)) delete cleanEnvironment[name];
    if (name.startsWith("GH_") || name.startsWith("GITHUB_") || name.includes("TOKEN") || ["ALL_PROXY", "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "all_proxy", "http_proxy", "https_proxy", "no_proxy"].includes(name)) delete cleanEnvironment[name];
  }
  const currentBranch = spawnSync(git, ["symbolic-ref", "--quiet", "--short", "HEAD"], { cwd, encoding: "utf8", env: cleanEnvironment });
  if (currentBranch.status !== 0 || currentBranch.stdout.trim() !== branch) fail("current branch does not match requested branch");
  const gitDir = spawnSync(git, ["rev-parse", "--git-dir"], { cwd, encoding: "utf8", env: cleanEnvironment });
  const commonDir = spawnSync(git, ["rev-parse", "--git-common-dir"], { cwd, encoding: "utf8", env: cleanEnvironment });
  if (gitDir.status !== 0 || commonDir.status !== 0 || !lstatSync(resolve(cwd, ".git"), { throwIfNoEntry: false })?.isFile() || gitDir.stdout.trim() === commonDir.stdout.trim()) fail("current checkout is not a linked worktree");
  const membership = spawnSync(git, ["worktree", "list", "--porcelain"], { cwd, encoding: "utf8", env: cleanEnvironment });
  if (membership.status !== 0 || !membership.stdout.split("\n").includes(`worktree ${resolve(cwd)}`)) fail("workspace is not a registered linked worktree");
  const record = registeredWorkspace(cwd, branch.split("/")[1].split("-")[0], { ...environment, FACTORY_WORKSPACE_BRANCH: branch });
  const root = cwd;
  const unsafeConfig = spawnSync(git, ["config", "--local", "--get-regexp", "^(url\\.|http\\.|include\\.|includeIf\\.|core\\.hookspath$)"], { cwd: root, encoding: "utf8", env: cleanEnvironment });
  if (unsafeConfig.status === 0) fail("repository Git config contains transport-affecting settings");
  if (unsafeConfig.status !== 1) fail(unsafeConfig.stderr.trim() || "repository Git config inspection failed");
  const head = spawnSync(git, ["rev-parse", "--verify", "HEAD^{commit}"], { cwd: root, encoding: "utf8", env: cleanEnvironment });
  if (head.status !== 0) fail(head.stderr.trim() || "HEAD commit resolution failed");
  if (head.stdout.trim() !== expectedCommit) fail("HEAD does not match expected commit");
  if (record.head !== expectedCommit) fail("registered HEAD does not match expected commit");
  const ancestry = spawnSync(git, ["merge-base", "--is-ancestor", record.base_revision, record.head], { cwd: root, env: cleanEnvironment });
  if (ancestry.status !== 0) fail("workspace HEAD does not contain its registered base revision");
  const status = spawnSync(git, ["status", "--porcelain"], { cwd: root, encoding: "utf8", env: cleanEnvironment });
  if (status.status !== 0 || status.stdout.trim()) fail("worktree must be clean after commit");
  const issue = spawnSync(gh, ["issue", "view", branch.split("/")[1].split("-")[0], "--repo", "github.com/edoworks/factory", "--json", "state", "--jq", ".state"], { cwd: root, encoding: "utf8", env: cleanEnvironment });
  if (issue.status !== 0 || issue.stdout.trim().toUpperCase() !== "OPEN") fail("issue open state was not verified");
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
