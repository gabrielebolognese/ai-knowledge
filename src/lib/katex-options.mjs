// Shared KaTeX options for rehype-katex (inline/display $...$ math) and <MathSteps>/<Step>.
// \hl{...} highlights the term that changed in a step (styled by .hl in global.css).
/** @type {import('katex').KatexOptions} */
export const katexOptions = {
  throwOnError: false,
  strict: 'ignore',
  output: 'htmlAndMathml',
  trust: (context) => context.command === '\\htmlClass',
  macros: {
    '\\hl': '\\htmlClass{hl}{#1}',
    '\\R': '\\mathbb{R}',
  },
};
