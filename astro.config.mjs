// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import { unified } from '@astrojs/markdown-remark';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import remarkLesson from './src/lib/remark-lesson.mjs';
import { katexOptions } from './src/lib/katex-options.mjs';

// Static, read-only site. No server, no database: progress lives in localStorage.
export default defineConfig({
  site: 'https://gabrielebolognese.github.io',
  output: 'static',
  trailingSlash: 'ignore',
  build: { format: 'directory' },
  markdown: {
    // Astro 7 defaults to the Sätteri processor; lessons need remark/rehype plugins
    // (math, citation numbering), so use the unified pipeline.
    processor: unified({
      remarkPlugins: [remarkMath, remarkLesson],
      rehypePlugins: [[rehypeKatex, katexOptions]],
    }),
    shikiConfig: {
      // Colours come from CSS variables mapped to the design tokens (src/styles/tokens.css).
      theme: 'css-variables',
      wrap: false,
    },
  },
  integrations: [mdx()],
  devToolbar: { enabled: false },
});
