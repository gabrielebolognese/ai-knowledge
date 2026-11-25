import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

// Numbers on the landing page must come from curriculum.json, so the test recomputes them.
const curriculum = JSON.parse(readFileSync(new URL('../src/data/curriculum.json', import.meta.url), 'utf8'));
const slugs = new Set<string>();
for (const t of curriculum.tracks) for (const m of t.modules) for (const l of m.lessons) slugs.add(l.slug);

test.describe('landing page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('hero shows the promise and the three entry paths', async ({ page }) => {
    await expect(page.locator('h1')).toHaveCount(1);
    await expect(page.locator('h1')).toContainText('Learn deep learning from zero to building your own chess engine');
    await expect(page.locator('h1')).toContainText('free');
    await expect(page.locator('[data-cta="start"]')).toHaveText(/Start the course/);
    await expect(page.locator('[data-cta="setup"]')).toHaveText(/Set up Python first/);
    await expect(page.locator('[data-cta="projects"]')).toHaveText(/Jump to a project/);
    // Exactly one filled primary button in the hero.
    await expect(page.locator('.hero .btn-primary')).toHaveCount(1);
  });

  test('"Start the course" goes to /course/', async ({ page }) => {
    await page.locator('[data-cta="start"]').click();
    await expect(page).toHaveURL(/\/course\/?$/);
  });

  test('"Set up Python first" goes to the setup track', async ({ page }) => {
    await page.locator('[data-cta="setup"]').click();
    await expect(page).toHaveURL(/\/course\/setup\//);
    await expect(page.locator('h1')).toBeVisible();
  });

  test('"Jump to a project" goes to /projects/', async ({ page }) => {
    await page.locator('[data-cta="projects"]').click();
    await expect(page).toHaveURL(/\/projects\/?$/);
  });

  test('numbers come from curriculum.json', async ({ page }) => {
    const trust = page.locator('.trust');
    await expect(trust).toContainText(`${slugs.size} lessons`);
    await expect(trust).toContainText(`${Object.keys(curriculum.sourceRegistry).length} cited sources`);
    const beginner = curriculum.tracks.find((t: any) => t.id === 'beginner');
    const n = beginner.modules.reduce((s: number, m: any) => s + m.lessons.length, 0);
    const stop = page.locator('.stop[data-track="beginner"]');
    await expect(stop.locator('dd').nth(0)).toHaveText(String(beginner.modules.length));
    await expect(stop.locator('dd').nth(1)).toHaveText(String(n));
  });

  test('six project cards with original SVG art link to real lessons', async ({ page }) => {
    const cards = page.locator('.project-card');
    await expect(cards).toHaveCount(6);
    for (const kind of ['digit', 'letter', 'doodle', 'text', 'code', 'chess']) {
      await expect(page.locator(`.project-card svg.pa--${kind}`)).toHaveCount(1);
    }
    const hrefs = await cards.evaluateAll((els) => els.map((e) => e.getAttribute('href')));
    for (const href of hrefs) {
      const res = await page.request.get(href!);
      expect(res.status(), href!).toBe(200);
    }
  });

  test('sources, certificate preview, FAQ and footer are present', async ({ page }) => {
    const refs = page.locator('.sample__refs li a');
    await expect(refs).toHaveCount(4);
    for (const a of await refs.all()) await expect(a).toHaveAttribute('href', /^https:\/\//);
    await page.locator('.sample__cite a[data-ref="2"]').hover();
    await expect(page.locator('#lref-2')).toHaveClass(/is-hl/);
    await expect(page.locator('.cert__preview svg')).toBeVisible();
    await expect(page.locator('a[href="/certificate/"]').first()).toBeVisible();
    for (const q of ['free', 'account', 'progress stored', 'phone']) {
      await expect(page.locator('.faq summary', { hasText: new RegExp(q, 'i') })).toHaveCount(1);
    }
    await expect(page.locator('footer a[href="https://github.com/gabrielebolognese/ai-knowledge"]').first()).toBeVisible();
    await expect(page.locator('footer')).toContainText(/licen/i);
  });
});
