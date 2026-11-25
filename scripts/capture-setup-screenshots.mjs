#!/usr/bin/env node
/**
 * Captures the annotated screenshots used by the Setup track.
 *
 *   node scripts/capture-setup-screenshots.mjs            # all shots
 *   node scripts/capture-setup-screenshots.mjs vscode     # only shots whose file name contains "vscode"
 *
 * How it works: headless Chromium (Playwright) opens each official page at 1440x900 in light mode,
 * dismisses cookie banners, performs any clicks the shot needs (for example the PyTorch selector tiles),
 * scrolls the element to click into view, injects an accent-coloured outline plus a numbered badge on
 * that element, and screenshots the viewport. Images are re-encoded with sharp (palette PNG) to stay
 * well under 400 KB, and a manifest (public/screenshots/setup/manifest.json) records the URL, the
 * capture date and the position of every badge (in % of the image) so lessons can be checked against it.
 *
 * If an official page changes its layout, a locator below will fail loudly: fix the locator, rerun,
 * and update the "taken" date in the lessons (src/content/lessons/setup/*.mdx).
 */
import { chromium } from 'playwright';
import sharp from 'sharp';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const OUT = path.join(ROOT, 'public', 'screenshots', 'setup');
const W = 1440, H = 900;
const ACCENT = '#3340C9';
const MAX_BYTES = 400 * 1024;
const today = new Date().toISOString().slice(0, 10);

/** Click whichever cookie/consent button is visible (prefer "reject"). */
async function dismissBanners(page) {
  // Consent managers that live in a closed shadow root (e.g. Transcend on pytorch.org) cannot be clicked;
  // hide their containers instead. This changes only our screenshot, not any setting on the site.
  await page.addStyleTag({ content: '#transcend-consent-manager,#onetrust-consent-sdk,#CybotCookiebotDialog{display:none!important}' }).catch(() => {});
  const labels = [/^\s*reject all\s*$/i, /^\s*reject\s*$/i, /^\s*decline\s*$/i, /necessary cookies only/i, /^\s*accept all\s*$/i, /^\s*accept\s*$/i, /^\s*got it\s*$/i];
  for (const frame of page.frames()) {
    for (const re of labels) {
      const btn = frame.locator('button, a, [role=button]').filter({ hasText: re }).first();
      try {
        if (await btn.isVisible({ timeout: 300 })) { await btn.click({ timeout: 2000 }); await page.waitForTimeout(500); return; }
      } catch { /* not present */ }
    }
  }
  // Fallback: banners built from plain divs or inside shadow roots (getByText pierces open shadow DOM).
  for (const t of ['Reject all', 'Decline', 'Accept all']) {
    const el = page.getByText(t, { exact: true }).first();
    try { if (await el.isVisible({ timeout: 300 })) { await el.click({ timeout: 2000 }); await page.waitForTimeout(500); return; } } catch { /* next */ }
  }
}

/**
 * Each shot: url, file, optional prepare(page), and marks: [{ locate(page) -> Locator, label }].
 * The first mark is scrolled to sit about 35% down the viewport. `scrollTo` overrides that anchor.
 */
