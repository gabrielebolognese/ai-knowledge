# Bundled data: sources and licences

Everything in this folder is committed to the repository on purpose, because each
file's licence allows redistribution. Larger datasets (TinyShakespeare, SST-2) are
**not** committed; the scripts download them into `../data/` (git-ignored).

| File | What | Source | Licence | Changes |
|---|---|---|---|---|
| `names.txt` | 32,033 lowercase first names, one per line (228,145 bytes) | Andrej Karpathy, [makemore](https://github.com/karpathy/makemore) (`names.txt`), built from the US Social Security Administration's [baby-name data](https://www.ssa.gov/oact/babynames/limits.html) | The file is distributed in the makemore repository under the **MIT licence** (copy in `makemore-LICENSE.txt`). The underlying SSA name counts are a work of the US federal government and are in the public domain in the US. | None (byte-for-byte copy, fetched 2026-11-25) |
| `sentiment-labelled-sentences/` | 3,000 review sentences labelled 1 (positive) / 0 (negative): 1,000 each from Amazon, Yelp and IMDb | D. Kotzias, M. Denil, N. de Freitas, P. Smyth, *From Group to Individual Labels Using Deep Features*, KDD 2015. Downloaded from the [UCI Machine Learning Repository, dataset 331](https://archive.ics.uci.edu/dataset/331/sentiment+labelled+sentences), [doi:10.24432/C57604](https://doi.org/10.24432/C57604) | **CC BY 4.0** ([licence text](https://creativecommons.org/licenses/by/4.0/)), as stated on the UCI page | The three `.txt` files and `readme.txt` are unchanged; the macOS metadata files in the zip (`__MACOSX/`, `.DS_Store`) were left out |
| `challenge.tsv` | 48 short sentences written for this course to probe negation and contrast ("not good", "boring at first, but ...") | Own work, AI Knowledge course | **CC0 1.0** ([public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/)) | n/a |

## Required attribution (CC BY 4.0)

> Sentiment Labelled Sentences, by Dimitrios Kotzias, Misha Denil, Nando de Freitas
> and Padhraic Smyth (2015), UCI Machine Learning Repository,
> https://doi.org/10.24432/C57604, licensed under CC BY 4.0. Redistributed unchanged.

## Not bundled (downloaded at run time)

- **TinyShakespeare** (`input.txt`, 1,115,394 characters), from
  [karpathy/char-rnn](https://github.com/karpathy/char-rnn). Shakespeare's plays are in
  the public domain; the repository is MIT-licensed. Downloaded rather than bundled only to
  keep the repository small.
- **SST-2** (Stanford Sentiment Treebank, binary version from the GLUE benchmark,
  [SST-2.zip](https://dl.fbaipublicfiles.com/glue/data/SST-2.zip)). Socher et al., 2013,
  https://aclanthology.org/D13-1170/. The dataset does not state a licence (the Hugging
  Face card says "unknown"), so the course only downloads it for study and cites the paper;
  it is never redistributed.
