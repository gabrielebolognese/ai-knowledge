import { test, expect } from '@playwright/test';

// Navigation pages: header, track pages, projects, glossary and the Pagefind search palette.
test.describe('navigation pages', () => {
  test('header has the five sections, search and overall progress', async ({ page }) => {
    await page.goto('/course/');
    const nav = page.locator('header nav[aria-label="Main"] a');
    await expect(nav).toHaveText(['Course', 'Projects', 'Exercises', 'Glossary', 'Certificate']);
    await expect(page.getByTestId('header-progress')).toContainText('0%');
  });

  test('search palette finds lessons and glossary terms from the static index', async ({ page }) => {
    await page.goto('/projects/');
    await page.locator('[data-search-open]').click();
    await page.locator('[data-search-input]').fill('gradient');
    await expect(page.locator('.sp__item').first()).toBeVisible({ timeout: 10_000 });
    await expect(page.locator('.sp__group', { hasText: 'Glossary' })).toHaveCount(1);
    await expect(page.locator('.sp__item[href="/glossary/gradient-descent/"]')).toHaveCount(1);
    await page.keyboard.press('Escape');
    await page.keyboard.press('/');
    await expect(page.locator('[data-search-dialog]')).toBeVisible();
  });

  test('every track page renders, project tracks show their quick start', async ({ page }) => {
    for (const id of ['setup', 'beginner', 'intermediate', 'advanced', 'project-digits-letters', 'project-doodles', 'project-text', 'project-code-autocomplete', 'project-chess']) {
      await page.goto(`/course/${id}/`);
      await expect(page.locator('h1')).toBeVisible();
      await expect(page.locator('li[data-node]').first()).toBeVisible();
      if (id.startsWith('project-')) await expect(page.locator('.tp-quick li').first()).toBeVisible();
    }
  });

  test('projects page has six cards with quick-start lists and working start links', async ({ page }) => {
    await page.goto('/projects/');
    const cards = page.locator('.pj-card');
    await expect(cards).toHaveCount(6);
    for (const key of ['digits', 'letters', 'doodles', 'text', 'code', 'chess']) {
      const href = await page.getByTestId(`start-${key}`).getAttribute('href');
      expect((await page.request.get(href!)).status(), href!).toBe(200);
      expect(await page.locator(`[data-project="${key}"] .pj-quick__list li`).count()).toBeGreaterThan(0);
    }
  });

  test('glossary index is alphabetical and links to term pages', async ({ page }) => {
    await page.goto('/glossary/');
    const terms = await page.locator('.gl-entry__term').allTextContents();
    expect(terms.length).toBeGreaterThan(20);
    const sorted = [...terms].sort((a, b) => a.localeCompare(b, 'en', { sensitivity: 'base' }));
    expect(terms).toEqual(sorted);
    await page.locator('.gl-entry__term', { hasText: /^Gradient descent$/ }).click();
    await expect(page).toHaveURL(/\/glossary\/gradient-descent\/$/);
    await expect(page.locator('h1')).toHaveText('Gradient descent');
    await expect(page.locator('.gt-refs li a').first()).toHaveAttribute('href', /^https:\/\//);
  });

  test('a planned lesson renders a coming-soon page that can still be marked complete', async ({ page }) => {
    await page.goto('/course/');
    const planned = page.locator('li[data-node][data-written="false"] a.node__link').first();
    const href = (await planned.getAttribute('href'))!;
    await page.goto(href);
    await expect(page.locator('.planned__badge')).toContainText('Coming soon');
    const toggle = page.locator('.planned__cta [data-lesson-toggle]');
    await toggle.click();
    await page.reload();
    await expect(toggle).toHaveAttribute('aria-pressed', 'true');
  });
});