const SHOTS = [
  {
    file: 'python-downloads-install-manager.png', id: 'SS-W02a',
    url: 'https://www.python.org/downloads/',
    marks: [{ locate: (p) => p.locator('a.button', { hasText: 'Download Python install manager' }).first(), label: 'Download Python install manager' }],
  },
  {
    file: 'python-windows-page.png', id: 'SS-W02',
    url: 'https://www.python.org/downloads/windows/',
    marks: [{ locate: (p) => p.getByRole('link', { name: /Latest Python install manager/ }).first(), label: 'Latest Python install manager - Python install manager 26.4' }],
  },
  {
    file: 'python-pymanager-msix.png', id: 'SS-W03',
    url: 'https://www.python.org/downloads/release/pymanager-264/',
    marks: [{ locate: (p) => p.locator('a.button', { hasText: 'Download Installer (MSIX)' }).first(), label: 'Download Installer (MSIX)' }],
  },
  {
    file: 'python-windows-legacy-installer.png', id: 'SS-W05a',
    url: 'https://www.python.org/downloads/windows/',
    marks: [
      { locate: (p) => p.getByRole('link', { name: 'Python 3.14.10 - Oct. 25, 2026' }).first(), label: 'Python 3.14.10 section' },
      { locate: (p) => p.locator('a[href$="python-3.14.10-amd64.exe"]').first(), label: 'Windows installer (64-bit)' },
    ],
  },
  {
    file: 'python-macos-installer.png', id: 'SS-M04',
    url: 'https://www.python.org/downloads/macos/',
    marks: [
      { locate: (p) => p.getByRole('link', { name: 'Python 3.14.10 - Oct. 25, 2026' }).first(), label: 'Python 3.14.10' },
      { locate: (p) => p.locator('a[href$="python-3.14.10-macos11.pkg"]').first(), label: 'macOS installer' },
    ],
  },
  {
    file: 'homebrew-install-command.png', id: 'SS-M05',
    url: 'https://brew.sh/',
    marks: [{ locate: (p) => p.locator('#selectable, .command, figure.highlight, pre').filter({ hasText: 'install.sh' }).first(), label: 'Install command' }],
  },
  {
    file: 'vscode-download-windows.png', id: 'SS-W07',
    url: 'https://code.visualstudio.com/download',
    marks: [{ locate: (p) => p.locator('#download-alt-win'), label: 'Download for Windows x64 · User Installer' }],
  },
  {
    file: 'vscode-download-mac.png', id: 'SS-M06',
    url: 'https://code.visualstudio.com/download',
    marks: [{ locate: (p) => p.locator('#download-alt-main-osx'), label: 'Download for macOS Universal' }],
  },
  {
    file: 'vscode-download-linux.png', id: 'SS-L02',
    url: 'https://code.visualstudio.com/download',
    marks: [
      { locate: (p) => p.locator('#download-alt-main-linux64_deb'), label: '.deb (Debian, Ubuntu)' },
      { locate: (p) => p.locator('a.dlink', { hasText: /^\.rpm$/ }).first(), label: '.rpm (Fedora, RHEL)' },
    ],
  },
  {
    file: 'marketplace-python-extension.png', id: 'SS-W09',
    url: 'https://marketplace.visualstudio.com/items?itemName=ms-python.python',
    marks: [
      { locate: (p) => p.locator('.ux-item-publisher, [data-automation-id="publisher"], #publisher').first(), label: 'Publisher: Microsoft' },
      { locate: (p) => p.getByRole('button', { name: 'Install' }).first(), label: 'Install' },
    ],
    scrollTo: 'top',
  },
  {
    file: 'marketplace-jupyter-extension.png', id: 'SS-W10',
    url: 'https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter',
    marks: [
      { locate: (p) => p.locator('.ux-item-publisher, [data-automation-id="publisher"], #publisher').first(), label: 'Publisher: Microsoft' },
      { locate: (p) => p.getByRole('button', { name: 'Install' }).first(), label: 'Install' },
    ],
    scrollTo: 'top',
  },
  ...[
    { file: 'pytorch-selector-windows-cpu.png', id: 'SS-W15', os: '#windows', acc: '#accnone', accLabel: 'CPU' },
    { file: 'pytorch-selector-windows-cuda.png', id: 'SS-W16', os: '#windows', acc: '[id="cuda.x"]', accLabel: 'CUDA 13.2' },
    { file: 'pytorch-selector-mac.png', id: 'SS-M07', os: '#macos', acc: '#accnone', accLabel: 'Default' },
    { file: 'pytorch-selector-linux-cpu.png', id: 'SS-L03', os: '#linux', acc: '#accnone', accLabel: 'CPU' },
  ].map((s) => ({
    file: s.file, id: s.id,
    url: 'https://pytorch.org/get-started/locally/',
    prepare: async (p) => {
      for (const sel of ['#stable', s.os, '#pip', '#python', s.acc]) {
        const el = p.locator(sel).first();
        if (await el.isVisible().catch(() => false)) { await el.click(); await p.waitForTimeout(250); }
      }
    },
    marks: [
      { locate: (p) => p.locator(s.os).first(), label: 'Your OS' },
      { locate: (p) => p.locator('#pip').first(), label: 'Package: Pip' },
      { locate: (p) => p.locator(s.acc).first(), label: `Compute Platform: ${s.accLabel}` },
      { locate: (p) => p.locator('#command').first(), label: 'Run this Command' },
    ],
    anchor: 0.22,
  })),
  {
    file: 'colab-new-notebook.png', id: 'SS-C01',
    url: 'https://colab.research.google.com/',
    marks: [{ locate: (p) => p.locator('text=New notebook').first(), label: 'New notebook' }],
    scrollTo: 'top',
  },
  {
    file: 'git-for-windows-download.png', id: 'SS-W19',
    url: 'https://git-scm.com/install/windows',
    marks: [{ locate: (p) => p.getByRole('link', { name: /Click here to download|64-bit Git for Windows Setup|Git for Windows\/x64 Setup/i }).first(), label: 'Download Git for Windows (x64)' }],
  },
  {
    file: 'github-desktop-download.png', id: 'SS-W19b',
    url: 'https://desktop.github.com/download/',
    marks: [{ locate: (p) => p.getByRole('link', { name: /Download for Windows/i }).first(), label: 'Download for Windows' }],
    scrollTo: 'top',
  },
];

