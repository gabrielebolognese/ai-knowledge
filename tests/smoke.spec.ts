import { test, expect } from '@playwright/test';

const LESSON = '/course/beginner/artificial-neuron/';

test.describe('lesson page smoke test', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
  });

  test('the lesson renders as a sourced, Wikipedia-style article', async ({ page }) => {
    await page.goto(LESSON);
    await expect(page.locator('h1')).toHaveText('The artificial neuron');
    await expect(page.locator('.breadcrumb')).toContainText('Course');
    await expect(page.locator('.infobox')).toContainText('Level');
    await expect(page.locator('.hatnote')).toBeVisible();

    // Citations are numbered by first use and resolve to the References list.
    const firstCite = page.locator('sup.cite a').first();
    await expect(firstCite).toHaveText('[1]');
    await expect(page.locator('#references')).toBeVisible();
    expect(await page.locator('ol.references > li').count()).toBeGreaterThanOrEqual(3);
    await expect(page.locator('#ref-1 a.ext')).toHaveAttribute('href', /^https:\/\//);

    // KaTeX math, the analogy callout, glossary terms, code file and exercises are present.
    await expect(page.locator('.katex').first()).toBeVisible();
    await expect(page.locator('[data-analogy]').first()).toBeVisible();
    await expect(page.locator('.term__link').first()).toHaveAttribute('href', /\/glossary\/#/);
    await expect(page.locator('[data-codefile] pre.astro-code')).toBeVisible();
    expect(await page.locator('[data-exercise]').count()).toBeGreaterThanOrEqual(2);

    // Step-by-step math: starts at step 1, reveals more on "Next step", "Show all" reveals all.
    const ms = page.locator('[data-mathsteps]').first();
    await expect(ms.locator('[data-ms-count]')).toHaveText(/^Step 1 of \d+$/);
    await expect(ms.locator('[data-step]:visible')).toHaveCount(1);
    await ms.locator('[data-ms-next]').click();
    await expect(ms.locator('[data-ms-count]')).toHaveText(/^Step 2 of/);
    await expect(ms.locator('[data-step]:visible')).toHaveCount(2);
    await ms.locator('[data-ms-all]').click();
    const total = await ms.locator('[data-step]').count();
    await expect(ms.locator('[data-step]:visible')).toHaveCount(total);
  });

  test('mark complete persists after reload', async ({ page }) => {
    await page.goto(LESSON);
    const toggle = page.locator('[data-lesson-toggle="artificial-neuron"][data-primary]');
    await expect(toggle).toHaveAttribute('aria-pressed', 'false');
    await toggle.click();
    await expect(toggle).toHaveAttribute('aria-pressed', 'true');
    await expect(toggle).toContainText('Completed');

    await page.reload();
    const after = page.locator('[data-lesson-toggle="artificial-neuron"][data-primary]');
    await expect(after).toHaveAttribute('aria-pressed', 'true');
    // The mirrored rail button and the outline reflect it too.
    await expect(page.locator('.lesson-aside [data-lesson-toggle="artificial-neuron"]')).toHaveAttribute('aria-pressed', 'true');
    await expect(page.locator('.lesson-rail a[data-lesson-status="artificial-neuron"]')).toHaveAttribute('data-done', 'true');

    const stored = await page.evaluate(() => JSON.parse(localStorage.getItem('aik-progress-v1') || '{}'));
    expect(stored.lessons['artificial-neuron'].done).toBe(true);
    expect(typeof stored.lessons['artificial-neuron'].at).toBe('string');
    expect(stored.lastVisited.slug).toBe('artificial-neuron');

    // Undo also persists (full control).
    await after.click();
    await page.reload();
    await expect(page.locator('[data-lesson-toggle="artificial-neuron"][data-primary]')).toHaveAttribute('aria-pressed', 'false');
  });

  test('exercise self-check marks the exercise done', async ({ page }) => {
    await page.goto(LESSON);
    const ex = page.locator('[data-exercise="neuron-weighted-sum"]');
    await ex.locator('input[type=text]').fill('4');
    await ex.locator('[data-ex-check]').click();
    await expect(ex).toHaveAttribute('data-result', 'incorrect');
    await ex.locator('input[type=text]').fill('5');
    await ex.locator('[data-ex-check]').click();
    await expect(ex).toHaveAttribute('data-result', 'correct');
    await expect(ex.locator('input[data-exercise-toggle]')).toBeChecked();
    await page.reload();
    await expect(page.locator('[data-exercise="neuron-weighted-sum"] input[data-exercise-toggle]')).toBeChecked();
  });

  test('narrow windows get the desktop-only notice', async ({ page }) => {
    await page.setViewportSize({ width: 800, height: 900 });
    await page.goto(LESSON);
    await expect(page.locator('.desktop-notice')).toBeVisible();
    await expect(page.locator('.desktop-notice')).toContainText('designed for PC');
  });
});
