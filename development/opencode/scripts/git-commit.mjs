#!/usr/bin/env node
import { closeSync, lstatSync, openSync, readFileSync, realpathSync, renameSync, unlinkSync, writeFileSync, writeSync } from "node:fs";
import { isAbsolute, resolve } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const fail = (message) => { throw new Error(message); };
const pinned = (name, environment) => {
  const value = environment[name];
  if (!value || !isAbsolute(value) || /\s/.test(value)) fail(`${name} must identify a pinned executable without whitespace`);
  return realpathSync(value);
};
const cleanEnvironment = (environment) => {
  const result = { ...environment, GIT_CONFIG_NOSYSTEM: "1", GIT_CONFIG_GLOBAL: "/dev/null" };
  for (const name of Object.keys(result)) {
    if (name.startsWith("GIT_") && !["GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL"].includes(name)) delete result[name];
    if (name.startsWith("GH_") || name.startsWith("GITHUB_") || name.includes("TOKEN") || ["ALL_PROXY", "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "all_proxy", "http_proxy", "https_proxy", "no_proxy"].includes(name)) delete result[name];
  }
  return result;
};
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
const acquireLock = (statePath) => {
  const lockPath = `${statePath}.lock`;
  try {
    const descriptor = openSync(lockPath, "wx", 0o600);
    writeSync(descriptor, `${process.pid}\n`);
    closeSync(descriptor);
    return lockPath;
  } catch (error) {
    if (error.code !== "EEXIST") fail(`workspace registry lock failed: ${error.message}`);
    const entry = lstatSync(lockPath, { throwIfNoEntry: false });
    if (!entry?.isFile() || entry.isSymbolicLink()) fail("workspace registry lock is unsafe");
    fail("workspace registry is locked; stale-lock removal requires separate owner authorization");
  }
};

export function commitFeature(issue, args, environment = process.env) {
  if (!/^\d+$/.test(String(issue)) || !Array.isArray(args) || args.length !== 2 || args[0] !== "-m" || typeof args[1] !== "string" || !args[1].trim() || /[\r\n]/.test(args[1])) fail("usage: git-commit.mjs ISSUE -m MESSAGE");
  const git = pinned("FACTORY_DEV_GIT", environment);
  const gh = pinned("FACTORY_DEV_GH", environment);
  const cwd = process.cwd();
  const env = cleanEnvironment(environment);
  const branch = spawnSync(git, ["symbolic-ref", "--quiet", "--short", "HEAD"], { cwd, encoding: "utf8", env });
  if (branch.status !== 0 || !new RegExp(`^feature/${issue}-[a-z0-9]+(?:-[a-z0-9]+)*$`).test(branch.stdout.trim())) fail("current branch must be feature/ISSUE-SLUG");
  const gitDir = spawnSync(git, ["rev-parse", "--git-dir"], { cwd, encoding: "utf8", env });
  const commonDir = spawnSync(git, ["rev-parse", "--git-common-dir"], { cwd, encoding: "utf8", env });
  if (gitDir.status !== 0 || commonDir.status !== 0 || !lstatSync(resolve(cwd, ".git"), { throwIfNoEntry: false })?.isFile() || gitDir.stdout.trim() === commonDir.stdout.trim()) fail("current checkout is not a linked worktree");
  const statePath = safeStatePath(`${environment.HOME || process.env.HOME}/Library/Application Support/EdoworksFactory/workspaces.json`);
  const stateEntry = lstatSync(statePath, { throwIfNoEntry: false });
  if (!stateEntry) fail("workspace registry is unavailable");
  if (stateEntry.isSymbolicLink()) fail("workspace registry must not be a symlink");
  const lockPath = acquireLock(statePath);
  try {
    let state;
  try { state = JSON.parse(readFileSync(statePath, "utf8")); } catch (error) { fail(error.code === "ENOENT" ? "workspace registry is unavailable" : "workspace registry is invalid"); }
  if (state.schema_version !== 2 || !Array.isArray(state.workspaces)) fail("workspace registry schema is invalid");
  if (state.workspaces.some((item) => !validRecord(item))) fail("workspace registry record is invalid");
  for (const field of ["issue", "branch", "path"]) {
    if (new Set(state.workspaces.map((item) => String(item[field]))).size !== state.workspaces.length) fail(`workspace registry contains duplicate ${field}`);
  }
  const record = state.workspaces.find((item) => resolve(item.path) === resolve(cwd) && String(item.issue) === String(issue) && item.branch === branch.stdout.trim());
  if (!record) fail("workspace registration is invalid");
  const membership = spawnSync(git, ["worktree", "list", "--porcelain"], { cwd, encoding: "utf8", env });
  if (membership.status !== 0 || !membership.stdout.split("\n").includes(`worktree ${resolve(cwd)}`)) fail("workspace is not a registered linked worktree");
  const head = spawnSync(git, ["rev-parse", "HEAD"], { cwd, encoding: "utf8", env });
  if (head.status !== 0 || head.stdout.trim() !== record.head) fail("registered HEAD does not match the current worktree");
  const ancestry = spawnSync(git, ["merge-base", "--is-ancestor", record.base_revision, record.head], { cwd, env });
  if (ancestry.status !== 0) fail("workspace HEAD does not contain its registered base revision");
  const metadata = spawnSync(git, ["show", "-s", "--format=%an%x00%ae%x00%cn%x00%ce", "HEAD"], { cwd, encoding: "utf8", env });
  const commitIdentity = metadata.stdout.trimEnd().split("\0");
  if (metadata.status !== 0 || commitIdentity.length !== 4 || commitIdentity.some((value) => !value || /[\r\n\0]/.test(value))) fail("registered HEAD commit identity is invalid");
  [env.GIT_AUTHOR_NAME, env.GIT_AUTHOR_EMAIL, env.GIT_COMMITTER_NAME, env.GIT_COMMITTER_EMAIL] = commitIdentity;
  const issueResult = spawnSync(gh, ["issue", "view", String(issue), "--repo", "github.com/edoworks/factory", "--json", "state", "--jq", ".state"], { cwd, encoding: "utf8", env });
  if (issueResult.status !== 0 || issueResult.stdout.trim().toUpperCase() !== "OPEN") fail("issue is not open");
  const identity = spawnSync(gh, ["api", "--hostname", "github.com", "user", "--jq", ".login"], { cwd, encoding: "utf8", env });
  if (identity.status !== 0 || identity.stdout.trim() !== "hellofoculoom") fail("GitHub identity must be hellofoculoom");
  const config = spawnSync(git, ["config", "--local", "--get-regexp", "^(url\\.|http\\.|include\\.|includeIf\\.|core\\.hookspath$)"], { cwd, encoding: "utf8", env });
  if (config.status === 0) fail("repository Git config contains transport-affecting settings");
  if (config.status !== 1) fail("repository Git config inspection failed");
  const check = spawnSync(git, ["diff", "--cached", "--check"], { cwd, encoding: "utf8", env });
  if (check.status !== 0) fail(check.stdout.trim() || check.stderr.trim() || "staged changes contain whitespace errors");
  const staged = spawnSync(git, ["diff", "--cached", "--quiet"], { cwd, env });
  if (staged.status === 0) fail("staged changes are required");
  if (staged.status !== 1) fail("staged changes could not be inspected");
  const result = spawnSync(git, ["commit", "-m", args[1]], { cwd, encoding: "utf8", env });
  if (result.status !== 0) fail(result.stderr.trim() || "git commit failed");
  const priorHead = record.head;
  const temporary = `${statePath}.tmp-${process.pid}`;
  let temporaryCreated = false;
  try {
    const committed = spawnSync(git, ["rev-parse", "HEAD"], { cwd, encoding: "utf8", env });
    if (committed.status !== 0 || !/^[0-9a-f]{40}$/.test(committed.stdout.trim())) fail("committed HEAD could not be recorded");
    record.head = committed.stdout.trim();
    const descriptor = openSync(temporary, "wx", 0o600);
    temporaryCreated = true;
    try { writeFileSync(descriptor, `${JSON.stringify(state, null, 2)}\n`); } finally { closeSync(descriptor); }
    renameSync(temporary, statePath);
    temporaryCreated = false;
  } catch (error) {
    let cleanupError;
    if (temporaryCreated) {
      try { unlinkSync(temporary); } catch (cleanup) { if (cleanup.code !== "ENOENT") cleanupError = cleanup; }
    }
    const rollback = spawnSync(git, ["reset", "--soft", priorHead], { cwd, encoding: "utf8", env });
    if (rollback.status !== 0) fail(`registry update failed (${error.message}); commit rollback failed: ${rollback.stderr.trim()}`);
    if (cleanupError) fail(`registry update failed (${error.message}); temporary cleanup failed after commit rollback: ${cleanupError.message}`);
    throw error;
  }
  return result.stdout;
  } finally {
    unlinkSync(lockPath);
  }
}

if (process.argv[1] && fileURLToPath(import.meta.url) === realpathSync(process.argv[1])) {
  try {
    if (process.argv.length !== 5) fail("usage: git-commit.mjs ISSUE -m MESSAGE");
    process.stdout.write(commitFeature(process.argv[2], process.argv.slice(3)));
  } catch (error) { process.stderr.write(`ERROR: ${error.message}\n`); process.exitCode = 1; }
}
