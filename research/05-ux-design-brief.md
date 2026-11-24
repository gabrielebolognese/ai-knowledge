# 05 — UX and Design Brief: a premium light learning site that reads like Wikipedia

> Scope: this brief is the single source of truth for every UI step (scaffold, landing, dashboard, lessons, exercise library, glossary, certificate). It was written on 2026-11-24 from public pages only (no logins, no posting). Where a statement comes from a source, the source is linked inline and listed in [Sources](#sources). Anything marked **Decision** is our own choice, not a claim about another product.
>
> Working name used in this document: **AI Knowledge** (repo `ai-knowledge`). No logo, mascot or brand asset is specified or borrowed. The identity is a typographic one: a serif wordmark plus a small geometric "node" glyph made of our own SVG circles (see [§6.1](#61-wordmark-and-glyph)).

---

## 1. What the research says, and what we take from it

### 1.1 Brilliant and Duolingo (public pages only)

| Observation (source) | What we take (Decision) | What we deliberately do **not** copy |
|---|---|---|
| Brilliant's public home page describes learning "by doing" on an interactive canvas, with guiding questions, a plan that adapts to your level, and a place to "track your progress and know what to practice next" ([brilliant.org](https://brilliant.org)). Its own write-up lists sequencing from a simple case upward, one manageable idea per section, retrieval practice, and instant feedback ([How Brilliant teaches math](https://brilliant.org/resources/choosing-brilliant/how-brilliant-teaches-math/)); it recommends short daily sessions ([Why Brilliant](https://brilliant.org/help/why-brilliant/)). | One idea per lesson step; a "check yourself" question after every concept; the next action is always the biggest button on screen; lessons sized to 10-15 minutes. | Their layouts, illustration style, character-driven tutor, paywall and streak-pressure copy. |
| Duolingo's own explanation of its path says the home screen became "a path that you'll follow step by step", each circle is one level, and the goal was a "clear path to follow" so learners know each step is the right next one ([Introducing the new Duolingo learning path](https://blog.duolingo.com/new-duolingo-home-screen-design/)). Press coverage of the same redesign describes circles as lessons where finishing one unlocks the next ([NBC News interview](https://www.nbcnews.com/tech/tech-news/duolingos-update-redesign-luis-von-ahn-interview-rcna44655)). A UX critique pointed out that being unable to zoom out the course map makes earlier lessons hard to find (reported in the search summary of [uxdesign.cc](https://uxdesign.cc/duolingos-redesign-4-things-they-got-right-1-possible-improvement-acec8af9ec10); paywalled, not read in full). | A **path map** of nodes per module with exactly one highlighted "current" node. We fix the critique: our map is zoomable by being collapsible per module, and any node is reachable at any time (**no locks**, the user asked for full control). | Their mascot, owl-green palette, hearts/lives, leaderboards, notifications and "locked until previous" mechanic. |
| Wikipedia's [Gamification](https://en.wikipedia.org/wiki/Gamification) overview describes using game-design elements such as progress and feedback in non-game contexts. The [Zeigarnik effect](https://en.wikipedia.org/wiki/Zeigarnik_effect) is the commonly cited reason that visible unfinished tasks pull people back (the effect's replication is debated, so we use it as a design heuristic, not a promise). | Progress rings that are always visible; "in progress" lessons visually distinct from "not started"; a resume card on the dashboard. | Streak guilt, loss framing. Our gamification is **positive only**: completion, milestones, certificate. |
| [Cognitive load](https://en.wikipedia.org/wiki/Cognitive_load) and [progressive disclosure](https://www.nngroup.com/articles/progressive-disclosure/) research: show the minimum first, reveal detail on demand. [Hick's law](https://en.wikipedia.org/wiki/Hick%27s_law) and [Fitts's law](https://en.wikipedia.org/wiki/Fitts%27s_law) back few choices and large targets. | Math revealed one step at a time; glossary in hover cards, not inline paragraphs; at most **one primary button** per view. | Dense dashboards, many equal-weight CTAs. |

### 1.2 Wikipedia's style, as rules we can implement

From the [Manual of Style](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style), its [Lead section](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Lead_section), [Layout](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Layout), [Linking](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Linking), [Hatnote](https://en.wikipedia.org/wiki/Wikipedia:Hatnote), [Footnotes help](https://en.wikipedia.org/wiki/Help:Footnotes) and [Infobox help](https://en.wikipedia.org/wiki/Help:Infobox) pages, we adopt these **structural** conventions (the visual look stays ours):

1. **Lead first.** Every lesson opens with a short lead (2-4 sentences) that defines the topic in plain words and says why it matters. The lead is bold-free except for the lesson's own title term on first use.
2. **Hatnote** (italic one-liner above the lead): "For the full-size version, see *Backpropagation, step by step*." It points to a different or deeper page; it is never decoration. Per the Hatnote guideline its purpose is to help readers who landed on the wrong page find the right one.
3. **Infobox** at the top-right of the lesson: a compact fact table (level, time, prerequisites, you will build, tools, next lesson).
4. **Sections** with `h2`/`h3` only (no `h4+`), a generated contents list for lessons longer than 4 sections.
5. **Wikilinks**: link the first occurrence of a term in a section to its glossary entry or an authoritative source; do not link every repeat; do not overlink common words ([Linking](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Linking)).
6. **Inline citations** as superscript numbers `[1]` that jump to the **References** list at the bottom; clicking a reference's caret `^` jumps back ([Footnotes](https://en.wikipedia.org/wiki/Help:Footnotes)).
7. **End matter order** (adapted from the Layout page): *Summary → Check yourself → See also → Notes → References → Further reading → External links*. Our "Check yourself" and "Mark complete" sit **before** See also so the call to action is not buried.
8. **Neutral, summarised, encyclopaedic tone**, short paragraphs, no second-person hype. Beginners get analogies in a distinct callout so the encyclopaedic text stays clean.

### 1.3 Premium light references (public marketing/docs pages)

We looked at the public pages of [Linear](https://linear.app), [Stripe Docs](https://stripe.com/docs), [Vercel](https://vercel.com) and [Notion](https://www.notion.com) for **general patterns only**: generous whitespace, very restrained colour (one accent), hairline borders instead of heavy boxes, soft layered shadows, tight but legible headings, subtle gradient washes behind hero sections, product-like illustrations built from the real UI, a sticky left nav and an on-this-page right rail in docs. We copy none of their layouts, wording or assets. Our differentiators are **(a)** warm paper background rather than cold white or grey, **(b)** a high-contrast editorial serif for display, **(c)** gold-leaf details reserved for achievement moments.

### 1.4 Readability and accessibility facts we rely on

- **Line length.** Baymard reports Emil Ruder's 50-60 characters per line, with up to 75 considered acceptable ([Baymard](https://baymard.com/blog/line-length-readability)); Butterick's Practical Typography recommends 45-90 characters, including spaces ([Practical Typography](https://practicaltypography.com/line-length.html)). **Decision:** body measure `max-width: 68ch` (inside the 60-75 target); infobox and side rails live outside the measure.
- **Contrast.** WCAG 2.2 SC 1.4.3 requires 4.5:1 for normal text and 3:1 for large text ([Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)); SC 1.4.11 requires 3:1 for UI components and graphical objects ([Non-text Contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)); SC 1.4.1 forbids colour as the only signal ([Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)); SC 2.5.8 sets a 24 x 24 CSS px minimum target ([Target Size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)); focus appearance guidance is in [Focus Appearance](https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html). **Decision:** every text token below was computed to pass 4.5:1 on its intended surface (see the contrast table in [§3.1](#31-colour-tokens)); our target size is 40 px minimum for primary controls.
- **Motion.** All animation must respect [`prefers-reduced-motion`](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion).
- **Hover-only is not allowed** on its own: hover cards must also open on keyboard focus and tap/click, following the WAI-ARIA [tooltip](https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/) and [disclosure](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/) patterns; use the [meter](https://www.w3.org/WAI/ARIA/apg/patterns/meter/) role semantics for progress rings.

---

## 2. Design principles

1. **Quiet confidence.** One accent colour, warm paper, ink-black text. Decoration is reserved for achievement (gold) and navigation (accent). If an element is not helping a reader read, learn or decide, remove it.
2. **Read first, play second.** The lesson page is an *article*. Interactivity (reveals, quizzes, mark-complete) wraps around the text; it never replaces it. A reader who ignores every interactive element still gets a complete, sourced article.
3. **Always one obvious next step.** Each page has exactly one primary action: *Continue*, *Start*, *Mark complete*, *Download certificate*.
4. **Everything is reachable.** No locks, no gating. Prerequisites are advice ("recommended first") not walls. Skip paths are first-class: "I already have Python set up → jump to Beginner 1".
5. **Show the piece, then the whole.** Math and code are revealed in small steps with a plain-English translation next to each symbol. Analogy first, symbols second.
6. **Sourced by construction.** A claim without a citation is a bug. The layout makes citations cheap to read (hover preview) and impossible to miss (numbered superscripts, a References section on every lesson).
7. **Desktop-native.** Designed for 1280-1920 px wide screens, mouse and keyboard. We use the width: a three-column lesson (nav · article · on-this-page). Below 1024 px we show a polite desktop-only notice, not a broken layout.
8. **Calm celebration.** Success is acknowledged with a short, tasteful animation and a clear state change, never with confetti storms, sounds, or guilt.
9. **Original identity.** Typography-led, paper-and-ink, gold-leaf accents. Nothing resembles another product's mascot, palette, or screens.
10. **Local and private.** State lives in `localStorage` only; the UI must say so once, plainly ("Progress is saved in this browser only") and offer export/import/reset.

---

## 3. Design tokens

Implement as CSS custom properties on `:root` (light theme only; no dark mode in v1). Prefer a single `tokens.css` that the whole site imports. Hex values are the contract; `oklch()` conversions are optional ([MDN oklch](https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/oklch)).

### 3.1 Colour tokens

```css
:root {
  /* Surfaces: warm paper */
  --paper:        #FAF7F2;  /* page background */
  --surface:      #FFFFFF;  /* cards, article panel */
  --surface-2:    #F3EEE6;  /* wells, code-adjacent areas, hover fill */
  --surface-3:    #EAE3D7;  /* pressed fill, table header */
  --line:         #E6DFD3;  /* hairlines, card borders (decorative) */
  --line-strong:  #8F8677;  /* UI component borders, unchecked boxes (>=3:1) */

  /* Ink: text */
  --ink:          #1B1A17;  /* headings, body */
  --ink-2:        #4A463F;  /* secondary text */
  --ink-3:        #6B655A;  /* captions, meta (>=4.5:1 on paper/surface) */
  --ink-inverse:  #FFFFFF;

  /* Signature accent: "Ultramarine" */
  --accent:       #3340C9;  /* primary buttons, current node, links' underline */
  --accent-hover: #2832A3;
  --accent-soft:  #ECEEFC;  /* selected rows, soft badges, focus halo fill */
  --link:         #2A37B0;  /* body links */
  --link-visited: #5B2E91;

  /* Status */
  --success:      #1E7B3F;  --success-soft: #E6F3EA;
  --warn:         #8F5400;  --warn-soft:    #FBF0DC;
  --danger:       #B3261E;  --danger-soft:  #FBE9E7;

  /* Level colours: beginner / intermediate / advanced */
  --lvl-beginner:     #0F766E;  --lvl-beginner-soft:     #E1F2F0;  /* teal   */
  --lvl-intermediate: #6D3FC4;  --lvl-intermediate-soft: #EFE9FA;  /* violet */
  --lvl-advanced:     #B4233C;  --lvl-advanced-soft:     #FBE7EA;  /* crimson */

  /* Gold: achievements only (never body text) */
  --gold-1: #F3E2A9; --gold-2: #D8B45A; --gold-3: #B8892F; --gold-4: #7A5A12;
  --gold-text: #7A5A12;  /* the only gold allowed on text on light surfaces */

  /* Code */
  --code-bg: #F6F2EA; --code-ink: #2B2924;
  --tok-keyword:#6D3FC4; --tok-string:#1E7B3F; --tok-number:#B4233C; --tok-comment:#6B655A; --tok-func:#2A37B0;
}
```

Contrast audit (computed with the WCAG relative-luminance formula; all text pairs pass AA 4.5:1, non-text pairs pass 3:1):

| Foreground | on `--paper` #FAF7F2 | on `--surface` #FFFFFF | on `--surface-2` #F3EEE6 |
|---|---|---|---|
| `--ink` #1B1A17 | 16.3 | 17.4 | 15.1 |
| `--ink-2` #4A463F | 8.8 | 9.4 | 8.1 |
| `--ink-3` #6B655A | 5.4 | 5.8 | 5.0 |
| `--link` #2A37B0 | 8.7 | 9.2 | 8.0 |
| `--accent` #3340C9 | 7.2 | 7.7 | 6.7 |
| `--success` #1E7B3F | 5.0 | 5.3 | 4.6 |
| `--warn` #8F5400 | 5.7 | 6.1 | 5.3 |
| `--danger` #B3261E | 6.1 | 6.5 | 5.7 |
| `--lvl-beginner` #0F766E | 5.1 | 5.5 | 4.7 |
| `--lvl-intermediate` #6D3FC4 | 6.2 | 6.7 | 5.8 |
| `--lvl-advanced` #B4233C | 6.1 | 6.5 | 5.6 |
| `--gold-text` #7A5A12 | 6.0 | 6.4 | 5.5 |
| `--line-strong` #8F8677 (non-text, needs 3:1) | 3.4 | 3.6 | n/a |

Other verified pairs: white on `--accent` 7.7; white on `--success` 5.3; coloured text on its own `*-soft` badge background: accent 8.0, success 4.6, warn 5.4, danger 5.6, beginner 4.7, intermediate 5.6, advanced 5.5 (all >= 4.5). `--line` (#E6DFD3) is decorative only; never rely on it to delimit an interactive control. **Level colours are never the only signal:** every level badge also carries the word and a shape (circle = Beginner, diamond = Intermediate, hexagon = Advanced) per [Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html).

Colour usage rules:
- Page = `--paper`; reading panel and cards = `--surface`; wells = `--surface-2`.
- Links in prose: `--link`, 1 px underline at 25% opacity that goes to 100% on hover; visited `--link-visited`.
- Exactly one filled accent button visible per viewport; secondary buttons are outlined with `--line-strong`.
- Gold only on: certificate, completed-track medal, the 100% progress ring end cap, and the "Certificate ready" banner.

### 3.2 Type system

All fonts are free (SIL OFL) and self-hosted through [Fontsource](https://fontsource.org/docs/getting-started/install) so the site works offline and without calling Google at runtime.

| Role | Family | Fontsource package | Notes |
|---|---|---|---|
| Display (h1, h2 on landing, big numerals, lesson titles) | [Fraunces](https://fontsource.org/fonts/fraunces) variable, optical size on, weights 400/500/600 | `@fontsource-variable/fraunces` | Warm, high-contrast editorial serif. Use `font-variation-settings: "opsz" 144, "SOFT" 30` at display sizes only. |
| UI and body | [Inter](https://fontsource.org/fonts/inter) variable, weights 400/500/600 | `@fontsource-variable/inter` | Keep Inter's default features; enable `font-variant-numeric: tabular-nums` only on numerals in tables and progress. |
| Code and math-in-code | [JetBrains Mono](https://fontsource.org/fonts/jetbrains-mono) variable | `@fontsource-variable/jetbrains-mono` | Ligatures **off** for teaching (`font-variant-ligatures: none`). |
| Certificate name and ornamental caps | [Cormorant Garamond](https://fontsource.org/fonts/cormorant-garamond) 500/600 + 500 italic | `@fontsource/cormorant-garamond` | Used on the certificate only. Optional signature flourish: [Pinyon Script](https://fontsource.org/fonts/pinyon-script) (`@fontsource/pinyon-script`). |

Alternates if a worker finds a licence or rendering problem: [Newsreader](https://fontsource.org/fonts/newsreader) or [Source Serif 4](https://fontsource.org/fonts/source-serif-4) (display), [Instrument Serif](https://fontsource.org/fonts/instrument-serif) (landing only).

Fallback stacks: serif `"Fraunces Variable", "Iowan Old Style", Georgia, serif`; sans `"Inter Variable", system-ui, "Segoe UI", sans-serif`; mono `"JetBrains Mono Variable", ui-monospace, Consolas, monospace`.

**Type scale** (ratio 1.250 "major third" from a 17 px body; px values at 1x; implement as `rem` with `html { font-size: 100% }`):

| Token | Size / line-height | Font | Weight | Use |
|---|---|---|---|---|
| `--t-display` | 72 / 76 px, tracking -0.02em | Fraunces | 500 | Landing hero only |
| `--t-h1` | 44 / 52 px, -0.015em | Fraunces | 500 | Lesson/page title |
| `--t-h2` | 30 / 38 px, -0.01em | Fraunces | 500 | Section heading (with hairline rule beneath, as on Wikipedia) |
| `--t-h3` | 21 / 30 px | Inter | 600 | Sub-section |
| `--t-lead` | 20 / 32 px | Inter | 400 | Lesson lead paragraph |
| `--t-body` | 17 / 28 px (1.65) | Inter | 400 | Article text |
| `--t-ui` | 15 / 22 px | Inter | 500 | Buttons, nav, tabs |
| `--t-small` | 13.5 / 20 px | Inter | 400 | Captions, infobox rows, references |
| `--t-micro` | 12 / 16 px, +0.06em, uppercase | Inter | 600 | Eyebrows, badges |
| `--t-code` | 15 / 24 px | JetBrains Mono | 400 | Code blocks (inline code 0.92em) |

Measure: article `max-width: 68ch`. Headings never exceed `24ch`. Paragraph spacing `1.1em`; no first-line indent. Use `text-wrap: balance` for headings and `text-wrap: pretty` for paragraphs.

### 3.3 Spacing, layout, radius, shadow

Spacing is a 4 px base: `--s-1: 4px; --s-2: 8px; --s-3: 12px; --s-4: 16px; --s-5: 24px; --s-6: 32px; --s-7: 48px; --s-8: 64px; --s-9: 96px; --s-10: 144px`. Section padding on landing: `--s-9` vertical. Card padding: `--s-5`. Never use values outside the scale.

Layout grid (desktop only):
- Container max `1280px`, side gutters `48px`; landing may bleed to `1440px` for hero art.
- Lesson page: `grid-template-columns: 264px minmax(0, 1fr) 248px; gap: 48px` where the centre column holds the 68ch article plus the right-floating infobox (see wireframe). Left = course outline, right = "On this page" + progress.
- Minimum supported viewport: **1024 px**. Below that, show the desktop-only notice ([C11](#c11-desktop-only-notice)).
- Top bar height `64px`, sticky, `--paper` at 85% with `backdrop-filter: blur(12px)` and a hairline bottom border that appears after 8 px scroll.

Radius: `--r-xs: 6px` (inputs, code), `--r-sm: 10px` (buttons, badges), `--r-md: 16px` (cards), `--r-lg: 24px` (hero panels, modal), `--r-pill: 999px`.

Shadow (warm, low-contrast, layered; colour is ink at low alpha, never pure black):
```css
--sh-1: 0 1px 2px rgb(27 26 23 / 0.06), 0 0 0 1px rgb(27 26 23 / 0.04);               /* resting card */
--sh-2: 0 2px 4px rgb(27 26 23 / 0.05), 0 8px 20px rgb(27 26 23 / 0.07);              /* hover card, popover */
--sh-3: 0 4px 8px rgb(27 26 23 / 0.06), 0 24px 56px rgb(27 26 23 / 0.12);             /* modal, certificate preview */
--sh-accent: 0 1px 0 rgb(255 255 255 / 0.25) inset, 0 6px 16px rgb(51 64 201 / 0.28); /* primary button */
--focus: 0 0 0 3px #FAF7F2, 0 0 0 5px #3340C9;                                         /* focus ring: 2px gap + 2px ring, 7.2:1 */
```

Z-index scale: base 0, sticky 10, popover 30, modal 50, toast 60.

### 3.4 Motion tokens

`--ease-out: cubic-bezier(0.16, 1, 0.3, 1)`; `--ease-in-out: cubic-bezier(0.65, 0, 0.35, 1)`; durations `--d-fast: 120ms`, `--d-base: 200ms`, `--d-slow: 360ms`, `--d-celebrate: 900ms`. Animate only `transform`, `opacity`, `stroke-dashoffset`, `clip-path`. Wrap all non-essential motion in `@media (prefers-reduced-motion: no-preference)`; under `reduce` swap to instant state changes plus a 1-frame colour flash.

---

## 4. Component inventory

Each component lists purpose, anatomy, states, and accessibility. Build them as framework components (Astro + a few interactive islands) in `src/components/`, each with a CSS module or scoped styles that read only from tokens.

### C1. Path map node
- **Purpose:** one lesson (or project step) on the course path; the visual spine of the dashboard and track pages.
- **Anatomy:** 56 px circle (diamond for the first node of a module = "module start"; hexagon for module capstone). Inner icon: number, check, or small glyph. Label to the right: title (15/22 600), meta line "8 min · Beginner" in `--ink-3`. Nodes are joined by a 3 px vertical connector; completed segments draw in `--accent`, upcoming in `--line`.
- **States:** `not-started` (surface fill, 2 px `--line-strong` border, number) · `current` (accent fill, white number, 6 px `--accent-soft` halo that pulses once on load, label bold, "Continue" chip) · `in-progress` (ring partly drawn around the circle) · `complete` (accent-soft fill, accent check icon) · `capstone-complete` (gold ring `--gold-3`). **No `locked` state.** Hover: raise 2 px, `--sh-2`, tooltip with lead sentence. Focus: `--focus`.
- **A11y:** each node is an `<a>` with `aria-current="step"` on the current one and a visually hidden state word ("completed", "in progress").
- **Layout:** the map is a single column of module groups; module headers collapse (disclosure pattern) so the whole course fits on a screen — this addresses the "can't zoom out" critique noted in §1.1.

### C2. Lesson card
- **Purpose:** compact entry to a lesson/exercise in lists (dashboard "Up next", track pages, search results).
- **Anatomy:** 16 px radius surface, `--sh-1`, 24 px padding. Top row: level badge (shape + word) and time. Title in Fraunces 21/28. Two-line summary clamp. Footer: progress ring (24 px) or check + "Open" arrow link. Optional 4 px left edge in level colour (decorative; level is also in text).
- **States:** default, hover (`--sh-2`, translateY(-2px)), focus-visible, completed (check + "Completed" text, 100% opacity; do not grey out), current.

### C3. Progress ring
- **Purpose:** circular progress for lesson, module, track and overall.
- **Anatomy:** SVG, stroke width 6 (ring) at 72 px, 4 at 40 px, 3 at 24 px; track `--line`, value `--accent`; at 100% the stroke becomes a `--gold-2 → --gold-3` linear gradient and a check appears in the centre. Centre text: `42%` (Inter 600, tabular numerals) on large sizes; none on small.
- **Behaviour:** `stroke-dashoffset` animates over `--d-slow` with `--ease-out` when it enters the viewport the first time and on every value change. Round caps.
- **A11y:** `role="meter"` (or `role="progressbar"`) with `aria-valuenow/min/max` and an `aria-label` such as "Beginner track: 5 of 12 lessons complete" ([meter pattern](https://www.w3.org/WAI/ARIA/apg/patterns/meter/)).

### C4. Infobox
- **Purpose:** the Wikipedia-style fact table at the top-right of each lesson and track page.
- **Anatomy:** 280 px wide, floats right of the lead inside the article column (`float: right; margin: 0 0 24px 32px`), `--surface-2` fill, 1 px `--line` border, 10 px radius. Header band: lesson title (Fraunces 17/24) on `--surface-3`. Optional 16:10 diagram slot at the top (SVG only). Rows (label `--ink-3` 13.5 px / value `--ink` 13.5 px), separated by hairlines: **Level**, **Time**, **Prerequisites** (links), **You will learn**, **You will build**, **Tools**, **Next** (link), **Last reviewed** (date). Footer: "Mark complete" is **not** here (see C10).
- **Rules:** rows with no value are omitted; max 8 rows.

### C5. Analogy callout
- **Purpose:** beginner-friendly everyday analogy placed right after a concept is stated formally.
- **Anatomy:** full article width, 16 px radius, `--accent-soft` background, 4 px left bar `--accent`, small icon (our own SVG lightbulb/handshake line icon, 20 px), eyebrow "Think of it like…" in `--t-micro` accent, body text 17/28. One analogy per concept; max 2 sentences plus an optional "Where the analogy breaks down" line in `--ink-3` italic (honesty about limits).
- **Variants:** `analogy` (accent), `pitfall` (warn-soft background, left bar `--warn`, eyebrow "Common mistake"), `note` (surface-2, eyebrow "Note"), `tip` (success-soft, "Tip"), `warning` (danger-soft, "Careful"). All variants carry an icon plus the word, never colour alone.

### C6. Step-by-step math reveal
- **Purpose:** show a derivation piece by piece, with plain-English translations, so beginners never face a wall of symbols.
- **Anatomy:** panel on `--surface` with 1 px `--line` border, 16 px radius. Header: title ("Computing one neuron's output") and a stepper "Step 2 of 5" with dots. Body: left 60% the **current expression** rendered by KaTeX (self-hosted CSS/fonts) at 24 px with the *newly added or changed term* highlighted in `--accent-soft` fill with `--accent` text; right 40% a **"In words"** box translating the new term and, where useful, a number-example row ("with x = 2, w = 3 → 6"). Previous steps remain visible as faded (70% opacity) lines above, so the derivation accumulates. Footer controls: **Back**, **Next step** (primary, `→` key), **Show all**, **Reset**.
- **States:** collapsed (only step 1 + "Walk through it" button), stepping, fully revealed. Keyboard: Left/Right arrows when focused; each step announced via `aria-live="polite"`.
- **Rules:** one new idea per step; every symbol introduced gets a one-line "In words". A symbols legend (variable → meaning) is always available in a disclosure under the panel. Numeric worked example with small integers precedes the general formula.
- **No-JS / print fallback:** all steps rendered in order as a numbered list.

### C7. Citation superscript and references list
- **Inline marker:** `<sup>` containing an `<a href="#ref-3">[3]</a>`, `--link` colour, 12 px, no underline, 24 x 24 px hit area (use padding), `scroll-margin-top: 88px` on targets so the sticky bar does not hide them. Hover/focus shows a **preview card** (see C8 style) with the full reference and a "Open source ↗" link. Clicking jumps to the reference and flashes it with `--accent-soft` for 1.2 s.
- **References section:** ordered list, `--t-small`, each item: author/org, *title* (link), publisher, date, "Retrieved YYYY-MM-DD". Each item begins with a caret `^` link back to the in-text marker(s) (letters `a b c` if cited several times), mirroring the Wikipedia footnote behaviour ([Help:Footnotes](https://en.wikipedia.org/wiki/Help:Footnotes)). A small tag after the link marks the source type: *Paper*, *Docs*, *Book*, *Video*, *Dataset*, *Wikipedia*.
- **Rules:** every statistic, date, definition from outside, install step and link-out has a marker. References are deduplicated per lesson and numbered by first use. External links open in the same tab by default with an `↗` glyph (our own SVG); open-in-new-tab only for downloads.
- **Further reading / External links** sit under References, un-numbered, 3-6 items.

### C8. Glossary hover card
- **Purpose:** define a term without leaving the page.
- **Trigger:** term styled with a dotted 1 px underline in `--ink-3` (`text-decoration-style: dotted`), `cursor: help`. Opens on hover (120 ms delay), keyboard focus, or click/tap.
- **Card:** 320 px, 16 px radius, `--sh-2` on `--surface`, 16 px padding. Content: term (Fraunces 17), one-sentence definition, optional tiny diagram, "Full entry →" link to `/glossary/#term`, and "Level: Beginner" badge. Dismiss: Esc, click outside, mouse leaves with 150 ms grace. Position with the [Popover API](https://developer.mozilla.org/en-US/docs/Web/API/Popover_API) or an anchored-positioning fallback; flips above/below to stay in viewport.
- **A11y:** the trigger is a `<button>` with `aria-describedby` to the card's `role="tooltip"` per the [tooltip pattern](https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/); the card content is also available at `/glossary/`.

### C9. Exercise card
- **Purpose:** an item in the exercise library and inline "Check yourself" blocks.
- **Anatomy (library card):** type chip (Quiz · Predict the output · Fill the code · Notebook task · Mini project), level badge, title, estimated time, concepts as small tags, status (not started / done). Footer: "Open" and a checkbox "Done".
- **Anatomy (inline quiz):** question (17/28), options as large radio rows (min height 48 px, `--line-strong` border), **Check** button; feedback panel slides in below: correct = `--success-soft` + check icon + short explanation + citation; incorrect = `--warn-soft` + "Not quite" + hint, **Try again** and **Show answer** (reveals the explanation; answers are never hidden permanently, because this is a self-study site). Since there is no server, answers are stored in the page as data; honesty copy: "This is for you, there is no grading."
- **Types of answer input:** single choice, multi-choice, numeric (with tolerance), short text (case-insensitive match against a list), ordering (drag with keyboard alternative: up/down buttons), code reading ("what does this print?").

### C10. Mark-complete button
- **Purpose:** the user's main control, at the **end of the lesson** and mirrored in the sticky right rail.
- **Anatomy:** large primary button 48 px tall, min-width 220 px: label "Mark lesson complete" with a hollow check circle. Pressing it: the circle fills and draws a check (`--d-base`), label becomes "Completed · Undo", the lesson's progress ring and path node update live, and a toast says "Saved in this browser". The button then offers a secondary "Next: *<title>* →" which becomes the new primary.
- **States:** default, pressed, completed (success-soft background with success text, still clickable to undo — full control), disabled never.
- **Keyboard:** `Enter/Space`; global shortcut `M` toggles complete (shown in a keycap hint).
- **A11y:** `aria-pressed` reflects completion; status changes announced in a polite live region.
- **Also available:** a small checkbox on every path node and list card so the user can mark lessons complete or incomplete in bulk from the dashboard.

### C11. Desktop-only notice
- **Purpose:** friendly gate under 1024 px viewport width.
- **Anatomy:** full-viewport `--paper` overlay (CSS-only via a `@media (max-width: 1023px)` rule so it works before JS), centred 480 px card: small monitor line-icon (own SVG), heading "Best on a computer" (Fraunces 30), body "This course has side-by-side code, math and diagrams that need a larger screen. Open it on a desktop or laptop (1024 px or wider).", and a secondary "Copy page link" button. The page content underneath stays in the DOM but `inert`. A "Continue anyway" text link may be offered (**Decision:** yes, small, lowers frustration for narrow desktop windows; it sets a session flag only).

### C12. Supporting components (small)
- **Button:** sizes 40/48 px; primary (accent fill, white text, `--sh-accent`), secondary (surface fill, 1 px `--line-strong`, ink text), ghost (no border, accent text). Radius `--r-sm`. Hover: darken to `--accent-hover`, translateY(-1px). Active: translateY(0), shadow shrinks. Min target 40 px.
- **Level badge:** `--t-micro`, pill, `*-soft` background, level-colour text, leading shape icon (circle/diamond/hexagon).
- **Code block:** `--code-bg`, 1 px `--line`, 10 px radius, filename tab, **Copy** button (top-right; label changes to "Copied" for 1.5 s), line numbers off by default, optional highlighted lines in `--accent-soft`. Shiki-style highlighting using the `--tok-*` tokens. A "Run it yourself" footer links to the companion script path in the repo.
- **Screenshot figure (setup track):** image with 1 px `--line` border, 10 px radius, `--sh-1`, caption "Figure 3. …" and numbered **annotation pins** (accent circles with white numbers) overlaid, each explained in a numbered list under the figure ("1 Click **Download Python**"). Click opens a lightbox (dialog pattern; Esc closes).
- **Command/OS tabs:** segmented control Windows · macOS · Linux (remember the choice in `localStorage`), the three panels never shown together.
- **Toast:** bottom-centre, `--ink` background, white text, 3 s, `role="status"`.
- **Search palette:** `/` or `Ctrl K` opens a centred modal with a text field and grouped results (Lessons, Glossary, Exercises); arrows + Enter; fully local (prebuilt index).
- **Breadcrumb:** `Course › Beginner › Module 2 › Lesson 3`, 13.5 px, `--ink-3`.
- **Empty state:** small line-art, one sentence, one action.
- **Data panel (settings):** export progress as JSON, import JSON, reset with a two-step confirmation (type the word `reset`).

---

## 5. Page wireframes (text)

Notation: `[...]` = button/link, `( )` = progress ring, `▒` = illustration/art area, `│` = column divider. All widths assume a 1440 px viewport.

### 5.1 Landing page (`/`)

```
┌─ TOP BAR (64px, sticky) ─────────────────────────────────────────────────────┐
│ ◦◦ AI Knowledge        Course   Projects   Exercises   Glossary     [Start ▸]│
└──────────────────────────────────────────────────────────────────────────────┘
HERO (min-height 720px; two columns 7/5; soft accent wash radial at top-right)
│ eyebrow: FREE · SELF-PACED · NO ACCOUNT                  │ ▒ Live "neural net" art:
│ H1 (Fraunces 72): Learn deep learning                    │   a small interactive node graph
│   by building it.                                        │   (own SVG): hover a node → its
│ Lead 20px: From installing Python to a working           │   connections light up; values
│ neural-network chess engine. Sourced, summarised,        │   flow left→right on a 6s loop
│ and free.                                                │   (static under reduced motion)
│ [Start the course ▸]  [I already know Python → Beginner] │
│ small: "Progress stays in your browser. Certificate when you finish."
TRUST STRIP (single hairline row): "~N lessons · 6 projects · M cited sources · 0 accounts"
  (numbers generated from content at build time)
SECTION "Three ways in" (3 equal cards)
│ Start from zero (Setup track)  │ Learn by building (Project tracks) │ Jump to a topic (Library) │
SECTION "What you will build" — 6 project tiles in a 3x2 grid, each with a tiny real output
  preview (own drawn SVG: digit grid, letter grid, doodle strokes, text sample, code
  completion ghost text, chess board with eval bar). Each tile: title, level badge, time, [Open ▸].
SECTION "How a lesson works" — a faux lesson page screenshot built from real components
  (infobox, analogy callout, math reveal, citation hover) with 4 numbered annotations.
SECTION "The path" — horizontal 4-stop strip: Setup → Beginner → Intermediate → Advanced,
  each with level colour shape, module count, hours.
SECTION "Sourced like an encyclopaedia" — two columns: sample paragraph with citation
  superscripts on the left, matching References list on the right.
SECTION "Certificate" — angled preview of the certificate (sh-3) + "Finish all required
  lessons, type your name, download it." [See the certificate]
FINAL CTA band (ink background #1B1A17, paper text): "Open lesson 1." [Start ▸]
FOOTER: repo link (GitHub), licence note, "Built without tracking. Progress is saved only in your browser.", sources policy link.
```
Exactly one filled primary button per viewport; the secondary hero link is text-style.

### 5.2 Course dashboard (`/course/`)

```
TOP BAR (same; "Course" active)
┌ LEFT RAIL 264 ┐ ┌ MAIN (≈ 760px column, centred in remaining space) ───────┐ ┌ RIGHT 280 ┐
│ Your progress │ │ H1: Your course                                         │ │ Overall ( 34% ) │
│ ( overall 34%)│ │ ┌ RESUME CARD (accent-soft, 24 radius) ───────────────┐ │ │ 21 / 62 lessons│
│ Setup  ✔ 4/4  │ │ │ Continue · Beginner 3 · Lesson 2                    │ │ │ Certificate:   │
│ Beginner 5/16 │ │ │ "Gradient descent as walking downhill"  8 min       │ │ │ 34% to unlock  │
│ Intermed. 0/18│ │ │ [Continue ▸]                                        │ │ │ [View certificate] (ghost)
│ Advanced 0/14 │ │ └────────────────────────────────────────────────────┘ │ │ Streak: none   │
│ Projects 0/6  │ │ Skip-ahead chips: [Skip setup] [I know the math] [Go straight to a project]│ │ Settings:      │
│ ───────────── │ │ PATH MAP (C1) grouped by track → module (collapsible)    │ │ export/import  │
│ Exercises     │ │  ◆ Setup ───────────── (4/4)                             │ │ /reset         │
│ Glossary      │ │     ● Install Python          ✔                          │ └────────────────┘
│ Search /      │ │  ◆ Beginner ────────── (5/16)                            │
└───────────────┘ │     ● What is a neuron?       ✔ ...  ◉ current ...       │
                  └──────────────────────────────────────────────────────────┘
```
Right rail "Streak" is intentionally **omitted** (no streak mechanics); it shows "Total time estimate left: 14 h" instead. The track chips filter the map; **Expand all / Collapse all** controls sit above the map.

### 5.3 Lesson page (`/course/<track>/<lesson>/`)

```
TOP BAR  +  BREADCRUMB  Course › Beginner › Module 2 › Gradient descent
┌ LEFT 264 ───────────┐ ┌ ARTICLE (68ch) ─────────────────────────────┐ ┌ RIGHT 248 sticky ┐
│ Module outline      │ │ hatnote (italic): For the calculus version,  │ │ On this page      │
│ ✔ 2.1 Loss          │ │   see "Derivatives for gradient descent".    │ │  Lead             │
│ ◉ 2.2 Gradient desc │ │ H1  Gradient descent                         │ │  What it is       │
│ ○ 2.3 Learning rate │ │ [Beginner ●] 9 min   ┌ INFOBOX (float R) ─┐  │ │  The maths        │
│ ○ 2.4 Batches       │ │ LEAD 2-4 sentences.   │ Level / Time /     │  │ │  Try it           │
│ ...                 │ │ Bold only the title.  │ Prereqs / You will │  │ │  Check yourself   │
│ ( module 25% )      │ │ ## What it is         │ learn / Build /    │  │ │  References       │
│ [Prev] [Next]       │ │ text… [1]             │ Tools / Next       │  │ │ (module ring 25%) │
│                     │ │ ▌Think of it like…    └────────────────────┘  │ │ [Mark complete]   │
│                     │ │ ▌(analogy callout)                           │ │ Shortcuts: M, ←→  │
│                     │ │ ## The maths, piece by piece                 │ └───────────────────┘
│                     │ │ [MATH REVEAL  Step 1 of 4 … Next step ▸]     │
│                     │ │ ## Try it (code block + "Run locally" link)  │
│                     │ │ ## Summary (3-5 bullets)                     │
│                     │ │ ## Check yourself (2-4 exercise cards)       │
│                     │ │ [Mark lesson complete]   [Next: Learning rate ▸]
│                     │ │ ## See also / Notes                          │
│                     │ │ ## References  (^ 1. … ^ 2. …)               │
│                     │ │ ## Further reading / External links          │
└─────────────────────┘ └──────────────────────────────────────────────┘
```
The infobox floats beside the lead only; sections below use the full 68ch. The sticky right rail repeats Mark complete so the action is never far.

### 5.4 Project track page (`/projects/<project>/`)

```
HEADER BAND (surface-2): breadcrumb · H1 "Handwritten digits (MNIST)" · lead
  ▒ big result preview (e.g. 28x28 digit canvas and predicted bars, static SVG) │ INFOBOX
  [Start project ▸]   or   "Continue: Step 3 of 7"      ( ring 3/7 )
SECTION "What you will build"   — 3 bullet outcomes + final demo description
SECTION "Before you start"      — prerequisites with links and [Skip to project] note
SECTION "Project path"          — vertical path map of 6-9 steps (C1), capstone hexagon last
   each step: concept lesson → code step → "Run it" check → reflection question
SECTION "Companion code"        — repo path, `python train.py` commands (OS tabs), expected
                                  output sample + expected accuracy range, troubleshooting accordion
SECTION "Dataset and licence"   — source link, size, licence note, citation
SECTION "Going further"         — 3 stretch tasks linking to library exercises
SECTION "References" + "See also"
```

### 5.5 Exercise library (`/exercises/`)

```
H1 Exercise library · lead "All the practice in the course, in one place."
┌ FILTERS (left 264, sticky) ──────┐ ┌ RESULTS (grid 2 columns of exercise cards) ─────────────┐
│ Search (/ ) [___________]        │ │ 48 exercises · sorted by: [Course order ▾]              │
│ Level   ☐ Beginner ☐ Inter. ☐ Adv│ │ ┌ card ──────────┐ ┌ card ──────────┐                   │
│ Type    ☐ Quiz ☐ Predict ☐ Code… │ │ │ Quiz · ● Beg.  │ │ Fill the code  │                   │
│ Topic   ☐ Neurons ☐ CNN ☐ RNN …  │ │ │ Dot products   │ │ ...            │                   │
│ Status  ○ All ○ To do ○ Done     │ │ └────────────────┘ └────────────────┘                   │
│ [Clear filters]                  │ │ pagination: none; sections by module with sticky headers │
└──────────────────────────────────┘ └────────────────────────────────────────────────────────┘
```
Filters are URL-reflected (`?level=beginner&type=quiz`) so views are linkable. An exercise opens in a right-side **drawer** (640 px) that keeps the library visible, with the same inline exercise UI and a "Open the lesson it belongs to" link.

### 5.6 Glossary (`/glossary/`)

```
H1 Glossary · lead · A-Z jump bar (sticky) [A][B][C]… with unavailable letters disabled
┌ LEFT: filter by level/topic ┐ ┌ ENTRIES (single column, 68ch, hairline-separated) ──────┐
│ search field                │ │ gradient descent  (Beginner ●)                          │
│                             │ │ Definition, 1-3 sentences with citation [n]             │
│                             │ │ ▌Analogy line                                           │
│                             │ │ See also: loss function, learning rate · Used in: lesson links │
└─────────────────────────────┘ └─────────────────────────────────────────────────────────┘
```
Each entry has an anchor (`#gradient-descent`) and a **copy link** icon on hover. Entries cite sources like articles do.

### 5.7 Certificate (`/certificate/`)

```
H1 Your certificate · status banner:
  - locked-ish (progress < 100% of required): "You have completed 34%. Finish the required lessons to download. [Continue course ▸]"
    (**Decision:** preview is always viewable with the name "Your Name"; **download** enabled only at 100% of required lessons; this is honour-based and local, so a "Download anyway (unofficial preview)" link is **not** offered; the claim of certification must stay honest.)
  - ready: gold-bordered banner "Course complete" + subtle one-time shimmer.
LEFT (5/12): FORM
   Name field (label "Name on certificate", 48px, max 48 chars, live preview) ·
   Optional: Date (defaults to today, editable) · Optional: title line toggle ("Deep Learning Foundations" fixed)
   [Download PNG ▸] (primary)   [Download PDF] (secondary)   note: "Generated in your browser. Nothing is uploaded."
RIGHT (7/12): LIVE PREVIEW at 1.0 aspect 11:8.5 landscape, --sh-3, tilt 0deg
   Under the preview: certificate ID (derived locally from name+date hash) and a one-sentence
   honesty note: "Self-issued certificate of completion from a free open-source course. Not an accredited credential."
```
Note on the honest-copy decision: the user asked for a "certification course"; we deliver a certificate of completion and say so in the footer line on the certificate itself (small, tasteful) to avoid misrepresenting accreditation.

---

## 6. Certificate art direction

Goal: a **horizontal, asymmetric, near-royal** certificate that is easy to personalise and download. Render with HTML/SVG into a `<canvas>` (see the [Canvas API](https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D) and [`toBlob`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement/toBlob)) at **3300 x 2550 px** (11 x 8.5 in at 300 dpi) for PNG, and place the same render into a one-page landscape PDF. **Wait for fonts first:** `await document.fonts.load('italic 600 120px "Cormorant Garamond"')` and the other families before drawing.

### 6.1 Wordmark and glyph
Wordmark: "AI Knowledge" set in Fraunces 500 with a small 3-circle node glyph (one filled gold-3, two outlined) joined by two lines; drawn from simple SVG circles and lines (original, ours). Used in the top bar, the certificate header and the favicon (the glyph only).

### 6.2 Palette (certificate-only tokens; extends §3.1)
```
--c-navy-900:#0B1B3A  --c-navy-800:#10265A  --c-navy-700:#173473   /* primary field */
--c-ox-900:#4A0F1B    --c-ox-700:#6E1A2B    --c-ox-500:#8E2A3E     /* oxblood accent panel */
--c-cream:#F6EFD9     --c-cream-2:#EFE5C8                             /* parchment */
--c-gold-1:#F3E2A9  --c-gold-2:#D8B45A  --c-gold-3:#B8892F  --c-gold-4:#7A5A12   /* foil stops */
```
Verified contrast (computed): gold #D8B45A on navy #0B1B3A 8.6:1; cream on navy 14.8:1; gold on oxblood #4A0F1B 7.7:1; navy on cream 14.8:1; oxblood #5A1222 on cream 11.8:1. The certificate therefore reads cleanly in print and on screen.

**Gold foil gradient** (for strokes, the seal, the name underline and the title caps): a linear gradient at 115° with stops `0% #7A5A12, 18% #D8B45A, 34% #F3E2A9, 50% #B8892F, 68% #F3E2A9, 84% #D8B45A, 100% #7A5A12`; add a 1 px lighter top edge and 1 px darker bottom edge on large text via two offset draws to imitate a bevel. In CSS, text can use [`background-clip: text`](https://developer.mozilla.org/en-US/docs/Web/CSS/background-clip); on the canvas use `createLinearGradient`. Optional soft foil sheen: a [conic-gradient](https://developer.mozilla.org/en-US/docs/Web/CSS/conic-gradient) at 6% opacity over the seal.

### 6.3 Composition (asymmetric)
Canvas 3300 x 2550, margin 140. Use a **~38 / 62 split** with the split deliberately off-centre:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│                                                         ✦ │
│▓ OXBLOOD / NAVY     ▓│  CERTIFICATE OF COMPLETION          (gold caps, tracked)  │
│▓ PANEL (x 0-1250)   ▓│  ──────── ✦ ────────                                       │
│▓                    ▓│  This certifies that                                       │
│▓  guilloche         ▓│                                                            │
│▓  rosette (large,   ▓│  Gabriele Example Name     ← Cormorant Garamond italic 600,│
│▓  gold hairlines,   ▓│  ═══════════════════════     ~210 px, navy on cream, gold   │
│▓  cropped by edge)  ▓│                              foil underline with end flourish│
│▓                    ▓│  has completed the free open course                         │
│▓      ( WAX SEAL )  ▓│  DEEP LEARNING FROM ZERO TO NEURAL CHESS ENGINE             │
│▓      overlapping   ▓│  (Fraunces 500 caps, navy)                                 │
│▓      the panel     ▓│  covering Python setup, neural-network foundations, CNNs,   │
│▓      edge          ▓│  sequence models, transformers and a neural chess evaluator.│
│▓                    ▓│                                                            │
│▓ Level ribbon:      ▓│  Date 24 November 2026        Certificate ID AK-7F3C-91B2   │
│▓ Beginner→Advanced  ▓│  ───────────────              ───────────────────           │
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│  small print (cream-on-cream 60%): self-issued certificate  │
└──────────────────────────────────────────────────────────────────────────────────┘
```
Details:
- **Left panel (0 to ~1250 px, full height):** deep navy `#0B1B3A → #10265A` vertical gradient with an oxblood diagonal band (`#4A0F1B → #6E1A2B`) crossing from lower-left to mid-right at roughly 8 degrees, so the panel itself is asymmetric. Carries the wordmark at top (cream), the large guilloche rosette and the seal. The panel's right edge is a **gold hairline double rule** with a notched, slightly scalloped edge cut (circles of 18 px radius along the edge at 60 px pitch).
- **Right field (~1250-3300 px):** parchment `#F6EFD9` with a very subtle paper-grain noise (3% opacity) and a faint guilloche band (gold at 12% opacity) running along the bottom 260 px as a footer ornament. A thin gold frame inset 110 px from the right/top/bottom edges, with **cut corners** (45-degree chamfers, 70 px). A small gold fleuron in the top-right corner only (not mirrored) maintains the asymmetry.
- **Seal overlap:** the wax-seal emblem sits at the panel/field boundary around (x 1250, y 1800), overlapping both so the composition "locks" together.
- **Text alignment:** all right-field text is **left-aligned** on a 1400 px start line (not centred): this is what makes the layout feel editorial rather than template-like. Only the seal and the ID row break the alignment.

### 6.4 Guilloche pattern (generated, resolution-independent)
Guilloche is the interlaced engraved line pattern used on banknotes and certificates ([Guilloché](https://en.wikipedia.org/wiki/Guilloch%C3%A9)). Generate it procedurally rather than shipping an image:
- **Rosette:** for `k` curves `i = 0..N-1` (N = 36 to 60) draw the parametric epitrochoid-like path `x(t) = (R - r) cos t + d cos(((R - r)/r) t + φ_i)`, `y(t) = (R - r) sin t - d sin(((R - r)/r) t + φ_i)` with `R = 520, r = 130..170, d = 90..140`, phase `φ_i = i * 2π / N`, `t ∈ [0, 2π·r/gcd]`. Stroke 1.6 px gold foil gradient at 55% opacity on the navy panel; draw twice with a 0.4 rotation offset for a moiré effect. Centre the rosette at about (x 520, y 1250) and let it bleed off the left edge.
- **Border band:** a sinusoidal wave band: `y(x) = A sin(ωx) + B sin(3ωx + φ)` for 5 phase-shifted strands, stroke 1 px, gold at 12% opacity on parchment.
- **Determinism:** seed any random choice from a hash of the name + date so the same inputs reproduce the same ID (and the pattern can vary subtly per person, like a security print).

### 6.5 Wax-seal emblem (own artwork)
Circular emblem, diameter ~420 px: irregular wax edge (a circle whose radius is modulated by a low-amplitude noise `r(θ) = R(1 + 0.04 sin 7θ + 0.025 sin 13θ + 0.015 sin 23θ)`), oxblood radial gradient (`#8E2A3E` centre → `#4A0F1B` edge), inner debossed ring (gold-edged, 6 px, inner shadow) and our own **node glyph** (three circles and lines) plus an abstract laurel of two curved leaf rows, all drawn in the gold gradient with a subtle emboss (offset light and dark shadows). A short ribbon tail (two angled tapering rectangles, navy with gold hairlines) hangs from the lower edge at 15 degrees. No existing crests, university seals or brand marks.

### 6.6 Typography on the certificate
| Element | Font | Size at 3300 px | Colour |
|---|---|---|---|
| "CERTIFICATE OF COMPLETION" | Cormorant Garamond 600 caps, tracking +0.28em | 72 px | gold foil gradient |
| "This certifies that" | Cormorant Garamond italic 500 | 64 px | `#4A463F` |
| **Name** | Cormorant Garamond italic 600 (fallback Fraunces italic) | 210 px, auto-shrinks to fit 1700 px width down to 120 px | `#0B1B3A` |
| Course title | Fraunces 500 caps, tracking +0.08em | 78 px | `#0B1B3A` |
| Description | Inter 400 | 46 px | `#4A463F` |
| Date and ID labels | Inter 600 caps tracking +0.14em | 34 px | `#7A5A12` |
| Small print | Inter 400 | 30 px | `#6B655A` |

Name handling: trim, collapse whitespace, max 48 characters, preserve diacritics and non-Latin scripts (fall back to a serif system font for glyphs the web font lacks), never auto-capitalise. Empty name shows a placeholder "Your Name" in 50% opacity in the preview and the download button stays disabled.

### 6.7 Download behaviour
- **PNG** via `canvas.toBlob('image/png')`, filename `ai-knowledge-certificate-<name-slug>.png`.
- **PDF** landscape Letter (or A4 toggle) with the PNG embedded at full resolution (use a tiny client-side PDF writer; no network).
- A **print stylesheet** (`@page { size: landscape; margin: 0 }`) so Ctrl+P also yields a clean page.
- The Name and Date are remembered in `localStorage` for convenience; the form offers "Clear".

### 6.8 Certificate on-screen preview polish
Preview sits on a `--surface-2` stage with `--sh-3`. On first reveal after completing the final lesson, the gold elements get a single left-to-right **foil sheen sweep** (a 20% white gradient highlight moving across in `--d-celebrate`), then rest. No confetti. Hovering the preview lifts it 4 px with the shadow growing; no 3D tilt (keeps it crisp and print-faithful).

---

## 7. Micro-interactions

All motion obeys §3.4 and is disabled or replaced by instant state changes under `prefers-reduced-motion: reduce`.

| Trigger | Interaction | Spec |
|---|---|---|
| Page load | Content fades up 8 px | `--d-slow`, `--ease-out`, stagger 40 ms for up to 6 items; never on subsequent in-page navigation |
| Top bar scroll | Hairline border and blur fade in after 8 px scroll | opacity 0 → 1 over `--d-fast` |
| Link hover | Underline opacity 25% → 100% | `--d-fast` |
| Button hover/press | Lift 1 px with deeper shadow; press returns to 0 | `--d-fast` |
| Card hover | translateY(-2px) and `--sh-1 → --sh-2` | `--d-base`; arrow icon nudges 3 px right |
| Path node current | One soft halo pulse on load, then still | 1 cycle, 1.2 s |
| Path connector | Completed segment "draws" down to the newly completed node | `stroke-dashoffset`, `--d-slow` |
| Progress ring change | Animated sweep from old to new value | `--d-slow`, `--ease-out`; number counts up |
| Mark complete | Circle fills, check strokes in, button turns success-soft; ring on path updates; toast "Saved in this browser" | total 400 ms; also fires a tiny scale pulse (1 → 1.04 → 1) on the lesson's ring |
| Module completed | Module header gets a gold hairline underline that draws left to right; a one-line toast "Module complete: Neural networks, from scratch" | 600 ms |
| Track completed | Medal icon in gold gradient appears beside the track name; one foil sheen sweep | 900 ms |
| Whole course completed | Banner on dashboard: "Course complete. Your certificate is ready." with `[Open certificate]`; certificate sheen sweep once | `--d-celebrate`; **no** confetti, sound or modal takeover |
| Citation hover | Preview card fades in 120 ms after hover or immediately on focus | `--d-fast`; card stays while pointer is over it |
| Citation jump | Target reference flashes `--accent-soft` | 1.2 s fade out |
| Glossary hover/focus | Card slides 4 px and fades in; closes on Esc | `--d-fast` |
| Math reveal next step | New line slides in 12 px from below with the changed term highlighted; older lines fade to 70% | `--d-base`; arrow keys supported |
| Quiz answer | Correct: row border turns success, check icon scales 0.6 → 1; incorrect: gentle 4 px horizontal shake once (skipped under reduced motion) and a hint appears | 240 ms |
| Copy code | Button label "Copy" → "Copied" with check | 1.5 s then reverts |
| Tab/OS switch | Underline indicator glides between segments; panel crossfades | `--d-base`; choice persisted |
| Search palette | Scale 0.98 → 1 and fade; results update as you type with 80 ms debounce | `--d-fast` |
| Keyboard focus | Visible ring appears instantly (no animation) | `--focus` token |
| Landing hero art | Slow value flow along edges every 6 s; hovering a node highlights its connections | paused when tab hidden or reduced motion |
| Section reveal on landing | Elements enter viewport with 12 px rise and fade, once | `IntersectionObserver`, `--d-slow` |

Haptics, sound, auto-playing video and parallax are **out**. Timers and streak counters are **out**.

---

## 8. Accessibility and quality checklist (for QA steps)

1. All text tokens meet WCAG 2.2 AA 4.5:1 as in §3.1; UI boundaries meet 3:1 ([SC 1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)); verified automatically in tests where possible.
2. Every interactive element is keyboard reachable with a visible `--focus` ring; target size at least 24 x 24 px (we use 40+) ([SC 2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)).
3. Colour is never the only signal (level shapes + words, status icons + words).
4. Semantic landmarks: `header`, `nav`, `main`, `aside`, `article`, `footer`; one `h1` per page; no skipped heading levels; "Skip to content" link first in tab order.
5. Progress rings use `role="meter"` or `progressbar` with labels; live regions announce mark-complete.
6. Hover cards are reachable by focus and click; Esc dismisses.
7. `prefers-reduced-motion` honoured everywhere; verified by toggling in devtools.
8. Body line length 60-75ch; checked at 1280, 1440, 1920 px viewports.
9. Images (screenshots) have meaningful `alt`; annotation pins are in the DOM as a numbered list.
10. The site works with JavaScript disabled for reading (articles, references, glossary static); only progress, reveals, quizzes and certificate need JS.
11. Zero third-party network requests at runtime (fonts and KaTeX self-hosted; outbound links only on click).

---

## 9. Voice and content conventions that the UI depends on

- **Titles** are noun phrases in sentence case ("Gradient descent", not "How To Understand Gradient Descent!").
- **Leads** define, then motivate; **summaries** are 3-5 bullets; **analogies** appear after the formal statement, never instead of it.
- **Setup pages** present numbered steps, each with: the exact link ("Open https://www.python.org/downloads/"), an annotated screenshot, and a "What you should see" line plus a "If you see something else" accordion.
- **Math pages** follow: intuition (analogy) → tiny numeric example → symbols one at a time (C6) → general formula → code that computes the same thing.
- **Citations:** at least one per factual paragraph on average, primary sources preferred (papers, official docs), Wikipedia acceptable for definitions; no "citation needed" placeholders may ship.
- **Badges/time:** each lesson front-matter provides `level`, `minutes`, `prereqs[]`, `tools[]`, `outcomes[]`, `next`, `reviewed` date; the infobox and cards are generated from them (single source of truth).
- **Honesty clauses:** progress is local; the certificate is a self-issued completion certificate; datasets are downloaded at run time under their own terms.

---

## 10. What "original identity" means here (guardrails for workers)

- Do **not** use any brand name, logo, mascot, character, icon set or illustration style from Brilliant, Duolingo, Linear, Stripe, Vercel, Notion or Wikipedia. Do not use Wikipedia's globe, its Vector skin colours, or its blue-link-on-white look; we use only its **structure** (lead, infobox, hatnote, citations, References).
- Do not copy copy: all wording is ours.
- Icons: draw our own simple 1.75 px-stroke line icons or use an open-licensed set (e.g. a permissively licensed icon library installed as a dependency) and record the licence in the README.
- Illustrations: produced as inline SVG from geometric primitives (circles, lines, rounded rects) in the token palette; no stock photos, no AI-generated art.
- Distinguishing traits to preserve across pages: warm paper background, Fraunces display headings with hairline rules, ultramarine accent, shape-coded level badges, gold leaf reserved for achievement.

---

## 11. Handoff checklist for downstream steps

| Step | Must read in this brief |
|---|---|
| Scaffold / design system | §3 tokens (put them in `src/styles/tokens.css`), §4 component list, §8 checklist |
| Landing page | §5.1, §6.1, §7 |
| Dashboard, tracks, library, glossary, search | §5.2, §5.4-5.6, C1-C3, C9, C12 |
| Lesson layout and content schema | §1.2, §4 (C4-C8, C10), §5.3, §9 (front-matter fields) |
| Certificate generator | §5.7, §6, C10 completion gating, §7 |
| Content writers | §1.2, §9, C5 variants, C7 rules |
| QA | §8, contrast table in §3.1, §10 |

Open items intentionally left to implementers (low risk): final icon library choice (record licence), KaTeX vs MathML rendering (KaTeX self-hosted recommended), the PDF writer library for the certificate, exact illustration drawings for project tiles.

---

## Sources

Fetched or checked (HTTP 200) on 2026-11-24. Social/marketing sites were read as public pages only.

**Learning UX**
- Brilliant home page: <https://brilliant.org>; courses/topics: <https://brilliant.org/courses/>; about: <https://brilliant.org/about/>
- Brilliant, "How Brilliant teaches math": <https://brilliant.org/resources/choosing-brilliant/how-brilliant-teaches-math/>; "Why Brilliant": <https://brilliant.org/help/why-brilliant/>
- Wikipedia, Brilliant (website): <https://en.wikipedia.org/wiki/Brilliant_%28website%29>
- Duolingo blog, "Introducing the new Duolingo learning path": <https://blog.duolingo.com/new-duolingo-home-screen-design/>; Duolingo design hub: <https://blog.duolingo.com/hub/design/>
- NBC News, Duolingo redesign interview: <https://www.nbcnews.com/tech/tech-news/duolingos-update-redesign-luis-von-ahn-interview-rcna44655>
- uxdesign.cc critique (summary only, member-only article): <https://uxdesign.cc/duolingos-redesign-4-things-they-got-right-1-possible-improvement-acec8af9ec10>
- Wikipedia, [Gamification](https://en.wikipedia.org/wiki/Gamification), [Zeigarnik effect](https://en.wikipedia.org/wiki/Zeigarnik_effect), [Cognitive load](https://en.wikipedia.org/wiki/Cognitive_load), [Spaced repetition](https://en.wikipedia.org/wiki/Spaced_repetition), [Hick's law](https://en.wikipedia.org/wiki/Hick%27s_law), [Fitts's law](https://en.wikipedia.org/wiki/Fitts%27s_law)
- Nielsen Norman Group: [Progressive disclosure](https://www.nngroup.com/articles/progressive-disclosure/), [Minimize cognitive load](https://www.nngroup.com/articles/minimize-cognitive-load/)

**Wikipedia style**
- [Manual of Style](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style), [Lead section](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Lead_section), [Layout](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Layout), [Linking](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Linking), [Hatnote](https://en.wikipedia.org/wiki/Wikipedia:Hatnote), [Help:Footnotes](https://en.wikipedia.org/wiki/Help:Footnotes), [Help:Infobox](https://en.wikipedia.org/wiki/Help:Infobox)

**Premium light-theme references (patterns only)**
- <https://linear.app>, <https://stripe.com/docs>, <https://vercel.com>, <https://www.notion.com>

**Readability and accessibility**
- Baymard, line length: <https://baymard.com/blog/line-length-readability>; Butterick, line length: <https://practicaltypography.com/line-length.html>
- WCAG 2.2 Understanding: [Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html), [Non-text Contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html), [Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html), [Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html), [Focus Appearance](https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html)
- WAI-ARIA Authoring Practices: [Tooltip](https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/), [Dialog (modal)](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/), [Meter](https://www.w3.org/WAI/ARIA/apg/patterns/meter/), [Disclosure](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/)
- MDN: [prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion), [Popover API](https://developer.mozilla.org/en-US/docs/Web/API/Popover_API), [localStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage), [Canvas 2D](https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D), [canvas.toBlob](https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement/toBlob), [background-clip](https://developer.mozilla.org/en-US/docs/Web/CSS/background-clip), [conic-gradient](https://developer.mozilla.org/en-US/docs/Web/CSS/conic-gradient), [oklch()](https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/oklch)

**Fonts (all via Fontsource)**
- [Install guide](https://fontsource.org/docs/getting-started/install); [Fraunces](https://fontsource.org/fonts/fraunces), [Inter](https://fontsource.org/fonts/inter), [JetBrains Mono](https://fontsource.org/fonts/jetbrains-mono), [Cormorant Garamond](https://fontsource.org/fonts/cormorant-garamond), [Pinyon Script](https://fontsource.org/fonts/pinyon-script), [Newsreader](https://fontsource.org/fonts/newsreader), [Source Serif 4](https://fontsource.org/fonts/source-serif-4), [Instrument Serif](https://fontsource.org/fonts/instrument-serif)

**Certificate motifs**
- Wikipedia: [Guilloché](https://en.wikipedia.org/wiki/Guilloch%C3%A9), [Gold leaf](https://en.wikipedia.org/wiki/Gold_leaf), [Seal (emblem)](https://en.wikipedia.org/wiki/Seal_%28emblem%29)

*Limitations:* Duolingo's main page and parts of its blog returned little or no readable text to a non-browser fetch, so Duolingo observations rest on its path-introduction blog post and press coverage; Brilliant's claims are limited to what its public pages state (marketing statements, not independent evidence). Linear, Stripe, Vercel and Notion were used as pattern inspiration only, not analysed in detail by script. The goal-gradient effect is not cited because a dedicated Wikipedia page was not available (404); progress rings are justified here as a design choice, not a sourced claim.
