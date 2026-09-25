import { appendFile, mkdir } from "node:fs/promises";
import { createHash } from "node:crypto";
import { dirname, join } from "node:path";
import { homedir } from "node:os";

function attributionPath() {
  return process.env.MODEL_ROUTING_ATTRIBUTION_LOG
    || join(process.env.XDG_STATE_HOME || join(homedir(), ".local", "state"), "opencode", "routing", "tool-attribution.jsonl");
}

export async function recordToolAttribution({ sessionID, agent, provider, model, tool, path = attributionPath() }) {
  const record = { timestamp: new Date().toISOString(), session: createHash("sha256").update(String(sessionID)).digest("hex").slice(0, 16), agent, provider, model, tool };
  try {
    await mkdir(dirname(path), { recursive: true, mode: 0o700 });
    await appendFile(path, `${JSON.stringify(record)}\n`, { encoding: "utf8", mode: 0o600 });
  } catch {
    // Attribution is fail-open and must never block tool execution.
  }
}

export function messageText(message) {
  const parts = Array.isArray(message?.parts) ? message.parts : [];
  return parts.filter((part) => part?.type === "text").map((part) => String(part.text ?? "")).join("\n").trim();
}
