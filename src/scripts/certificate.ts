/**
 * Certificate page logic: live preview, name auto-fit, unlock rule, PNG/PDF export.
 *
 * Export path: the live <svg> is cloned, the certificate fonts are inlined into it as
 * data: URLs (@font-face), the clone is drawn into a 3508 x 2480 canvas (A4 landscape at
 * 300 dpi) and saved with canvas.toBlob. The PDF embeds that render on one A4 landscape
 * page with jsPDF. All files are served by the static site, so it works offline.
 *
 * Test hook: ?demo=1 bypasses the lock (for automated tests only; the banner says so).
 */
import { getState, setName, subscribe, type ProgressState } from '../lib/progress';
import { certStatus, certificateId, formatDate, nameSlug, normalizeName, todayISO, NAME_MAX, type CertData } from '../lib/certificate';

import cg600Url from '@fontsource/cormorant-garamond/files/cormorant-garamond-latin-600-normal.woff2?url';
import cg500iUrl from '@fontsource/cormorant-garamond/files/cormorant-garamond-latin-500-italic.woff2?url';
import cg600iUrl from '@fontsource/cormorant-garamond/files/cormorant-garamond-latin-600-italic.woff2?url';
import cg600iExtUrl from '@fontsource/cormorant-garamond/files/cormorant-garamond-latin-ext-600-italic.woff2?url';
import frauncesUrl from '@fontsource-variable/fraunces/files/fraunces-latin-wght-normal.woff2?url';
import interUrl from '@fontsource-variable/inter/files/inter-latin-wght-normal.woff2?url';
import pinyonUrl from '@fontsource/pinyon-script/files/pinyon-script-latin-400-normal.woff2?url';

const W = 3508;
const H = 2480;
const DATE_KEY = 'aik-cert-date';
const SVGNS = 'http://www.w3.org/2000/svg';

const LATIN = 'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD';
const LATIN_EXT = 'U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF';

interface FontSpec {
  family: string;
  style: 'normal' | 'italic';
  weight: string;
  url: string;
  range?: string;
}
const FONTS: FontSpec[] = [
  { family: 'AIK Cormorant', style: 'normal', weight: '600', url: cg600Url, range: LATIN },
  { family: 'AIK Cormorant', style: 'italic', weight: '500', url: cg500iUrl, range: LATIN },
  { family: 'AIK Cormorant', style: 'italic', weight: '600', url: cg600iUrl, range: LATIN },
  { family: 'AIK Cormorant', style: 'italic', weight: '600', url: cg600iExtUrl, range: LATIN_EXT },
  { family: 'AIK Fraunces', style: 'normal', weight: '100 900', url: frauncesUrl },
  { family: 'AIK Inter', style: 'normal', weight: '100 900', url: interUrl },
  { family: 'AIK Pinyon', style: 'normal', weight: '400', url: pinyonUrl },
];

const page = document.querySelector<HTMLElement>('[data-cert-page]');
const svg = document.querySelector<SVGSVGElement>('[data-cert-svg]');
const dataEl = document.getElementById('aik-cert-data');

if (page && svg && dataEl) init(page, svg, JSON.parse(dataEl.textContent || '{}') as CertData);

