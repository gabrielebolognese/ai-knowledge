// Remark plugin for lessons (runs on .md and .mdx).
//  - Numbers <Cite id="..."/> by first use, like Wikipedia footnotes, and injects
//    `n` (reference number) and `k` (occurrence index, for the a/b/c back-links).
//  - Exposes the order to the layout via remarkPluginFrontmatter:
//      citeOrder: string[]               ids in first-use order
//      citeCounts: Record<id, number>    how many times each id is cited
//      inlineExercises: string[]         ids of <Exercise id> placed in the body
//      hasDisplayMath: boolean
//  No external visitor dependency: a tiny recursive walk is enough.

function attr(node, name) {
  const a = (node.attributes || []).find((x) => x.type === 'mdxJsxAttribute' && x.name === name);
  if (!a) return undefined;
  return typeof a.value === 'string' ? a.value : undefined;
}

function setAttr(node, name, value) {
  node.attributes = (node.attributes || []).filter((x) => !(x.type === 'mdxJsxAttribute' && x.name === name));
  node.attributes.push({ type: 'mdxJsxAttribute', name, value: String(value) });
}

function walk(node, fn) {
  fn(node);
  if (node.children) for (const child of node.children) walk(child, fn);
}

export default function remarkLesson() {
  return (tree, file) => {
    const order = [];
    const counts = {};
    const inlineExercises = [];
    let hasDisplayMath = false;

    walk(tree, (node) => {
      if (node.type === 'math') hasDisplayMath = true;
      if (node.type !== 'mdxJsxTextElement' && node.type !== 'mdxJsxFlowElement') return;
      if (node.name === 'Cite') {
        const id = attr(node, 'id');
        if (!id) return;
        if (!(id in counts)) {
          order.push(id);
          counts[id] = 0;
        }
        counts[id] += 1;
        setAttr(node, 'n', order.indexOf(id) + 1);
        setAttr(node, 'k', counts[id]);
      } else if (node.name === 'Exercise') {
        const id = attr(node, 'id');
        if (id) inlineExercises.push(id);
      } else if (node.name === 'MathSteps') {
        hasDisplayMath = true;
      }
    });

    file.data.astro ??= {};
    file.data.astro.frontmatter ??= {};
    Object.assign(file.data.astro.frontmatter, {
      citeOrder: order,
      citeCounts: counts,
      inlineExercises,
      hasDisplayMath,
    });
  };
}
