#!/usr/bin/env node
import { createHash } from "node:crypto";
import { readFileSync, realpathSync } from "node:fs";
import { dirname, isAbsolute, relative, resolve } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

export const REQUIRED_SECTIONS = ["Outcome", "Scope", "Out of scope", "Acceptance criteria", "Verification", "Dependencies", "Authority and privacy", "Source provenance", "Classification", "Priority", "Triage review"];
const ALLOWED = new Set(["bug", "documentation", "enhancement", "good first issue", "help wanted", "question", "duplicate", "invalid", "wontfix"]);
const fail = (message) => { throw new Error(message); };
const requireString = (value, field) => { if (typeof value !== "string" || !value.trim()) fail(`${field} must be a non-empty string`); };
const requireArray = (value, field) => { if (!Array.isArray(value) || !value.length) fail(`${field} must be a non-empty array`); value.forEach((item) => requireString(item, `${field} entry`)); };
export const sha256 = (text) => createHash("sha256").update(text).digest("hex");
const githubCli = () => {
  const configured = process.env.FACTORY_DEV_GH;
  if (!configured || !isAbsolute(configured)) fail("FACTORY_DEV_GH must identify the pinned GitHub CLI");
  return realpathSync(configured);
};

export function validateIssueIntent(intentPath) {
  const absolute = realpathSync(intentPath);
  const intent = JSON.parse(readFileSync(absolute, "utf8"));
  if (intent.schema_version !== 1) fail("schema_version must be 1");
  requireString(intent.repo, "repo");
  if (intent.repo !== "edoworks/factory") fail("repo must be edoworks/factory");
  for (const field of ["title", "body_file", "body_sha256", "classification", "priority"]) requireString(intent[field], field);
  for (const field of ["labels", "dependencies", "authority_constraints", "source_provenance", "duplicate_review", "reprioritization_review"]) requireArray(intent[field], field);
  if (!ALLOWED.has(intent.classification) || !intent.labels.includes(intent.classification)) fail("labels must include an allowed classification");
  if (!/^P[0-3]$/.test(intent.priority)) fail("priority must be P0, P1, P2, or P3");
  if (isAbsolute(intent.body_file)) fail("body_file must be relative");
  const directory = dirname(absolute);
  const bodyPath = realpathSync(resolve(directory, intent.body_file));
  const bodyRelative = relative(directory, bodyPath);
  if (bodyRelative.startsWith("..") || isAbsolute(bodyRelative)) fail("body_file must stay within the intent directory");
  const body = readFileSync(bodyPath, "utf8");
  if (sha256(body) !== intent.body_sha256) fail("body_sha256 does not match body_file");
  const headings = new Map([...body.matchAll(/^# (.+?)\s*$/gm)].map((match, index, matches) => [match[1].toLowerCase(), body.slice(match.index + match[0].length, matches[index + 1]?.index ?? body.length).trim()]));
  for (const section of REQUIRED_SECTIONS) if (!headings.get(section.toLowerCase())) fail(`body is missing non-empty '# ${section}' section`);
  return { intent, intentPath: absolute, bodyPath, body };
}

export function verifyReadback(validated, remote) {
  if (remote.title !== validated.intent.title) fail("remote title differs from frozen intent");
  if (remote.body !== validated.body) fail("remote body differs from frozen body_file");
  return true;
}

function main(argv) {
  const [command, intentPath, issueNumber, ...extra] = argv;
  if (command === "hash") {
    if (extra.length || !intentPath || issueNumber) fail("usage: issue-intent.mjs hash BODY.md");
    process.stdout.write(`${sha256(readFileSync(realpathSync(intentPath), "utf8"))}\n`);
    return;
  }
  if (extra.length || !intentPath || !["validate", "create", "verify-remote"].includes(command)) fail("usage: issue-intent.mjs hash BODY.md | validate INTENT.json | create INTENT.json | verify-remote INTENT.json ISSUE_NUMBER");
  const validated = validateIssueIntent(intentPath);
  if (command === "create") {
    if (issueNumber) fail("unexpected issue number");
    const args = ["issue", "create", "--repo", validated.intent.repo, "--title", validated.intent.title, "--body", validated.body];
    for (const label of validated.intent.labels) args.push("--label", label);
    const result = spawnSync(githubCli(), args, { encoding: "utf8" });
    if (result.status !== 0) fail(result.stderr.trim() || "gh issue create failed");
    process.stdout.write(result.stdout);
    return;
  } else if (command === "verify-remote") {
    if (!/^\d+$/.test(issueNumber ?? "")) fail("issue number must be numeric");
    const result = spawnSync(githubCli(), ["issue", "view", "--repo", "edoworks/factory", issueNumber, "--json", "title,body,labels"], { encoding: "utf8" });
    if (result.status !== 0) fail(result.stderr.trim() || "gh issue view failed");
    const remote = JSON.parse(result.stdout);
    verifyReadback(validated, remote);
    const labels = new Set((remote.labels ?? []).map((label) => label.name ?? label));
    for (const label of validated.intent.labels) if (!labels.has(label)) fail(`remote issue is missing label: ${label}`);
  } else if (issueNumber) fail("unexpected issue number");
  process.stdout.write(`${command === "validate" ? "VALID" : "MATCH"}\n`);
}

if (process.argv[1] && fileURLToPath(import.meta.url) === realpathSync(process.argv[1])) {
  try { main(process.argv.slice(2)); } catch (error) { process.stderr.write(`ERROR: ${error.message}\n`); process.exitCode = 1; }
}
