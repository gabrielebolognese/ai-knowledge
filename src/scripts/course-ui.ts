/**
 * Course map behaviour (dashboard, track pages, projects). Reads the course order that
 * CourseData.astro embeds as JSON and the progress store; never talks to a server.
 *
 *   [data-track-map]                 container of li[data-node] in course order: each node gets
 *                                     data-state = done | next | later (later = "locked-looking",
 *                                     still a normal link)
 *   [data-continue][data-scope]      "Continue where you left off" card/button; scope = all | <track id>
 *                                     children: [data-continue-link] (href), [data-continue-title],
 *                                     [data-continue-meta], [data-continue-eyebrow]
 *   [data-level-filter] button[data-value]   level filter (all | beginner | intermediate | advanced),
 *                                     reflected in ?level=
 *   [data-module-collapse]           disclosure button for a module's node list (aria-controls)
 *   [data-expand-all] / [data-collapse-all]
 *   [data-cert-progress]             certificate progress summary (data-core, data-projects JSON)
 *   [data-time-left]                 reading time left (required tracks)
 *   [data-first-todo="a,b,c"]        link: href becomes the first not-done slug's URL (fallback: as rendered)
 */
import { subscribe, type ProgressState } from '../lib/progress';

interface OrderItem {
  slug: string;
  title: string;
  track: string;
  trackTitle: string;
  url: string;
  minutes: number;
  n: number;
  of: number;
  optional: boolean;
  kind: 'core' | 'project';
  written: boolean;
}

const dataEl = document.getElementById('aik-course-order');
const order: OrderItem[] = dataEl ? JSON.parse(dataEl.textContent || '[]') : [];
const bySlug = new Map(order.map((o) => [o.slug, o]));
const FALLBACK_TRACKS = ['beginner', 'intermediate', 'advanced'];

const isDone = (s: ProgressState, slug: string) => !!s.lessons[slug]?.done;

function firstTodo(state: ProgressState, items: OrderItem[]) {
  return items.find((o) => !isDone(state, o.slug));
}

/** The lesson the learner should open next, or null if everything is complete. */
export function continueTarget(state: ProgressState, scope = 'all'): { item: OrderItem; resumed: boolean } | null {
  const inScope = scope === 'all' ? order : order.filter((o) => o.track === scope);
  const lv = state.lastVisited ? bySlug.get(state.lastVisited.slug) : undefined;
  if (lv && (scope === 'all' || lv.track === scope)) {
    if (!isDone(state, lv.slug)) return { item: lv, resumed: true };
    const trackItems = order.filter((o) => o.track === lv.track);
    const after = trackItems.slice(trackItems.findIndex((o) => o.slug === lv.slug) + 1);
    const nxt = firstTodo(state, after) ?? firstTodo(state, trackItems);
    if (nxt) return { item: nxt, resumed: true };
  }
  if (scope !== 'all') {
    const t = firstTodo(state, inScope);
    return t ? { item: t, resumed: false } : null;
  }
  for (const id of FALLBACK_TRACKS) {
    const t = firstTodo(state, order.filter((o) => o.track === id));
    if (t) return { item: t, resumed: false };
  }
  const rest = firstTodo(state, order.filter((o) => o.kind === 'project')) ?? firstTodo(state, order);
  return rest ? { item: rest, resumed: false } : null;
}

function renderMaps(state: ProgressState) {
  const target = continueTarget(state, 'all')?.item.slug;
  document.querySelectorAll<HTMLElement>('[data-track-map]').forEach((map) => {
    const nodes = [...map.querySelectorAll<HTMLElement>('li[data-node]')];
    let nextFound = false;
    for (const li of nodes) {
      const slug = li.dataset.node!;
      let st: 'done' | 'next' | 'later';
      if (isDone(state, slug)) st = 'done';
      else if (!nextFound) {
        st = 'next';
        nextFound = true;
      } else st = 'later';
      li.dataset.state = st;
      const link = li.querySelector<HTMLAnchorElement>('a.node__link');
      if (link) {
        if (slug === target) link.setAttribute('aria-current', 'step');
        else link.removeAttribute('aria-current');
      }
      const sr = li.querySelector<HTMLElement>('[data-node-state]');
      if (sr) sr.textContent = st === 'done' ? '(completed)' : st === 'next' ? '(up next)' : '(not started)';
    }
  });
}

function renderContinue(state: ProgressState) {
  const anyProgress = Object.values(state.lessons).some((m) => m.done) || !!state.lastVisited;
  document.querySelectorAll<HTMLElement>('[data-continue]').forEach((el) => {
    const scope = el.dataset.scope || 'all';
    const t = continueTarget(state, scope);
    el.dataset.complete = String(!t);
    if (!t) return;
    const { item, resumed } = t;
    const link = el.matches('a') ? (el as HTMLAnchorElement) : el.querySelector<HTMLAnchorElement>('[data-continue-link]');
    if (link) link.href = item.url;
    const title = el.querySelector<HTMLElement>('[data-continue-title]');
    if (title) title.textContent = item.title;
    const meta = el.querySelector<HTMLElement>('[data-continue-meta]');
    if (meta) meta.textContent = `${item.trackTitle} · Lesson ${item.n} of ${item.of} · ${item.minutes} min${item.written ? '' : ' · coming soon'}`;
    const eyebrow = el.querySelector<HTMLElement>('[data-continue-eyebrow]');
    if (eyebrow) eyebrow.textContent = resumed ? 'Continue where you left off' : anyProgress ? 'Up next' : 'Start here';
    const label = el.querySelector<HTMLElement>('[data-continue-label]');
    if (label) label.textContent = resumed || anyProgress ? 'Continue' : 'Start';
  });
}

