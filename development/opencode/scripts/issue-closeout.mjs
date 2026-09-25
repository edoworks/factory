#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";

export function parseIssueNumbers(value) {
  if (typeof value !== "string" || !value.trim()) throw new Error("--issues must contain one or more numeric issue numbers");
  const numbers = value.split(",").map((entry) => entry.trim());
  if (numbers.some((number) => !/^\d+$/.test(number) || Number(number) < 1)) throw new Error("--issues must contain positive numeric issue numbers");
  if (new Set(numbers).size !== numbers.length) throw new Error("--issues must not contain duplicates");
  return numbers;
}

export function assertClosed(issues) {
  const open = issues.filter((issue) => issue.state !== "CLOSED");
  if (open.length) throw new Error(`tracking issues are not closed: ${open.map((issue) => `${issue.number}:${issue.state ?? "UNKNOWN"}`).join(", ")}`);
  return true;
}

function main(argv) {
  if (argv[0] !== "verify") throw new Error("usage: issue-closeout.mjs verify --repo edoworks/factory --issues NUMBER[,NUMBER...]");
  const repoIndex = argv.indexOf("--repo");
  const issuesIndex = argv.indexOf("--issues");
  if (argv[repoIndex + 1] !== "edoworks/factory" || issuesIndex < 0) throw new Error("repo must be edoworks/factory");
  const states = parseIssueNumbers(argv[issuesIndex + 1]).map((number) => {
    const result = spawnSync("gh", ["issue", "view", "--repo", "edoworks/factory", number, "--json", "number,title,state"], { encoding: "utf8" });
    if (result.status !== 0) throw new Error(result.stderr.trim() || `could not read edoworks/factory#${number}`);
    return JSON.parse(result.stdout);
  });
  assertClosed(states);
  process.stdout.write("CLOSED\n");
}

if (process.argv[1] && fileURLToPath(import.meta.url) === realpathSync(process.argv[1])) {
  try { main(process.argv.slice(2)); } catch (error) { process.stderr.write(`ERROR: ${error.message}\n`); process.exitCode = 1; }
}
