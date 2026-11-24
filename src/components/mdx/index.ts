// Components available in every lesson MDX file without imports.
// Passed to <Content components={mdxComponents} /> by the lesson page.
import Infobox from './Infobox.astro';
import Analogy from './Analogy.astro';
import MathSteps from './MathSteps.astro';
import Step from './Step.astro';
import Cite from './Cite.astro';
import Term from './Term.astro';
import Figure from './Figure.astro';
import Screenshot from './Screenshot.astro';
import Callout from './Callout.astro';
import Exercise from './Exercise.astro';
import CodeFile from './CodeFile.astro';

export const mdxComponents = { Infobox, Analogy, MathSteps, Step, Cite, Term, Figure, Screenshot, Callout, Exercise, CodeFile };
export { Infobox, Analogy, MathSteps, Step, Cite, Term, Figure, Screenshot, Callout, Exercise, CodeFile };
