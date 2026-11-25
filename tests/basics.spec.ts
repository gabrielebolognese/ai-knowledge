import { test, expect } from '@playwright/test';

// Site basics: titles and meta on every page type, favicon, the 404 page and a visible keyboard focus ring.
const PAGES = ['/', '/course/', '/course/beginner/', '/course/beginner/vectors-dot-product/', '/projects/', '/exercises/', '/glossary/', '/glossary/backpropagation/', '/certificate/'];

test.describe('site basics', () => {
  test('every page type has a title, description, favicon and one h1', async ({ page }) => {
    for (const path of PAGES) {
      const res = await page.goto(path);
      expect(res?.status(), path).toBe(200);
      await expect(page, path).toHaveTitle(/AI Knowledge/);
      const desc = await page.locator('meta[name="description"]').getAttribute('content');
      expect(desc?.length ?? 0, `${path} description`).toBeGreaterThan(40);
      await expect(page.locator('meta[property="og:title"]'), path).toHaveCount(1);
      await expect(page.locator('link[rel="icon"]'), path).toHaveAttribute('href', '/favicon.svg');
      await expect(page.locator('h1'), path).toHaveCount(1);
    }
    const icon = await page.request.get('/favicon.svg');
    expect(icon.status()).toBe(200);
  });

  test('unknown URLs get the 404 page with ways back into the course', async ({ page }) => {
    const res = await page.goto('/this-page-does-not-exist/');
    expect(res?.status()).toBe(404);
    await expect(page).toHaveTitle(/Page not found/);
    await expect(page.locator('h1')).toContainText('not in the course');
    await expect(page.locator('main a[href="/course/"]')).toBeVisible();
  });

  test('keyboard focus is visible', async ({ page }) => {
    await page.goto('/course/');
    await page.keyboard.press('Tab'); // skip link
    await page.keyboard.press('Tab');
    const shadow = await page.evaluate(() => getComputedStyle(document.activeElement as Element).boxShadow);
    expect(shadow).not.toBe('none');
  });
});
