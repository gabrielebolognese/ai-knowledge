# AI Knowledge

**A free, read-only deep learning course, from installing Python to a neural-network chess engine.**

AI Knowledge is a static website, meant for desktop, that teaches deep learning from zero. Lessons are
written in a Wikipedia style: short, neutral, and every claim links to its source. Math is shown one
step at a time, and beginner lessons explain each idea with an analogy (and say where the analogy stops
working). Six project tracks end in real, runnable models, and finishing the course unlocks a
certificate you can download with your name on it.

There is no account, no database and no payment. Your progress is saved in your own browser
(`localStorage`).

| | |
|---|---|
| Lessons | 79 in 9 tracks (about 29 hours including setup) |
| Exercises | 274 self-check exercises (quiz, numeric, short answer, think-it-through) |
| Glossary | 150 terms, each with sources |
| Sources | 267 cited references in the curriculum registry, plus the lessons' own |
| Projects | 6 models with companion code that runs on a laptop CPU |

## Features

- **Three ways in.** Start the full course, set up Python first (an optional setup track with direct
  official download links and annotated screenshots), or jump straight to a project. Each project lists
  the lessons it needs, and you can tick off the ones you already know.
- **Beginner to advanced.** Setup → Beginner (the math piece by piece, a first model in NumPy) →
  Intermediate (backprop, PyTorch, training, regularization, optimizers) → Advanced (CNNs, RNNs,
  attention, Transformers, tokenization, game-tree search, self-play, efficient inference).
- **Six project tracks:**
  1. Handwritten digits (MNIST) and letters (EMNIST), with a drawing app
  2. Doodle recognition (Quick, Draw!), with a drawing app
  3. Small-text models: a name generator (bigram → MLP → GRU/LSTM) and a short-text sentiment classifier
  4. Code autocompletion with a tiny GPT trained on the Python standard library
  5. A mini-Stockfish: alpha-beta search with a neural evaluator that speaks UCI, so you can play it in
     a chess GUI
- **Wikipedia-style articles:** a lead paragraph, an infobox, a table of contents, numbered citations,
  "See also", references, further reading and glossary links in the text.
- **Step-by-step math** (`MathSteps`): each line of a derivation shows on its own, with a plain-words
  explanation and the symbols used, rendered with KaTeX.
- **Full progress control:** mark any lesson, module, track or exercise as done or not done with one
  click (or press <kbd>M</kbd> on a lesson). A "Continue" card, progress rings, and export, import and
  reset of your progress as JSON.
- **Exercise library:** every exercise in one place, with filters by track, level, type, difficulty and
  status, plus search.
- **Glossary and search:** an A–Z glossary and full-text site search (Pagefind; press <kbd>/</kbd>).
- **Certificate:** a horizontal, asymmetric A4 certificate (navy band, guilloche rosette, wax seal,
  gold frame). Type your name and download it as a 300 dpi PNG or a PDF. It unlocks when you finish
  the Beginner, Intermediate and Advanced tracks plus one project track; the setup track is optional.
  Everything is generated in your browser.
- **Light, premium design:** a warm paper palette, Fraunces, Inter and JetBrains Mono, AA contrast
  and visible keyboard focus. Built for screens 1024 px and wider.

## Run the website

