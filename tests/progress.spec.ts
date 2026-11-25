import { test, expect, type Page } from '@playwright/test';
import { readFileSync } from 'node:fs';

// Progress is stored only in localStorage ('aik-progress-v1'); these tests drive the dashboard,
// the data panel and the exercise library, and check that marks survive reloads and show up
// on other pages.
const curriculum = JSON.parse(readFileSync(new URL('../src/data/curriculum.json', import.meta.url), 'utf8'));
const beginner = curriculum.tracks.find((t: any) => t.id === 'beginner');
const LESSON = 'artificial-neuron';
const LESSON_URL = '/course/beginner/artificial-neuron/';
const STORAGE_KEY = 'aik-progress-v1';

const node = (page: Page, slug: string) => page.locator(`li[data-node="${slug}"]`).first();
const nodeToggle = (page: Page, slug: string) => node(page, slug).locator(`button[data-lesson-toggle="${slug}"]`);
const stored = (page: Page) => page.evaluate((k) => JSON.parse(localStorage.getItem(k) || '{}'), STORAGE_KEY);

test.describe('progress', () => {
  test('marking a lesson on the dashboard persists after reload and shows on the lesson page', async ({ page }) => {
    await page.goto('/course/');
    const toggle = nodeToggle(page, LESSON);
    await expect(toggle).toHaveAttribute('aria-pressed', 'false');
    await toggle.click(); // one click
    await expect(toggle).toHaveAttribute('aria-pressed', 'true');
    await expect(node(page, LESSON)).toHaveAttribute('data-state', 'done');
    // The beginner track counter and the header ring both move.
    const total = beginner.modules.reduce((s: number, m: any) => s + m.lessons.length, 0);
    await expect(page.locator('.pm__head[data-progress-slugs]').filter({ has: page.locator('#pm-beginner') }).locator('[data-progress-text]').first()).toHaveText(`1 / ${total}`);
    await expect(page.locator('[data-testid="header-progress"] [data-progress-pct]')).not.toHaveText('0%');

    await page.reload();
    await expect(nodeToggle(page, LESSON)).toHaveAttribute('aria-pressed', 'true');
    await expect(node(page, LESSON)).toHaveAttribute('data-state', 'done');

    await page.goto(LESSON_URL);
    await expect(page.locator('.complete-cta [data-lesson-toggle]')).toHaveAttribute('aria-pressed', 'true');
    await expect(page.locator('.lesson-meta__status')).toHaveAttribute('data-done', 'true');

    // Unmark from the dashboard again: one click, also persisted.
    await page.goto('/course/');
    await nodeToggle(page, LESSON).click();
    await page.reload();
    await expect(nodeToggle(page, LESSON)).toHaveAttribute('aria-pressed', 'false');
  });

  test('"Continue" points at the next lesson and every node is a link', async ({ page }) => {
    await page.goto('/course/');
    const first = beginner.modules[0].lessons[0];
    await expect(page.getByTestId('continue')).toHaveAttribute('href', `/course/beginner/${first.slug}/`);
    await nodeToggle(page, first.slug).click();
    const second = beginner.modules[0].lessons[1];
    await expect(page.getByTestId('continue')).toHaveAttribute('href', `/course/beginner/${second.slug}/`);
    // Upcoming lessons only look locked: they are still plain links to real pages.
    const later = page.locator('li[data-node][data-state="later"] a.node__link').first();
    const href = await later.getAttribute('href');
    const res = await page.request.get(href!);
    expect(res.status()).toBe(200);
  });

  test('"Mark module complete" marks and unmarks a whole module', async ({ page }) => {
    await page.goto('/course/');
    const mod = beginner.modules[2]; // the math module
    const slugs: string[] = mod.lessons.map((l: any) => l.slug);
    const moduleEl = page.locator(`[data-module="${mod.id}"]`);
    const bulk = moduleEl.locator('button[data-bulk-toggle]');
    await expect(bulk).toContainText('Mark module complete');
    await bulk.click();
    for (const s of slugs) await expect(nodeToggle(page, s)).toHaveAttribute('aria-pressed', 'true');
    await expect(moduleEl).toHaveAttribute('data-complete', 'true');
    await expect(bulk).toContainText('Unmark module');

    await page.reload();
    for (const s of slugs) await expect(nodeToggle(page, s)).toHaveAttribute('aria-pressed', 'true');
    const state = await stored(page);
    for (const s of slugs) expect(state.lessons[s]?.done).toBe(true);
    // Lessons outside the module are untouched.
    expect(state.lessons[beginner.modules[0].lessons[0].slug]?.done ?? false).toBe(false);

    await page.locator(`[data-module="${mod.id}"] button[data-bulk-toggle]`).click();
    for (const s of slugs) await expect(nodeToggle(page, s)).toHaveAttribute('aria-pressed', 'false');
  });

  test('export → reset → import restores the saved state', async ({ page }) => {
    await page.goto('/course/');
    await nodeToggle(page, LESSON).click();
    await nodeToggle(page, 'gradient-descent').click();
    // An exercise mark and a certificate name are part of the state too.
    await page.evaluate((k) => {
      const s = JSON.parse(localStorage.getItem(k)!);
      s.exercises['neuron-weighted-sum'] = { done: true, at: new Date().toISOString() };
      s.name = 'Ada Lovelace';
      localStorage.setItem(k, JSON.stringify(s));
    }, STORAGE_KEY);
    await page.reload();
    const before = await stored(page);
    expect(before.lessons[LESSON].done).toBe(true);

    const [download] = await Promise.all([page.waitForEvent('download'), page.locator('[data-pp-export]').click()]);
    expect(download.suggestedFilename()).toMatch(/^ai-knowledge-progress-\d{4}-\d{2}-\d{2}\.json$/);
    const file = await download.path();
    const exported = JSON.parse(readFileSync(file!, 'utf8'));
    expect(exported.lessons[LESSON].done).toBe(true);

    // Reset needs a typed confirmation.
    await page.locator('[data-pp-reset]').click();
    const confirm = page.locator('[data-pp-reset-confirm]');
    await expect(confirm).toBeDisabled();
    await page.locator('[data-pp-reset-input]').fill('reset');
    await expect(confirm).toBeEnabled();
    await confirm.click();
    await expect(nodeToggle(page, LESSON)).toHaveAttribute('aria-pressed', 'false');
    await page.reload();
    await expect(nodeToggle(page, LESSON)).toHaveAttribute('aria-pressed', 'false');
    const empty = await stored(page);
    expect(Object.keys(empty.lessons ?? {})).toHaveLength(0);

    // Import the exported file (replace).
    await page.locator('[data-pp-file]').setInputFiles(file!);
    await expect(page.locator('[data-pp-import-summary]')).toContainText('2 completed lessons');
    await page.locator('[data-pp-replace]').click();
    await expect(nodeToggle(page, LESSON)).toHaveAttribute('aria-pressed', 'true');
    await page.reload();
    await expect(nodeToggle(page, LESSON)).toHaveAttribute('aria-pressed', 'true');
    await expect(nodeToggle(page, 'gradient-descent')).toHaveAttribute('aria-pressed', 'true');
    const after = await stored(page);
    expect(after.lessons).toEqual(before.lessons);
    expect(after.exercises).toEqual(before.exercises);
    expect(after.name).toBe('Ada Lovelace');
  });

  test('exercise library: filters, search, mark done persists', async ({ page }) => {
    await page.goto('/exercises/');
    const items = page.locator('[data-lib-item]');
    const total = await items.count();
    expect(total).toBeGreaterThan(50);
    await expect(page.locator('[data-lib-count]')).toHaveText(`Showing ${total} of ${total} exercises`);

    // Track + type filter.
    await page.locator('[data-lib-track]').selectOption('beginner');
    await page.locator('input[name="type"][value="numeric"]').check();
    const visible = page.locator('[data-lib-item]:not([hidden])');
    const n = await visible.count();
    expect(n).toBeGreaterThan(0);
    expect(n).toBeLessThan(total);
    for (const it of await visible.all()) {
      await expect(it).toHaveAttribute('data-track', 'beginner');
      await expect(it).toHaveAttribute('data-type', 'numeric');
    }
    await expect(page).toHaveURL(/track=beginner/);
    await expect(page).toHaveURL(/type=numeric/);

    // Mark the first visible one done, from the library.
    const first = visible.first();
    const id = (await first.getAttribute('data-lib-item'))!;
    await first.locator(`input[data-exercise-toggle="${id}"]`).check();
    await expect(page.locator('[data-lib-done]')).toHaveText(`1 / ${total} done`);

    // Status filter: "Done" shows exactly that one; "To do" hides it.
    await page.locator('input[name="status"][value="done"]').check({ force: true });
    await expect(page.locator('[data-lib-item]:not([hidden])')).toHaveCount(1);
    await expect(page.locator(`[data-lib-item="${id}"]`)).toBeVisible();
    await page.locator('input[name="status"][value="todo"]').check({ force: true });
    await expect(page.locator(`[data-lib-item="${id}"]`)).toBeHidden();

    // Reload: filters come back from the URL and the mark persists.
    await page.reload();
    await page.locator('[data-lib-clear]').click();
    await expect(page.locator('[data-lib-count]')).toHaveText(`Showing ${total} of ${total} exercises`);
    await expect(page.locator(`input[data-exercise-toggle="${id}"]`)).toBeChecked();

    // Text search narrows the list, and each result links back to its lesson.
    await page.locator('[data-lib-q]').fill('softmax');
    const hits = page.locator('[data-lib-item]:not([hidden])');
    expect(await hits.count()).toBeGreaterThan(0);
    expect(await hits.count()).toBeLessThan(total);
    const lessonHref = await hits.first().locator('[data-lib-lesson]').getAttribute('href');
    expect(lessonHref).toMatch(/^\/course\/[a-z-]+\/[a-z0-9-]+\/$/);

    // The same mark shows on the lesson page.
    await page.locator('[data-lib-q]').fill('');
    const owner = await page.locator(`[data-lib-item="${id}"] [data-lib-lesson]`).getAttribute('href');
    await page.goto(owner!);
    await expect(page.locator(`input[data-exercise-toggle="${id}"]`)).toBeChecked();
  });
});
