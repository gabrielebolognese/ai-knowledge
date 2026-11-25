/**
 * Declarative bindings between the DOM and the progress store, loaded on every page.
 * Any page or component can use these data attributes without writing JS:
 *
 *   [data-lesson-toggle="<slug>"]        button: toggles lesson completion (aria-pressed reflects it)
 *   [data-lesson-status="<slug>"]        element: gets data-done="true|false"
 *   [data-bulk-toggle="a,b,c"]           button: marks all listed lessons complete, or unmarks them all
 *                                         when every one is already done (module / track "mark all");
 *                                         optional data-bulk-name="Module title" for the toast
 *   [data-exercise-toggle="<id>"]        checkbox or button: toggles an exercise "done" mark
 *   [data-exercise-status="<id>"]        element: gets data-done
 *   [data-progress-slugs="a,b,c"]        element: gets data-done-count, data-total, --pct; children
 *                                         [data-progress-text] receive "n / N" and [data-progress-pct] "42%"
 *   [data-progress-ring]                 (same element) SVG ring circle .ring-value gets its dashoffset
 *   [data-progress-name]                 input: two-way bound to the certificate name
 *   [data-last-visited='{"slug":..}']    element: records the visit on load
 */
import {
  subscribe,
  toggleLesson,
  setLessons,
  toggleExercise,
  setExercise,
  setName,
  setLastVisited,
  type ProgressState,
} from '../lib/progress';
import { showToast } from '../lib/toast';

function render(state: ProgressState) {
  document.querySelectorAll<HTMLElement>('[data-lesson-toggle]').forEach((el) => {
    const done = !!state.lessons[el.dataset.lessonToggle!]?.done;
    el.setAttribute('aria-pressed', String(done));
    el.dataset.done = String(done);
    const label = el.querySelector<HTMLElement>('[data-label]');
    if (label) label.textContent = done ? el.dataset.labelDone || 'Completed · Undo' : el.dataset.labelTodo || 'Mark lesson complete';
  });
  document.querySelectorAll<HTMLElement>('[data-bulk-toggle]').forEach((el) => {
    const slugs = bulkSlugs(el);
    const done = slugs.length > 0 && slugs.every((s) => state.lessons[s]?.done);
    el.setAttribute('aria-pressed', String(done));
    el.dataset.done = String(done);
    const label = el.querySelector<HTMLElement>('[data-label]');
    if (label) label.textContent = done ? el.dataset.labelDone || 'Unmark all' : el.dataset.labelTodo || 'Mark all complete';
  });
  document.querySelectorAll<HTMLElement>('[data-lesson-status]').forEach((el) => {
    el.dataset.done = String(!!state.lessons[el.dataset.lessonStatus!]?.done);
  });
  document.querySelectorAll<HTMLElement>('[data-exercise-status]').forEach((el) => {
    el.dataset.done = String(!!state.exercises[el.dataset.exerciseStatus!]?.done);
  });
  document.querySelectorAll<HTMLElement>('[data-exercise-toggle]').forEach((el) => {
    const done = !!state.exercises[el.dataset.exerciseToggle!]?.done;
    if (el instanceof HTMLInputElement) el.checked = done;
    else el.setAttribute('aria-pressed', String(done));
  });
  document.querySelectorAll<HTMLElement>('[data-progress-slugs]').forEach((el) => {
    const slugs = el.dataset.progressSlugs!.split(',').filter(Boolean);
    const done = slugs.filter((s) => state.lessons[s]?.done).length;
    const pct = slugs.length ? Math.round((done / slugs.length) * 100) : 0;
    el.dataset.doneCount = String(done);
    el.dataset.total = String(slugs.length);
    el.dataset.complete = String(slugs.length > 0 && done === slugs.length);
    el.style.setProperty('--pct', String(pct));
    if (el.getAttribute('role') === 'meter' || el.getAttribute('role') === 'progressbar') el.setAttribute('aria-valuenow', String(pct));
    el.querySelectorAll<HTMLElement>('[data-progress-text]').forEach((t) => (t.textContent = `${done} / ${slugs.length}`));
    el.querySelectorAll<HTMLElement>('[data-progress-pct]').forEach((t) => (t.textContent = `${pct}%`));
    el.querySelectorAll<SVGCircleElement>('circle.ring-value').forEach((c) => {
      const r = Number(c.getAttribute('r'));
      const len = 2 * Math.PI * r;
      c.style.strokeDasharray = String(len);
      c.style.strokeDashoffset = String(len * (1 - pct / 100));
    });
  });
  document.querySelectorAll<HTMLInputElement>('input[data-progress-name]').forEach((el) => {
    if (document.activeElement !== el) el.value = state.name;
  });
}

