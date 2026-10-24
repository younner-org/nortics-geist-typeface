# Quality assurance

What was verified on the shipped files (version 1.100), how to repeat it, and what is known not to be perfect. Commands are in [BUILD.md](BUILD.md).

## 1. Summary

| Check | Result |
| --- | --- |
| Names, weights, RIBBI rules, `fsSelection`/`macStyle`, designer, vendor ID (`qa_names.py`) | **40 / 40 fonts, no problems** |
| Unique `usWeightClass` per family and unique PostScript names | **yes** |
| Arrow ligatures: 9 sequences, one ligature glyph, advance = characters x 580 (`qa_arrows.py`) | **9/9 in all 40 fonts** |
| Language sets English, Portuguese, Spanish (also French, Italian, German) | **fully mapped in all 40 fonts** |
| WOFF2 files identical in content to their TTF (glyphs, weight, name, metrics) | **40 / 40** |
| Browser load test of `web/webfonts.css` | **40 / 40 faces loaded, 0 errors** |
| Remaining sharp corners, Rounded families (`qa_audit.py`) | see section 2 |

## 2. Corner audit (Rounded families)

A *corner* is a vertex where the outline turns by 20° or more and both neighbouring segments are at least 8 units long. Shorter segments are counted as *micro* irregularities (grid quantization of tiny arcs, see section 4). Source: `qa_audit.py`.

| Font | Glyphs checked | Glyphs with a corner | Corners | Micro |
| --- | ---: | ---: | ---: | ---: |
| Sans Thin | 973 | 0 | 0 | 441 |
| Sans UltraLight | 973 | 0 | 0 | 283 |
| Sans ExtraLight | 973 | 0 | 0 | 150 |
| Sans SemiLight | 973 | 0 | 0 | 236 |
| Sans Light | 973 | 0 | 0 | 162 |
| Sans Regular | 973 | 0 | 0 | 299 |
| Sans Medium | 973 | 0 | 0 | 186 |
| Sans SemiBold | 973 | 0 | 0 | 212 |
| Sans Bold | 973 | 0 | 0 | 244 |
| Sans ExtraBold | 973 | 1 (`B`) | 1 | 187 |
| Sans Black | 973 | 0 | 0 | 353 |
| Mono Thin | 1157 | 7 (ligatures) | 17 | 334 |
| Mono ExtraLight | 1157 | 0 | 0 | 210 |
| Mono SemiLight | 1157 | 0 | 0 | 175 |
| Mono Light | 1157 | 0 | 0 | 242 |
| Mono Regular | 1157 | 0 | 0 | 171 |
| Mono Medium | 1157 | 0 | 0 | 203 |
| Mono SemiBold | 1157 | 2 (ligatures) | 6 | 210 |
| Mono Bold | 1157 | 3 (ligatures) | 7 | 212 |
| Mono ExtraBold | 1157 | 0 | 0 | 207 |

For comparison, the original Geist Regular has about 8,000 corners by the same measure. The Sharp families are not audited: they keep the original corners by design.

## 3. How to repeat

```
python source/qa_names.py "fonts/*/ttf/*.ttf"
for each family dir:  python source/qa_arrows.py fonts/<family>/ttf
python source/qa_audit.py "fonts/geist-rounded-by-nortics/ttf/*.ttf" "fonts/geist-rounded-mono-by-nortics/ttf/*.ttf"
python source/gen_docs.py        # regenerates the language and block coverage tables
```

## 4. Known limitations

- **Residual corner in the sans ExtraBold `B`** (1 corner). It is a join the rounding step could not resolve cleanly.
- **Mono ligatures:** in Thin (7 glyphs), SemiBold (2) and Bold (3) a few text ligatures (`%%`, `###`, `</>`, `!?`, `|=`...) keep corners of 20-23°. They are arcs of 10-12 units straddling the 20° detection threshold, not square corners, and they are rarely used.
- **Micro irregularities:** TrueType stores integer coordinates, so very small arcs (about 10 units) cannot be perfectly smooth; the deviation is at most 1 unit (about 0.7 px at 700 px font size). This is what the *Micro* column counts.
- **Kerning and mark anchors were not adjusted for the spacing change.** Kerning pairs keep their upstream values (on top of the new, tighter spacing), and mark-to-base anchors stayed at their old coordinates while base glyphs moved 10 units to the left, so combining accents typed as separate characters sit up to 10 units (1% of the em) to the right of the ideal position. Precomposed accented letters are not affected.
- **Unhinted:** all glyph programs were removed; very low-resolution GDI rendering looks softer than with a hinted font.
- **No italics and no variable font** are provided.
- **Non-Latin scripts** were not reviewed by hand (see [GLYPH-COVERAGE.md](GLYPH-COVERAGE.md)).
- **Mono dashes** are limited by the fixed cell: hyphen +50%, en dash +45% and em dash +7% relative to Geist Mono.

## 5. Reporting a problem

Open an issue with the font file name, the text that shows the problem, the application and operating system, and a screenshot if possible. See [CONTRIBUTING.md](../CONTRIBUTING.md).
