import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';
import { makeSchemas } from './lib/schema.mjs';

const schemas = makeSchemas(z);

// src/content/lessons/<track>/<slug>.mdx  → entry id "<track>/<slug>"
const lessons = defineCollection({
  loader: glob({
    pattern: '**/[^_]*.mdx',
    base: './src/content/lessons',
    generateId: ({ entry }) => entry.replace(/\\/g, '/').replace(/\.mdx$/, ''),
  }),
  schema: schemas.lesson,
});

// src/content/glossary/<term>.md  → entry id "<term>"
const glossary = defineCollection({
  loader: glob({
    pattern: '**/[^_]*.md',
    base: './src/content/glossary',
    generateId: ({ entry }) => entry.replace(/\\/g, '/').replace(/\.md$/, ''),
  }),
  schema: schemas.glossary,
});

export const collections = { lessons, glossary };
