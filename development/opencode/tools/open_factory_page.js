import { spawnSync } from "node:child_process";
import { tool } from "@opencode-ai/plugin";

const OPEN = "/usr/bin/open";
const CHROME_BUNDLE = "com.google.Chrome";
const REPOSITORY_PATH = "/edoworks/factory";
const fail = (message) => { throw new Error(message); };

const allowedPath = (pathname) => [
  /^\/edoworks\/factory\/?$/,
  /^\/edoworks\/factory\/issues\/[1-9]\d*\/?$/,
  /^\/edoworks\/factory\/pull\/[1-9]\d*(?:\/(?:files|commits|checks))?\/?$/,
  /^\/edoworks\/factory\/commit\/[0-9a-f]{40}\/?$/,
  /^\/edoworks\/factory\/(?:blob|tree)\/[0-9a-f]{40}\/[A-Za-z0-9._~+\/-]+$/,
  /^\/edoworks\/factory\/actions\/runs\/[1-9]\d*(?:\/job\/[1-9]\d*)?\/?$/,
].some((pattern) => pattern.test(pathname));

export function validateFactoryPageUrl(raw) {
  if (typeof raw !== "string" || !raw || /[\s\\%]/.test(raw)) fail("Factory page URL contains prohibited characters");
  if (raw !== "https://github.com" && !raw.startsWith("https://github.com/")) {
    fail("Factory page URL raw origin is not approved");
  }

  let url;
  try {
    url = new URL(raw);
  } catch {
    fail("Factory page URL is invalid");
  }
  if (url.protocol !== "https:" || url.hostname !== "github.com" || url.username || url.password || url.port) {
    fail("Factory page URL authority is not approved");
  }
  if (!url.pathname.startsWith(`${REPOSITORY_PATH}/`) && url.pathname !== REPOSITORY_PATH) {
    fail("Factory page URL repository is not approved");
  }
  if (url.pathname.includes("%") || !allowedPath(url.pathname)) fail("Factory page URL path is not approved");
  if (url.search && url.search !== "?plain=1") fail("Factory page URL query is not approved");
  if (url.hash && !/^#[A-Za-z0-9._~:-]+$/.test(url.hash)) fail("Factory page URL fragment is not approved");
  return url.href;
}

export function openFactoryPage(raw, launch = spawnSync) {
  const url = validateFactoryPageUrl(raw);
  const args = ["-n", "-b", CHROME_BUNDLE, "--args", "--guest", url];
  const result = launch(OPEN, args, { encoding: "utf8", shell: false, timeout: 10000 });
  if (result.error || result.status !== 0) fail("Chrome Guest failed to open the Factory page");
  return { launchAccepted: true, requestedBrowser: CHROME_BUNDLE, requestedMode: "guest", url };
}

const factoryPageTool = tool({
  description: "Open one validated public edoworks/factory GitHub review page in Chrome Guest without browser interaction.",
  args: {
    url: tool.schema.string().describe("Exact approved Factory GitHub issue, PR, commit, action, or revision-bound document URL"),
  },
  async execute(args) {
    return JSON.stringify(openFactoryPage(args.url));
  },
});

export default factoryPageTool;
