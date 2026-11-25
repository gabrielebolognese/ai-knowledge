import { defineConfig, devices } from '@playwright/test';

// Tests run against the production build (astro build + pagefind) served by `astro preview`.
// 4329 collided with another local Astro preview (the default-ish port range); use a less common one.
const PORT = Number(process.env.AIK_TEST_PORT || 4391);

export default defineConfig({
  testDir: './tests',
  timeout: 60_000,
  // One worker: deterministic runs; every test still gets its own fresh browser context (own localStorage).
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [['list']],
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    viewport: { width: 1440, height: 900 },
    trace: 'retain-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 900 } } }],
  webServer: {
    command: `npm run build && npx astro preview --ignore-lock --host 127.0.0.1 --port ${PORT}`,
    url: `http://127.0.0.1:${PORT}/`,
    timeout: 600_000,
    reuseExistingServer: !process.env.CI,
    stdout: 'ignore',
    stderr: 'pipe',
  },
});
