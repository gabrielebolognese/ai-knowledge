/**
 * Structural checks for src/data/curriculum.json (used by scripts/validate-content.mjs,
 * and runnable on its own: `node scripts/lib/check-curriculum.mjs`).
 *
 * The curriculum is the map every content step writes against, so these rules keep it coherent:
 *  - all tracks from src/lib/schema.mjs are present, in course order, with modules and lessons
 *  - lesson entries: slug (kebab-case, unique), title, track = parent track, module = parent module title,
 *    level, order (strictly increasing within a track), minutes (10-30, bite-sized), 3-5 goals,
 *    planned exercises (count >= 2, one valid type per exercise), sources that resolve in sourceRegistry (https)
 *  - prerequisites resolve and are taught EARLIER in the course order
 *    (setup → beginner → intermediate → advanced → each project track; earlier in the same track counts too);
 *    no lesson outside setup depends on a setup lesson (setup is optional); no project depends on another project
 *  - project tracks: codeDir, codeFiles inside it, quickStart (non-project lessons that cover every direct
 *    non-project prerequisite of the track), recommendedPath (track ids or lesson slugs, ending with the track)
 *  - certificateRequirement: all of beginner/intermediate/advanced plus at least one project track; setup not required
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const SLUG = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
export const MINUTES = [10, 30];
export const GOALS = [3, 5];
const CORE = ['setup', 'beginner', 'intermediate', 'advanced'];

/** Flatten a curriculum into lesson entries, normalising string entries to { slug }. */
export function curriculumEntries(cur) {
  const out = [];
  for (const t of cur?.tracks ?? []) {
    const mods = t.modules ?? [{ title: t.title, lessons: t.lessons ?? [] }];
    for (const m of mods) {
      for (const item of m.lessons ?? []) {
        const e = typeof item === 'string' ? { slug: item } : item ?? {};
        out.push({ ...e, slug: e.slug, _track: t.id, _module: m.title });
      }
    }
  }
  return out;
}

/**
 * @param {any} cur parsed curriculum.json
 * @param {{ TRACKS: readonly string[], LEVELS: readonly string[], EXERCISE_TYPES: readonly string[], root?: string }} opts
 * @returns {{ errors: string[], warnings: string[], entries: any[] }}
 */
