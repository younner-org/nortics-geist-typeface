# Contributing

Thanks for your interest in Nortics Geist. Issues and pull requests are welcome.

## Reporting a problem

Open an issue (there is a template) with:

- the font file name and version (for example `GeistRoundedMonoByNortics-Regular.ttf`, 1.100);
- the exact text that shows the problem, ideally as a screenshot;
- the application and operating system, and whether you use the TTF or the WOFF2.

Rendering problems that also appear in the original Geist belong upstream: <https://github.com/vercel/geist-font>.

## Proposing a change

1. **Fonts are generated, not edited.** Do not edit the `.ttf`/`.woff2` files directly. Change the scripts in `source/` (see [docs/BUILD.md](docs/BUILD.md)) and rebuild.
2. Regenerate what depends on the fonts: `make_woff2.py`, `gen_web.py`, `gen_docs.py` and, if the look changed, `make_images.py`.
3. Run the QA scripts (`qa_names.py`, `qa_arrows.py`, `qa_audit.py`) and compare with [docs/QA.md](docs/QA.md). Do not make the results worse without explaining why; update `docs/QA.md` when the numbers legitimately change.
4. Describe the visual effect of the change (before/after images are very helpful) and add an entry to [CHANGELOG.md](CHANGELOG.md).

## Rules for fonts in this repository

- Only fonts derived from **OFL-licensed** sources may live in `fonts/`. Never add fonts under a different license, trial fonts or commercial fonts, and never add glyph outlines copied from them.
- Keep the copyright notice and the license in the font metadata and in [OFL.txt](OFL.txt).
- Do not use a Reserved Font Name of any upstream project in a new family name.
- By contributing you agree that your contribution is released under the same terms as the part of the project it touches: **OFL 1.1** for fonts, **MIT** for scripts and documentation (see [LICENSE.md](LICENSE.md)).

## Code style

Plain Python 3, no heavy dependencies beyond those in `source/requirements.txt`. Keep scripts runnable from the command line with `--help` or a docstring, and avoid hard-coded personal paths.
