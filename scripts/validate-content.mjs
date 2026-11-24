#!/usr/bin/env node
/**
 * Content validator for AI Knowledge lessons and glossary entries.
 *
 * Usage:
 *   node scripts/validate-content.mjs                 # everything
 *   node scripts/validate-content.mjs --track beginner
 *   node scripts/validate-content.mjs --strict        # warnings also fail
 *
 * Enforces the authoring rules in docs/authoring.md. Exits 1 and lists every failure.
 *
 * Lesson rules (errors):
 *  - every lesson listed in src/data/curriculum.json (if present) exists as
 *    src/content/lessons/<track>/<slug>.mdx
 *  - frontmatter matches the schema in src/lib/schema.mjs (same schema the site build uses);
 *    folder = track, file name = slug, slugs unique
 *  - >= 3 sources, every source URL is https, source ids unique, every source cited at least once
 *  - every <Cite id> resolves to a frontmatter source
 *  - >= 8 hyperlinks in the body (<Term> + markdown links + <Cite> + <a href>)
 *  - every <Term slug> has a glossary entry; internal /course/<track>/<slug>/ links resolve
 *  - >= 2 exercises; ids unique across the site; mcq answers resolve to an option; numeric answers are numbers
 *  - beginner and intermediate lessons contain >= 1 <Analogy>
 *  - any display math ($$...$$, \[...\], \begin{...}) requires <MathSteps>; every <MathSteps> has >= 2 <Step tex="...">;
 *    no <Step> outside a <MathSteps>
 *  - prerequisites / seeAlso slugs exist (and are not the lesson itself)
 *  - <CodeFile path> exists and its lines/highlight ranges fit the file
 *  - local <Figure>/<Screenshot> images exist in public/; remote ones are https; alt text present
 *  - the body opens with a lead paragraph (no heading/component first) and has no "# h1"
 * Warnings: word count outside 800–1800, h4+ headings, lessons missing from the curriculum.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import YAML from 'yaml';
import { z } from 'zod';
import { makeSchemas, TRACKS } from '../src/lib/schema.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const LESSONS_DIR = path.join(ROOT, 'src/content/lessons');
const GLOSSARY_DIR = path.join(ROOT, 'src/content/glossary');
const CURRICULUM = path.join(ROOT, 'src/data/curriculum.json');
const PUBLIC_DIR = path.join(ROOT, 'public');

const MIN_SOURCES = 3;
const MIN_LINKS = 8;
const MIN_EXERCISES = 2;
const WORDS = [800, 1800];

// ---------- args ----------
const args = process.argv.slice(2);
let onlyTrack = null;
let strict = false;
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--track') onlyTrack = args[++i];
  else if (args[i].startsWith('--track=')) onlyTrack = args[i].slice(8);
  else if (args[i] === '--strict') strict = true;
  else if (args[i] === '--help' || args[i] === '-h') {
    console.log('Usage: node scripts/validate-content.mjs [--track <id>] [--strict]');
    process.exit(0);
  } else {
    console.error(`Unknown argument: ${args[i]}`);
    process.exit(2);
  }
}
if (onlyTrack && !TRACKS.includes(onlyTrack)) {
  console.error(`Unknown track "${onlyTrack}". Valid: ${TRACKS.join(', ')}`);
  process.exit(2);
}

const schemas = makeSchemas(z);
const errors = []; // { file, msg }
const warnings = [];
const rel = (p) => path.relative(ROOT, p).split(path.sep).join('/');
const err = (file, msg) => errors.push({ file: rel(file), msg });
const warn = (file, msg) => warnings.push({ file: rel(file), msg });

// ---------- helpers ----------
function walk(dir, ext) {
  if (!fs.existsSync(dir)) return [];
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) out.push(...walk(p, ext));
    else if (e.name.endsWith(ext) && !e.name.startsWith('_')) out.push(p);
  }
  return out;
}

function splitFrontmatter(text) {
  const m = /^﻿?---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/.exec(text);
  if (!m) return null;
  return { fm: m[1], body: m[2], bodyLine: m[1].split('\n').length + 3 };
}

function formatZod(e) {
  return e.issues.map((i) => `frontmatter ${i.path.join('.') || '(root)'}: ${i.message}`);
}

/** Remove code (fenced + inline) and comments so rules only see prose/components. */
function stripCode(body) {
  return body
    .replace(/^(```|~~~)[^\n]*\n[\s\S]*?^\1[ \t]*$/gm, '')
    .replace(/\{\/\*[\s\S]*?\*\/\}/g, '')
    .replace(/<!--[\s\S]*?-->/g, '')
    .replace(/`[^`\n]+`/g, '``');
}

/** Attribute value (string literal) from a JSX tag source. */
function attrOf(tag, name) {
  const m = new RegExp(`\\b${name}\\s*=\\s*(?:"([^"]*)"|'([^']*)'|\\{\\s*["'\`]([^"'\`]*)["'\`]\\s*\\})`).exec(tag);
  return m ? (m[1] ?? m[2] ?? m[3]) : undefined;
}

/** All opening tags of a component, e.g. tags(body, 'Cite') → ['<Cite id="x" />', ...]. Handles multi-line tags. */
function tags(body, name) {
  const out = [];
  const re = new RegExp(`<${name}(?=[\\s/>])`, 'g');
  let m;
  while ((m = re.exec(body))) {
    // scan to the matching '>' while respecting quotes and {...} expressions
    let i = m.index + name.length + 1;
    let depth = 0;
    let quote = null;
    for (; i < body.length; i++) {
      const c = body[i];
      if (quote) {
        if (c === quote && body[i - 1] !== '\\') quote = null;
      } else if (c === '"' || c === "'" || c === '`') quote = c;
      else if (c === '{') depth++;
      else if (c === '}') depth--;
      else if (c === '>' && depth === 0) break;
    }
    out.push(body.slice(m.index, i + 1));
  }
  return out;
}

function countWords(body) {
  const text = stripCode(body)
    .replace(/<MathSteps[\s\S]*?<\/MathSteps>/g, ' ')
    .replace(/\$\$[\s\S]*?\$\$/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/[#*_>|`~-]/g, ' ');
  return (text.match(/[A-Za-z0-9][A-Za-z0-9'’.-]*/g) || []).length;
}

function parseRange(s) {
  const m = /^(\d+)\s*-\s*(\d+)$/.exec(String(s).trim());
  return m ? [Number(m[1]), Number(m[2])] : null;
}

// ---------- load glossary ----------
const glossaryFiles = walk(GLOSSARY_DIR, '.md');
const glossarySlugs = new Set(glossaryFiles.map((f) => path.basename(f, '.md')));
const glossaryEntries = [];
for (const file of glossaryFiles) {
  const parts = splitFrontmatter(fs.readFileSync(file, 'utf8'));
  if (!parts) {
    err(file, 'missing YAML frontmatter (--- ... ---)');
    continue;
  }
  let data;
  try {
    data = YAML.parse(parts.fm);
  } catch (e) {
    err(file, `YAML error: ${e.message.split('\n')[0]}`);
    continue;
  }
  const r = schemas.glossary.safeParse(data);
  if (!r.success) {
    formatZod(r.error).forEach((m) => err(file, m));
    continue;
  }
  glossaryEntries.push({ file, slug: path.basename(file, '.md'), data: r.data });
}
if (!onlyTrack) {
  for (const g of glossaryEntries) {
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(g.slug)) err(g.file, `glossary file name "${g.slug}" must be lowercase-kebab-case`);
    for (const s of g.data.sources) if (!s.url.startsWith('https://')) err(g.file, `source "${s.id}" URL must use https: ${s.url}`);
    for (const r of g.data.related) if (!glossarySlugs.has(r)) err(g.file, `related term "${r}" has no glossary entry`);
  }
}

// ---------- load lessons ----------
const lessonFiles = walk(LESSONS_DIR, '.mdx');
const lessons = [];
for (const file of lessonFiles) {
  const text = fs.readFileSync(file, 'utf8');
  const parts = splitFrontmatter(text);
  const folder = path.basename(path.dirname(file));
  const fileSlug = path.basename(file, '.mdx');
  if (!parts) {
    err(file, 'missing YAML frontmatter (--- ... ---)');
    continue;
  }
  let raw;
  try {
    raw = YAML.parse(parts.fm);
  } catch (e) {
    err(file, `YAML error: ${e.message.split('\n')[0]}`);
    continue;
  }
  const r = schemas.lesson.safeParse(raw);
  lessons.push({ file, folder, fileSlug, body: parts.body, raw, data: r.success ? r.data : null, zodError: r.success ? null : r.error });
}

const allSlugs = new Map(); // slug -> lesson
for (const l of lessons) {
  const slug = l.data?.slug ?? l.raw?.slug ?? l.fileSlug;
  if (allSlugs.has(slug)) err(l.file, `duplicate slug "${slug}" (also in ${rel(allSlugs.get(slug).file)})`);
  else allSlugs.set(slug, l);
}
const exerciseOwners = new Map();
for (const l of lessons) {
  for (const ex of l.data?.exercises ?? []) {
    if (exerciseOwners.has(ex.id) && exerciseOwners.get(ex.id) !== l) err(l.file, `exercise id "${ex.id}" is also used in ${rel(exerciseOwners.get(ex.id).file)}; ids must be unique site-wide`);
    else exerciseOwners.set(ex.id, l);
  }
}

// ---------- curriculum ----------
let curriculumPairs = null;
if (fs.existsSync(CURRICULUM)) {
  try {
    const cur = JSON.parse(fs.readFileSync(CURRICULUM, 'utf8'));
    curriculumPairs = [];
    if (!Array.isArray(cur.tracks)) err(CURRICULUM, 'curriculum.json must have a "tracks" array');
    for (const t of cur.tracks ?? []) {
      if (!TRACKS.includes(t.id)) err(CURRICULUM, `unknown track id "${t.id}"`);
      const mods = t.modules ?? [{ lessons: t.lessons ?? [] }];
      for (const m of mods) for (const item of m.lessons ?? []) {
        const slug = typeof item === 'string' ? item : item?.slug;
        if (!slug) err(CURRICULUM, `track "${t.id}" has a lesson entry without a slug`);
        else curriculumPairs.push({ track: t.id, slug });
      }
    }
  } catch (e) {
    err(CURRICULUM, `invalid JSON: ${e.message}`);
  }
}
if (curriculumPairs) {
  const seen = new Set();
  for (const { track, slug } of curriculumPairs) {
    if (onlyTrack && track !== onlyTrack) continue;
    if (seen.has(slug)) err(CURRICULUM, `slug "${slug}" is listed more than once`);
    seen.add(slug);
    const expected = path.join(LESSONS_DIR, track, `${slug}.mdx`);
    if (!fs.existsSync(expected)) err(CURRICULUM, `curriculum lesson missing: ${rel(expected)}`);
  }
  const inCurriculum = new Set(curriculumPairs.map((p) => p.slug));
  for (const l of lessons) {
    if (onlyTrack && l.folder !== onlyTrack) continue;
    const slug = l.data?.slug ?? l.fileSlug;
    if (!inCurriculum.has(slug)) warn(l.file, `lesson "${slug}" is not listed in src/data/curriculum.json`);
  }
}

// ---------- per-lesson rules ----------
const selected = lessons.filter((l) => !onlyTrack || l.folder === onlyTrack || l.data?.track === onlyTrack);

for (const l of selected) {
  const { file } = l;
  if (l.zodError) {
    formatZod(l.zodError).forEach((m) => err(file, m));
    continue;
  }
  const d = l.data;
  const body = stripCode(l.body);

  // structure
  if (d.track !== l.folder) err(file, `track "${d.track}" does not match its folder "${l.folder}"`);
  if (d.slug !== l.fileSlug) err(file, `slug "${d.slug}" does not match the file name "${l.fileSlug}.mdx"`);
  const firstBlock = body.split(/\r?\n/).map((s) => s.trim()).find((s) => s && !s.startsWith('import ') && !s.startsWith('export '));
  if (!firstBlock) err(file, 'lesson body is empty');
  else if (/^(#|<(?!Term|Cite)[A-Z])/.test(firstBlock)) err(file, 'the body must open with a lead paragraph (2-4 sentences) before any heading or block component');
  if (/^#\s/m.test(body)) err(file, 'do not use "# " (h1) in the body; the title comes from frontmatter');
  if (/^#{4,}\s/m.test(body)) warn(file, 'use only ## and ### headings (Wikipedia-style sections)');

  // sources
  if (d.sources.length < MIN_SOURCES) err(file, `needs >= ${MIN_SOURCES} sources (has ${d.sources.length})`);
  const sourceIds = new Set();
  for (const s of d.sources) {
    if (sourceIds.has(s.id)) err(file, `duplicate source id "${s.id}"`);
    sourceIds.add(s.id);
    if (!/^https:\/\/[^\s]+\.[^\s]+/.test(s.url)) err(file, `source "${s.id}" must have an https URL (got ${s.url})`);
    if (!s.author && !s.publisher) err(file, `source "${s.id}" needs an author or a publisher`);
  }
  for (const f of d.furtherReading) if (!f.url.startsWith('https://')) err(file, `further reading "${f.title}" must use https`);

  // citations
  const citeTags = tags(body, 'Cite');
  const cited = new Set();
  for (const t of citeTags) {
    const id = attrOf(t, 'id');
    if (!id) err(file, `<Cite> without an id: ${t}`);
    else if (!sourceIds.has(id)) err(file, `<Cite id="${id}"> does not match any frontmatter source id`);
    else cited.add(id);
  }
  for (const id of sourceIds) if (!cited.has(id)) err(file, `source "${id}" is never cited in the text (cite it with <Cite id="${id}" /> or move it to furtherReading)`);

  // glossary terms
  const termTags = tags(body, 'Term');
  for (const t of termTags) {
    const slug = attrOf(t, 'slug');
    if (!slug) err(file, `<Term> without a slug: ${t}`);
    else if (!glossarySlugs.has(slug)) err(file, `<Term slug="${slug}"> has no glossary entry (create src/content/glossary/${slug}.md)`);
  }

  // hyperlinks
  const mdLinks = [...body.matchAll(/(?<!!)\[([^\]\n]+)\]\(([^)\s]+)(?:\s+"[^"]*")?\)/g)].map((m) => m[2]);
  const htmlLinks = [...body.matchAll(/<a\s[^>]*href=["']([^"']+)["']/g)].map((m) => m[1]);
  for (const href of [...mdLinks, ...htmlLinks]) {
    if (href.startsWith('http://')) err(file, `use https for links: ${href}`);
    const m = /^\/course\/([^/]+)\/([^/#?]+)\/?/.exec(href);
    if (m) {
      const target = allSlugs.get(m[2]);
      if (!target) err(file, `internal link ${href} points to a lesson that does not exist`);
      else if (target.data && target.data.track !== m[1]) err(file, `internal link ${href}: lesson "${m[2]}" is in track "${target.data.track}"`);
    }
  }
  const linkCount = termTags.length + citeTags.length + mdLinks.length + htmlLinks.length;
  if (linkCount < MIN_LINKS) err(file, `needs >= ${MIN_LINKS} hyperlinks (Term + markdown links + Cite), found ${linkCount}`);

  // exercises
  if (d.exercises.length < MIN_EXERCISES) err(file, `needs >= ${MIN_EXERCISES} exercises (has ${d.exercises.length})`);
  const exIds = new Set(d.exercises.map((e) => e.id));
  for (const ex of d.exercises) {
    if (ex.type === 'mcq') {
      if (!ex.options || ex.options.length < 2) err(file, `exercise "${ex.id}": mcq needs >= 2 options`);
      else {
        const ok = typeof ex.answer === 'number' ? Number.isInteger(ex.answer) && ex.answer >= 0 && ex.answer < ex.options.length : ex.options.includes(ex.answer);
        if (!ok) err(file, `exercise "${ex.id}": answer must be a 0-based option index or the exact text of one option`);
      }
    }
    if (ex.type === 'numeric' && !Number.isFinite(Number(ex.answer))) err(file, `exercise "${ex.id}": numeric answer must be a number`);
    if (ex.type !== 'mcq' && ex.options) warn(file, `exercise "${ex.id}": options are only used by mcq`);
  }
  for (const t of tags(body, 'Exercise')) {
    const id = attrOf(t, 'id');
    if (!id) err(file, `<Exercise> without an id: ${t}`);
    else if (!exIds.has(id)) err(file, `<Exercise id="${id}"> is not defined in this lesson's frontmatter exercises`);
  }

  // analogies
  if ((d.level === 'beginner' || d.level === 'intermediate') && tags(body, 'Analogy').length < 1)
    err(file, `${d.level} lessons need at least one <Analogy> callout`);

  // math: display math must be presented step by step
  const msBlocks = [...body.matchAll(/<MathSteps\b[\s\S]*?<\/MathSteps>/g)].map((m) => m[0]);
  const withoutMs = body.replace(/<MathSteps\b[\s\S]*?<\/MathSteps>/g, '');
  const hasDisplayMath = /\$\$[\s\S]+?\$\$/.test(withoutMs) || /\\\[[\s\S]+?\\\]/.test(withoutMs) || /\\begin\{(equation|align|gather|aligned|cases|bmatrix|pmatrix)\*?\}/.test(withoutMs);
  if (hasDisplayMath && msBlocks.length === 0) err(file, 'has display math but no <MathSteps>: present derivations one step at a time');
  let stepsInside = 0;
  for (const block of msBlocks) {
    const steps = tags(block, 'Step');
    stepsInside += steps.length;
    if (!attrOf(block, 'title')) err(file, '<MathSteps> needs a title');
    if (steps.length < 2) err(file, `<MathSteps title="${attrOf(block, 'title') ?? ''}"> needs >= 2 <Step> elements (has ${steps.length})`);
    for (const s of steps) if (!attrOf(s, 'tex')) err(file, `<Step> without tex="...": ${s.slice(0, 80)}`);
    for (const s of steps) if (!attrOf(s, 'words') && /\/>\s*$/.test(s)) err(file, `<Step tex="${attrOf(s, 'tex')}"> needs words="..." or child text explaining it in words`);
  }
  if (tags(body, 'MathSteps').length !== msBlocks.length) err(file, '<MathSteps> must be closed with </MathSteps>');
  if (tags(body, 'Step').length !== stepsInside) err(file, '<Step> must be placed inside a <MathSteps> block');

  // prerequisites / see also
  for (const key of ['prerequisites', 'seeAlso']) {
    for (const s of d[key]) {
      if (s === d.slug) err(file, `${key} must not include the lesson itself`);
      else if (!allSlugs.has(s)) err(file, `${key}: lesson "${s}" does not exist`);
    }
  }

  // code files
  for (const t of tags(body, 'CodeFile')) {
    const p = attrOf(t, 'path');
    if (!p) {
      err(file, `<CodeFile> without a path: ${t}`);
      continue;
    }
    if (!/^code\//.test(p.replace(/^\.\//, ''))) err(file, `<CodeFile path="${p}"> must point inside code/`);
    const abs = path.join(ROOT, p);
    if (!fs.existsSync(abs) || !fs.statSync(abs).isFile()) {
      err(file, `<CodeFile path="${p}"> does not exist`);
      continue;
    }
    const n = fs.readFileSync(abs, 'utf8').replace(/\r\n/g, '\n').replace(/\n$/, '').split('\n').length;
    const lines = attrOf(t, 'lines');
    let lo = 1;
    let hi = n;
    if (lines) {
      const r = parseRange(lines);
      if (!r) err(file, `<CodeFile lines="${lines}"> must look like "10-40"`);
      else if (r[0] < 1 || r[1] > n || r[0] > r[1]) err(file, `<CodeFile path="${p}" lines="${lines}"> is outside the file (1-${n})`);
      else [lo, hi] = r;
    }
    const hl = attrOf(t, 'highlight');
    if (hl) for (const part of hl.split(',').map((s) => s.trim()).filter(Boolean)) {
      const [a, b] = part.split('-').map(Number);
      if (!Number.isInteger(a) || a < lo || (b || a) > hi) err(file, `<CodeFile path="${p}" highlight="${hl}"> must fall within lines ${lo}-${hi}`);
    }
  }

  // images
  for (const name of ['Figure', 'Screenshot']) {
    for (const t of tags(body, name)) {
      const src = attrOf(t, 'src');
      if (!src) err(file, `<${name}> without src`);
      else if (src.startsWith('/')) {
        if (!fs.existsSync(path.join(PUBLIC_DIR, src))) err(file, `<${name} src="${src}"> not found in public/`);
      } else if (!src.startsWith('https://')) err(file, `<${name} src="${src}"> must be a /public path or an https URL`);
      if (!attrOf(t, 'alt')) err(file, `<${name}> needs alt text`);
      if (!attrOf(t, 'caption')) err(file, `<${name}> needs a caption`);
    }
  }
  for (const m of body.matchAll(/!\[([^\]]*)\]\(([^)\s]+)/g)) {
    if (!m[1].trim()) err(file, `markdown image ${m[2]} needs alt text`);
    if (m[2].startsWith('/') && !fs.existsSync(path.join(PUBLIC_DIR, m[2]))) err(file, `image ${m[2]} not found in public/`);
  }

  // length
  const words = countWords(l.body);
  if (words < WORDS[0] || words > WORDS[1]) warn(file, `${words} words of prose; aim for ${WORDS[0]}-${WORDS[1]}`);
}

// ---------- report ----------
const scope = onlyTrack ? `track "${onlyTrack}"` : 'all tracks';
const group = (list) => {
  const by = new Map();
  for (const { file, msg } of list) {
    if (!by.has(file)) by.set(file, []);
    by.get(file).push(msg);
  }
  return by;
};
if (warnings.length) {
  console.log(`\nWarnings (${warnings.length}):`);
  for (const [file, msgs] of group(warnings)) {
    console.log(`  ${file}`);
    msgs.forEach((m) => console.log(`    ! ${m}`));
  }
}
if (errors.length) {
  console.error(`\nFailures (${errors.length}):`);
  for (const [file, msgs] of group(errors)) {
    console.error(`  ${file}`);
    msgs.forEach((m) => console.error(`    ✗ ${m}`));
  }
}
const summary = `${selected.length} lesson(s) and ${onlyTrack ? 0 : glossaryEntries.length} glossary entr${glossaryEntries.length === 1 ? 'y' : 'ies'} checked (${scope}${curriculumPairs ? ', with curriculum.json' : ', no curriculum.json yet'}): ${errors.length} failure(s), ${warnings.length} warning(s).`;
if (errors.length || (strict && warnings.length)) {
  console.error(`\n✗ ${summary}`);
  process.exit(1);
}
console.log(`\n✓ ${summary}`);