function renderCert(state: ProgressState) {
  document.querySelectorAll<HTMLElement>('[data-cert-progress]').forEach((el) => {
    const core = (el.dataset.core || '').split(',').filter(Boolean);
    const projects: Record<string, string[]> = JSON.parse(el.dataset.projects || '{}');
    const minProjects = Number(el.dataset.minProjects || '1');
    const coreDone = core.filter((s) => isDone(state, s)).length;
    const projStats = Object.entries(projects)
      .map(([id, slugs]) => ({ id, done: slugs.filter((s) => isDone(state, s)).length, total: slugs.length }))
      .sort((a, b) => b.done / b.total - a.done / a.total);
    const best = projStats.slice(0, minProjects);
    const projectsComplete = projStats.filter((p) => p.done === p.total).length;
    const done = coreDone + best.reduce((s, p) => s + p.done, 0);
    const total = core.length + best.reduce((s, p) => s + p.total, 0);
    const pct = total ? Math.round((done / total) * 100) : 0;
    const unlocked = coreDone === core.length && projectsComplete >= minProjects;
    el.dataset.unlocked = String(unlocked);
    el.style.setProperty('--pct', String(pct));
    const set = (sel: string, text: string) => el.querySelectorAll<HTMLElement>(sel).forEach((t) => (t.textContent = text));
    set('[data-cert-core]', `${coreDone} / ${core.length}`);
    set('[data-cert-projects]', `${Math.min(projectsComplete, minProjects)} / ${minProjects}`);
    set('[data-cert-pct]', `${pct}%`);
    set('[data-cert-status]', unlocked ? 'Unlocked: your certificate is ready.' : `${pct}% of the way to your certificate`);
  });
}

function renderTimeLeft(state: ProgressState) {
  const left = order.filter((o) => !o.optional && !isDone(state, o.slug)).reduce((s, o) => s + o.minutes, 0);
  const h = Math.round((left / 60) * 2) / 2;
  const text = left === 0 ? 'Nothing left: every required lesson is complete' : left < 60 ? `About ${left} min of reading left` : `About ${h % 1 ? h.toFixed(1) : h} h of reading left`;
  document.querySelectorAll<HTMLElement>('[data-time-left]').forEach((el) => (el.textContent = text));
}

function renderFirstTodo(state: ProgressState) {
  document.querySelectorAll<HTMLAnchorElement>('a[data-first-todo]').forEach((a) => {
    const slugs = a.dataset.firstTodo!.split(',').filter(Boolean);
    const s = slugs.find((x) => !isDone(state, x));
    const item = s ? bySlug.get(s) : undefined;
    if (item) a.href = item.url;
    a.dataset.allDone = String(!s);
  });
}

// ---- Level filter ----
function applyLevel(level: string) {
  document.querySelectorAll<HTMLElement>('[data-level-filter] button[data-value]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.value === level)));
  document.querySelectorAll<HTMLElement>('li[data-node]').forEach((li) => {
    li.hidden = level !== 'all' && li.dataset.level !== level;
  });
  document.querySelectorAll<HTMLElement>('[data-module]').forEach((m) => {
    m.hidden = !m.querySelector('li[data-node]:not([hidden])');
  });
  document.querySelectorAll<HTMLElement>('[data-track-section]').forEach((t) => {
    t.hidden = !t.querySelector('li[data-node]:not([hidden])');
  });
  const empty = document.querySelector<HTMLElement>('[data-filter-empty]');
  if (empty) empty.hidden = !!document.querySelector('li[data-node]:not([hidden])');
}

const filter = document.querySelector<HTMLElement>('[data-level-filter]');
if (filter) {
  const initial = new URLSearchParams(location.search).get('level') || 'all';
  applyLevel(['all', 'beginner', 'intermediate', 'advanced'].includes(initial) ? initial : 'all');
  filter.addEventListener('click', (e) => {
    const b = (e.target as HTMLElement).closest<HTMLButtonElement>('button[data-value]');
    if (!b) return;
    const level = b.dataset.value!;
    applyLevel(level);
    const url = new URL(location.href);
    if (level === 'all') url.searchParams.delete('level');
    else url.searchParams.set('level', level);
    history.replaceState(null, '', url);
  });
}

// ---- Collapse / expand modules ----
function setExpanded(btn: HTMLElement, open: boolean) {
  btn.setAttribute('aria-expanded', String(open));
  const panel = document.getElementById(btn.getAttribute('aria-controls') || '');
  if (panel) panel.hidden = !open;
}
document.addEventListener('click', (e) => {
  const t = e.target as HTMLElement;
  const col = t.closest<HTMLElement>('[data-module-collapse]');
  if (col) {
    setExpanded(col, col.getAttribute('aria-expanded') !== 'true');
    return;
  }
  if (t.closest('[data-level-filter-reset]')) document.querySelector<HTMLButtonElement>('[data-level-filter] button[data-value="all"]')?.click();
  if (t.closest('[data-expand-all]')) document.querySelectorAll<HTMLElement>('[data-module-collapse]').forEach((b) => setExpanded(b, true));
  if (t.closest('[data-collapse-all]')) document.querySelectorAll<HTMLElement>('[data-module-collapse]').forEach((b) => setExpanded(b, false));
});

subscribe((state) => {
  renderMaps(state);
  renderContinue(state);
  renderCert(state);
  renderTimeLeft(state);
  renderFirstTodo(state);
});

// Hydration marker: path maps, "Continue" and the level filter are live.
document.documentElement.dataset.courseReady = 'true';
