# Changelog

Font version numbers are written as in the font files (`1.100`). Repository tags use the same number with a leading `v` (`v1.100`).

## 1.100 - first public release

Four families, 40 static fonts (TTF and WOFF2).

### Families
- Geist Rounded by Nortics (sans, 11 weights) and Geist Rounded Mono by Nortics (9 weights): rounded corners, radius 20/1000 em.
- Geist Sharp by Nortics (sans, 11 weights) and Geist Sharp Mono by Nortics (9 weights): same design with square corners.

### Design
- New terminals on `t l J j f` (flat foot, tight outer curve); in the Mono the typewriter `l`, `i`, `j` flags are kept.
- Hyphen, en dash and em dash 50% longer (limited by the cell in the Mono).
- Spacing tightened by 0.020 em per character (Mono cell 600 → 580).
- New weights: 150 UltraLight (sans) and 250 SemiLight (sans and Mono).
- Arrow ligatures `->` `-->` `--->` `<-` `<--` `<---` `<->` `<-->` `<--->`; added `<-->` and `<--->` (sans and Mono) and `<---` (Mono).
- Fixed the Geist Mono ligature advance so every ligature occupies N cells and columns stay aligned.

### Technical
- Overlaps removed; hinting removed; static TrueType only (no variable font, no italics).
- RIBBI naming, unique weight classes, vertical metrics 1111 / -225 / 0 with `USE_TYPO_METRICS`.
- Designer metadata: Andre Dorneles; manufacturer Nortics; vendor ID `NRTC`.

### Documentation
- Specification, design changes, OpenType features, glyph coverage, usage, build, QA and licensing guides in `docs/`.
- Build, packaging and QA scripts in `source/`.
