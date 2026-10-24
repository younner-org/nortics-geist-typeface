# Design changes relative to Geist

Everything that was changed from the upstream Geist fonts, with the parameters used. `w` is the vertical stem width of the weight being built, `th` the horizontal stroke thickness, `xh` the x-height. Units are font units (1000 per em). The source of every step is in [`source/`](../source/).

## 0. Source

| Item | Value |
| --- | --- |
| Upstream | [vercel/geist-font](https://github.com/vercel/geist-font), `Geist[wght].ttf` and `GeistMono[wght].ttf` (variable fonts, wght 100-900), Geist 1.800 |
| Method | each static font is an **instance** of the upstream variable font at `wght` = the weight value of the file (`fontTools.varLib.instancer`) |
| Sans weights | 100, 150, 200, 250, 300, 400, 500, 600, 700, 800, 900 |
| Mono weights | 100, 200, 250, 300, 400, 500, 600, 700, 800 (900 is not built) |

The build order for each font is: instance → remove overlaps → hand-designed glyphs → dashes → arrows → corner rounding (Rounded only) → spacing → names and metrics. See [BUILD.md](BUILD.md).

## 1. Overlap removal

Variable-font instances contain overlapping contours. They are merged with skia-pathops before any other step so that the intersection points become real vertices. Without this the corner rounding would miss the corners where two strokes meet.

## 2. Hand-designed terminals (`t l J j f`)

The upstream letters end in wide, U-shaped hooks (outer radius about 1.6 w). They are redrawn as a flat foot with a tight outer curve. The new outlines are generated from measurements taken from each weight, so they follow the weight from Thin to Black. The same shapes propagate to every glyph that reuses the base outline: `ĺ ľ ļ ł ť ţ ț ŧ ĵ Ĵ Ĳ ﬁ ﬂ` and the `ff`/`tt` ligatures.

| Glyph | Sans | Mono |
| --- | --- | --- |
| **t** | stem `w`; crossbar from `xh - th` to `xh`, left end unchanged, right end = max(original end, stem + 1.0 w); flat foot of thickness `th` to the same right end; outer curve radius `min(0.95 w, xh - th - 5)` | same |
| **l** | stem `w`; flat foot of thickness `th`, tail 0.94 w beyond the stem; outer curve radius 0.95 w | **unchanged**: the typewriter `l`, `i`, `I`, `j` flags keep `I`, `l` and `1` distinguishable in code |
| **J** | stem on the right; flat foot 2.0 w long to the left, left side bearing 0.65 w; outer curve radius 0.95 w; advance recomputed keeping the original right side bearing | foot 2.2 w long, glyph centered in the cell |
| **j** | drawn from the dotless `ȷ`; foot reaches the original left end; outer curve radius 0.95 w (`j`, `ĵ` inherit it) | keeps the typewriter flag at x-height, only the foot is redrawn |
| **f** | hook outer radius `min(0.95 w, top - xh - 10)`, vertical terminal of thickness `th`; terminal and crossbar end at the same x | same |

`th` is measured per weight as the length of the left-most vertical edge of the upstream `f` crossbar; `xh` is the height of the upstream `x`. Where the new shape is wider than the old one, the advance width is increased by the difference.

## 3. Dashes

| Glyph | Sans | Mono (cell 600 → 580 after spacing) |
| --- | --- | --- |
| hyphen | length x 1.5 (331 → 497), extends to the right, advance grows by the difference | x 1.5, cap 540 |
| en dash | x 1.5 (503 → 755) | x 1.5, cap 580 |
| em dash | x 1.5 (819 → 1229) | x 1.5, cap 600 (the full cell) |

All three are scaled so that the hyphen < en dash < em dash hierarchy survives. The Mono cannot grow beyond its fixed cell, so its en dash and em dash are limited by the caps above. The lengths above are for the Regular weight; every weight is lengthened by the same factor (x 1.5).

## 4. Corner rounding (Rounded families only)

Radius **R = 20** font units (0.020 em). The Sharp families skip this step.

1. Every glyph is flattened (composites are decomposed) into simple outlines.
2. A vertex is a **corner** when the tangents of its two neighbouring segments turn by 12° or more. This includes line-to-line, line-to-curve and curve-to-curve joins.
3. For each corner the tangent length is `t = R · tan(turn / 2)`, limited to `3 R`.
4. Each segment may give away at most 92% of its length to the corners at its two ends; if two corners compete, both `t` values are scaled down proportionally (so short edges get a smaller radius than 20). A fillet is skipped when `t < 0.8`.
5. The neighbouring segments are trimmed by `t` (curves are cut at the equivalent arc length with exact sub-curve extraction) and the gap is filled with a fillet:
   - line-to-line: a circular arc of radius `t / tan(turn / 2)` split into pieces of at most 45°, each piece one quadratic Bezier with the exact circle tangent control point;
   - other joins: a single quadratic Bezier whose control point is the intersection of the two end tangents (a straight chamfer if the tangents do not intersect sensibly).
6. The result is tangent-continuous at every join. Glyph programs (hinting) are removed in the process.

Consequences: thin weights and short edges get a smaller effective radius; very sharp spikes are rounded with a radius smaller than 20.

## 5. Spacing

**-20 font units per character** (-0.020 em), split evenly on both sides of each glyph.

- Plain glyphs: advance width -20, outline moved 10 units to the left.
- Grid ligatures (arrows and the Mono code ligatures): one uniform horizontal scale of 580/600 about the origin, so every cell shrinks by 20 and nothing is cut or sheared.
- Mono: the cell goes from 600 to **580**; the few symbols that were 500 wide in Geist Mono become 480 wide.
- Kerning (GPOS) was not rescaled, and mark-to-base anchors were not moved (see [QA.md](QA.md), known limitations).

## 6. Arrow ligatures

Inherited from Geist: `->` `-->` `--->` `<-` `<--` `<->` (and, in the sans, `<---`).

Added by this project, built by stretching the shaft of an existing double arrow and registering the rule in the `liga` lookup:

| Sequence | Sans | Mono |
| --- | --- | --- |
| `<---` | inherited | **added** |
| `<-->` | **added** | **added** |
| `<--->` | **added** | **added** |

Mono ligature fix: upstream draws an N-character ligature hanging back N-1 cells but advances a single cell, so the arrow overlaps the previous character. Each affected glyph (69 in the `liga` lookup) is rebased to its own origin and advances N cells, which keeps monospaced columns aligned. The full list is in [OPENTYPE-FEATURES.md](OPENTYPE-FEATURES.md).

## 7. Weights

Two intermediate weights were added: **150 UltraLight** (sans) and **250 SemiLight** (sans and mono). SemiLight is the exact midpoint between ExtraLight and Light: stem width 59 between 50 and 68 in the sans, 56 between 48 and 64 in the Mono.

## 8. Metrics, naming and metadata

- Units per em 1000. `hhea` and OS/2 typo: ascender **1111**, descender **-225**, line gap 0, `USE_TYPO_METRICS` on, so the default line height is 1.336 em. (The Geist statics compared during development used 1005 / -295.) `usWin*` are computed per font from the glyph extents.
- Names follow the RIBBI rule; the four families have distinct names. Designer: **Andre Dorneles**; manufacturer: Nortics; vendor ID `NRTC`; version 1.100. The Geist copyright line is preserved. Details: [SPECIFICATION.md](SPECIFICATION.md).
- No hinting, no italics, no variable font.

## 9. What was not changed

- Kerning and mark positioning values, OpenType lookups other than the arrow ligatures, and the stylistic sets are inherited as they are.
- Other scripts (for example Cyrillic and Greek) are only touched by the automatic steps (overlap removal, corner rounding, spacing).
- Alternate glyphs (stylistic sets) get the automatic steps; the hand-drawn terminals appear in them only where they reuse the base outline.
