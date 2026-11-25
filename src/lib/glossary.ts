/** Glossary helpers (build time): sorted entries and the lessons that link to each term. */
import { getCollection, type CollectionEntry } from 'astro:content';
import { getCatalog, type CatLesson } from './catalog';

export type GlossaryEntry = CollectionEntry<'glossary'>;

let cache: { entries: GlossaryEntry[]; usedIn: Map<string, CatLesson[]> } | null = null;

export async function getGlossary() {
  if (cache) return cache;
  const entries = (await getCollection('glossary')).sort((a, b) => a.data.term.localeCompare(b.data.term, 'en', { sensitivity: 'base' }));
  const cat = await getCatalog();
  const usedIn = new Map<string, CatLesson[]>();
  for (const l of cat.all) {
    const body = l.entry?.body ?? '';
    for (const m of body.matchAll(/<Term\s+slug="([a-z0-9-]+)"/g)) {
      const list = usedIn.get(m[1]) ?? [];
      if (!list.includes(l)) list.push(l);
      usedIn.set(m[1], list);
    }
  }
  cache = { entries, usedIn };
  return cache;
}

/** First letter used for the A-Z index ("#" for digits and symbols). */
export const letterOf = (term: string) => {
  const c = term.trim()[0]?.toUpperCase() ?? '#';
  return /[A-Z]/.test(c) ? c : '#';
};
