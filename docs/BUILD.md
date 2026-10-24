# Building the fonts

Every font in `fonts/` is produced by the scripts in [`source/`](../source/) from the two upstream variable fonts. Nothing is edited by hand.

## Requirements

Python 3.10+ and:

```
pip install -r source/requirements.txt
```

| Package | Used for | Version used for the shipped files |
| --- | --- | --- |
| `fonttools` | reading/writing fonts, instancing, name table | 4.63.0 |
| `brotli` | WOFF2 output | 1.2.0 |
| `skia-pathops` | overlap removal | 0.9.2 |
| `freetype-py`, `pillow`, `uharfbuzz` | QA and the specimen images only | 2.5.1 / 13.0.0 / 0.57.0 |

The shipped files were built with Python 3.14.3. Other versions of fontTools or skia-pathops may produce files that differ by a few bytes; the design is the same.

## 1. Get the upstream fonts

From [vercel/geist-font](https://github.com/vercel/geist-font) (SIL OFL 1.1):

```
fonts/Geist/variable/Geist[wght].ttf
fonts/GeistMono/variable/GeistMono[wght].ttf
```

## 2. Build the TTFs

```
python source/build_family.py --geist-vf "Geist[wght].ttf" --geist-mono-vf "GeistMono[wght].ttf" --out build
```

Output: `build/rounded/*.ttf` and `build/sharp/*.ttf` (20 fonts each; about 40 s per font).

| Option | Meaning |
| --- | --- |
| `--style` | `rounded`, `sharp` or `all` (default): which corner style to build |
| `--kind` | `sans`, `mono` or `all` (default) |
| `--sub` | a single weight by subfamily name, e.g. `Regular` (handy for testing) |
| `--radius` | corner radius in font units, Rounded only (default 20) |
| `--track` | spacing removed per character in font units (default 20) |

All names, weights, vertical metrics, the version and the credits are constants at the top of `build_family.py`.

## 3. Package

Copy the TTFs into `fonts/<family>/ttf/` (family folders: `geist-rounded-by-nortics`, `geist-rounded-mono-by-nortics`, `geist-sharp-by-nortics`, `geist-sharp-mono-by-nortics`), then:

```
python source/make_woff2.py fonts          # fonts/<family>/woff2/
python source/gen_web.py                   # web/webfonts.css, web/specimen.html
python source/gen_docs.py                  # docs/SPECIFICATION.md, OPENTYPE-FEATURES.md, GLYPH-COVERAGE.md
python source/make_images.py --fonts fonts --out docs/images --geist-vf "Geist[wght].ttf"
```

## 4. Verify

```
python source/qa_names.py "fonts/*/ttf/*.ttf"                 # names, unique weights, RIBBI, metadata
python source/qa_arrows.py fonts/geist-rounded-mono-by-nortics/ttf   # arrow ligatures (run per family)
python source/qa_audit.py "fonts/geist-rounded-by-nortics/ttf/*.ttf" # remaining sharp corners
```

The expected results and the known exceptions are in [QA.md](QA.md).

## How the pipeline is organised

| File | Role |
| --- | --- |
| `build_family.py` | orchestration, names and metrics |
| `designs.py` | hand-designed `t l J j f` and the dashes |
| `arrows.py` | Mono ligature fix, new arrow ligatures |
| `fontround.py` | outline model, corner rounding, corner audit |
| `tracking.py` | spacing |
| `render_text.py`, `qa_*.py`, `make_images.py` | QA and documentation tools |
