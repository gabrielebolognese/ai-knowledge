#!/usr/bin/env node
/**
 * Link checker for the built site (dist/).
 *
 *   node scripts/check-links.mjs                 internal + external, writes research/link-report.md
 *   node scripts/check-links.mjs --internal-only internal links only (fast, offline)
 *   node scripts/check-links.mjs --dist other/   check another build folder
 *   node scripts/check-links.mjs --concurrency 6 --delay 300
 *
 * Internal: every href/src (and srcset entry) that points inside the site must resolve to a file in
 * dist/ (path, path.html or path/index.html). Fragments (#id) on internal pages must match an id
 * (or name) on the target page. Exit code 1 if any internal link is broken.
 *
 * External: each unique http(s) URL is requested with HEAD, falling back to GET, with retries,
 * a per-host polite delay and limited concurrency. 2xx/3xx = ok; 401/403/429/999 and Cloudflare-style
 * challenges = "unverified" (bot protection, not proof of a dead link); 404/410, DNS errors and
 * persistent 5xx/timeouts = broken. External failures are reported, not fatal, unless --strict-external.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const flag = (n) => args.includes(n);
const opt = (n, d) => { const i = args.indexOf(n); return i >= 0 && args[i + 1] ? args[i + 1] : d; };

const DIST = path.resolve(ROOT, opt('--dist', 'dist'));
const INTERNAL_ONLY = flag('--internal-only');
const STRICT_EXTERNAL = flag('--strict-external');
const CONCURRENCY = Number(opt('--concurrency', 8));
const HOST_DELAY_MS = Number(opt('--delay', 400));
const TIMEOUT_MS = Number(opt('--timeout', 20000));
const RETRIES = Number(opt('--retries', 2));
const REPORT = path.resolve(ROOT, opt('--report', 'research/link-report.md'));
const SITE_ORIGINS = ['https://gabrielebolognese.github.io']; // absolute links to our own site are treated as internal

if (!fs.existsSync(DIST)) {
  console.error(`✗ ${path.relative(ROOT, DIST)} not found. Run "npm run build" first.`);
  process.exit(2);
}

// ---------- collect pages ----------
function walk(dir) {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) out.push(...walk(p));
    else out.push(p);
  }
  return out;
}
const allFiles = walk(DIST);
const htmlFiles = allFiles.filter((f) => f.endsWith('.html'));
const isPagefind = (f) => f.split(path.sep).includes('pagefind');

const decodeEntities = (s) =>
  s.replace(/&amp;/g, '&').replace(/&#38;/g, '&').replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>');

const idCache = new Map();
function idsOf(file) {
  if (!idCache.has(file)) {
    const html = fs.readFileSync(file, 'utf8');
    const ids = new Set();
    for (const m of html.matchAll(/\s(?:id|name)=["']([^"']+)["']/g)) ids.add(decodeEntities(m[1]));
    idCache.set(file, ids);
  }
  return idCache.get(file);
}

function resolveTarget(urlPath) {
  let p = decodeURIComponent(urlPath);
  const base = path.join(DIST, p);
  const candidates = p.endsWith('/') ? [path.join(base, 'index.html')] : [base, base + '.html', path.join(base, 'index.html')];
  for (const c of candidates) if (fs.existsSync(c) && fs.statSync(c).isFile()) return c;
  return null;
}

const internalBroken = [];
const external = new Map(); // url -> Set(pages)
let internalCount = 0;

for (const file of htmlFiles) {
  if (isPagefind(file)) continue;
  // Inline <script> bodies hold template strings like href="${url}", not links.
  const html = fs.readFileSync(file, 'utf8').replace(/(<script\b[^>]*>)[\s\S]*?<\/script>/gi, '$1</script>');
  const pageRel = '/' + path.relative(DIST, file).split(path.sep).join('/');
  const pageUrl = new URL(pageRel.replace(/index\.html$/, ''), 'https://site.invalid');
  const refs = [];
  for (const m of html.matchAll(/\s(href|src|poster|action)=["']([^"']*)["']/g)) refs.push(decodeEntities(m[2]));
  for (const m of html.matchAll(/\ssrcset=["']([^"']*)["']/g)) {
    for (const part of decodeEntities(m[1]).split(',')) { const u = part.trim().split(/\s+/)[0]; if (u) refs.push(u); }
  }
  for (let ref of refs) {
    ref = ref.trim();
    if (!ref || ref.startsWith('data:') || ref.startsWith('mailto:') || ref.startsWith('tel:') || ref.startsWith('javascript:') || ref.startsWith('blob:')) continue;
    if (/^https?:\/\//i.test(ref)) {
      const own = SITE_ORIGINS.find((o) => ref.startsWith(o));
      if (!own) {
        const clean = ref.split('#')[0];
        if (!external.has(clean)) external.set(clean, new Set());
        external.get(clean).add(pageRel);
        continue;
      }
      ref = ref.slice(own.length) || '/';
    }
    if (ref.startsWith('//')) continue;
    let u;
    try { u = new URL(ref, pageUrl); } catch { internalBroken.push({ page: pageRel, ref, why: 'unparseable URL' }); continue; }
    if (u.origin !== 'https://site.invalid') continue;
    internalCount++;
    const target = u.pathname === pageUrl.pathname && !ref.split('#')[0] ? file : resolveTarget(u.pathname);
    if (!target) { internalBroken.push({ page: pageRel, ref, why: 'no such file in dist/' }); continue; }
    const frag = u.hash ? decodeURIComponent(u.hash.slice(1)) : '';
    if (frag && target.endsWith('.html') && !idsOf(target).has(frag)) {
      internalBroken.push({ page: pageRel, ref, why: `missing #${frag} on target page` });
    }
  }
}

console.log(`Internal: ${internalCount} links on ${htmlFiles.filter((f) => !isPagefind(f)).length} pages, ${internalBroken.length} broken.`);
for (const b of internalBroken.slice(0, 200)) console.log(`  ✗ ${b.page} → ${b.ref} (${b.why})`);

if (INTERNAL_ONLY) process.exit(internalBroken.length ? 1 : 0);

// ---------- external ----------
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36 ai-knowledge-linkcheck';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const hostNext = new Map();
async function politeSlot(host) {
  for (;;) {
    const now = Date.now();
    const next = hostNext.get(host) ?? 0;
    if (now >= next) { hostNext.set(host, now + HOST_DELAY_MS); return; }
    await sleep(next - now);
  }
}

async function request(url, method) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  try {
    const res = await fetch(url, {
      method,
      redirect: 'follow',
      signal: ctrl.signal,
      headers: { 'user-agent': UA, accept: 'text/html,application/xhtml+xml,application/pdf,*/*;q=0.8', 'accept-language': 'en' },
    });
    const challenge = res.headers.get('cf-mitigated') === 'challenge';
    if (method === 'GET') await res.body?.cancel().catch(() => {});
    return { status: res.status, finalUrl: res.url, challenge };
  } catch (e) {
    return { error: e.name === 'AbortError' ? 'timeout' : (e.cause?.code || e.message) };
  } finally { clearTimeout(t); }
}

