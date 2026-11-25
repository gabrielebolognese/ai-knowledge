/**
 * Pure helpers for the certificate page (no DOM): name clean-up, certificate ID,
 * file names, date formatting and the unlock rule from curriculum.json
 * (certificateRequirement). Shared by the page script and the tests' expectations.
 */

export const NAME_MAX = 48;

export interface CertLesson {
  slug: string;
  title: string;
  url: string;
  minutes: number;
}
export interface CertTrack {
  id: string;
  title: string;
  short: string;
  url: string;
  lessons: CertLesson[];
}
export interface CertData {
  description: string;
  core: CertTrack[];
  projects: CertTrack[];
  minProjects: number;
  /** minutes of every lesson in the course (for the "hours of study" line) */
  minutes: Record<string, number>;
}

/** Trim, collapse whitespace, cap at 48 characters. Never changes case or diacritics. */
export function normalizeName(raw: string): string {
  return raw.replace(/\s+/g, ' ').trim().slice(0, NAME_MAX).trim();
}

function fnv1a(text: string, seed = 0x811c9dc5): number {
  let h = seed >>> 0;
  for (const ch of text) {
    const cp = ch.codePointAt(0)!;
    h ^= cp & 0xff;
    h = Math.imul(h, 0x01000193) >>> 0;
    if (cp > 0xff) {
      h ^= cp >>> 8;
      h = Math.imul(h, 0x01000193) >>> 0;
    }
  }
  return h >>> 0;
}

/** Short, deterministic ID from name + date: AK-XXXX-XXXX (same inputs → same ID). */
export function certificateId(name: string, isoDate: string): string {
  const key = `${normalizeName(name).normalize('NFC')}|${isoDate}`;
  const a = fnv1a(key).toString(16).padStart(8, '0');
  const b = fnv1a(key.split('').reverse().join(''), 0x9e3779b9).toString(16).padStart(8, '0');
  return `AK-${a.slice(0, 4)}-${b.slice(0, 4)}`.toUpperCase();
}

/** ASCII file-name slug; falls back to "learner" for names without Latin letters. */
export function nameSlug(name: string): string {
  const s = normalizeName(name)
    .normalize('NFKD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 40);
  return s || 'learner';
}

export function todayISO(d = new Date()): string {
  const p = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

/** "25 November 2026" from "2026-11-25" (no time-zone shift). */
export function formatDate(iso: string): string {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
  if (!m) return iso;
  const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  return `${Number(m[3])} ${months[Number(m[2]) - 1]} ${m[1]}`;
}

export interface TrackStat {
  track: CertTrack;
  done: number;
  total: number;
  remaining: CertLesson[];
  complete: boolean;
}
export interface CertStatus {
  unlocked: boolean;
  pct: number;
  core: TrackStat[];
  projects: TrackStat[];
  coreDone: number;
  coreTotal: number;
  projectsComplete: number;
  /** lessons completed anywhere in the course, and their reading time */
  lessonsDone: number;
  minutesDone: number;
}

function stat(track: CertTrack, isDone: (s: string) => boolean): TrackStat {
  const remaining = track.lessons.filter((l) => !isDone(l.slug));
  return { track, done: track.lessons.length - remaining.length, total: track.lessons.length, remaining, complete: remaining.length === 0 };
}

/**
 * certificateRequirement: every lesson of the listed core tracks plus every lesson of at
 * least `minProjects` project tracks. Percentage counts the core lessons plus the
 * `minProjects` project tracks closest to completion (same rule as the dashboard card).
 */
export function certStatus(data: CertData, isDone: (slug: string) => boolean): CertStatus {
  const core = data.core.map((t) => stat(t, isDone));
  const projects = data.projects.map((t) => stat(t, isDone)).sort((a, b) => b.done / (b.total || 1) - a.done / (a.total || 1));
  const coreDone = core.reduce((s, t) => s + t.done, 0);
  const coreTotal = core.reduce((s, t) => s + t.total, 0);
  const best = projects.slice(0, data.minProjects);
  const projectsComplete = projects.filter((p) => p.complete).length;
  const done = coreDone + best.reduce((s, p) => s + p.done, 0);
  const total = coreTotal + best.reduce((s, p) => s + p.total, 0);
  let lessonsDone = 0;
  let minutesDone = 0;
  for (const [slug, min] of Object.entries(data.minutes)) {
    if (isDone(slug)) {
      lessonsDone += 1;
      minutesDone += min;
    }
  }
  return {
    unlocked: coreDone === coreTotal && projectsComplete >= data.minProjects,
    pct: total ? Math.floor((done / total) * 100) : 0,
    core,
    projects,
    coreDone,
    coreTotal,
    projectsComplete,
    lessonsDone,
    minutesDone,
  };
}
