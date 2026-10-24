# OpenType features

OpenType layout features of **Nortics Geist 1.100**, read from the shipped fonts by [`source/gen_docs.py`](../source/gen_docs.py).

## 1. Feature matrix

A tick means the feature tag is present in the GSUB/GPOS table of the family's Regular. The feature set is inherited from Geist / Geist Mono; the lookups are unchanged except for the arrow ligatures described in section 2.

| Tag | Description | Table | Geist Rounded by Nortics | Geist Rounded Mono by Nortics | Geist Sharp by Nortics | Geist Sharp Mono by Nortics |
| --- | --- | --- | --- | --- | --- | --- |
| `aalt` | Access All Alternates | GSUB | yes | yes | yes | yes |
| `case` | Case-Sensitive Forms | GSUB | yes | yes | yes | yes |
| `ccmp` | Glyph Composition / Decomposition | GSUB | yes | yes | yes | yes |
| `dlig` | Discretionary Ligatures | GSUB | yes | - | yes | - |
| `dnom` | Denominators | GSUB | yes | yes | yes | yes |
| `frac` | Fractions | GSUB | yes | yes | yes | yes |
| `kern` | Kerning | GPOS | yes | - | yes | - |
| `liga` | Standard Ligatures (arrows, operators, ff fi fl tt) | GSUB | yes | yes | yes | yes |
| `locl` | Localized Forms | GSUB | yes | yes | yes | yes |
| `mark` | Mark Positioning | GPOS | yes | yes | yes | yes |
| `mkmk` | Mark to Mark Positioning | GPOS | yes | yes | yes | yes |
| `numr` | Numerators | GSUB | yes | yes | yes | yes |
| `ordn` | Ordinals | GSUB | yes | yes | yes | yes |
| `pnum` | Proportional Figures | GSUB | yes | - | yes | - |
| `sinf` | Scientific Inferiors | GSUB | yes | yes | yes | yes |
| `ss01` | Stylistic Set 1 | GSUB | yes | yes | yes | yes |
| `ss02` | Stylistic Set 2 | GSUB | yes | yes | yes | yes |
| `ss03` | Stylistic Set 3 | GSUB | yes | yes | yes | yes |
| `ss04` | Stylistic Set 4 | GSUB | yes | yes | yes | yes |
| `ss05` | Stylistic Set 5 | GSUB | yes | - | yes | - |
| `ss06` | Stylistic Set 6 | GSUB | yes | yes | yes | yes |
| `ss07` | Stylistic Set 7 | GSUB | yes | yes | yes | yes |
| `ss08` | Stylistic Set 8 | GSUB | yes | yes | yes | yes |
| `ss09` | Stylistic Set 9 | GSUB | yes | yes | yes | yes |
| `ss10` | Stylistic Set 10 | GSUB | yes | yes | yes | yes |
| `ss11` | Stylistic Set 11 | GSUB | yes | yes | yes | yes |
| `subs` | Subscript | GSUB | yes | yes | yes | yes |
| `sups` | Superscript | GSUB | yes | yes | yes | yes |
| `tnum` | Tabular Figures | GSUB | yes | - | yes | - |

Stylistic sets and alternates are inherited from Geist. Alternate glyphs receive the same automatic processing as every other glyph (overlap removal, corner rounding in the Rounded families, spacing), but the hand-drawn terminals of `t l J j f` ([DESIGN-CHANGES.md](DESIGN-CHANGES.md)) are only applied where a glyph reuses the base outline (accented forms and ligatures).

## 2. Arrow ligatures

Typing a sequence of hyphens with `<` or `>` produces a single connected arrow. The feature is `liga`, which is **on by default** in browsers and most design/code editors.

| Type | Arrow |
| --- | --- |
| `->` `-->` `--->` | right arrows with a 1-, 2- and 3-hyphen shaft |
| `<-` `<--` `<---` | left arrows |
| `<->` `<-->` `<--->` | double-headed arrows |

`<-->` and `<--->` (and, in the Mono, `<---`) are additions of this project: upstream either did not ligate them or produced a left arrow followed by a stray `>`. They are built by stretching the shaft of the existing double arrow.

In Geist Mono an N-character ligature used to be drawn hanging back N-1 cells while advancing only one cell, so it overlapped the previous character and broke column alignment. In Nortics Geist every ligature advances exactly N cells (N x 580 units), so monospaced columns stay aligned.