function init(page: HTMLElement, svg: SVGSVGElement, data: CertData) {
  const demo = new URLSearchParams(location.search).get('demo') === '1';
  const q = <T extends Element = HTMLElement>(sel: string, root: ParentNode = document) => root.querySelector<T>(sel);
  const nameInput = q<HTMLInputElement>('[data-cert-input]')!;
  const dateInput = q<HTMLInputElement>('[data-cert-date-input]')!;
  const count = q('[data-cert-count]');
  const statusOut = q('[data-cert-status]');
  const btnPng = q<HTMLButtonElement>('[data-cert-download="png"]')!;
  const btnPdf = q<HTMLButtonElement>('[data-cert-download="pdf"]')!;
  const nameText = q<SVGTextElement>('[data-cert-name]', svg)!;
  const measure = q<SVGTextElement>('[data-cert-measure]', svg)!;
  const watermark = q<SVGGElement>('[data-cert-watermark]', svg)!;
  const setText = (sel: string, text: string, root: ParentNode = svg) => root.querySelectorAll(sel).forEach((n) => (n.textContent = text));

  let unlocked = false;
  let busy = false;
  let lastStatus = certStatus(data, () => false);

  // ---------- fonts (registered once, reused for the export) ----------
  const fontBytes = new Map<string, string>(); // url -> base64
  const fontsReady = loadFonts();

  async function loadFonts() {
    await Promise.all(
      FONTS.map(async (spec) => {
        try {
          const res = await fetch(spec.url);
          if (!res.ok) throw new Error(String(res.status));
          const buf = await res.arrayBuffer();
          fontBytes.set(spec.url, toBase64(buf));
          const face = new FontFace(spec.family, buf, { style: spec.style, weight: spec.weight, ...(spec.range ? { unicodeRange: spec.range } : {}) });
          await face.load();
          document.fonts.add(face);
        } catch (err) {
          console.warn('[certificate] font not loaded, falling back to system serif', spec.url, err);
        }
      }),
    );
    try {
      await document.fonts.ready;
    } catch {}
    page.dataset.fonts = 'ready';
  }

  function fontCSS(): string {
    return FONTS.filter((s) => fontBytes.has(s.url))
      .map(
        (s) =>
          `@font-face{font-family:'${s.family}';font-style:${s.style};font-weight:${s.weight};font-display:block;${s.range ? `unicode-range:${s.range};` : ''}src:url(data:font/woff2;base64,${fontBytes.get(s.url)}) format('woff2');}`,
      )
      .join('\n');
  }

  // ---------- name auto-fit ----------
  const MAX_W = Number(nameText.dataset.maxWidth || 1740);
  const CY = Number(nameText.dataset.centerY || 772);
  const X0 = Number(nameText.getAttribute('x') || 1560);
  const ONE_LINE_MAX = 228;
  const ONE_LINE_PREFERRED_MIN = 150;
  const TWO_LINE_MAX = 140;

  function textLen(s: string): number {
    measure.textContent = s; // measured at font-size 100
    const len = measure.getComputedTextLength();
    return len > 0 ? len : s.length * 42;
  }

  function fitName(name: string) {
    const shown = name || 'Your Name';
    let lines = [shown];
    let size = Math.min(ONE_LINE_MAX, (MAX_W * 100) / textLen(shown));
    if (size < ONE_LINE_PREFERRED_MIN && shown.includes(' ')) {
      const words = shown.split(' ');
      let best: { a: string; b: string; m: number } | null = null;
      for (let i = 1; i < words.length; i++) {
        const a = words.slice(0, i).join(' ');
        const b = words.slice(i).join(' ');
        const m = Math.max(textLen(a), textLen(b));
        if (!best || m < best.m) best = { a, b, m };
      }
      if (best) {
        const s2 = Math.min(TWO_LINE_MAX, (MAX_W * 100) / best.m);
        if (s2 > size) {
          lines = [best.a, best.b];
          size = s2;
        }
      }
    }
    size = Math.floor(size * 10) / 10;
    while (nameText.firstChild) nameText.removeChild(nameText.firstChild);
    nameText.setAttribute('font-size', String(size));
    nameText.setAttribute('opacity', name ? '1' : '0.42');
    const centres = lines.length === 1 ? [CY] : [CY - 0.56 * size, CY + 0.56 * size];
    lines.forEach((line, i) => {
      const t = document.createElementNS(SVGNS, 'tspan');
      t.setAttribute('x', String(X0));
      t.setAttribute('y', (centres[i] + 0.3 * size).toFixed(1));
      t.textContent = line;
      nameText.appendChild(t);
    });
    nameText.dataset.lines = String(lines.length);
    nameText.dataset.size = String(size);
  }

  // ---------- state → preview ----------
  const currentName = () => normalizeName(nameInput.value);
  const currentDate = () => (/^\d{4}-\d{2}-\d{2}$/.test(dateInput.value) ? dateInput.value : todayISO());

  function shownStats() {
    const s = lastStatus;
    let lessons = s.lessonsDone;
    let minutes = s.minutesDone;
    let projects = s.projects.filter((p) => p.complete).map((p) => p.track);
    if (demo && !s.unlocked) {
      // Demo numbers: what a learner who just met the requirement would see.
      const chess = data.projects.find((p) => p.id === 'project-chess') ?? data.projects[0];
      const req = [...data.core.flatMap((t) => t.lessons), ...(chess ? chess.lessons : [])];
      lessons = Math.max(lessons, req.length);
      minutes = Math.max(minutes, req.reduce((n, l) => n + l.minutes, 0));
      if (!projects.length && chess) projects = [chess];
    }
    return { lessons, minutes, projects };
  }

  function render() {
    const name = currentName();
    const iso = currentDate();
    const id = certificateId(name || 'Your Name', iso);
    fitName(name);
    setText('[data-cert-date]', formatDate(iso));
    setText('[data-cert-id]', id);
    setText('[data-cert-id-out]', id, document);
    const st = shownStats();
    const hours = Math.max(st.minutes ? 1 : 0, Math.round(st.minutes / 60));
    setText('[data-cert-lessons]', String(st.lessons));
    setText('[data-cert-hours]', String(hours));
    setText('[data-cert-hours-label]', hours === 1 ? ' hour of study' : ' hours of study');
    const k = st.projects.length;
    setText('[data-cert-project-label]', k <= 1 ? 'Project: ' : k === 2 ? 'Projects: ' : 'Projects built: ');
    setText('[data-cert-project]', k === 0 ? '—' : k === 1 ? st.projects[0].short : k === 2 ? `${st.projects[0].short} & ${st.projects[1].short}` : String(k));
    setText('[data-cert-desc]', `Certificate of completion awarded to ${name || 'Your Name'} on ${formatDate(iso)} for the course Deep Learning: From Foundations to Neural Chess Engines. ID ${id}.`);
    if (count) count.textContent = String(nameInput.value.length);
    const canDownload = (unlocked || demo) && !!name && !busy;
    btnPng.disabled = !canDownload;
    btnPdf.disabled = !canDownload;
    watermark.style.display = unlocked || demo ? 'none' : '';
  }

  function renderRequirements(state: ProgressState) {
    const isDone = (slug: string) => !!state.lessons[slug]?.done;
    lastStatus = certStatus(data, isDone);
    unlocked = lastStatus.unlocked;
    page.dataset.state = unlocked ? 'ready' : demo ? 'demo' : 'locked';
    page.dataset.unlocked = String(unlocked);
    setText('[data-cert-pct]', `${lastStatus.pct}%`, document);

    let openedOne = false;
    for (const t of lastStatus.core) {
      const li = document.querySelector<HTMLElement>(`[data-req-track="${t.track.id}"]`);
      if (!li) continue;
      li.dataset.complete = String(t.complete);
      setText('[data-req-count]', `${t.done} / ${t.total}`, li);
      const bar = li.querySelector<HTMLElement>('[data-req-bar]');
      if (bar) bar.style.width = `${t.total ? (t.done / t.total) * 100 : 0}%`;
      const ul = li.querySelector('[data-req-remaining]')!;
      ul.replaceChildren(
        ...(t.remaining.length
          ? t.remaining.map((l) => {
              const item = document.createElement('li');
              const a = document.createElement('a');
              a.href = l.url;
              a.textContent = l.title;
              a.dataset.reqLink = '';
              const m = document.createElement('span');
              m.className = 'req__pcount';
              m.textContent = `${l.minutes} min`;
              item.append(a, m);
              return item;
            })
          : [Object.assign(document.createElement('li'), { className: 'req__done-note', textContent: 'All lessons complete.' })]),
      );
      const det = li.querySelector('details')!;
      if (!t.complete && !openedOne) {
        det.open = true;
        openedOne = true;
      }
    }
    const pj = document.querySelector<HTMLElement>('[data-req-projects]');
    if (pj) {
      const ok = lastStatus.projectsComplete >= data.minProjects;
      pj.dataset.complete = String(ok);
      setText('[data-req-count]', `${Math.min(lastStatus.projectsComplete, data.minProjects)} / ${data.minProjects}`, pj);
      const best = lastStatus.projects[0];
      const bar = pj.querySelector<HTMLElement>('[data-req-bar]');
      if (bar) bar.style.width = ok ? '100%' : `${best && best.total ? (best.done / best.total) * 100 : 0}%`;
      for (const p of lastStatus.projects) {
        const row = pj.querySelector<HTMLElement>(`[data-req-project="${p.track.id}"]`);
        if (!row) continue;
        row.dataset.complete = String(p.complete);
        setText('[data-req-pcount]', `${p.done} / ${p.total}`, row);
        const a = row.querySelector<HTMLAnchorElement>('a');
        if (a) a.href = p.remaining[0]?.url ?? p.track.url;
      }
      if (!ok && !openedOne) pj.querySelector('details')!.open = true;
    }
    render();
  }

  // ---------- inputs ----------
  nameInput.maxLength = NAME_MAX;
  nameInput.value = normalizeName(getState().name || '');
  let savedDate = '';
  try {
    savedDate = localStorage.getItem(DATE_KEY) || '';
  } catch {}
  dateInput.value = /^\d{4}-\d{2}-\d{2}$/.test(savedDate) ? savedDate : todayISO();

  let saveTimer = 0;
  nameInput.addEventListener('input', () => {
    render();
    window.clearTimeout(saveTimer);
    saveTimer = window.setTimeout(() => setName(currentName()), 250);
  });
  nameInput.addEventListener('change', () => setName(currentName()));
  dateInput.addEventListener('change', () => {
    try {
      if (dateInput.value) localStorage.setItem(DATE_KEY, dateInput.value);
      else localStorage.removeItem(DATE_KEY);
    } catch {}
    render();
  });
  document.querySelector('[data-cert-clear]')?.addEventListener('click', () => {
    nameInput.value = '';
    setName('');
    render();
    nameInput.focus();
  });

  subscribe((state) => {
    if (document.activeElement !== nameInput && normalizeName(state.name || '') !== currentName()) nameInput.value = normalizeName(state.name || '');
    renderRequirements(state);
  });

  fontsReady.then(() => {
    render();
    page.dataset.ready = 'true';
  });

  // ---------- export ----------
  async function svgMarkup(): Promise<string> {
    await fontsReady;
    render(); // re-fit with final font metrics
    const clone = svg.cloneNode(true) as SVGSVGElement;
    clone.querySelector('[data-cert-measure]')?.remove();
    clone.querySelector('[data-cert-watermark]')?.remove();
    clone.removeAttribute('class');
    clone.setAttribute('width', String(W));
    clone.setAttribute('height', String(H));
    const style = document.createElementNS(SVGNS, 'style');
    style.textContent = fontCSS();
    const defs = clone.querySelector('defs') ?? clone.insertBefore(document.createElementNS(SVGNS, 'defs'), clone.firstChild);
    defs.insertBefore(style, defs.firstChild);
    return new XMLSerializer().serializeToString(clone);
  }

  async function loadImage(url: string): Promise<HTMLImageElement> {
    const img = new Image();
    img.width = W;
    img.height = H;
    await new Promise<void>((resolve, reject) => {
      img.onload = () => resolve();
      img.onerror = () => reject(new Error('The certificate image could not be rendered.'));
      img.src = url;
    });
    try {
      await img.decode();
    } catch {}
    return img;
  }

  async function renderCanvas(): Promise<HTMLCanvasElement> {
    const markup = await svgMarkup();
    const url = URL.createObjectURL(new Blob([markup], { type: 'image/svg+xml;charset=utf-8' }));
    try {
      const img = await loadImage(url);
      // Give the SVG image's inlined fonts one more frame before rasterising.
      await new Promise((r) => requestAnimationFrame(() => setTimeout(r, 60)));
      const canvas = document.createElement('canvas');
      canvas.width = W;
      canvas.height = H;
      const ctx = canvas.getContext('2d')!;
      ctx.fillStyle = '#F6EFD9';
      ctx.fillRect(0, 0, W, H);
      ctx.drawImage(img, 0, 0, W, H);
      return canvas;
    } finally {
      URL.revokeObjectURL(url);
    }
  }

  const toBlob = (canvas: HTMLCanvasElement, type: string, quality?: number) =>
    new Promise<Blob>((resolve, reject) => canvas.toBlob((b) => (b ? resolve(b) : reject(new Error('Canvas export failed.'))), type, quality));

  function save(blob: Blob, filename: string) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.rel = 'noopener';
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 10_000);
  }

  async function download(kind: 'png' | 'pdf') {
    const name = currentName();
    if (!name || !(unlocked || demo) || busy) return;
    busy = true;
    render();
    if (statusOut) statusOut.textContent = `Rendering your ${kind.toUpperCase()}…`;
    try {
      setName(name);
      try {
        localStorage.setItem(DATE_KEY, currentDate());
      } catch {}
      const canvas = await renderCanvas();
      const base = `ai-knowledge-certificate-${nameSlug(name)}`;
      if (kind === 'png') {
        save(await toBlob(canvas, 'image/png'), `${base}.png`);
      } else {
        const { jsPDF } = await import('jspdf');
        const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4', compress: true });
        const id = certificateId(name, currentDate());
        doc.setProperties({
          title: `AI Knowledge certificate of completion: ${name}`,
          subject: `Deep Learning: From Foundations to Neural Chess Engines. Certificate ID ${id}`,
          author: 'AI Knowledge',
          creator: 'AI Knowledge certificate generator (in-browser)',
          keywords: 'deep learning, certificate of completion, AI Knowledge',
        });
        const jpeg = new Uint8Array(await (await toBlob(canvas, 'image/jpeg', 0.95)).arrayBuffer());
        doc.addImage(jpeg, 'JPEG', 0, 0, 297, 210, undefined, 'NONE');
        save(doc.output('blob'), `${base}.pdf`);
      }
      if (statusOut) statusOut.textContent = `Saved ${base}.${kind}. Generated in your browser; nothing was uploaded.`;
    } catch (err) {
      console.error('[certificate] export failed', err);
      if (statusOut) statusOut.textContent = `Sorry, the ${kind.toUpperCase()} could not be generated: ${(err as Error).message}`;
    } finally {
      busy = false;
      render();
    }
  }

  btnPng.addEventListener('click', () => download('png'));
  btnPdf.addEventListener('click', () => download('pdf'));
}

function toBase64(buf: ArrayBuffer): string {
  const bytes = new Uint8Array(buf);
  let bin = '';
  const CHUNK = 0x8000;
  for (let i = 0; i < bytes.length; i += CHUNK) bin += String.fromCharCode(...bytes.subarray(i, i + CHUNK));
  return btoa(bin);
}
