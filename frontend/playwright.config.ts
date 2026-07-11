import { defineConfig, devices } from "@playwright/test";

const pythonBin = process.env.PYTHON_BIN ?? "../.venv/bin/python";
const backendPort = 8010;
const frontendPort = 5174;
const playwrightDatabaseUrl =
  process.env.PLAYWRIGHT_DATABASE_URL ?? `sqlite:////tmp/atlas-playwright-${Date.now()}.sqlite`;

export default defineConfig({
  testDir: "./tests",
  timeout: 60_000,
  expect: {
    timeout: 10_000,
  },
  use: {
    baseURL: `http://127.0.0.1:${frontendPort}`,
    trace: "on-first-retry",
  },
  webServer: [
    {
      command: `${pythonBin} -m uvicorn app.main:app --host 127.0.0.1 --port ${backendPort}`,
      cwd: "../backend",
      env: {
        DATABASE_URL: playwrightDatabaseUrl,
        JWT_SECRET_KEY: "playwright-secret",
        CORS_ORIGINS: `["http://127.0.0.1:${frontendPort}","http://localhost:${frontendPort}"]`,
      },
      url: `http://127.0.0.1:${backendPort}/health`,
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command: `npm run dev -- --host 127.0.0.1 --port ${frontendPort} --strictPort`,
      env: {
        VITE_API_BASE_URL: `http://127.0.0.1:${backendPort}/api`,
      },
      url: `http://127.0.0.1:${frontendPort}`,
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