async function annotate(page, boxes) {
  await page.evaluate(({ boxes, ACCENT }) => {
    document.querySelectorAll('.aik-mark').forEach((n) => n.remove());
    boxes.forEach((b, i) => {
      const pad = 6;
      const ring = document.createElement('div');
      ring.className = 'aik-mark';
      Object.assign(ring.style, {
        position: 'absolute', left: `${b.x + window.scrollX - pad}px`, top: `${b.y + window.scrollY - pad}px`,
        width: `${b.width + pad * 2}px`, height: `${b.height + pad * 2}px`, border: `4px solid ${ACCENT}`,
        borderRadius: '10px', boxShadow: '0 0 0 4px rgba(255,255,255,0.85), 0 0 0 9999px rgba(15,18,40,0.07)',
        zIndex: 2147483646, pointerEvents: 'none', boxSizing: 'border-box',
      });
      const badge = document.createElement('div');
      badge.className = 'aik-mark';
      badge.textContent = String(i + 1);
      // Badge sits outside the ring (left, vertically centred) so it never covers the label to click.
      const left = b.x + window.scrollX, top = b.y + window.scrollY;
      let bx = left - pad - 46, by = top + b.height / 2 - 18;
      if (bx < 4) { bx = Math.max(4, left - pad - 6); by = top - pad - 46; }
      if (by < window.scrollY + 4) { bx = left + b.width + pad + 10; by = top + b.height / 2 - 18; }
      Object.assign(badge.style, {
        position: 'absolute', left: `${bx}px`, top: `${by}px`, width: '36px', height: '36px', borderRadius: '50%',
        background: ACCENT, color: '#fff', font: '700 19px/36px system-ui, Segoe UI, Arial, sans-serif', textAlign: 'center',
        boxShadow: '0 0 0 3px #fff, 0 2px 8px rgba(0,0,0,0.35)', zIndex: 2147483647, pointerEvents: 'none',
      });
      // Only the first ring dims the page; later rings just outline.
      if (i > 0) ring.style.boxShadow = '0 0 0 4px rgba(255,255,255,0.85)';
      document.body.appendChild(ring);
      document.body.appendChild(badge);
    });
  }, { boxes, ACCENT });
}

const CROP_W = 1040;
/** 16:10 crop around the union of the marks, with room for the badges, clamped to the viewport. */
function cropAround(boxes) {
  const x0 = Math.min(...boxes.map((b) => b.x)) - 70, x1 = Math.max(...boxes.map((b) => b.x + b.width)) + 70;
  const y0 = Math.min(...boxes.map((b) => b.y)) - 60, y1 = Math.max(...boxes.map((b) => b.y + b.height)) + 60;
  const width = Math.min(W, Math.max(CROP_W, x1 - x0, Math.ceil((y1 - y0) * 1.6)));
  const height = Math.min(H, Math.round(width / 1.6));
  const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
  const x = clamp(Math.round((x0 + x1) / 2 - width / 2), 0, W - width);
  const y = clamp(Math.round((y0 + y1) / 2 - height / 2), 0, H - height);
  return { x, y, width, height };
}