The `liga` tables below also contain, in the sans, the text ligatures `ff`, `fi`, `fl` and `tt`, and, in the Mono, the code ligatures inherited from Geist Mono (`!=`, `==`, `=>`, `</>` and so on).

To disable ligatures: `font-variant-ligatures: none;` (CSS) or `font-feature-settings: "liga" 0;`.

### `liga` rules - Geist Rounded by Nortics (13)

| Input | Chars | Output glyph | Advance |
| --- | --- | --- | --- |
| `->` | 2 | `hyphen_greater.liga` | 1160 (2.0 cells) |
| `<-` | 2 | `less_hyphen.liga` | 1160 (2.0 cells) |
| `ff` | 2 | `f_f.liga` | 663 (1.1 cells) |
| `fi` | 2 | `fi` | 579 (1.0 cells) |
| `fl` | 2 | `fl` | 622 (1.1 cells) |
| `tt` | 2 | `t_t.liga` | 673 (1.2 cells) |
| `-->` | 3 | `hyphen_hyphen_greater.liga` | 1740 (3.0 cells) |
| `<--` | 3 | `less_hyphen_hyphen.liga` | 1740 (3.0 cells) |
| `<->` | 3 | `less_hyphen_greater.liga` | 1740 (3.0 cells) |
| `--->` | 4 | `hyphen_hyphen_hyphen_greater.liga` | 2320 (4.0 cells) |
| `<---` | 4 | `less_hyphen_hyphen_hyphen.liga` | 2320 (4.0 cells) |
| `<-->` | 4 | `less_hyphen_hyphen_greater.liga` | 2320 (4.0 cells) |
| `<--->` | 5 | `less_hyphen_hyphen_hyphen_greater.liga` | 2900 (5.0 cells) |

### `liga` rules - Geist Rounded Mono by Nortics (72)

