/**
 * Progress store. Browser-only, no server, no database.
 *
 * localStorage key: 'aik-progress-v1'
 * Shape: {
 *   version: 1,
 *   lessons:   { [slug]: { done: boolean, at: string /* ISO time *\/ } },
 *   exercises: { [id]:   { done: boolean, at: string } },
 *   name: string,                 // name printed on the certificate
 *   lastVisited: { slug, track, title, at } | null
 * }
 *
 * API: getState, subscribe, isLessonDone, toggleLesson, setLesson, setLessons (bulk),
 * isExerciseDone, toggleExercise, setExercise, setExercises (bulk), setName,
 * setLastVisited, exportJSON, importJSON, reset, registerMigration.
 * Cross-tab sync: listens to the 'storage' event.
 */

export const STORAGE_KEY = 'aik-progress-v1';
export const SCHEMA_VERSION = 1;

export interface Mark {
  done: boolean;
  at: string;
}
export interface LastVisited {
  slug: string;
  track?: string;
  title?: string;
  at: string;
}
export interface ProgressState {
  version: number;
  lessons: Record<string, Mark>;
  exercises: Record<string, Mark>;
  name: string;
  lastVisited: LastVisited | null;
}

type Listener = (state: ProgressState) => void;
type Migration = (raw: any) => any;

const listeners = new Set<Listener>();
/** Migrations keyed by the version they upgrade FROM (n → n + 1). */
const migrations = new Map<number, Migration>();
/** Older storage keys that should be read (and migrated) when the current key is empty. */
const LEGACY_KEYS: string[] = [];

let memoryFallback: string | null = null;
let cache: ProgressState | null = null;

export function emptyState(): ProgressState {
  return { version: SCHEMA_VERSION, lessons: {}, exercises: {}, name: '', lastVisited: null };
}

function storage(): Storage | null {
  try {
    if (typeof window === 'undefined' || !window.localStorage) return null;
    const probe = '__aik_probe__';
    window.localStorage.setItem(probe, '1');
    window.localStorage.removeItem(probe);
    return window.localStorage;
  } catch {
    return null; // private mode / disabled storage: keep progress in memory for this tab
  }
}

function readRaw(key = STORAGE_KEY): string | null {
  const s = storage();
  return s ? s.getItem(key) : key === STORAGE_KEY ? memoryFallback : null;
}

function writeRaw(value: string) {
  const s = storage();
  if (s) s.setItem(STORAGE_KEY, value);
  else memoryFallback = value;
}

/** Register a migration that upgrades data stored with `fromVersion` to `fromVersion + 1`. */
export function registerMigration(fromVersion: number, fn: Migration) {
  migrations.set(fromVersion, fn);
}

function isMarkMap(v: unknown): v is Record<string, Mark> {
  return !!v && typeof v === 'object' && !Array.isArray(v);
}

function sanitizeMarks(v: unknown): Record<string, Mark> {
  const out: Record<string, Mark> = {};
  if (!isMarkMap(v)) return out;
  for (const [k, m] of Object.entries(v)) {
    if (!k) continue;
    if (typeof m === 'boolean') out[k] = { done: m, at: new Date().toISOString() };
    else if (m && typeof m === 'object') {
      const mark = m as Partial<Mark>;
      out[k] = { done: !!mark.done, at: typeof mark.at === 'string' ? mark.at : new Date().toISOString() };
    }
  }
  return out;
}

/** Bring any parsed object up to the current schema. Unknown/garbage input yields an empty state. */
export function migrate(raw: any): ProgressState {
  if (!raw || typeof raw !== 'object') return emptyState();
  let data = { ...raw };
  let v = typeof data.version === 'number' ? data.version : 0;
  while (v < SCHEMA_VERSION) {
    const fn = migrations.get(v);
    if (fn) data = fn(data) ?? data;
    v += 1;
    data.version = v;
  }
  const lv = data.lastVisited;
  return {
    version: SCHEMA_VERSION,
    lessons: sanitizeMarks(data.lessons),
    exercises: sanitizeMarks(data.exercises),
    name: typeof data.name === 'string' ? data.name.slice(0, 120) : '',
    lastVisited:
      lv && typeof lv === 'object' && typeof lv.slug === 'string'
        ? { slug: lv.slug, track: lv.track, title: lv.title, at: typeof lv.at === 'string' ? lv.at : new Date().toISOString() }
        : null,
  };
}

