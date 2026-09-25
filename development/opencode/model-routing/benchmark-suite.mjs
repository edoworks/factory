import { createHash } from "node:crypto";

export const benchmarkFixtures = {
  routine: [
    { prompt: "Return only compact JSON with keys policy and test. From this text: 'Repository policy is AGENTS.md. Verification command is npm test.'", expect: { kind: "json", equals: { policy: "AGENTS.md", test: "npm test" } } },
    { prompt: "Return exactly SAFE if this shell command is read-only, otherwise return exactly MUTATING: git status --short --branch", expect: { kind: "exact", value: "SAFE" } }
  ],
  standard: [
    { prompt: "Review this JavaScript and return only compact JSON with keys severity and fix. Code: async function load(){ return fetch('/x').json() }. The fix must identify the missing await before calling json().", expect: { kind: "json", matches: { severity: "bug|high|error|major", fix: "await" } } },
    { prompt: "Return only compact JSON with keys risk and action. A patch changes an authorization default from deny to allow only to make tests pass. Classify the risk and state the required action.", expect: { kind: "json", matches: { risk: "high|critical|security", action: "reject|revert|restore|do not" } } },
    { prompt: "Return only compact JSON with keys allowed and reason. Policy: never expose /var/run/docker.sock to a construction container. Proposal: mount /var/run/docker.sock read-write. Determine whether it is allowed.", expect: { kind: "json", equals: { allowed: false }, matches: { reason: "docker|socket|policy|never" } } }
  ]
};

export function benchmarkSuiteDigest(tier, minimumQuality, suiteVersion) {
  return createHash("sha256").update(JSON.stringify({ tier, minimum_quality: minimumQuality, suite_version: suiteVersion, checker_version: 1, fixtures: benchmarkFixtures[tier] })).digest("hex");
}
