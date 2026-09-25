#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { closeSync, constants, fstatSync, lstatSync, openSync, readFileSync } from "node:fs";
import { dirname } from "node:path";
import { pathToFileURL } from "node:url";

const ENDPOINT = "https://ntfy.sh";
const TOPIC_FILE = "/Users/hello/factory-secrets/ntfy_topic";
const TOPIC_PATTERN = /^[-_a-zA-Z0-9]{32,64}$/;

export function loadTopic({ path = TOPIC_FILE, lstat = lstatSync, open = openSync, fstat = fstatSync, readFile = readFileSync, close = closeSync, uid = process.getuid() } = {}) {
  let descriptor;
  try {
    const directory = lstat(dirname(path));
    if (!directory.isDirectory() || directory.isSymbolicLink() || (directory.mode & 0o777) !== 0o700 || directory.uid !== uid) return null;
    descriptor = open(path, constants.O_RDONLY | constants.O_NOFOLLOW);
    const file = fstat(descriptor);
    if (!file.isFile() || (file.mode & 0o777) !== 0o400 || file.uid !== uid || file.size > 128) return null;
    const topic = readFile(descriptor, "utf8").trim();
    return TOPIC_PATTERN.test(topic) ? topic : null;
  } catch { return null; } finally { if (descriptor !== undefined) close(descriptor); }
}

export async function publishCompletion({ result = "completed", topic, fetchImpl = fetch, sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms)) } = {}) {
  if (!new Set(["completed", "blocked"]).has(result)) throw new Error("result must be completed or blocked");
  if (!TOPIC_PATTERN.test(topic ?? "")) return { status: "not_configured" };
  for (let attempt = 1; attempt <= 3; attempt += 1) {
    try {
      const response = await fetchImpl(ENDPOINT, { method: "POST", redirect: "error", signal: AbortSignal.timeout(10000), headers: { "content-type": "application/json" }, body: JSON.stringify({ topic, message: result === "completed" ? "A non-trivial OpenCode task completed." : "A non-trivial OpenCode task needs attention.", title: result === "completed" ? "OpenCode task complete" : "OpenCode task blocked", tags: [result === "completed" ? "white_check_mark" : "warning"] }) });
      if (response.ok) return { status: "sent", attempts: attempt };
      if (response.status !== 429) return { status: "failed", attempts: attempt };
    } catch { return { status: "delivery_uncertain", attempts: attempt }; }
    if (attempt < 3) await sleep(100 * 2 ** (attempt - 1));
  }
  return { status: "failed", attempts: 3 };
}

function fallback(result) {
  return spawnSync("/usr/bin/osascript", ["-e", `display notification "OpenCode task ${result}" with title "OpenCode"`], { stdio: "ignore", timeout: 5000 }).status === 0 ? "sent" : "failed";
}

export async function notifyCompletion({ result = "completed", topicSource, ...options } = {}) {
  try {
    const delivery = await publishCompletion({ ...options, result, topic: loadTopic(topicSource) });
    return delivery.status === "sent" ? delivery : { ...delivery, fallback: fallback(result) };
  } catch { return { status: "failed_before_delivery", fallback: fallback(result) }; }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const index = process.argv.indexOf("--result");
  const result = index < 0 ? "completed" : process.argv[index + 1];
  process.stdout.write(`${JSON.stringify(await notifyCompletion({ result }))}\n`);
}