function classify(r) {
  if (r.error) return /ENOTFOUND|EAI_AGAIN|ERR_INVALID_URL/.test(r.error) ? 'broken' : 'error';
  if (r.challenge) return 'unverified';
  if (r.status >= 200 && r.status < 400) return 'ok';
  if ([401, 403, 429, 999, 418, 451].includes(r.status)) return 'unverified';
  if ([404, 410].includes(r.status)) return 'broken';
  return 'error'; // 5xx, 400, 405 ... retried below
}

async function check(url) {
  const host = new URL(url).host;
  let last;
  for (let attempt = 0; attempt <= RETRIES; attempt++) {
    if (attempt) await sleep(1500 * attempt);
    await politeSlot(host);
    let r = await request(url, 'HEAD');
    let c = classify(r);
    if (c !== 'ok') { await politeSlot(host); r = await request(url, 'GET'); c = classify(r); }
    last = { ...r, verdict: c };
    if (c === 'ok' || c === 'broken' || c === 'unverified') break;
  }
  if (last.verdict === 'error') last.verdict = last.status && last.status < 500 && ![400, 405].includes(last.status) ? 'broken' : 'error';
  return last;
}

const urls = [...external.keys()].sort();
console.log(`External: checking ${urls.length} unique URLs (concurrency ${CONCURRENCY}, ${HOST_DELAY_MS} ms per host)...`);
const results = new Map();
let idx = 0, done = 0;
await Promise.all(Array.from({ length: CONCURRENCY }, async () => {
  while (idx < urls.length) {
    const url = urls[idx++];
    results.set(url, await check(url));
    if (++done % 50 === 0) console.log(`  ${done}/${urls.length}`);
  }
}));

const by = (v) => urls.filter((u) => results.get(u).verdict === v);
const ok = by('ok'), unverified = by('unverified'), broken = by('broken'), errors = by('error');
const row = (u) => {
  const r = results.get(u);
  const pages = [...external.get(u)].slice(0, 3).join(', ') + (external.get(u).size > 3 ? ` (+${external.get(u).size - 3})` : '');
  return `| ${u.replace(/\|/g, '%7C')} | ${r.status ?? r.error} | ${pages} |`;
};
const table = (list) => list.length ? ['| URL | Result | Linked from |', '|---|---|---|', ...list.map(row)].join('\n') : '_None._';
const md = `# Link report

Generated by \`node scripts/check-links.mjs\` on ${new Date().toISOString().slice(0, 10)} against \`${path.relative(ROOT, DIST)}/\`.

## Summary

| Check | Count |
|---|---|
| Internal links checked | ${internalCount} |
| Internal links broken | ${internalBroken.length} |
| Unique external URLs | ${urls.length} |
| External OK (2xx/3xx) | ${ok.length} |
| External unverified (401/403/429/999 or bot challenge) | ${unverified.length} |
| External broken (404/410/DNS) | ${broken.length} |
| External errors (timeouts, 5xx after ${RETRIES} retries) | ${errors.length} |

"Unverified" means the server refused an automated client (bot protection, rate limit, login wall).
These links were opened by hand where it mattered; a refusal is not evidence that the page is gone.

## Internal broken links

${internalBroken.length ? ['| Page | Link | Why |', '|---|---|---|', ...internalBroken.map((b) => `| ${b.page} | ${b.ref} | ${b.why} |`)].join('\n') : '_None._'}

## External broken

${table(broken)}

## External errors

${table(errors)}

## External unverified

${table(unverified)}
`;
fs.mkdirSync(path.dirname(REPORT), { recursive: true });
fs.writeFileSync(REPORT, md);
console.log(`External: ${ok.length} ok, ${unverified.length} unverified, ${broken.length} broken, ${errors.length} errors.`);
for (const u of [...broken, ...errors]) console.log(`  ✗ ${u} (${results.get(u).status ?? results.get(u).error})`);
console.log(`Report: ${path.relative(ROOT, REPORT)}`);
process.exit(internalBroken.length || (STRICT_EXTERNAL && broken.length) ? 1 : 0);
