import { defineConfig } from "@playwright/test";
import path from "node:path";
import { fileURLToPath } from "node:url";
const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const url = "http://127.0.0.1:8174";
export default defineConfig({
  testDir: "e2e",
  workers: 1,
  timeout: 30000,
  use: {
    baseURL: url,
    launchOptions: { executablePath: process.env.CHROME_PATH || undefined },
    viewport: { width: 1440, height: 1000 },
  },
  webServer: {
    cwd: repo,
    command:
      (process.env.TEST_PYTHON || ".venv/bin/python") +
      " -m tests.smoke_server",
    url: url + "/api/health",
    reuseExistingServer: false,
    timeout: 60000,
  },
});