export function checkCurriculum(cur, { TRACKS, LEVELS, EXERCISE_TYPES, root }) {
  const errors = [];
  const warnings = [];
  const E = (m) => errors.push(m);
  const W = (m) => warnings.push(m);

  if (!cur || !Array.isArray(cur.tracks)) {
    E('curriculum.json must have a "tracks" array');
    return { errors, warnings, entries: [] };
  }

  // ---- tracks
  const trackIds = cur.tracks.map((t) => t.id);
  for (const id of trackIds) if (!TRACKS.includes(id)) E(`unknown track id "${id}"`);
  for (const id of TRACKS) if (!trackIds.includes(id)) E(`track "${id}" is missing`);
  const dupTracks = trackIds.filter((id, i) => trackIds.indexOf(id) !== i);
  for (const id of new Set(dupTracks)) E(`track "${id}" appears more than once`);
  const known = trackIds.filter((id) => TRACKS.includes(id));
  if (known.join() !== TRACKS.filter((id) => known.includes(id)).join()) E(`tracks must be in course order: ${TRACKS.join(', ')}`);

  const registry = cur.sourceRegistry ?? {};
  for (const [id, s] of Object.entries(registry)) {
    if (!s || typeof s.url !== 'string' || !/^https:\/\/\S+$/.test(s.url)) E(`sourceRegistry "${id}" needs an https url`);
    if (!s?.title) E(`sourceRegistry "${id}" needs a title`);
  }

  // ---- lessons: build the global course order first
  const entries = curriculumEntries(cur);
  const rank = new Map(); // slug -> global position
  const bySlug = new Map();
  entries.forEach((e, i) => {
    if (!e.slug) return;
    if (bySlug.has(e.slug)) E(`slug "${e.slug}" is listed more than once`);
    else {
      bySlug.set(e.slug, e);
      rank.set(e.slug, i);
    }
  });

  for (const t of cur.tracks) {
    const where = `track "${t.id}"`;
    if (!t.title) E(`${where} needs a title`);
    if (!t.blurb) W(`${where} has no blurb`);
    if (!Array.isArray(t.modules) || !t.modules.length) E(`${where} needs a non-empty "modules" array`);
    const isProject = String(t.id).startsWith('project-');
    if (t.kind && t.kind !== (isProject ? 'project' : 'core')) E(`${where}: kind must be "${isProject ? 'project' : 'core'}"`);
    if (t.id === 'setup' && t.optional !== true) E('track "setup" must be marked "optional": true');
    let lastOrder = -Infinity;
    const moduleIds = new Set();
    for (const m of t.modules ?? []) {
      if (!m.title) E(`${where} has a module without a title`);
      if (m.id) {
        if (moduleIds.has(m.id)) E(`${where}: duplicate module id "${m.id}"`);
        moduleIds.add(m.id);
      }
      if (!Array.isArray(m.lessons) || !m.lessons.length) E(`${where}, module "${m.title}" has no lessons`);
      for (const item of m.lessons ?? []) {
        if (typeof item === 'string') continue; // legacy short form: slug only
        const l = item ?? {};
        const at = `lesson "${l.slug ?? '?'}"`;
        if (!l.slug) {
          E(`${where} has a lesson entry without a slug`);
          continue;
        }
        if (!SLUG.test(l.slug)) E(`${at}: slug must be lowercase-kebab-case`);
        if (!l.title) E(`${at}: missing title`);
        if (l.track !== undefined && l.track !== t.id) E(`${at}: track "${l.track}" does not match its parent track "${t.id}"`);
        if (l.module !== undefined && l.module !== m.title) E(`${at}: module "${l.module}" does not match its parent module "${m.title}"`);
        if (l.level !== undefined && !LEVELS.includes(l.level)) E(`${at}: level must be one of ${LEVELS.join(', ')}`);
        if (l.order !== undefined) {
          if (typeof l.order !== 'number' || l.order <= lastOrder) E(`${at}: order must increase within the track (got ${l.order} after ${lastOrder})`);
          lastOrder = l.order;
        }
        if (l.minutes !== undefined && !(Number.isInteger(l.minutes) && l.minutes >= MINUTES[0] && l.minutes <= MINUTES[1]))
          E(`${at}: minutes must be an integer in ${MINUTES[0]}-${MINUTES[1]} (bite-sized), got ${l.minutes}`);
        if (l.goals !== undefined && (!Array.isArray(l.goals) || l.goals.length < GOALS[0] || l.goals.length > GOALS[1]))
          E(`${at}: needs ${GOALS[0]}-${GOALS[1]} learning goals`);
        if (l.exercises !== undefined) {
          const x = l.exercises;
          if (!Number.isInteger(x?.count) || x.count < 2) E(`${at}: plan at least 2 exercises`);
          if (!Array.isArray(x?.types) || x.types.length !== x.count) E(`${at}: exercises.types needs one type per planned exercise`);
          for (const ty of x?.types ?? []) if (!EXERCISE_TYPES.includes(ty)) E(`${at}: unknown exercise type "${ty}" (use ${EXERCISE_TYPES.join(', ')})`);
        }
        for (const s of l.sources ?? []) {
          const id = typeof s === 'string' ? s : s?.id;
          const reg = registry[id];
          if (!reg) E(`${at}: source "${id}" is not in sourceRegistry`);
          else if (typeof s === 'object' && s.url && s.url !== reg.url) E(`${at}: source "${id}" url differs from sourceRegistry`);
        }
        if (l.sources !== undefined && (l.sources?.length ?? 0) < 3) E(`${at}: list at least 3 key sources`);

        // prerequisites
        for (const p of l.prerequisites ?? []) {
          const pe = bySlug.get(p);
          if (p === l.slug) E(`${at}: lists itself as a prerequisite`);
          else if (!pe) E(`${at}: prerequisite "${p}" is not in the curriculum`);
          else {
            if (rank.get(p) >= rank.get(l.slug)) E(`${at}: prerequisite "${p}" must be taught earlier in the course order`);
            if (pe._track === 'setup' && t.id !== 'setup') E(`${at}: depends on setup lesson "${p}", but setup is optional (use "needs" instead)`);
            if (String(pe._track).startsWith('project-') && pe._track !== t.id) E(`${at}: depends on another project's lesson "${p}"; project tracks must stay independent`);
          }
        }

        // code files
        for (const f of l.codeFiles ?? []) {
          if (!/^code\//.test(f)) E(`${at}: code file "${f}" must live under code/`);
          if (isProject && t.codeDir && !f.startsWith(t.codeDir)) E(`${at}: code file "${f}" must live under the track's codeDir ${t.codeDir}`);
        }
        if (isProject && !(l.codeFiles ?? []).length) E(`${at}: project lessons must list the code files they show (codeFiles)`);
      }
    }

    // project-only fields
    if (isProject) {
      if (!t.codeDir || !/^code\/projects\/[a-z0-9-]+\/$/.test(t.codeDir)) E(`${where}: codeDir must look like "code/projects/<name>/"`);
      const qs = t.quickStart;
      if (!Array.isArray(qs) || !qs.length) E(`${where}: needs a non-empty quickStart list`);
      for (const s of qs ?? []) {
        const e = bySlug.get(s);
        if (!e) E(`${where}: quickStart lesson "${s}" is not in the curriculum`);
        else if (!CORE.includes(e._track) || e._track === 'setup') E(`${where}: quickStart lesson "${s}" must come from beginner, intermediate or advanced`);
      }
      const own = entries.filter((e) => e._track === t.id);
      const needed = new Set(own.flatMap((e) => e.prerequisites ?? []).filter((p) => bySlug.get(p) && bySlug.get(p)._track !== t.id));
      for (const p of needed) if (!(qs ?? []).includes(p)) E(`${where}: quickStart must include "${p}" (a direct prerequisite of one of its lessons)`);
      const rp = t.recommendedPath;
      if (!Array.isArray(rp) || !rp.length) E(`${where}: needs a recommendedPath`);
      else {
        for (const s of rp) if (!TRACKS.includes(s) && !bySlug.has(s)) E(`${where}: recommendedPath item "${s}" is neither a track id nor a lesson slug`);
        if (rp[rp.length - 1] !== t.id) E(`${where}: recommendedPath must end with "${t.id}"`);
      }
    }
  }

  // ---- certificate requirement
  const cr = cur.certificateRequirement;
  if (!cr) E('missing certificateRequirement');
  else {
    const all = cr.allLessonsInTracks ?? [];
    for (const id of ['beginner', 'intermediate', 'advanced']) if (!all.includes(id)) E(`certificateRequirement.allLessonsInTracks must include "${id}"`);
    if (all.includes('setup') || cr.setupRequired) E('certificateRequirement must not require the optional setup track');
    const projects = TRACKS.filter((id) => id.startsWith('project-'));
    for (const id of projects) if (!(cr.projectTracks ?? []).includes(id)) E(`certificateRequirement.projectTracks must include "${id}"`);
    if (!(Number.isInteger(cr.minProjectTracksCompleted) && cr.minProjectTracksCompleted >= 1)) E('certificateRequirement.minProjectTracksCompleted must be >= 1');
  }

  // ---- skip paths (optional)
  for (const sp of cur.skipPaths ?? []) {
    const at = `skipPaths "${sp.id ?? '?'}"`;
    if (!sp.id || !sp.label) E(`${at} needs an id and a label`);
    for (const id of sp.skipTracks ?? []) {
      if (!TRACKS.includes(id)) E(`${at}: unknown track "${id}"`);
      else if (id.startsWith('project-')) E(`${at}: project tracks are never skipped, they are chosen`);
    }
    for (const s of sp.skipLessons ?? []) if (!bySlug.has(s)) E(`${at}: lesson "${s}" is not in the curriculum`);
    if (sp.startAt !== 'quickStart' && !bySlug.has(sp.startAt)) E(`${at}: startAt must be a lesson slug or "quickStart"`);
    else if (bySlug.has(sp.startAt)) {
      const start = bySlug.get(sp.startAt);
      if ((sp.skipTracks ?? []).includes(start._track) || (sp.skipLessons ?? []).includes(sp.startAt)) E(`${at}: startAt "${sp.startAt}" is itself skipped`);
    }
  }

  // ---- environment help (optional)
  for (const [k, list] of Object.entries(cur.environmentHelp ?? {})) {
    for (const s of list) if (!bySlug.has(s)) E(`environmentHelp.${k}: lesson "${s}" is not in the curriculum`);
  }
  for (const e of entries) for (const n of e.needs ?? []) if (cur.environmentHelp && !cur.environmentHelp[n]) W(`lesson "${e.slug}": needs "${n}" has no environmentHelp entry`);

  // Code files are written by later steps, so their existence is checked per lesson (<CodeFile>) and by the
  // validator's --complete mode, not here.
  void root;

  return { errors, warnings, entries };
}

// ---- CLI
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
  const { TRACKS, LEVELS, EXERCISE_TYPES } = await import('../../src/lib/schema.mjs');
  const cur = JSON.parse(fs.readFileSync(path.join(root, 'src/data/curriculum.json'), 'utf8'));
  const { errors, warnings, entries } = checkCurriculum(cur, { TRACKS, LEVELS, EXERCISE_TYPES, root });
  warnings.forEach((w) => console.log(`  ! ${w}`));
  errors.forEach((e) => console.error(`  ✗ ${e}`));
  const mins = entries.reduce((a, e) => a + (e.minutes ?? 0), 0);
  const msg = `${entries.length} lessons in ${cur.tracks.length} tracks, ${Math.round(mins / 6) / 10} h: ${errors.length} error(s), ${warnings.length} warning(s)`;
  if (errors.length) {
    console.error(`✗ ${msg}`);
    process.exit(1);
  }
  console.log(`✓ ${msg}`);
}
