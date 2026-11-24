# Authoring guide

This guide is the contract for everyone who writes lessons, glossary entries or companion code for **AI Knowledge**. The validator (`npm run validate`, or `node scripts/validate-content.mjs --track <id>`) enforces the rules marked **(checked)**; reviewers enforce the rest. The two sample lessons, [`beginner/artificial-neuron.mdx`](../src/content/lessons/beginner/artificial-neuron.mdx) and [`beginner/gradient-descent.mdx`](../src/content/lessons/beginner/gradient-descent.mdx), follow every rule and are the best templates to copy.

Design background: [`research/05-ux-design-brief.md`](../research/05-ux-design-brief.md) (§1.2 Wikipedia conventions, §4 components, §9 voice).

---

## 1. Tone and length

- **Wikipedia-style, neutral and encyclopaedic.** State facts and attribute them. No hype ("amazing", "super easy"), no second-person cheerleading, no jokes in the main text. Analogies, tips and warnings live in their own callouts so the article text stays clean.
- **Summarised and easy to read.** Short paragraphs (2-4 sentences), one idea per paragraph, plain words first and the technical term right after ("the step size, called the *learning rate*").
- **800-1800 words of prose per lesson** (code, math blocks and frontmatter don't count). The validator warns outside this range. Split a lesson that runs longer.
- **Link generously, but not to every repeat.** Link the first mention of a term in each section, either to the glossary with `<Term>` or to an authoritative source. Do not link common words.
- **Original wording with citations.** Never paste text from a source. Read, close the tab, write it in your own words, then cite. Short quotations are allowed only in quotation marks with a citation.
- **Sentence-case noun-phrase titles**: "Gradient descent", not "How To Understand Gradient Descent!".
- Use British or American spelling consistently within a lesson.
- **Be honest about limits.** Say when a claim is a rule of thumb, when results vary, and where an analogy stops being true.

## 2. Files and frontmatter

Lessons are MDX files at `src/content/lessons/<track>/<slug>.mdx`. The folder must equal `track` and the file name must equal `slug` **(checked)**. Slugs are lowercase-kebab-case and unique across the whole site **(checked)**. Files that start with `_` are ignored (use them for drafts).

Tracks: `setup`, `beginner`, `intermediate`, `advanced`, `project-digits-letters`, `project-doodles`, `project-text`, `project-code-autocomplete`, `project-chess`.

The schema lives in [`src/lib/schema.mjs`](../src/lib/schema.mjs). The site build and the validator both use it, so a lesson that validates also builds.

```yaml
---
title: Gradient descent              # sentence case, at most 90 characters
slug: gradient-descent               # = file name
track: beginner                      # = folder
level: beginner                      # beginner | intermediate | advanced
order: 20                            # sort order inside the track (curriculum.json wins when present)
minutes: 14                          # honest reading + exercise time
summary: One or two sentences, at most 300 characters, used on cards and in search.
module: Neural networks from scratch # optional: groups lessons in the outline
hatnote: For X, see "Y".             # optional italic pointer to a related/deeper page
prerequisites: [artificial-neuron]   # slugs that must exist (checked); advice, never a lock
tools: [Python 3]                    # optional, shown in the infobox
outcomes: [Explain what a gradient tells you]   # optional "You will learn" (max 4 shown)
build: A five-step gradient descent in plain Python   # optional "You will build"
reviewed: 2026-11-24                 # optional "Last reviewed"
seeAlso: [artificial-neuron]         # slugs that must exist (checked)
sources:                             # at least 3 (checked)
  - id: d2l-gd                       # short token, unique in the lesson
    title: "Dive into Deep Learning, 12.3 Gradient Descent"
    author: Aston Zhang, Zachary Lipton, Mu Li, Alexander Smola   # author or publisher required
    publisher: d2l.ai
    year: 2023                       # optional
    url: https://d2l.ai/chapter_optimization/gd.html   # https only (checked)
    accessed: 2026-11-24             # YYYY-MM-DD
    type: book                       # optional: paper|docs|book|video|dataset|wikipedia|article|course|code
furtherReading:                      # optional, un-numbered, https only
  - title: "3Blue1Brown: Gradient descent"
    url: https://www.3blue1brown.com/lessons/gradient-descent
exercises:                           # at least 2 (checked); ids unique site-wide (checked)
  - id: gd-one-step
    type: numeric                    # mcq | numeric | short | reveal
    difficulty: easy                 # easy | medium | hard
    title: One update by hand        # optional
    prompt: "Start at $w = 1$ with $\\eta = 0.25$. What is $w$ after one step?"
    answer: 2                        # see "Exercises" below
    tolerance: 0.001                 # numeric only; default 0.5% of the answer
    hint: Optional nudge shown after a wrong answer.
    explanation: Why the answer is right (shown with the answer).
---
```

YAML tip: inside double quotes a backslash must be doubled (`"$\\eta$"`). In unquoted or single-quoted values write it once (`$\eta$`).

## 3. Article structure (the Wikipedia layout)

The layout generates the breadcrumb, title, level badge, infobox, track outline, "On this page", Exercises, Mark complete, See also, References, Further reading and previous/next links from frontmatter. You write only the body:

1. **Lead** (2-4 sentences, no heading). Define the topic in plain words, then say why it matters. Bold only the lesson's own term on first use. The body must open with this paragraph **(checked)**.
2. **Sections** with `##` and `###` only. Never `#`, which is reserved for the title **(checked)**; `####` and deeper trigger a warning.
3. For math topics, follow this order: intuition (analogy), then a tiny numeric example, then symbols one at a time (`<MathSteps>`), then the general formula, then code that computes the same thing.
4. A **Try it** section with a `<CodeFile>` from `code/` whenever there is runnable code.
5. A **Summary** section with 3-5 bullets.
6. Do not write "References", "Exercises" or "See also" headings yourself: the layout adds them.

## 4. Citations (sourced by construction)

- Every statistic, date, definition from outside, install step and claim about a tool or paper gets a `<Cite id="..." />` right after the punctuation it supports: `…first suggested it in 1847.<Cite id="wiki-gd" />`. On average there is at least one citation per factual paragraph.
- Each `<Cite id>` must match a frontmatter source **(checked)**, and every source must be cited at least once **(checked)**. A source you only recommend belongs in `furtherReading`.
- Numbers are assigned by first use, Wikipedia-style. Citing the same source again reuses its number and adds an a/b/c back-link.
- Prefer primary sources (papers, official docs, textbooks). Wikipedia is fine for definitions and history. Never ship a "citation needed".
- Optional page or section: `<Cite id="goodfellow-ch6" page="§6.4" />`.

## 5. Links

- At least **8 hyperlinks** per lesson, counting `<Term>`, `<Cite>`, markdown links and `<a href>` **(checked)**.
- External links use https **(checked)**. Internal lesson links use `/course/<track>/<slug>/` and must resolve **(checked)**.
- Setup lessons give the *exact* download/documentation URL as a visible link ("Open [python.org/downloads](https://www.python.org/downloads/)").

## 6. Components (available in every lesson without imports)

| Component | Use | Example |
|---|---|---|
| `<Term slug>` | Glossary wiki-link with a hover card. The glossary file must exist **(checked)**. | `<Term slug="learning-rate" />` or `<Term slug="weight">weights</Term>` |
| `<Cite id>` | Numbered footnote linking to References. | `<Cite id="d2l-gd" />` |
| `<Analogy breaks="...">` | Everyday analogy, placed after the formal statement. At most 2 sentences; `breaks` says where it stops being true. **Required (at least one) in beginner and intermediate lessons (checked).** | see samples |
| `<MathSteps title legend>` + `<Step tex words example>` | Reveals a derivation one step at a time. Use `\hl{...}` to highlight the new term in each step. **Every lesson with display math must use it; each block needs 2 or more Steps with `tex` and an in-words explanation (checked).** | see samples |
| `<Callout type>` | `tip`, `warning`, `note` or `pitfall` (common mistake). | `<Callout type="tip">…</Callout>` |
| `<Infobox title rows>` | Extra fact table (for example dataset facts) floating right. The lesson infobox is automatic. | `<Infobox title="MNIST" rows={[{ label: 'Images', value: '70,000' }]} />` |
| `<Figure src alt caption credit license licenseUrl sourceUrl>` | Numbered figure with a credit line. Local files go in `public/` **(checked)**; alt text and caption are required **(checked)**. | `<Figure src="/figures/x.svg" alt="…" caption="…" credit="Own work" license="CC BY 4.0" />` |
| `<Screenshot src alt caption source taken pins>` | Setup-track screenshot with numbered pins (`x`/`y` in % of the image) and the same steps as a list underneath. | `pins={[{ x: 22, y: 41, label: 'Click **Download**' }]}` |
| `<Exercise id>` | Places a frontmatter exercise inline ("check yourself"). The id must exist in this lesson **(checked)**. Exercises not placed inline appear in the Exercises section automatically. | `<Exercise id="gd-one-step" />` |
| `<CodeFile path lines highlight title>` | Shows a file from `code/` with highlighting, Copy and a GitHub link. The path must exist and the ranges must fit **(checked)**. `highlight` uses the file's own line numbers. | `<CodeFile path="code/samples/neuron.py" lines="9-26" highlight="11" />` |

Inline math uses `$...$`. Display math (`$$...$$`) is allowed only alongside `<MathSteps>`; prefer putting the formula inside a Step. In MDX, `{`, `}` and `<` in prose start JSX: write them inside math, inline code, or escape them.

## 7. Exercises

- At least **2 per lesson** **(checked)**, mixing types where possible, ordered from easy to hard.
- `mcq`: `options` (2 or more) plus `answer` as the 0-based index or the exact option text **(checked)**. One clearly right answer and plausible wrong ones built from real misconceptions.
- `numeric`: `answer` is a number **(checked)**; set `tolerance` for rounded answers.
- `short`: the learner writes an answer for themselves, then reveals the model answer. `answer` may be a string or a list of acceptable answers.
- `reveal`: a "think it through" question with a model answer.
- Always write an `explanation` that teaches. A bare "B is correct" is not enough. Prompts, options, hints and explanations support `**bold**`, `` `code` ``, `[links](https://…)` and `$math$`.
- Self-check only: nothing is graded and answers are always available. Learners tick **Done** to track practice (stored locally).

## 8. Glossary entries

`src/content/glossary/<term>.md`:

```yaml
---
term: Learning rate
short: >-
  One or two sentences (10-320 characters) shown in hover cards.
level: beginner           # optional
aliases: [step size]      # optional
related: [gradient-descent]   # glossary slugs that must exist (checked)
sources:                  # at least 1, https (checked)
  - id: wikipedia
    title: Learning rate
    publisher: Wikipedia
    url: https://en.wikipedia.org/wiki/Learning_rate
    accessed: 2026-11-24
---
Optional longer explanation in Markdown.
```

## 9. Companion code

- Code lives in `code/<project>/` (for example `code/digits/train.py`) and is shown with `<CodeFile>`, so lesson code and runnable code never drift apart.
- Datasets are downloaded at run time and never committed (see `.gitignore`); cite the dataset paper and state its terms in the lesson.
- Every script prints something a learner can compare with the lesson ("expected accuracy 97-98%").

## 10. Progress and the UI contract

Progress lives only in the browser's `localStorage`, under the key `aik-progress-v1` ([`src/lib/progress.ts`](../src/lib/progress.ts)):

```json
{ "version": 1,
  "lessons":   { "<slug>": { "done": true, "at": "2026-11-24T10:00:00.000Z" } },
  "exercises": { "<id>":   { "done": true, "at": "…" } },
  "name": "Name for the certificate",
  "lastVisited": { "slug": "…", "track": "…", "title": "…", "at": "…" } }
```

The API is `getState`, `subscribe`, `toggleLesson`, `setLesson`, `setLessons` (bulk), `toggleExercise`, `setExercise`, `setExercises`, `setName`, `setLastVisited`, `exportJSON`, `importJSON(text, 'replace' | 'merge')`, `reset` and `registerMigration(fromVersion, fn)`. Pages can bind without writing JS by using the data attributes documented in [`src/scripts/progress-ui.ts`](../src/scripts/progress-ui.ts) (`data-lesson-toggle`, `data-lesson-status`, `data-exercise-toggle`, `data-progress-slugs`, `data-progress-name`).

## 11. Curriculum file

`src/data/curriculum.json` is the course map: 9 tracks, their modules and every planned lesson. **Write lessons against it.** The reasoning behind it is in `research/curriculum-rationale.md`. `src/lib/course.ts` builds the outline, the prev/next links and the track titles/blurbs from it. The validator checks its structure through `scripts/lib/check-curriculum.mjs`, which you can also run on its own: `node scripts/lib/check-curriculum.mjs` **(checked)**.

Shape (abridged):

```json
{ "version": 1,
  "environmentHelp": { "torch": ["setup-install-pytorch", "setup-colab"] },
  "certificateRequirement": { "allLessonsInTracks": ["beginner", "intermediate", "advanced"],
    "projectTracks": ["project-digits-letters", "…"], "minProjectTracksCompleted": 1, "setupRequired": false },
  "tracks": [
    { "id": "project-chess", "title": "Mini chess engine", "kind": "project", "level": "advanced", "blurb": "…",
      "codeDir": "code/projects/chess/",
      "quickStart": ["python-for-ml", "game-tree-search", "…"],
      "recommendedPath": ["beginner", "intermediate", "game-tree-search", "project-chess"],
      "modules": [ { "id": "chess-classic", "title": "The classic engine", "lessons": [
        { "slug": "chess-board-moves", "title": "…", "track": "project-chess", "module": "The classic engine",
          "level": "intermediate", "order": 10, "minutes": 20,
          "goals": ["3 to 5 learning goals"], "prerequisites": ["python-for-ml"], "needs": ["chess"],
          "covers": "what the lesson must contain", "sources": [{ "id": "python-chess-core", "url": "https://…" }],
          "research": "03 a1, b1 (M1)", "exercises": { "count": 3, "types": ["numeric", "mcq", "short"] },
          "codeFiles": ["code/projects/chess/perft.py"], "screenshots": ["SS-W01"] } ] } ] } ],
  "sourceRegistry": { "python-chess-core": { "title": "…", "url": "https://…", "publisher": "…", "research": "03 b1" } } }
```

Rules for lesson writers:
- Use the entry's `slug`, `track`, `level` and `module` in the frontmatter. Put its `goals` into `outcomes` and its `prerequisites` into `prerequisites`. The validator warns when the level, module or prerequisites drift from the curriculum. If you change a title or goals, update the curriculum in the same commit.
- `sources` lists the **key** sources (ids in `sourceRegistry`, URLs from the research files). Copy them into the frontmatter with `accessed` dates, cite each one in the text, and add more if you need them.
- `research` points to the section of `research/0X-*.md` that holds the distilled facts, the math micro-steps and the analogies.
- `exercises` is the plan: at least that many exercises, of those types.
- `codeFiles` (project lessons, some core lessons) are the companion files the lesson shows with `<CodeFile>`. Project code lives in the track's `codeDir`.
- `screenshots` (setup lessons) are IDs from `research/04-setup.md` §8.
- `skipPaths` (top level) drive the dashboard's skip chips (Skip setup, I know Python, I know the math, Start at Intermediate, Go straight to a project). Skipping never marks lessons complete; see `skipPolicy`.
- `needs` names the software a lesson uses. Setup is optional, so **no lesson outside setup lists a setup lesson as a prerequisite**. Point to `environmentHelp` instead.

Rules the checker enforces: all 9 tracks in order; unique kebab-case slugs; 10–30 minutes per lesson; 3–5 goals; at least 2 planned exercises of schema types; at least 3 key sources that resolve in `sourceRegistry`; prerequisites that exist and come **earlier** in the course order (setup → beginner → intermediate → advanced → each project); no project lesson depends on another project; every project lists `codeFiles` under its `codeDir`; `quickStart` contains every direct non-project prerequisite of the track's lessons; `recommendedPath` ends with the track; the certificate needs all of beginner, intermediate and advanced plus at least one project, and never setup.

Planned lessons that are not written yet are reported as "planned", not as failures. `node scripts/validate-content.mjs --complete` (optionally with `--track <id>`) makes every curriculum lesson and its planned `codeFiles` mandatory. Use it when a track is finished, and in final QA. Lessons that exist but are missing from the curriculum produce a warning. The short form `"lessons": ["slug"]` is still accepted.

## 12. Before you commit

```bash
npm run validate -- --track <your-track>   # 0 failures
npm run build                              # site + search index
npx playwright test                        # smoke tests
```
