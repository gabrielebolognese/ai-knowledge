import { test, expect, type Page } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';

// Certificate generator: lock state, live preview, name auto-fit, PNG/PDF downloads.
// The sample PNG is copied to $FOREMAN_ARTIFACTS_DIR (or $CERT_SAMPLE_DIR) when set,
// otherwise to test-results/certificate-sample.png.
const SAMPLE_DIR = process.env.CERT_SAMPLE_DIR || process.env.FOREMAN_ARTIFACTS_DIR || path.join('test-results');

function pngSize(file: string) {
  const b = fs.readFileSync(file);
  expect(b.subarray(1, 4).toString('latin1')).toBe('PNG');
  return { width: b.readUInt32BE(16), height: b.readUInt32BE(20), bytes: b.length };
}

async function openReady(page: Page, url: string) {
  await page.goto(url);
  await expect(page.locator('[data-cert-page]')).toHaveAttribute('data-ready', 'true', { timeout: 20_000 });
}

test.describe('certificate', () => {
  test('locked by default: watermark, disabled downloads and links to the remaining lessons', async ({ page }) => {
    await openReady(page, '/certificate/');
    await expect(page.locator('[data-cert-page]')).toHaveAttribute('data-state', 'locked');
    await expect(page.locator('[data-cert-watermark]')).toBeVisible();
    await page.locator('[data-cert-input]').fill('Ada Lovelace');
    await expect(page.locator('[data-cert-download="png"]')).toBeDisabled();
    await expect(page.locator('[data-cert-download="pdf"]')).toBeDisabled();
    const links = page.locator('[data-req-remaining] a[data-req-link]');
    expect(await links.count()).toBeGreaterThan(10);
    const href = await links.first().getAttribute('href');
    expect(href).toMatch(/^\/course\/[a-z-]+\/[a-z0-9-]+\/$/);
    expect((await page.request.get(href!)).status()).toBe(200);
    await expect(page.locator('[data-req-projects] a[data-req-link]')).toHaveCount(5);
  });

  test('unlocks when certificateRequirement is met in localStorage', async ({ page }) => {
    await openReady(page, '/certificate/');
    const data = JSON.parse((await page.locator('#aik-cert-data').textContent())!);
    const slugs: string[] = [...data.core.flatMap((t: any) => t.lessons.map((l: any) => l.slug)), ...data.projects[0].lessons.map((l: any) => l.slug)];
    await page.evaluate((s) => {
      const lessons = Object.fromEntries(s.map((slug: string) => [slug, { done: true, at: new Date().toISOString() }]));
      localStorage.setItem('aik-progress-v1', JSON.stringify({ version: 1, lessons, exercises: {}, name: 'Grace Hopper', lastVisited: null }));
    }, slugs);
    await openReady(page, '/certificate/');
    await expect(page.locator('[data-cert-page]')).toHaveAttribute('data-state', 'ready');
    await expect(page.locator('[data-cert-input]')).toHaveValue('Grace Hopper');
    await expect(page.locator('[data-cert-watermark]')).toBeHidden();
    await expect(page.locator('[data-cert-download="png"]')).toBeEnabled();
    await expect(page.locator('[data-cert-lessons]')).toHaveText(String(slugs.length));
  });

  test('live preview, saved name and long names that still fit', async ({ page }) => {
    await openReady(page, '/certificate/?demo=1');
    const input = page.locator('[data-cert-input]');
    await input.fill('Marie Curie');
    await expect(page.locator('[data-cert-name]')).toHaveText('Marie Curie');
    await expect(page.locator('[data-cert-id]')).toHaveText(/^AK-[0-9A-F]{4}-[0-9A-F]{4}$/);
    // The name is saved in the progress store.
    await expect.poll(() => page.evaluate(() => JSON.parse(localStorage.getItem('aik-progress-v1') || '{}').name)).toBe('Marie Curie');

    const box = async () =>
      page.evaluate(() => {
        const t = document.querySelector('[data-cert-name]') as SVGTextElement;
        const b = t.getBBox();
        return { x: b.x, right: b.x + b.width, top: b.y, bottom: b.y + b.height, lines: t.dataset.lines, size: Number(t.dataset.size) };
      });
    for (const name of ['Maximiliana Wilhelmina Zoë Montgomery-Smith', 'Bartholomew Alexander Christopherson-Vanderbilt', 'Muhammadabdulrahmanalexanderchristophersonov']) {
      await input.fill(name);
      // One or two tspans; compare without the line-break space.
      await expect.poll(() => page.locator('[data-cert-name]').evaluate((t) => (t.textContent || '').replace(/\s/g, ''))).toBe(name.replace(/\s/g, ''));
      const b = await box();
      expect(b.right, `${name} overflows`).toBeLessThanOrEqual(1560 + 1740 + 2);
      expect(b.top, `${name} too high`).toBeGreaterThan(590);
      expect(b.bottom, `${name} too low`).toBeLessThan(962);
      expect(b.size).toBeGreaterThan(60);
    }
    // 48-character cap
    await input.fill('A'.repeat(60));
    await expect(input).toHaveValue('A'.repeat(48));
  });

  test('?demo=1 downloads a high-resolution PNG and an A4 PDF', async ({ page }) => {
    test.setTimeout(120_000);
    await openReady(page, '/certificate/?demo=1');
    await expect(page.locator('[data-cert-page]')).toHaveAttribute('data-state', 'demo');
    await expect(page.locator('[data-cert-watermark]')).toBeHidden();
    await page.locator('[data-cert-input]').fill('Alexandra Montgomery-Castellanos');
    const png = page.locator('[data-cert-download="png"]');
    await expect(png).toBeEnabled();

    const [dlPng] = await Promise.all([page.waitForEvent('download'), png.click()]);
    expect(dlPng.suggestedFilename()).toBe('ai-knowledge-certificate-alexandra-montgomery-castellanos.png');
    const pngPath = test.info().outputPath('certificate.png');
    await dlPng.saveAs(pngPath);
    const info = pngSize(pngPath);
    expect(info.width).toBe(3508);
    expect(info.height).toBe(2480);
    expect(info.bytes).toBeGreaterThan(300_000);
    fs.mkdirSync(SAMPLE_DIR, { recursive: true });
    fs.copyFileSync(pngPath, path.join(SAMPLE_DIR, 'certificate-sample.png'));

    const pdf = page.locator('[data-cert-download="pdf"]');
    await expect(pdf).toBeEnabled();
    const [dlPdf] = await Promise.all([page.waitForEvent('download'), pdf.click()]);
    expect(dlPdf.suggestedFilename()).toBe('ai-knowledge-certificate-alexandra-montgomery-castellanos.pdf');
    const pdfPath = test.info().outputPath('certificate.pdf');
    await dlPdf.saveAs(pdfPath);
    const bytes = fs.readFileSync(pdfPath);
    expect(bytes.subarray(0, 5).toString('latin1')).toBe('%PDF-');
    expect(bytes.length).toBeGreaterThan(200_000);
    // One A4 landscape page: MediaBox 841.89 x 595.28 pt.
    expect(bytes.toString('latin1')).toMatch(/\/MediaBox \[0 0 841\.8[89]\d* 595\.2[78]\d*\]/);
    await expect(page.locator('[data-cert-status]')).toContainText('Saved');
  });
});
