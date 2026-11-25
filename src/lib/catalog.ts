/**
 * Full course catalog (build time) for the dashboard, track pages, projects and exercise library.
 *
 * Unlike getCourse() (written lessons only), the catalog lists EVERY lesson planned in
 * src/data/curriculum.json, merged with the written lesson's frontmatter when it exists.
 * Planned-but-unwritten lessons still get a URL: /course/<track>/<slug>/ renders a
 * "coming soon" page from the curriculum entry, so every node on the path map is clickable.
 * Written lessons that are not (yet) in the curriculum are appended to their track.
 */
import { getCollection, type CollectionEntry } from 'astro:content';
import curriculum from '../data/curriculum.json';
import { TRACKS } from './schema.mjs';

type Level = 'beginner' | 'intermediate' | 'advanced';
export type Lesson = CollectionEntry<'lessons'>;

export interface CatLesson {
  slug: string;
  title: string;
  track: string;
  moduleId: string;
  moduleTitle: string;
  level: Level;
  minutes: number;
  summary: string;
  goals: string[];
  prerequisites: string[];
  sources: { id: string; url: string }[];
  codeFiles: string[];
  research?: string;
  written: boolean;
  url: string;
  /** 1-based position inside its track. */
  n: number;
  entry?: Lesson;
}
export interface CatModule {
  id: string;
  title: string;
  lessons: CatLesson[];
}
export interface CatTrack {
  id: string;
  title: string;
  kind: 'core' | 'project';
  level: Level;
  optional: boolean;
  blurb: string;
  outcome?: string;
  skipNote?: string;
  quickStart: string[];
  recommendedPath: string[];
  codeDir?: string;
  datasets: string[];
  modules: CatModule[];
  lessons: CatLesson[];
  minutes: number;
}
export interface SkipPath {
  id: string;
  label: string;
  description: string;
  skipTracks: string[];
  skipLessons: string[];
  startAt: string;
}
export interface Catalog {
  tracks: CatTrack[];
  bySlug: Map<string, CatLesson>;
  trackById: Map<string, CatTrack>;
  all: CatLesson[];
  skipPaths: SkipPath[];
  certificate: {
    description: string;
    allLessonsInTracks: string[];
    projectTracks: string[];
    minProjectTracksCompleted: number;
  };
  sourceRegistry: Record<string, { title: string; url: string; publisher?: string }>;
}

interface RawLesson {
  slug: string;
  title: string;
  track: string;
  module?: string;
  level: Level;
  minutes: number;
  goals?: string[];
  prerequisites?: string[];
  sources?: { id: string; url: string }[];
  codeFiles?: string[];
  research?: string;
  covers?: string;
}
interface RawTrack {
  id: string;
  title: string;
  kind: 'core' | 'project';
  level: Level;
  optional?: boolean;
  blurb: string;
  outcome?: string;
  skipNote?: string;
  quickStart?: string[];
  recommendedPath?: string[];
  codeDir?: string;
  datasets?: string[];
  modules: { id: string; title: string; lessons: RawLesson[] }[];
}

export const lessonHref = (track: string, slug: string) => `/course/${track}/${slug}/`;
export const REPO = 'https://github.com/gabrielebolognese/ai-knowledge';

let cached: Catalog | null = null;

