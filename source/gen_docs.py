"""Generate the data-driven documents from the fonts themselves:
docs/SPECIFICATION.md, docs/OPENTYPE-FEATURES.md, docs/GLYPH-COVERAGE.md

  python gen_docs.py            (run from the repository root or from source/)
"""
import glob
import os
import unicodedata
from fontTools.ttLib import TTFont

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FONTS = os.path.join(REPO, "fonts")
DOCS = os.path.join(REPO, "docs")
VERSION = "1.100"
ORDER = ["geist-rounded-by-nortics", "geist-rounded-mono-by-nortics",
         "geist-sharp-by-nortics", "geist-sharp-mono-by-nortics"]
STYLE = {"geist-rounded-by-nortics": ("Rounded", "Sans"), "geist-rounded-mono-by-nortics": ("Rounded", "Mono"),
         "geist-sharp-by-nortics": ("Sharp", "Sans"), "geist-sharp-mono-by-nortics": ("Sharp", "Mono")}


def md(cell):
    return str(cell).replace("|", "\\|")


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "| " + " | ".join("---" for _ in head) + " |"]
    out += ["| " + " | ".join(md(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def nm(t, i):
    return t['name'].getDebugName(i) or ""


def load(fdir):
    items = []
    for f in glob.glob(os.path.join(FONTS, fdir, "ttf", "*.ttf")):
        t = TTFont(f)
        items.append((t['OS/2'].usWeightClass, f, t))
    items.sort(key=lambda x: x[0])
    return items


FAM = {d: load(d) for d in ORDER}


def regular(d):
    return next(t for wc, f, t in FAM[d] if wc == 400)


def kb(p):
    return f"{os.path.getsize(p) / 1024:.0f}"


# ------------------------------------------------------------------ SPECIFICATION
def spec():
    o = ["# Specification", "",
         f"Technical specification of **Nortics Geist {VERSION}**. This file is generated from the font files by "
         "[`source/gen_docs.py`](../source/gen_docs.py); every value below was read from the shipped fonts.", "",
         "## 1. Families", ""]
    rows = []
    for d in ORDER:
        r = regular(d)
        wcs = [wc for wc, _, _ in FAM[d]]
        total = sum(os.path.getsize(f) for _, f, _ in FAM[d])
        rows.append([f"**{nm(r, 16)}**", " ".join(STYLE[d]), len(wcs), ", ".join(map(str, wcs)),
                     len(r.getGlyphOrder()), len(r.getBestCmap()), f"{total / 1024 / 1024:.1f} MB", f"`fonts/{d}/`"])
    o.append(table(["Family (nameID 16)", "Variant", "Fonts", "Weights (usWeightClass)", "Glyphs", "Mapped code points",
                    "TTF total", "Folder"], rows))
    o += ["", "Glyph and code-point counts are taken from the Regular of each family (all weights of a family share the "
          "same glyph set). Weight values 150 (UltraLight) and 250 (SemiLight) are non-standard intermediate weights; CSS "
          "`font-weight` accepts them as plain numbers.", "", "## 2. Weights, file names and name table", ""]
    for d in ORDER:
        o += [f"### {nm(regular(d), 16)}", ""]
        rows = []
        for wc, f, t in FAM[d]:
            w2 = f.replace(os.sep + "ttf" + os.sep, os.sep + "woff2" + os.sep)[:-4] + ".woff2"
            rows.append([wc, nm(t, 17), f"`{nm(t, 1)}`", f"`{nm(t, 2)}`", f"`{nm(t, 4)}`", f"`{nm(t, 6)}`",
                         f"`{os.path.basename(f)}`", kb(f), kb(w2) if os.path.exists(w2) else "-"])
        o.append(table(["wght", "Style", "nameID 1", "nameID 2", "nameID 4 (full)", "nameID 6 (PostScript)", "File",
                        "TTF KB", "WOFF2 KB"], rows))
        o.append("")
    o += ["Naming follows the RIBBI rule: only `Regular` and `Bold` use the bare family name in nameID 1; every other weight "
          "appends its style name to nameID 1 and sets nameID 2 to `Regular`. nameID 16/17 always carry the family and the "
          "style, which is what modern applications use to group the weights. The four families have different names, so "
          "they can be installed together and alongside the original Geist without conflicts.", "",
          "## 3. Metrics", ""]
    rows = []
    for d in ORDER:
        r = regular(d)
        wins = [(t['OS/2'].usWinAscent, t['OS/2'].usWinDescent) for _, _, t in FAM[d]]
        xs = [t['OS/2'].sxHeight for _, _, t in FAM[d]]
        cs = [t['OS/2'].sCapHeight for _, _, t in FAM[d]]
        rows.append([nm(r, 16), r['head'].unitsPerEm, r['hhea'].ascent, r['hhea'].descent, r['hhea'].lineGap,
                     r['OS/2'].sTypoAscender, r['OS/2'].sTypoDescender, r['OS/2'].sTypoLineGap,
                     f"{min(w[0] for w in wins)}-{max(w[0] for w in wins)} / {min(w[1] for w in wins)}-{max(w[1] for w in wins)}",
                     f"{min(xs)}-{max(xs)}", f"{min(cs)}-{max(cs)}"])
    o.append(table(["Family", "UPM", "hhea asc", "hhea desc", "hhea gap", "typo asc", "typo desc", "typo gap",
                    "win asc / desc (range)", "x-height (range)", "cap height (range)"], rows))
    o += ["", "- Units per em: **1000**. Vertical metrics are identical in `hhea` and OS/2 typo (ascender 1111, descender -225, "
          "line gap 0), `USE_TYPO_METRICS` (fsSelection bit 7) is set, so the default line height is 1.336 em in every "
          "application. `usWinAscent/usWinDescent` are computed per font from the real glyph extents so nothing is clipped.",
          "- Spacing: every advance width is 20 units (0.020 em) narrower than in Geist; for the Mono families the cell is "
          "**580** units instead of 600.",
          f"- Underline (Regular): sans position {regular('geist-rounded-by-nortics')['post'].underlinePosition}, thickness "
          f"{regular('geist-rounded-by-nortics')['post'].underlineThickness}; mono position "
          f"{regular('geist-rounded-mono-by-nortics')['post'].underlinePosition}, thickness "
          f"{regular('geist-rounded-mono-by-nortics')['post'].underlineThickness} (inherited from Geist).", ""]
    r = regular("geist-rounded-by-nortics")
    rm = regular("geist-rounded-mono-by-nortics")
    adv_mono = sorted({rm['hmtx'][g][0] for g in rm.getGlyphOrder() if rm['hmtx'][g][0] > 0 and not g.endswith('.liga')})
    o += [f"- Sans: space advance {r['hmtx']['space'][0]}, `n` advance {r['hmtx']['n'][0]}, `H` advance {r['hmtx']['H'][0]}.",
          f"- Mono: advance widths present in the glyph set (excluding ligature glyphs): {adv_mono}. Letters, digits and "
          "punctuation use the 580 cell; a small group of symbols inherited from Geist Mono is 480 wide.",
          f"- `post.isFixedPitch`: sans = {r['post'].isFixedPitch}, mono = {rm['post'].isFixedPitch}.", "",
          "## 4. Font-level metadata (identical in all 40 fonts unless noted)", ""]
    rr = regular("geist-rounded-by-nortics")
    meta = [["0 Copyright", nm(rr, 0)], ["3 Unique ID", "`<version>;NRTC;<PostScript name>`"], ["5 Version", nm(rr, 5)],
            ["8 Manufacturer", nm(rr, 8)], ["9 Designer", nm(rr, 9)], ["10 Description", "`<family>: <rounded|square>-corner adaptation of Geist (SIL OFL 1.1) by Andre Dorneles.`"],
            ["13 License", nm(rr, 13)], ["14 License URL", nm(rr, 14)],
            ["OS/2 achVendID", "`NRTC`"], ["head.fontRevision", f"{rr['head'].fontRevision:.3f}"],
            ["OS/2 fsType", f"{rr['OS/2'].fsType} (installable embedding, no restrictions)"],
            ["OS/2 fsSelection", "`0x00C0` Regular (REGULAR + USE_TYPO_METRICS), `0x00A0` Bold (BOLD + USE_TYPO_METRICS), `0x0080` every other weight"],
            ["head.macStyle", "`1` for Bold, `0` otherwise"], ["OS/2 usWidthClass", rr['OS/2'].usWidthClass]]
    o.append(table(["Field", "Value"], meta))
    o += ["", "The Geist copyright notice is preserved in nameID 0 as required by the SIL Open Font License; the modification "
          "notice is appended to it. See [LICENSING.md](LICENSING.md).", "", "## 5. File format", "",
          f"- Outlines: TrueType (`glyf`), quadratic Bezier, **unhinted** (all glyph programs removed; the `gasp` table "
          f"asks for grayscale smoothing). Tables of the sans Regular: `{', '.join(sorted(rr.keys()))}`.",
          "- Distribution formats: `.ttf` (desktop) and `.woff2` (web, Brotli) with identical content.",
          "- Static fonts only: **no variable font and no italics** are provided.",
          "- Overlaps are removed in every glyph (no overlapping contours).", ""]
    with open(os.path.join(DOCS, "SPECIFICATION.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(o))


# ------------------------------------------------------------------ OPENTYPE FEATURES
DESC = {"aalt": "Access All Alternates", "calt": "Contextual Alternates", "case": "Case-Sensitive Forms",
        "ccmp": "Glyph Composition / Decomposition", "cpsp": "Capital Spacing", "dnom": "Denominators",
        "frac": "Fractions", "kern": "Kerning", "liga": "Standard Ligatures (arrows, operators, ff fi fl tt)",
        "locl": "Localized Forms", "mark": "Mark Positioning", "mkmk": "Mark to Mark Positioning",
        "numr": "Numerators", "ordn": "Ordinals", "sinf": "Scientific Inferiors", "subs": "Subscript",
        "sups": "Superscript", "tnum": "Tabular Figures", "zero": "Slashed Zero", "pnum": "Proportional Figures",
        "lnum": "Lining Figures", "onum": "Oldstyle Figures", "dlig": "Discretionary Ligatures",
        "rlig": "Required Ligatures", "clig": "Contextual Ligatures"}
for i in range(1, 21):
    DESC[f"ss{i:02d}"] = f"Stylistic Set {i}"


def feats(t, table_tag):
    if table_tag not in t:
        return set()
    return {fr.FeatureTag for fr in t[table_tag].table.FeatureList.FeatureRecord}


def liga_rules(t):
    cmap = t.getBestCmap()
    rev = {}
    for cp, n in cmap.items():
        rev.setdefault(n, chr(cp))
    gsub = t['GSUB'].table
    idx = set()
    for fr in gsub.FeatureList.FeatureRecord:
        if fr.FeatureTag == 'liga':
            idx.update(fr.Feature.LookupListIndex)
    rules = []
    for li in sorted(idx):
        lk = gsub.LookupList.Lookup[li]
        for st in lk.SubTable:
            if lk.LookupType == 7:
                st = st.ExtSubTable
            if hasattr(st, 'ligatures'):
                for first, ligs in st.ligatures.items():
                    for lg in ligs:
                        comps = [first] + list(lg.Component)
                        rules.append(("".join(rev.get(c, f"<{c}>") for c in comps), len(comps), lg.LigGlyph))
    return rules


def features():
    o = ["# OpenType features", "",
         f"OpenType layout features of **Nortics Geist {VERSION}**, read from the shipped fonts by "
         "[`source/gen_docs.py`](../source/gen_docs.py).", "", "## 1. Feature matrix", "",
         "A tick means the feature tag is present in the GSUB/GPOS table of the family's Regular. The feature set is inherited "
         "from Geist / Geist Mono; the lookups are unchanged except for the arrow ligatures described in section 2.", ""]
    names = [nm(regular(d), 16) for d in ORDER]
    allf = {}
    for d in ORDER:
        t = regular(d)
        allf[d] = (feats(t, 'GSUB'), feats(t, 'GPOS'))
    tags = sorted(set().union(*[a | b for a, b in allf.values()]))
    rows = []
    for tag in tags:
        kind = "/".join(k for k, i in (("GSUB", 0), ("GPOS", 1)) if any(tag in allf[d][i] for d in ORDER))
        rows.append([f"`{tag}`", DESC.get(tag, "-"), kind] + ["yes" if (tag in allf[d][0] or tag in allf[d][1]) else "-" for d in ORDER])
    o.append(table(["Tag", "Description", "Table"] + names, rows))
    o += ["", "Stylistic sets and alternates are inherited from Geist. Alternate glyphs receive the same automatic processing as "
          "every other glyph (overlap removal, corner rounding in the Rounded families, spacing), but the hand-drawn terminals of "
          "`t l J j f` ([DESIGN-CHANGES.md](DESIGN-CHANGES.md)) are only applied where a glyph reuses the base outline "
          "(accented forms and ligatures).", "", "## 2. Arrow ligatures", "",
          "Typing a sequence of hyphens with `<` or `>` produces a single connected arrow. The feature is `liga`, which is "
          "**on by default** in browsers and most design/code editors.", "",
          table(["Type", "Arrow"], [["`->` `-->` `--->`", "right arrows with a 1-, 2- and 3-hyphen shaft"],
                                    ["`<-` `<--` `<---`", "left arrows"],
                                    ["`<->` `<-->` `<--->`", "double-headed arrows"]]), "",
          "`<-->` and `<--->` (and, in the Mono, `<---`) are additions of this project: upstream either did not ligate them "
          "or produced a left arrow followed by a stray `>`. They are built by stretching the shaft of the existing "
          "double arrow.", "",
          "In Geist Mono an N-character ligature used to be drawn hanging back N-1 cells while advancing only one cell, so it "
          "overlapped the previous character and broke column alignment. In Nortics Geist every ligature advances exactly "
          "N cells (N x 580 units), so monospaced columns stay aligned.", "",
          "The `liga` tables below also contain, in the sans, the text ligatures `ff`, `fi`, `fl` and `tt`, and, in the Mono, "
          "the code ligatures inherited from Geist Mono (`!=`, `==`, `=>`, `</>` and so on).", "",
          "To disable ligatures: `font-variant-ligatures: none;` (CSS) or `font-feature-settings: \"liga\" 0;`.", ""]
    for d in ("geist-rounded-by-nortics", "geist-rounded-mono-by-nortics"):
        t = regular(d)
        rules = sorted(liga_rules(t), key=lambda r: (r[1], r[0]))
        o += [f"### `liga` rules - {nm(t, 16)} ({len(rules)})", ""]
        rows = [[f"`{s}`", n, f"`{g}`", f"{t['hmtx'][g][0]} ({t['hmtx'][g][0] / 580:.1f} cells)" if g in t['hmtx'].metrics else "-"]
                for s, n, g in rules]
        o.append(table(["Input", "Chars", "Output glyph", "Advance"], rows))
        o.append("")
    o += ["The Sharp families have exactly the same features and rules (`fonts/geist-sharp-*`).", ""]
    with open(os.path.join(DOCS, "OPENTYPE-FEATURES.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(o))


# ------------------------------------------------------------------ COVERAGE
BLOCKS = [("Basic Latin", 0x0000, 0x007F), ("Latin-1 Supplement", 0x0080, 0x00FF),
          ("Latin Extended-A", 0x0100, 0x017F), ("Latin Extended-B", 0x0180, 0x024F),
          ("IPA Extensions", 0x0250, 0x02AF), ("Spacing Modifier Letters", 0x02B0, 0x02FF),
          ("Combining Diacritical Marks", 0x0300, 0x036F), ("Greek and Coptic", 0x0370, 0x03FF),
          ("Cyrillic", 0x0400, 0x04FF), ("Latin Extended Additional", 0x1E00, 0x1EFF),
          ("General Punctuation", 0x2000, 0x206F), ("Superscripts and Subscripts", 0x2070, 0x209F),
          ("Currency Symbols", 0x20A0, 0x20CF), ("Letterlike Symbols", 0x2100, 0x214F),
          ("Number Forms", 0x2150, 0x218F), ("Arrows", 0x2190, 0x21FF), ("Mathematical Operators", 0x2200, 0x22FF),
          ("Geometric Shapes", 0x25A0, 0x25FF), ("Miscellaneous Symbols", 0x2600, 0x26FF)]
PUNCT = ".,:;!?'\"()[]{}-\u2013\u2014\u2026/\\&@#%*+=<>_|~^$\u20ac\u00a3\u00a2\u00a5\u00b0\u00a9\u00ae\u2122\u00a7\u00b6\u2022\u00b7\u2018\u2019\u201c\u201d\u201e\u00ab\u00bb\u2039\u203a\u00b1\u00d7\u00f7"
LANGS = [
    ("English", "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789" + PUNCT, True),
    ("Portuguese (pt-BR, pt-PT)", "\u00e1\u00e0\u00e2\u00e3\u00e4\u00e7\u00e9\u00ea\u00ed\u00f3\u00f4\u00f5\u00fa\u00fc\u00c1\u00c0\u00c2\u00c3\u00c4\u00c7\u00c9\u00ca\u00cd\u00d3\u00d4\u00d5\u00da\u00dc\u00aa\u00ba", True),
    ("Spanish", "\u00e1\u00e9\u00ed\u00f3\u00fa\u00fc\u00f1\u00c1\u00c9\u00cd\u00d3\u00da\u00dc\u00d1\u00bf\u00a1", True),
    ("French (informative)", "\u00e0\u00e2\u00e6\u00e7\u00e9\u00e8\u00ea\u00eb\u00ee\u00ef\u00f4\u0153\u00f9\u00fb\u00fc\u00ff\u00c0\u00c2\u00c6\u00c7\u00c9\u00c8\u00ca\u00cb\u00ce\u00cf\u00d4\u0152\u00d9\u00db\u00dc\u0178", False),
    ("Italian (informative)", "\u00e0\u00e8\u00e9\u00ec\u00ed\u00ee\u00f2\u00f3\u00f9\u00fa\u00c0\u00c8\u00c9\u00cc\u00cd\u00ce\u00d2\u00d3\u00d9\u00da", False),
    ("German (informative)", "\u00e4\u00f6\u00fc\u00df\u00c4\u00d6\u00dc\u1e9e", False),
]


def coverage():
    o = ["# Glyph coverage", "",
         f"Character coverage of **Nortics Geist {VERSION}**, read from the `cmap` of the shipped fonts by "
         "[`source/gen_docs.py`](../source/gen_docs.py).", "", "## 1. Scope", "",
         "The project is **Latin-first**, with English, Portuguese and Spanish as the target languages. The design work "
         "(rounded corners, hand-drawn terminals, dashes, arrows, spacing) was reviewed for the Latin glyphs. The fonts "
         "also contain the other scripts and symbols inherited from Geist (for example Cyrillic and Greek); those glyphs "
         "went through the same automatic processing but were **not reviewed by hand**.", "",
         "## 2. Language support (checked against all 40 fonts)", "",
         "Every character listed must be mapped in the `cmap` of every font of the family.", ""]
    rows = []
    for lang, chars, target in LANGS:
        cells = []
        for d in ORDER:
            ok = 0
            missing = set()
            for wc, f, t in FAM[d]:
                cm = t.getBestCmap()
                miss = [c for c in chars if ord(c) not in cm]
                if not miss:
                    ok += 1
                missing |= set(miss)
            cells.append(f"{ok}/{len(FAM[d])}" + (f" (missing: {''.join(sorted(missing))})" if missing else ""))
        rows.append([f"**{lang}**" if target else lang, f"{len(set(chars))} characters"] + cells)
    o.append(table(["Language", "Checked set"] + [nm(regular(d), 16) for d in ORDER], rows))
    o += ["", "Target languages are in bold; the others are an informative check of the same Latin set. Checked sets: "
          "English = A-Z a-z 0-9 plus common punctuation, quotes, currency and symbols; Portuguese = "
          "`\u00e1\u00e0\u00e2\u00e3\u00e4\u00e7\u00e9\u00ea\u00ed\u00f3\u00f4\u00f5\u00fa\u00fc` + capitals + `\u00aa\u00ba`; Spanish = "
          "`\u00e1\u00e9\u00ed\u00f3\u00fa\u00fc\u00f1` + capitals + `\u00bf\u00a1`.", "", "## 3. Unicode blocks", ""]
    for d in ("geist-rounded-by-nortics", "geist-rounded-mono-by-nortics"):
        t = regular(d)
        cm = set(t.getBestCmap())
        rows = []
        for name, a, b in BLOCKS:
            assigned = [c for c in range(a, b + 1) if unicodedata.category(chr(c)) != "Cn"]
            cov = [c for c in assigned if c in cm]
            if cov:
                rows.append([name, f"U+{a:04X}-{b:04X}", len(assigned), len(cov), f"{100 * len(cov) / max(1, len(assigned)):.0f}%"])
        o += [f"### {nm(t, 16)} ({len(cm)} mapped code points)", "",
              table(["Block", "Range", "Assigned", "Covered", "Coverage"], rows), ""]
    o += ["The Sharp families have the same coverage as their Rounded counterparts.", ""]
    with open(os.path.join(DOCS, "GLYPH-COVERAGE.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(o))


if __name__ == "__main__":
    os.makedirs(DOCS, exist_ok=True)
    spec()
    features()
    coverage()
    print("docs written to", DOCS)