// v0 → v1: pre-release data had no version and stored booleans; sanitizeMarks already
// converts booleans, so this hook only documents the pattern for future versions.
registerMigration(0, (raw) => raw);

function parse(text: string | null): ProgressState | null {
  if (!text) return null;
  try {
    return migrate(JSON.parse(text));
  } catch {
    return null;
  }
}

function load(): ProgressState {
  let state = parse(readRaw());
  if (!state) {
    for (const key of LEGACY_KEYS) {
      state = parse(readRaw(key));
      if (state) break;
    }
  }
  return state ?? emptyState();
}

export function getState(): ProgressState {
  if (!cache) cache = load();
  return cache;
}

function commit(next: ProgressState) {
  cache = next;
  writeRaw(JSON.stringify(next));
  for (const fn of listeners) {
    try {
      fn(next);
    } catch (err) {
      console.error('[progress] listener failed', err);
    }
  }
}

function update(mutator: (draft: ProgressState) => void) {
  const draft: ProgressState = structuredClone(getState());
  mutator(draft);
  commit(draft);
  return draft;
}

/** Subscribe to changes. The listener is called immediately with the current state. Returns an unsubscribe function. */
export function subscribe(fn: Listener): () => void {
  listeners.add(fn);
  fn(getState());
  return () => listeners.delete(fn);
}

const now = () => new Date().toISOString();

// ---- lessons ----
export function isLessonDone(slug: string): boolean {
  return !!getState().lessons[slug]?.done;
}
export function setLesson(slug: string, done: boolean) {
  update((d) => {
    d.lessons[slug] = { done, at: now() };
  });
  return done;
}
export function toggleLesson(slug: string): boolean {
  return setLesson(slug, !isLessonDone(slug));
}
/** Bulk set, e.g. "mark the whole Setup track complete". */
export function setLessons(slugs: string[], done: boolean) {
  update((d) => {
    const at = now();
    for (const s of slugs) d.lessons[s] = { done, at };
  });
}

// ---- exercises ----
export function isExerciseDone(id: string): boolean {
  return !!getState().exercises[id]?.done;
}
export function setExercise(id: string, done: boolean) {
  update((d) => {
    d.exercises[id] = { done, at: now() };
  });
  return done;
}
export function toggleExercise(id: string): boolean {
  return setExercise(id, !isExerciseDone(id));
}
export function setExercises(ids: string[], done: boolean) {
  update((d) => {
    const at = now();
    for (const id of ids) d.exercises[id] = { done, at };
  });
}

// ---- misc ----
export function setName(name: string) {
  update((d) => {
    d.name = name.trim().slice(0, 120);
  });
}
export function setLastVisited(v: Omit<LastVisited, 'at'>) {
  update((d) => {
    d.lastVisited = { ...v, at: now() };
  });
}

/** Counts done items among the given slugs. */
export function countDone(slugs: string[]): number {
  const s = getState();
  return slugs.reduce((n, slug) => n + (s.lessons[slug]?.done ? 1 : 0), 0);
}

export function exportJSON(): string {
  return JSON.stringify({ ...getState(), exportedAt: now(), app: 'ai-knowledge' }, null, 2);
}

/**
 * Import a JSON export. mode 'replace' (default) overwrites; 'merge' keeps the most recent
 * mark for each item. Throws on invalid JSON.
 */
export function importJSON(text: string, mode: 'replace' | 'merge' = 'replace'): ProgressState {
  const incoming = migrate(JSON.parse(text));
  if (mode === 'replace') {
    commit(incoming);
    return incoming;
  }
  return update((d) => {
    for (const key of ['lessons', 'exercises'] as const) {
      for (const [id, mark] of Object.entries(incoming[key])) {
        const cur = d[key][id];
        if (!cur || cur.at < mark.at) d[key][id] = mark;
      }
    }
    if (incoming.name) d.name = incoming.name;
    if (incoming.lastVisited && (!d.lastVisited || d.lastVisited.at < incoming.lastVisited.at)) d.lastVisited = incoming.lastVisited;
  });
}

export function reset() {
  commit(emptyState());
}

// Keep tabs in sync.
if (typeof window !== 'undefined') {
  window.addEventListener('storage', (e) => {
    if (e.key !== STORAGE_KEY) return;
    cache = parse(e.newValue) ?? emptyState();
    for (const fn of listeners) fn(cache);
  });
}