export async function getCatalog(): Promise<Catalog> {
  if (cached) return cached;
  const written = await getCollection('lessons');
  const writtenBySlug = new Map(written.map((l) => [l.data.slug, l]));
  const used = new Set<string>();
  const raw = curriculum as unknown as {
    tracks: RawTrack[];
    skipPaths: SkipPath[];
    certificateRequirement: Catalog['certificate'];
    sourceRegistry: Catalog['sourceRegistry'];
  };

  const tracks: CatTrack[] = [];
  for (const id of TRACKS as readonly string[]) {
    const rt = raw.tracks.find((t) => t.id === id);
    if (!rt) continue;
    const modules: CatModule[] = rt.modules.map((m) => ({
      id: m.id,
      title: m.title,
      lessons: m.lessons.map((l) => {
        const e = writtenBySlug.get(l.slug);
        used.add(l.slug);
        return {
          slug: l.slug,
          title: e?.data.title ?? l.title,
          track: rt.id,
          moduleId: m.id,
          moduleTitle: m.title,
          level: e?.data.level ?? l.level,
          minutes: e?.data.minutes ?? l.minutes,
          summary: e?.data.summary ?? l.goals?.[0] ?? '',
          goals: e?.data.outcomes?.length ? e.data.outcomes : (l.goals ?? []),
          prerequisites: l.prerequisites ?? [],
          sources: l.sources ?? [],
          codeFiles: l.codeFiles ?? [],
          research: l.research,
          written: !!e,
          url: lessonHref(rt.id, l.slug),
          n: 0,
          entry: e,
        } satisfies CatLesson;
      }),
    }));
    // Written lessons missing from the curriculum: keep them reachable.
    const extra = written
      .filter((l) => l.data.track === id && !used.has(l.data.slug))
      .sort((a, b) => a.data.order - b.data.order);
    if (extra.length) {
      modules.push({
        id: `${id}-more`,
        title: 'More lessons',
        lessons: extra.map((e) => {
          used.add(e.data.slug);
          return {
            slug: e.data.slug, title: e.data.title, track: id, moduleId: `${id}-more`, moduleTitle: 'More lessons',
            level: e.data.level, minutes: e.data.minutes, summary: e.data.summary, goals: e.data.outcomes,
            prerequisites: e.data.prerequisites, sources: [], codeFiles: [], written: true,
            url: lessonHref(id, e.data.slug), n: 0, entry: e,
          };
        }),
      });
    }
    const lessons = modules.flatMap((m) => m.lessons);
    lessons.forEach((l, i) => (l.n = i + 1));
    tracks.push({
      id: rt.id,
      title: rt.title,
      kind: rt.kind,
      level: rt.level,
      optional: !!rt.optional,
      blurb: rt.blurb,
      outcome: rt.outcome,
      skipNote: rt.skipNote,
      quickStart: rt.quickStart ?? [],
      recommendedPath: rt.recommendedPath ?? [],
      codeDir: rt.codeDir,
      datasets: rt.datasets ?? [],
      modules,
      lessons,
      minutes: lessons.reduce((s, l) => s + l.minutes, 0),
    });
  }

  const all = tracks.flatMap((t) => t.lessons);
  cached = {
    tracks,
    all,
    bySlug: new Map(all.map((l) => [l.slug, l])),
    trackById: new Map(tracks.map((t) => [t.id, t])),
    skipPaths: raw.skipPaths ?? [],
    certificate: raw.certificateRequirement,
    sourceRegistry: raw.sourceRegistry ?? {},
  };
  return cached;
}

export const fmtMinutes = (min: number) => {
  if (min < 60) return `${min} min`;
  const h = Math.round((min / 60) * 2) / 2;
  return `${h % 1 ? h.toFixed(1) : h} h`;
};

export const LEVEL_WORD: Record<Level, string> = { beginner: 'Beginner', intermediate: 'Intermediate', advanced: 'Advanced' };

/** Six project cards: digits and letters share one track, split by module. */
export const PROJECTS = [
  { key: 'digits', art: 'digit', title: 'Handwritten digits', track: 'project-digits-letters', module: 'digits', tagline: 'Train a network on MNIST, then draw a number and watch it read your handwriting.' },
  { key: 'letters', art: 'letter', title: 'Handwritten letters', track: 'project-digits-letters', module: 'letters', tagline: 'Extend the same model to the 26 letters of EMNIST, where look-alikes such as l and I make it harder.' },
  { key: 'doodles', art: 'doodle', title: 'Doodle recognition', track: 'project-doodles', tagline: 'Stream real sketches from Quick, Draw! and build a canvas app that guesses while you draw.' },
  { key: 'text', art: 'text', title: 'Small-text models', track: 'project-text', tagline: 'Invent names character by character, write Shakespeare-like text and classify the sentiment of short reviews.' },
  { key: 'code', art: 'code', title: 'Code autocompletion', track: 'project-code-autocomplete', tagline: 'Train a tiny GPT on Python code and let it finish your lines.' },
  { key: 'chess', art: 'chess', title: 'Mini chess engine', track: 'project-chess', tagline: 'Alpha-beta search with a neural-network evaluator: a small engine in the spirit of Stockfish that speaks UCI.' },
] as const;
