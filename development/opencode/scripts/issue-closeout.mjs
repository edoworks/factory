#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { realpathSync } from "node:fs";
import { isAbsolute } from "node:path";
import { fileURLToPath } from "node:url";

const GITHUB_REPO = "github.com/edoworks/factory";
const GITHUB_IDENTITY = "hellofoculoom";

function fail(message) {
  throw new Error(message);
}

function githubCli(environment) {
  const configured = environment.FACTORY_DEV_GH;
  if (!configured || !isAbsolute(configured) || /\s/.test(configured)) fail("FACTORY_DEV_GH must identify the pinned GitHub CLI");
  return realpathSync(configured);
}

function cleanEnvironment(environment) {
  const clean = { ...environment };
  for (const name of Object.keys(clean)) {
    if (name === "GH_CONFIG_DIR") continue;
    if (name.startsWith("GH_") || name.startsWith("GITHUB_") || ["ALL_PROXY", "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "all_proxy", "http_proxy", "https_proxy", "no_proxy"].includes(name)) {
      delete clean[name];
    }
  }
  return clean;
}

function authenticatedGithubCli(environment) {
  const cli = githubCli(environment);
  const result = spawnSync(cli, ["api", "--hostname", "github.com", "user", "--jq", ".login"], { encoding: "utf8", env: cleanEnvironment(environment) });
  if (result.status !== 0) fail(result.stderr.trim() || "GitHub identity check failed");
  if (result.stdout.trim() !== GITHUB_IDENTITY) fail(`GitHub identity must be ${GITHUB_IDENTITY}`);
  return cli;
}

export function parseIssueNumbers(value) {
  if (typeof value !== "string" || !value.trim()) throw new Error("--issues must contain one or more numeric issue numbers");
  const numbers = value.split(",").map((entry) => entry.trim());
  if (numbers.length > 100 || numbers.some((number) => !/^[1-9]\d{0,9}$/.test(number))) throw new Error("--issues must contain at most 100 canonical positive numeric issue numbers");
  if (new Set(numbers).size !== numbers.length) throw new Error("--issues must not contain duplicates");
  return numbers;
}

export function assertClosed(issues) {
  const open = issues.filter((issue) => issue.state !== "CLOSED");
  if (open.length) throw new Error(`tracking issues are not closed: ${open.map((issue) => `${issue.number}:${issue.state ?? "UNKNOWN"}`).join(", ")}`);
  return true;
}

export function parseArguments(argv) {
  if (argv.length !== 5 || argv[0] !== "verify" || argv[1] !== "--repo" || argv[2] !== "edoworks/factory" || argv[3] !== "--issues") {
    fail("usage: issue-closeout.mjs verify --repo edoworks/factory --issues NUMBER[,NUMBER...]");
  }
  return parseIssueNumbers(argv[4]);
}

export function verifyIssueCloseout(numbers, environment = process.env) {
  const cli = authenticatedGithubCli(environment);
  const transportEnvironment = cleanEnvironment(environment);
  const states = numbers.map((number) => {
    const result = spawnSync(cli, ["issue", "view", "--repo", GITHUB_REPO, number, "--json", "number,title,state"], { encoding: "utf8", env: transportEnvironment });
    if (result.status !== 0) throw new Error(result.stderr.trim() || `could not read edoworks/factory#${number}`);
    const issue = JSON.parse(result.stdout);
    if (!issue || typeof issue !== "object" || Array.isArray(issue) || issue.number !== Number(number) || typeof issue.title !== "string" || !issue.title || !["OPEN", "CLOSED"].includes(issue.state)) {
      fail(`invalid issue receipt for edoworks/factory#${number}`);
    }
    return issue;
  });
  assertClosed(states);
  return true;
}

function main(argv) {
  verifyIssueCloseout(parseArguments(argv));
  process.stdout.write("CLOSED\n");
}

if (process.argv[1] && fileURLToPath(import.meta.url) === realpathSync(process.argv[1])) {
  try { main(process.argv.slice(2)); } catch (error) { process.stderr.write(`ERROR: ${error.message}\n`); process.exitCode = 1; }
}
