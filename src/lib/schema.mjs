// Single source of truth for content frontmatter.
// Used by src/content.config.ts (with `z` from astro/zod) and by
// scripts/validate-content.mjs (with `z` from zod). Both are Zod 4.

export const TRACKS = /** @type {const} */ ([
  'setup',
  'beginner',
  'intermediate',
  'advanced',
  'project-digits-letters',
  'project-doodles',
  'project-text',
  'project-code-autocomplete',
  'project-chess',
]);

export const LEVELS = /** @type {const} */ (['beginner', 'intermediate', 'advanced']);
export const EXERCISE_TYPES = /** @type {const} */ (['mcq', 'numeric', 'short', 'reveal']);
export const DIFFICULTIES = /** @type {const} */ (['easy', 'medium', 'hard']);

const SLUG = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;

/** @param {typeof import('zod/v4').z} z */
export function makeSchemas(z) {
  const isoDate = z.preprocess(
    (v) => (v instanceof Date ? v.toISOString().slice(0, 10) : v),
    z.string().regex(ISO_DATE, 'expected a date as YYYY-MM-DD'),
  );

  const slug = z.string().regex(SLUG, 'slugs are lowercase-kebab-case');

  const source = z.object({
    id: z.string().regex(/^[A-Za-z0-9][A-Za-z0-9_.:-]*$/, 'source ids are short tokens like "goodfellow2016"'),
    title: z.string().min(2),
    author: z.string().optional(),
    publisher: z.string().optional(),
    year: z.union([z.number().int(), z.string()]).optional(),
    url: z.string().regex(/^https?:\/\/\S+$/, 'source url must be an absolute http(s) URL'),
    accessed: isoDate,
    type: z.enum(['paper', 'docs', 'book', 'video', 'dataset', 'wikipedia', 'article', 'course', 'code']).optional(),
  });

  const exercise = z.object({
    id: z.string().regex(SLUG, 'exercise ids are lowercase-kebab-case and globally unique'),
    type: z.enum(EXERCISE_TYPES),
    difficulty: z.enum(DIFFICULTIES),
    title: z.string().optional(),
    prompt: z.string().min(5),
    options: z.array(z.string()).optional(),
    // mcq: 0-based option index or the exact option text; numeric: a number;
    // short: an accepted answer or a list of accepted answers; reveal: the model answer.
    answer: z.union([z.string(), z.number(), z.array(z.string())]),
    tolerance: z.number().nonnegative().optional(),
    hint: z.string().optional(),
    explanation: z.string().min(5),
    concepts: z.array(z.string()).optional(),
  });

  const lesson = z.object({
    title: z.string().min(2).max(90),
    slug,
    track: z.enum(TRACKS),
    level: z.enum(LEVELS),
    order: z.number(),
    minutes: z.number().int().positive().max(240),
    summary: z.string().min(20).max(300),
    module: z.string().optional(),
    hatnote: z.string().optional(),
    prerequisites: z.array(slug).default([]),
    tools: z.array(z.string()).default([]),
    outcomes: z.array(z.string()).default([]),
    build: z.string().optional(),
    reviewed: isoDate.optional(),
    sources: z.array(source),
    exercises: z.array(exercise),
    seeAlso: z.array(slug).default([]),
    furtherReading: z
      .array(z.object({ title: z.string(), url: z.string().regex(/^https?:\/\/\S+$/) }))
      .default([]),
  });

  const glossary = z.object({
    term: z.string().min(1),
    short: z.string().min(10).max(320),
    level: z.enum(LEVELS).optional(),
    aliases: z.array(z.string()).default([]),
    sources: z.array(source).min(1),
    related: z.array(slug).default([]),
  });

  return { source, exercise, lesson, glossary };
}