async function capture(browser, shot) {
  const page = await browser.newPage({ viewport: { width: W, height: H }, colorScheme: 'light', deviceScaleFactor: 1, locale: 'en-US' });
  try {
    await page.goto(shot.url, { waitUntil: 'networkidle', timeout: 60000 }).catch(() => page.waitForLoadState('load'));
    await page.waitForTimeout(1200);
    await dismissBanners(page);
    if (shot.prepare) await shot.prepare(page);
    const locators = shot.marks.map((m) => m.locate(page));
    for (const [i, l] of locators.entries()) {
      await l.waitFor({ state: 'visible', timeout: 15000 }).catch(() => { throw new Error(`${shot.file}: mark ${i + 1} (${shot.marks[i].label}) not found`); });
    }
    // Scroll: put the first mark ~35% down (or the anchor fraction), or stay at the top.
    if (shot.scrollTo === 'top') await page.evaluate(() => window.scrollTo(0, 0));
    else {
      const first = await locators[0].evaluate((el) => el.getBoundingClientRect().top + window.scrollY);
      await page.evaluate((y) => window.scrollTo(0, y), Math.max(0, first - H * (shot.anchor ?? 0.35)));
    }
    await page.waitForTimeout(500);
    const boxes = [];
    for (const l of locators) {
      const b = await l.evaluate((el) => { const r = el.getBoundingClientRect(); return { x: r.left, y: r.top, width: r.width, height: r.height }; });
      if (b.y < 0 || b.y + b.height > H) throw new Error(`${shot.file}: a mark is outside the viewport (y=${Math.round(b.y)})`);
      boxes.push(b);
    }
    await annotate(page, boxes);
    // Crop to a 16:10 region around the marks (at least CROP_W wide) so the text stays legible when the
    // image is shown in the ~730 px article column. shot.full keeps the whole viewport.
    const clip = shot.full ? { x: 0, y: 0, width: W, height: H } : cropAround(boxes);
    const raw = await page.screenshot({ type: 'png', clip });
    let png = await sharp(raw).png({ palette: true, quality: 90, effort: 10, compressionLevel: 9 }).toBuffer();
    if (png.length > MAX_BYTES) png = await sharp(raw).png({ palette: true, colours: 128, quality: 75, effort: 10 }).toBuffer();
    if (png.length > MAX_BYTES) throw new Error(`${shot.file}: ${png.length} bytes after compression`);
    fs.writeFileSync(path.join(OUT, shot.file), png);
    return {
      file: shot.file, id: shot.id, url: shot.url, taken: today, bytes: png.length, clip,
      marks: shot.marks.map((m, i) => ({
        n: i + 1, label: m.label,
        x: +(((boxes[i].x + boxes[i].width / 2 - clip.x) / clip.width) * 100).toFixed(1),
        y: +(((boxes[i].y + boxes[i].height / 2 - clip.y) / clip.height) * 100).toFixed(1),
      })),
    };
  } finally {
    await page.close();
  }
}

fs.mkdirSync(OUT, { recursive: true });
const filter = process.argv[2];
const manifestPath = path.join(OUT, 'manifest.json');
const manifest = fs.existsSync(manifestPath) ? JSON.parse(fs.readFileSync(manifestPath, 'utf8')) : { shots: {} };
const browser = await chromium.launch();
let failed = 0;
for (const shot of SHOTS.filter((s) => !filter || s.file.includes(filter))) {
  try {
    const r = await capture(browser, shot);
    manifest.shots[r.file] = r;
    console.log(`ok   ${r.file}  ${(r.bytes / 1024).toFixed(0)} KB  ${r.marks.map((m) => `${m.n}:${m.x},${m.y}`).join(' ')}`);
  } catch (e) {
    failed++;
    console.error(`FAIL ${shot.file}: ${e.message.split('\n')[0]}`);
  }
}
await browser.close();
manifest.viewport = `${W}x${H}`;
manifest.generator = 'scripts/capture-setup-screenshots.mjs';
fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2) + '\n');
process.exit(failed ? 1 : 0);