You need [Node.js](https://nodejs.org/) 22 or newer.

```bash
npm install
npm run dev          # http://localhost:4321 with hot reload
```

Other commands:

| Command | What it does |
|---|---|
| `npm run build` | Builds the static site into `dist/` and builds the search index (Pagefind) |
| `npm run preview` | Serves the built `dist/` locally |
| `npm run validate` | Checks every lesson, glossary entry and the curriculum (schema, citations, links, exercises, code excerpts) |
| `npm run check` | TypeScript and Astro type check |
| `npm test` | Playwright end-to-end tests. Builds and serves the site on port 4391 (`AIK_TEST_PORT` changes it). Run `npx playwright install chromium` once first |
| `node scripts/check-links.mjs` | Checks every internal link in `dist/` and every external link, and writes `research/link-report.md`. Add `--internal-only` for a fast offline check |

Site search only works after `npm run build` (the dev server has no search index).

`dist/` is plain static files, so you can host it on any static host (GitHub Pages, Netlify,
Cloudflare Pages). `dist/404.html` is the not-found page. The site is built for the root of a domain
(`site` in `astro.config.mjs`). If you host it under a sub-path such as `/ai-knowledge/`, set Astro's
`base` option.

## Run the Python projects

The companion code is in [`code/`](code/). The [setup track](src/content/lessons/setup/) explains
every step for Windows, macOS and Linux. Here is the short version:

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate      macOS/Linux:  source .venv/bin/activate
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r code/requirements.txt
python code/setup/verify_setup.py       # ends with "All checks passed."
```

The setup track installs Python 3.14; the companion code was smoke-tested with Python 3.13 and PyTorch 2.15 (CPU). A GPU is not needed. For a GPU
build, use the command that the [PyTorch selector](https://pytorch.org/get-started/locally/) gives you.

Every project has a fast `--smoke` mode and its own README with all commands and measured results:

| Project | Folder | First commands |
|---|---|---|
| Digits and letters | [`code/projects/project-digits-letters`](code/projects/project-digits-letters/README.md) | `python train.py` · `python draw_app.py` |
| Doodles | [`code/projects/project-doodles`](code/projects/project-doodles/README.md) | `python download.py` · `python train.py` · `python draw_app.py` |
| Small text | [`code/projects/project-text`](code/projects/project-text/README.md) | `python bigram.py` · `python char_rnn.py --smoke` · `python train_classifier.py --smoke` |
| Code autocompletion | [`code/projects/project-code-autocomplete`](code/projects/project-code-autocomplete/README.md) | `python train.py --smoke` · `python complete.py --prompt "def is_even(n):"` |
| Mini chess engine | [`code/projects/project-chess`](code/projects/project-chess/README.md) | `python search.py` · `python play.py --eval material` · `minifish.bat` / `minifish.sh` (UCI) |

Run commands from inside the project's folder. Datasets download on first use into each project's
`data/` folder, and checkpoints go to `checkpoints/`. Both are git-ignored.

Core-track scripts used by the lessons are in `code/core/beginner`, `code/core/intermediate` and
`code/core/advanced`, and the short lesson samples are in `code/samples`.

To check that all companion code still runs end to end (about 6 minutes on a laptop CPU):

```bash
python code/run_smoke_tests.py            # all projects; e.g. "python code/run_smoke_tests.py chess" for one
```

The latest results are in [`research/smoke-test-report.md`](research/smoke-test-report.md).

## Project structure

```
src/
  content/lessons/<track>/<slug>.mdx   79 lessons (frontmatter: sources, exercises, prerequisites)
  content/glossary/*.md                150 glossary entries
  data/curriculum.json                 the course map: tracks, modules, order, prerequisites, source registry
  components/mdx/                      lesson components: Cite, Term, MathSteps, Analogy, CodeFile, Screenshot, Exercise ...
  components/{course,landing,certificate,ui}/
  layouts/                             BaseLayout (page shell), LessonLayout (Wikipedia-style article)
  pages/                               landing, /course, /course/<track>/<slug>, /projects, /exercises,
                                       /glossary, /certificate, 404
  lib/                                 schema, catalog, progress store (localStorage), remark/KaTeX setup
  scripts/                             client-side scripts (progress UI, course page, certificate export)
  styles/                              design tokens and global, article and callout styles
public/                                favicon, lesson figures, setup screenshots and illustrations
code/                                  Python companion code (setup check, samples, core tracks, 5 project folders)
scripts/                               validator, link checker, setup screenshot capture
tests/                                 Playwright tests (landing, pages, progress, certificate, smoke)
research/                              the research behind the course, curriculum rationale, link and smoke reports
docs/authoring.md                      how to write lessons, glossary entries and companion code
```

## Add or edit a lesson

The full guide is [`docs/authoring.md`](docs/authoring.md). In short:

1. Add the lesson to `src/data/curriculum.json` (track, module, order, prerequisites, sources).
2. Create `src/content/lessons/<track>/<slug>.mdx` with the frontmatter from the guide: title, summary,
   outcomes, sources with URLs and access dates, exercises.
3. Write it: a lead, sections, at least one `<Cite>` per claim, `<Term>` links to the glossary,
   `<MathSteps>` for derivations, `<Analogy>` for beginner ideas, and `<CodeFile>` to quote companion code.
4. Run `npm run validate`, then `npm run build`, then `npm test`.

Progress keys are lesson slugs, so don't rename a published slug.

## Licences

- **Code** (everything in `src/` that is code, `scripts/`, `tests/`, `code/`): [MIT](LICENSE).
- **Course content** (lesson text, exercises, glossary, curriculum, research notes, original figures and
  illustrations): [CC BY 4.0](LICENSE-CONTENT.md). Credit "AI Knowledge by Gabriele Bolognese" with a link to
  this repository.
- **Screenshots of third-party sites** in `public/screenshots/setup/*.png` show pages owned by their
  publishers (python.org, Microsoft, PyTorch, Google and others). They are included only to show what
  to click.
- **Fonts:** Fraunces, Inter, JetBrains Mono, Cormorant Garamond and Pinyon Script, under the SIL Open
  Font License 1.1 (via Fontsource).
- **Dependencies:** each keeps its own licence. Note that the chess project imports
  [python-chess](https://github.com/niklasf/python-chess) (GPL-3.0).

### Datasets and attributions

| Dataset | Used in | Terms | In this repo? |
|---|---|---|---|
| [MNIST](https://docs.pytorch.org/vision/stable/generated/torchvision.datasets.MNIST.html) (LeCun, Cortes and Burges) | digits project, intermediate track | No licence stated by the authors | No: downloaded at run time by torchvision |
| [EMNIST](https://www.nist.gov/itl/products-and-services/emnist-dataset) (Cohen et al., 2017, NIST) | letters | No licence stated | No: downloaded at run time |
| [Quick, Draw!](https://github.com/googlecreativelab/quickdraw-dataset) by Google | doodles project | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | No: downloaded by `download.py`. The doodle figures in `public/figures/doodles/` are derived from it and credited |
| [Lichess evaluation database](https://database.lichess.org/) | chess project | CC0 | A 4,000-record sample in `code/projects/project-chess/sample/` |
| [names.txt](https://github.com/karpathy/makemore) (from US Social Security Administration data) | text project | MIT (makemore); the underlying data is a US government work | Yes, with its licence in `bundled/` |
| [Sentiment Labelled Sentences](https://archive.ics.uci.edu/dataset/331/sentiment+labelled+sentences) (Kotzias et al., 2015) | text project | CC BY 4.0 | Yes, in `bundled/` |
| [TinyShakespeare](https://github.com/karpathy/char-rnn) | text project | Public-domain text | No: downloaded at run time |
| [SST-2](https://aclanthology.org/D13-1170/) (Socher et al., 2013; GLUE) | text project | No licence stated; cite the paper | No: downloaded at run time |
| [CPython standard library](https://docs.python.org/3/license.html) | code autocompletion corpus | PSF License | No: read from your local Python install |

Full attribution texts are in each project's README and in `code/projects/project-text/bundled/LICENSES.md`.

## Status and quality checks

- `npm run validate`: 79 lessons and 150 glossary entries, 0 failures.
- `node scripts/check-links.mjs`: 0 broken internal links. See [`research/link-report.md`](research/link-report.md)
  for the external links (bot-protected publishers such as doi.org count as "unverified", not broken).
- `npm test`: the Playwright suite covers the landing page, every page type, progress (mark, undo, bulk,
  export, import, reset) and certificate export.
- `python code/run_smoke_tests.py`: every project's training and inference entry points.

AI Knowledge is a self-issued, free course certificate. It is not an accredited qualification.
