# Glyph coverage

Character coverage of **Nortics Geist 1.100**, read from the `cmap` of the shipped fonts by [`source/gen_docs.py`](../source/gen_docs.py).

## 1. Scope

The project is **Latin-first**, with English, Portuguese and Spanish as the target languages. The design work (rounded corners, hand-drawn terminals, dashes, arrows, spacing) was reviewed for the Latin glyphs. The fonts also contain the other scripts and symbols inherited from Geist (for example Cyrillic and Greek); those glyphs went through the same automatic processing but were **not reviewed by hand**.

## 2. Language support (checked against all 40 fonts)

Every character listed must be mapped in the `cmap` of every font of the family.

| Language | Checked set | Geist Rounded by Nortics | Geist Rounded Mono by Nortics | Geist Sharp by Nortics | Geist Sharp Mono by Nortics |
| --- | --- | --- | --- | --- | --- |
| **English** | 120 characters | 11/11 | 9/9 | 11/11 | 9/9 |
| **Portuguese (pt-BR, pt-PT)** | 30 characters | 11/11 | 9/9 | 11/11 | 9/9 |
| **Spanish** | 16 characters | 11/11 | 9/9 | 11/11 | 9/9 |
| French (informative) | 32 characters | 11/11 | 9/9 | 11/11 | 9/9 |
| Italian (informative) | 20 characters | 11/11 | 9/9 | 11/11 | 9/9 |
| German (informative) | 8 characters | 11/11 | 9/9 | 11/11 | 9/9 |

Target languages are in bold; the others are an informative check of the same Latin set. Checked sets: English = A-Z a-z 0-9 plus common punctuation, quotes, currency and symbols; Portuguese = `áàâãäçéêíóôõúü` + capitals + `ªº`; Spanish = `áéíóúüñ` + capitals + `¿¡`.

## 3. Unicode blocks

### Geist Rounded by Nortics (728 mapped code points)

| Block | Range | Assigned | Covered | Coverage |
| --- | --- | --- | --- | --- |
| Basic Latin | U+0000-007F | 128 | 95 | 74% |
| Latin-1 Supplement | U+0080-00FF | 128 | 95 | 74% |
| Latin Extended-A | U+0100-017F | 128 | 117 | 91% |
| Latin Extended-B | U+0180-024F | 208 | 19 | 9% |
| IPA Extensions | U+0250-02AF | 96 | 1 | 1% |
| Spacing Modifier Letters | U+02B0-02FF | 80 | 11 | 14% |
| Combining Diacritical Marks | U+0300-036F | 112 | 22 | 20% |
| Greek and Coptic | U+0370-03FF | 135 | 6 | 4% |
| Cyrillic | U+0400-04FF | 256 | 134 | 52% |
| Latin Extended Additional | U+1E00-1EFF | 256 | 99 | 39% |
| General Punctuation | U+2000-206F | 111 | 20 | 18% |
| Superscripts and Subscripts | U+2070-209F | 42 | 17 | 40% |
| Currency Symbols | U+20A0-20CF | 33 | 6 | 18% |
| Letterlike Symbols | U+2100-214F | 80 | 3 | 4% |
| Number Forms | U+2150-218F | 60 | 7 | 12% |
| Arrows | U+2190-21FF | 112 | 21 | 19% |
| Mathematical Operators | U+2200-22FF | 256 | 13 | 5% |
| Geometric Shapes | U+25A0-25FF | 96 | 12 | 12% |
| Miscellaneous Symbols | U+2600-26FF | 256 | 2 | 1% |

### Geist Rounded Mono by Nortics (889 mapped code points)

| Block | Range | Assigned | Covered | Coverage |
| --- | --- | --- | --- | --- |
| Basic Latin | U+0000-007F | 128 | 95 | 74% |
| Latin-1 Supplement | U+0080-00FF | 128 | 95 | 74% |
| Latin Extended-A | U+0100-017F | 128 | 115 | 90% |
| Latin Extended-B | U+0180-024F | 208 | 19 | 9% |
| IPA Extensions | U+0250-02AF | 96 | 1 | 1% |
| Spacing Modifier Letters | U+02B0-02FF | 80 | 11 | 14% |
| Combining Diacritical Marks | U+0300-036F | 112 | 22 | 20% |
| Greek and Coptic | U+0370-03FF | 135 | 5 | 4% |
| Cyrillic | U+0400-04FF | 256 | 134 | 52% |
| Latin Extended Additional | U+1E00-1EFF | 256 | 99 | 39% |
| General Punctuation | U+2000-206F | 111 | 20 | 18% |
| Superscripts and Subscripts | U+2070-209F | 42 | 17 | 40% |
| Currency Symbols | U+20A0-20CF | 33 | 6 | 18% |
| Letterlike Symbols | U+2100-214F | 80 | 4 | 5% |
| Number Forms | U+2150-218F | 60 | 7 | 12% |
| Arrows | U+2190-21FF | 112 | 21 | 19% |
| Mathematical Operators | U+2200-22FF | 256 | 13 | 5% |
| Geometric Shapes | U+25A0-25FF | 96 | 12 | 12% |

The Sharp families have the same coverage as their Rounded counterparts.