function bulkSlugs(el: HTMLElement) {
  return (el.dataset.bulkToggle || '').split(',').filter(Boolean);
}

function onBulkToggle(el: HTMLElement) {
  const slugs = bulkSlugs(el);
  if (!slugs.length) return;
  const allDone = el.dataset.done === 'true';
  setLessons(slugs, !allDone);
  const name = el.dataset.bulkName || 'Group';
  const msg = allDone ? `${name}: ${slugs.length} lessons marked not complete` : `${name} complete: ${slugs.length} lessons marked done`;
  showToast(msg);
  document.getElementById('progress-live')?.replaceChildren(msg);
}

function onLessonToggle(el: HTMLElement) {
  const slug = el.dataset.lessonToggle!;
  const done = toggleLesson(slug);
  showToast(done ? 'Marked complete · saved in this browser' : 'Marked as not complete');
  document.getElementById('progress-live')?.replaceChildren(done ? 'Lesson marked complete.' : 'Lesson marked not complete.');
}

document.addEventListener('click', (e) => {
  const target = e.target as HTMLElement;
  const bulk = target.closest<HTMLElement>('[data-bulk-toggle]');
  if (bulk) {
    e.preventDefault();
    onBulkToggle(bulk);
    return;
  }
  const lesson = target.closest<HTMLElement>('[data-lesson-toggle]');
  if (lesson) {
    e.preventDefault();
    onLessonToggle(lesson);
    return;
  }
  const ex = target.closest<HTMLElement>('[data-exercise-toggle]');
  if (ex && !(ex instanceof HTMLInputElement)) {
    e.preventDefault();
    toggleExercise(ex.dataset.exerciseToggle!);
  }
});

document.addEventListener('change', (e) => {
  const el = e.target as HTMLElement;
  if (el instanceof HTMLInputElement && el.dataset.exerciseToggle) setExercise(el.dataset.exerciseToggle, el.checked);
});

document.addEventListener('input', (e) => {
  const el = e.target as HTMLElement;
  if (el instanceof HTMLInputElement && 'progressName' in el.dataset) setName(el.value);
});

// Global shortcut: M toggles the page's primary lesson (the first toggle marked data-primary).
document.addEventListener('keydown', (e) => {
  if (e.key !== 'm' && e.key !== 'M') return;
  if (e.ctrlKey || e.metaKey || e.altKey) return;
  const t = e.target as HTMLElement;
  if (t.closest('input, textarea, select, [contenteditable="true"]')) return;
  const primary = document.querySelector<HTMLElement>('[data-lesson-toggle][data-primary]');
  if (primary) {
    e.preventDefault();
    onLessonToggle(primary);
  }
});

const visit = document.querySelector<HTMLElement>('[data-last-visited]');
if (visit) {
  try {
    setLastVisited(JSON.parse(visit.dataset.lastVisited!));
  } catch {
    /* ignore malformed */
  }
}

subscribe(render);

// Hydration marker: the bindings above are live (used by tests and safe to ignore otherwise).
document.documentElement.dataset.progressReady = 'true';
