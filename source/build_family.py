"""Nortics Geist - build script.

Builds the four families (Rounded / Sharp, each in Sans and Mono) as static TrueType fonts from the
variable fonts published by Vercel (https://github.com/vercel/geist-font).

  python build_family.py --geist-vf "Geist[wght].ttf" --geist-mono-vf "GeistMono[wght].ttf" --out build

Options
  --style  rounded | sharp | all     (default all)
  --kind   sans | mono | all         (default all)
  --sub    Regular | Light | ...     build a single weight (by subfamily name)
  --radius corner radius in font units, rounded style only (default 20)
  --track  spacing removed per character in font units (default 20)

Output: <out>/<style>/<Prefix>-<Subfamily>.ttf
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fontTools.ttLib import TTFont
from fontTools.ttLib.removeOverlaps import removeOverlaps
from fontTools.ttLib.tables._n_a_m_e import NameRecord
from fontTools.varLib.instancer import instantiateVariableFont, OverlapMode
from fontround import round_font_glyphs
from designs import apply_designs, capture_components, DESIGNS, DESIGNS_MONO, DASHES_SANS, DASHES_MONO
from arrows import fix_mono_ligatures, add_arrow, SANS_ARROWS, MONO_ARROWS
from tracking import apply_tracking

STYLES = {
    "rounded": dict(
        R=20.0,
        family={"sans": "Geist Rounded by Nortics", "mono": "Geist Rounded Mono by Nortics"},
        prefix={"sans": "GeistRoundedByNortics", "mono": "GeistRoundedMonoByNortics"},
        desc="rounded-corner adaptation of Geist"),
    "sharp": dict(
        R=0.0,
        family={"sans": "Geist Sharp by Nortics", "mono": "Geist Sharp Mono by Nortics"},
        prefix={"sans": "GeistSharpByNortics", "mono": "GeistSharpMonoByNortics"},
        desc="square-corner adaptation of Geist"),
}
WEIGHTS = {
    "sans": {100: "Thin", 150: "UltraLight", 200: "ExtraLight", 250: "SemiLight", 300: "Light", 400: "Regular",
             500: "Medium", 600: "SemiBold", 700: "Bold", 800: "ExtraBold", 900: "Black"},
    "mono": {100: "Thin", 200: "ExtraLight", 250: "SemiLight", 300: "Light", 400: "Regular",
             500: "Medium", 600: "SemiBold", 700: "Bold", 800: "ExtraBold"},
}
TRACK = 20          # font units removed per character (-0.020 em), split on both sides
ASC, DESC, LGAP = 1111, -225, 0
DESIGNER = "Andre Dorneles"
MANUFACTURER = "Nortics"
VENDOR = "NRTC"
VERSION = "1.100"
GEIST_COPY = "Copyright 2024 The Geist Project Authors (https://github.com/vercel/geist-font)"
LICENSE = ("This Font Software is licensed under the SIL Open Font License, Version 1.1. "
           "This license is available with a FAQ at: https://openfontlicense.org")


def setname(font, nid, value):
    name = font['name']
    name.names = [r for r in name.names if r.nameID != nid]
    if value is None:
        return
    for plat, enc, lang in ((3, 1, 0x0409), (1, 0, 0)):
        nr = NameRecord()
        nr.platformID, nr.platEncID, nr.langID, nr.nameID = plat, enc, lang, nid
        nr.string = value.encode('utf-16-be') if plat == 3 else value.encode('latin-1', 'replace')
        name.names.append(nr)


def finish(font, kind, style, sub, wc):
    st = STYLES[style]
    family, pfx = st["family"][kind], st["prefix"][kind]
    glyf = font['glyf']
    maxy = miny = 0
    for n in font.getGlyphOrder():
        g = glyf[n]
        if g.numberOfContours > 0:
            for _, y in g.coordinates:
                maxy, miny = max(maxy, y), min(miny, y)
    font['hhea'].ascent, font['hhea'].descent, font['hhea'].lineGap = ASC, DESC, LGAP
    o = font['OS/2']
    o.sTypoAscender, o.sTypoDescender, o.sTypoLineGap = ASC, DESC, LGAP
    o.usWinAscent, o.usWinDescent = max(ASC, maxy), max(-DESC, -miny)
    o.usWeightClass = wc
    o.achVendID = VENDOR
    sel = o.fsSelection & ~(0x01 | 0x20 | 0x40)
    if sub == "Regular":
        sel |= 0x40
    if sub == "Bold":
        sel |= 0x20
    o.fsSelection = sel | 0x80
    font['head'].macStyle = (font['head'].macStyle & ~0x03) | (0x01 if sub == "Bold" else 0)
    font['head'].fontRevision = float(VERSION)

    ribbi = sub in ("Regular", "Bold")
    ps = f"{pfx}-{sub}"
    setname(font, 1, family if ribbi else f"{family} {sub}")
    setname(font, 2, sub if ribbi else "Regular")
    setname(font, 3, f"{VERSION};{VENDOR};{ps}")
    setname(font, 4, f"{family} {sub}")
    setname(font, 5, f"Version {VERSION}; based on Geist 1.800 (OFL 1.1)")
    setname(font, 6, ps)
    setname(font, 7, None)
    setname(font, 8, MANUFACTURER)
    setname(font, 9, DESIGNER)
    setname(font, 10, f"{family}: {st['desc']} (SIL OFL 1.1) by {DESIGNER}.")
    setname(font, 11, None)
    setname(font, 12, None)
    setname(font, 13, LICENSE)
    setname(font, 14, "https://openfontlicense.org")
    setname(font, 16, family)
    setname(font, 17, sub)
    setname(font, 21, None)
    setname(font, 22, None)
    setname(font, 0, GEIST_COPY + f" | Modifications copyright 2026 {DESIGNER}.")


def process(font, kind, style, sub, wc, radius, track):
    mono = kind == "mono"
    comp = capture_components(font)
    removeOverlaps(font, ignoreErrors=True)
    designs = (DESIGNS_MONO + DASHES_MONO) if mono else (DESIGNS + DASHES_SANS)
    rep = apply_designs(font, comp, designs, verbose=False)
    if rep.get('_rebuilt'):
        removeOverlaps(font, glyphNames=rep['_rebuilt'], ignoreErrors=True)
    if mono:
        fix_mono_ligatures(font)
    for new, base, delta, chars in (MONO_ARROWS if mono else SANS_ARROWS):
        add_arrow(font, new, base, delta, chars)
    n = round_font_glyphs(font, radius if STYLES[style]["R"] > 0 else 0.0, 1.0)
    apply_tracking(font, track, mono)
    finish(font, kind, style, sub, wc)
    return n


def build(args, style, kind):
    vf = args.geist_vf if kind == "sans" else args.geist_mono_vf
    st = STYLES[style]
    out = os.path.join(args.out, style)
    os.makedirs(out, exist_ok=True)
    for wc, sub in WEIGHTS[kind].items():
        if args.sub and sub != args.sub:
            continue
        font = instantiateVariableFont(TTFont(vf), {"wght": float(wc)}, inplace=False,
                                       overlap=OverlapMode.KEEP_AND_DONT_SET_FLAGS)
        n = process(font, kind, style, sub, wc, args.radius, args.track)
        path = os.path.join(out, f"{st['prefix'][kind]}-{sub}.ttf")
        font.save(path)
        print(f"{style:7s} {kind:4s} {sub:11s} wc {wc:3d}  fillets {n}  -> {path}")


def main():
    ap = argparse.ArgumentParser(description="Build the Nortics Geist fonts.")
    ap.add_argument("--geist-vf", required=True, help='path to Geist[wght].ttf')
    ap.add_argument("--geist-mono-vf", required=True, help='path to GeistMono[wght].ttf')
    ap.add_argument("--out", default="build", help="output directory (default: build)")
    ap.add_argument("--style", default="all", choices=["rounded", "sharp", "all"])
    ap.add_argument("--kind", default="all", choices=["sans", "mono", "all"])
    ap.add_argument("--sub", default=None, help="build only this subfamily (e.g. Regular)")
    ap.add_argument("--radius", type=float, default=20.0, help="corner radius, rounded style (font units)")
    ap.add_argument("--track", type=float, default=TRACK, help="spacing removed per character (font units)")
    args = ap.parse_args()
    for s in (STYLES if args.style == "all" else [args.style]):
        for k in (("sans", "mono") if args.kind == "all" else (args.kind,)):
            build(args, s, k)
    print("DONE")


if __name__ == "__main__":
    main()
