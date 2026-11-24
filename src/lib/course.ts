/**
 * Course structure helpers (build time).
 *
 * Order of truth:
 *  1. src/data/curriculum.json, when present (written by the curriculum step). Accepted shape:
 *     { "tracks": [ { "id": "beginner", "title"?: "...", "modules": [ { "id"?: "...", "title": "...",
 *        "lessons": [ "slug" | { "slug": "..." } ] } ] } ] }
 *     A track may also list "lessons" directly instead of "modules".
 *  2. Otherwise: lesson frontmatter (track, module, order).
 */
import { getCollection, type CollectionEntry } from 'astro:content';
import { TRACKS } from './schema.mjs';

export type Lesson = CollectionEntry<'lessons'>;
export type TrackId = (typeof TRACKS)[number];

export interface TrackMeta {
  id: TrackId;
  title: string;
  short: string;
  kind: 'core' | 'project';
  level: 'beginner' | 'intermediate' | 'advanced';
  blurb: string;
}

export const TRACK_META: Record<TrackId, TrackMeta> = {
  setup: { id: 'setup', title: 'Setup', short: 'Setup', kind: 'core', level: 'beginner', blurb: 'Install Python, an editor and the libraries. Skip it if you are already set up.' },
  beginner: { id: 'beginner', title: 'Beginner', short: 'Beginner', kind: 'core', level: 'beginner', blurb: 'Python for ML, the math you need, and your first neural network.' },
  intermediate: { id: 'intermediate', title: 'Intermediate', short: 'Intermediate', kind: 'core', level: 'intermediate', blurb: 'PyTorch, training that works, CNNs and sequence models.' },
  advanced: { id: 'advanced', title: 'Advanced', short: 'Advanced', kind: 'core', level: 'advanced', blurb: 'Attention, Transformers, search and evaluation.' },
  'project-digits-letters': { id: 'project-digits-letters', title: 'Handwritten digits and letters', short: 'Digits & letters', kind: 'project', level: 'intermediate', blurb: 'Recognise handwritten digits (MNIST) and letters (EMNIST).' },
  'project-doodles': { id: 'project-doodles', title: 'Doodle recognition', short: 'Doodles', kind: 'project', level: 'intermediate', blurb: 'Classify quick sketches from the Quick, Draw! dataset.' },
  'project-text': { id: 'project-text', title: 'Small-text models', short: 'Small text', kind: 'project', level: 'intermediate', blurb: 'A character-level generator and a short-text classifier.' },
  'project-code-autocomplete': { id: 'project-code-autocomplete', title: 'Code autocompletion', short: 'Code completion', kind: 'project', level: 'advanced', blurb: 'Train a tiny GPT that completes Python code.' },
  'project-chess': { id: 'project-chess', title: 'Mini chess engine', short: 'Chess engine', kind: 'project', level: 'advanced', blurb: 'Alpha-beta search with a neural-network evaluator.' },
};

export const lessonUrl = (l: { data: { track: string; slug: string } } | { track: string; slug: string }) => {
  const d = 'data' in l ? l.data : l;
  return `/course/${d.track}/${d.slug}/`;
};

interface CurriculumModule {
  id?: string;
  title: string;
  lessons: (string | { slug: string })[];
}
interface CurriculumTrack {
  id: string;
  title?: string;
  modules?: CurriculumModule[];
  lessons?: (string | { slug: string })[];
}

const curriculumFiles = import.meta.glob<{ default: { tracks?: CurriculumTrack[] } }>('/src/data/curriculum.json', { eager: true });
const curriculum = Object.values(curriculumFiles)[0]?.default ?? null;

export interface ModuleGroup {
  title: string;
  lessons: Lesson[];
}
export interface TrackGroup {
  meta: TrackMeta;
  modules: ModuleGroup[];
  lessons: Lesson[];
}

const slugOf = (x: string | { slug: string }) => (typeof x === 'string' ? x : x.slug);

let cached: TrackGroup[] | null = null;

/** All tracks in course order, each with modules and a flat lesson list. */
export async function getCourse(): Promise<TrackGroup[]> {
  if (cached) return cached;
  const all = await getCollection('lessons');
  const bySlug = new Map(all.map((l) => [l.data.slug, l]));
  const used = new Set<string>();
  const groups: TrackGroup[] = [];

  for (const id of TRACKS as readonly TrackId[]) {
    const meta = TRACK_META[id];
    let modules: ModuleGroup[] = [];
    const ct = curriculum?.tracks?.find((t) => t.id === id);
    if (ct) {
      const mods: CurriculumModule[] = ct.modules ?? [{ title: meta.title, lessons: ct.lessons ?? [] }];
      modules = mods.map((m) => ({
        title: m.title,
        lessons: m.lessons.map(slugOf).map((s) => bySlug.get(s)).filter((l): l is Lesson => !!l),
      }));
    }
    modules.forEach((m) => m.lessons.forEach((l) => used.add(l.data.slug)));
    // Lessons not (yet) in the curriculum, grouped by frontmatter module.
    const rest = all
      .filter((l) => l.data.track === id && !used.has(l.data.slug))
      .sort((a, b) => a.data.order - b.data.order || a.data.title.localeCompare(b.data.title));
    for (const l of rest) {
      const title = l.data.module ?? meta.title;
      let mod = modules.find((m) => m.title === title);
      if (!mod) modules.push((mod = { title, lessons: [] }));
      mod.lessons.push(l);
      used.add(l.data.slug);
    }
    modules = modules.filter((m) => m.lessons.length);
    groups.push({ meta, modules, lessons: modules.flatMap((m) => m.lessons) });
  }
  cached = groups;
  return groups;
}

export async function getLessonBySlug(slug: string): Promise<Lesson | undefined> {
  const all = await getCollection('lessons');
  return all.find((l) => l.data.slug === slug);
}

/** Previous/next lesson inside the same track (projects and core tracks are separate paths). */
export async function getNeighbours(slug: string) {
  const course = await getCourse();
  for (const t of course) {
    const i = t.lessons.findIndex((l) => l.data.slug === slug);
    if (i === -1) continue;
    const mod = t.modules.find((m) => m.lessons.some((l) => l.data.slug === slug));
    return { track: t, module: mod, index: i, prev: t.lessons[i - 1], next: t.lessons[i + 1] };
  }
  return { track: undefined, module: undefined, index: -1, prev: undefined, next: undefined };
}