| Input | Chars | Output glyph | Advance |
| --- | --- | --- | --- |
| `!=` | 2 | `exclam_equal.liga` | 1160 (2.0 cells) |
| `!?` | 2 | `exclam_question.liga` | 1160 (2.0 cells) |
| `%%` | 2 | `percent_percent.liga` | 1160 (2.0 cells) |
| `--` | 2 | `hyphen_hyphen.liga` | 1160 (2.0 cells) |
| `-<` | 2 | `hyphen_less.liga` | 1160 (2.0 cells) |
| `->` | 2 | `hyphen_greater.liga` | 1160 (2.0 cells) |
| `-~` | 2 | `hyphen_asciitilde.liga` | 1160 (2.0 cells) |
| `.=` | 2 | `period_equal.liga` | 1160 (2.0 cells) |
| `/=` | 2 | `slash_equal.liga` | 1160 (2.0 cells) |
| `:=` | 2 | `colon_equal.liga` | 1160 (2.0 cells) |
| `<-` | 2 | `less_hyphen.liga` | 1160 (2.0 cells) |
| `<=` | 2 | `less_equal.liga` | 1160 (2.0 cells) |
| `<>` | 2 | `less_greater.liga` | 1160 (2.0 cells) |
| `<\|` | 2 | `less_bar.liga` | 1160 (2.0 cells) |
| `<~` | 2 | `less_asciitilde.liga` | 1160 (2.0 cells) |
| `==` | 2 | `equal_equal.liga` | 1160 (2.0 cells) |
| `=>` | 2 | `equal_greater.liga` | 1160 (2.0 cells) |
| `>-` | 2 | `greater_hyphen.liga` | 1160 (2.0 cells) |
| `>=` | 2 | `greater_equal.liga` | 1160 (2.0 cells) |
| `??` | 2 | `question_question.liga` | 1160 (2.0 cells) |
| `{\|` | 2 | `braceleft_bar.liga` | 1160 (2.0 cells) |
| `\|=` | 2 | `bar_equal.liga` | 1160 (2.0 cells) |
| `\|>` | 2 | `bar_greater.liga` | 1160 (2.0 cells) |
| `\|}` | 2 | `bar_braceright.liga` | 1160 (2.0 cells) |
| `~-` | 2 | `asciitilde_hyphen.liga` | 1160 (2.0 cells) |
| `~=` | 2 | `asciitilde_equal.liga` | 1160 (2.0 cells) |
| `~>` | 2 | `asciitilde_greater.liga` | 1160 (2.0 cells) |
| `~@` | 2 | `asciitilde_at.liga` | 1160 (2.0 cells) |
| `~~` | 2 | `asciitilde_asciitilde.liga` | 1160 (2.0 cells) |
| `!==` | 3 | `exclam_equal_equal.liga` | 1740 (3.0 cells) |
| `###` | 3 | `numbersign_numbersign_numbersign.liga` | 1740 (3.0 cells) |
| `---` | 3 | `hyphen_hyphen_hyphen.liga` | 1740 (3.0 cells) |
| `-->` | 3 | `hyphen_hyphen_greater.liga` | 1740 (3.0 cells) |
| `-<<` | 3 | `hyphen_less_less.liga` | 1740 (3.0 cells) |
| `->>` | 3 | `hyphen_greater_greater.liga` | 1740 (3.0 cells) |
| `...` | 3 | `period_period_period.liga` | 1740 (3.0 cells) |
| `..=` | 3 | `period_period_equal.liga` | 1740 (3.0 cells) |
| `<--` | 3 | `less_hyphen_hyphen.liga` | 1740 (3.0 cells) |
| `<-<` | 3 | `less_hyphen_less.liga` | 1740 (3.0 cells) |
| `<->` | 3 | `less_hyphen_greater.liga` | 1740 (3.0 cells) |
| `</>` | 3 | `less_slash_greater.liga` | 1740 (3.0 cells) |
| `<<-` | 3 | `less_less_hyphen.liga` | 1740 (3.0 cells) |
| `<<=` | 3 | `less_less_equal.liga` | 1740 (3.0 cells) |
| `<=<` | 3 | `less_equal_less.liga` | 1740 (3.0 cells) |
| `<==` | 3 | `less_equal_equal.liga` | 1740 (3.0 cells) |
| `<=>` | 3 | `less_equal_greater.liga` | 1740 (3.0 cells) |
| `<\|>` | 3 | `less_bar_greater.liga` | 1740 (3.0 cells) |
| `<\|\|` | 3 | `less_bar_bar.liga` | 1740 (3.0 cells) |
| `<~>` | 3 | `less_asciitilde_greater.liga` | 1740 (3.0 cells) |
| `<~~` | 3 | `less_asciitilde_asciitilde.liga` | 1740 (3.0 cells) |
| `=/=` | 3 | `equal_slash_equal.liga` | 1740 (3.0 cells) |
| `=<<` | 3 | `equal_less_less.liga` | 1740 (3.0 cells) |
| `===` | 3 | `equal_equal_equal.liga` | 1740 (3.0 cells) |
| `==>` | 3 | `equal_equal_greater.liga` | 1740 (3.0 cells) |
| `=>>` | 3 | `equal_greater_greater.liga` | 1740 (3.0 cells) |
| `>->` | 3 | `greater_hyphen_greater.liga` | 1740 (3.0 cells) |
| `>=>` | 3 | `greater_equal_greater.liga` | 1740 (3.0 cells) |
| `>>-` | 3 | `greater_greater_hyphen.liga` | 1740 (3.0 cells) |
| `>>=` | 3 | `greater_greater_equal.liga` | 1740 (3.0 cells) |
| `???` | 3 | `question_question_question.liga` | 1740 (3.0 cells) |
| `\|->` | 3 | `bar_hyphen_greater.liga` | 1740 (3.0 cells) |
| `\|\|=` | 3 | `bar_bar_equal.liga` | 1740 (3.0 cells) |
| `\|\|>` | 3 | `bar_bar_greater.liga` | 1740 (3.0 cells) |
| `~~>` | 3 | `asciitilde_asciitilde_greater.liga` | 1740 (3.0 cells) |
| `--->` | 4 | `hyphen_hyphen_hyphen_greater.liga` | 2320 (4.0 cells) |
| `<!--` | 4 | `less_exclam_hyphen_hyphen.liga` | 2320 (4.0 cells) |
| `<---` | 4 | `less_hyphen_hyphen_hyphen.liga` | 2320 (4.0 cells) |
| `<-->` | 4 | `less_hyphen_hyphen_greater.liga` | 2320 (4.0 cells) |
| `<==>` | 4 | `less_equal_equal_greater.liga` | 2320 (4.0 cells) |
| `<\|\|\|` | 4 | `less_bar_bar_bar.liga` | 2320 (4.0 cells) |
| `\|\|\|>` | 4 | `bar_bar_bar_greater.liga` | 2320 (4.0 cells) |
| `<--->` | 5 | `less_hyphen_hyphen_hyphen_greater.liga` | 2900 (5.0 cells) |

The Sharp families have exactly the same features and rules (`fonts/geist-sharp-*`).
