/**
 * Tiny inline renderer for short strings that come from frontmatter (exercise prompts,
 * options, explanations): escapes HTML, then supports `code`, **bold**, *italic*,
 * [text](https://link) and $inline math$ (KaTeX). Nothing else; keep frontmatter text short.
 */
import katex from 'katex';
import { katexOptions } from './katex-options.mjs';

const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

export function inlineMd(input: string | number | undefined | null): string {
  if (input === undefined || input === null) return '';
  const text = String(input);
  const parts: string[] = [];
  // Split out math and code first so their contents are not touched by other rules.
  const re = /(\$[^$\n]+\$|`[^`\n]+`)/g;
  let last = 0;
  let m: RegExpExecArray | null;
  while ((m = re.exec(text))) {
    parts.push(rest(text.slice(last, m.index)));
    const tok = m[0];
    if (tok.startsWith('$')) parts.push(katex.renderToString(tok.slice(1, -1), { ...katexOptions, displayMode: false }));
    else parts.push(`<code>${esc(tok.slice(1, -1))}</code>`);
    last = m.index + tok.length;
  }
  parts.push(rest(text.slice(last)));
  return parts.join('');
}

function rest(s: string): string {
  return esc(s)
    .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+|\/[^)\s]*)\)/g, '<a href="$2">$1</a>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/(^|[^*])\*([^*\s][^*]*)\*/g, '$1<em>$2</em>')
    .replace(/\n{2,}/g, '<br><br>');
}
