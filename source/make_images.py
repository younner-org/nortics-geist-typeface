"""Render the specimen images used in the documentation (needs Pillow, freetype-py, uharfbuzz).

  python make_images.py --fonts ../fonts --out ../docs/images [--geist-vf "Geist[wght].ttf"]

--geist-vf is optional; with it, design-changes.png also shows the original Geist for comparison.
"""
import argparse
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from render_text import render

ap = argparse.ArgumentParser()
ap.add_argument("--fonts", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--geist-vf", default=None)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)


def fam(d):
    items = []
    for f in glob.glob(os.path.join(a.fonts, d, "ttf", "*.ttf")):
        t = TTFont(f)
        items.append((t['OS/2'].usWeightClass, t['name'].getDebugName(17), f))
    return sorted(items)


def pick(d, wc=400):
    return next(f for w, s, f in fam(d) if w == wc)


LABEL = ImageFont.truetype(pick("geist-rounded-by-nortics"), 20)
BLUE, GREY = (124, 196, 255), (130, 130, 130)


def stack(tiles, path, pad=26):
    W = max(t.width for t in tiles)
    H = sum(t.height for t in tiles) + pad
    sheet = Image.new("RGB", (W, H), (14, 14, 14))
    y = pad // 2
    for t in tiles:
        sheet.paste(t, (0, y))
        y += t.height
    sheet.save(os.path.join(a.out, path), optimize=True)
    print("written", path, sheet.size)


def labelled(label, font, lines, size, color=BLUE):
    im = render(font, lines, size, bg=(14, 14, 14), pad=22)
    t = Image.new("RGB", (im.width, im.height + 30), (14, 14, 14))
    ImageDraw.Draw(t).text((22, 4), label, fill=color, font=LABEL)
    t.paste(im, (0, 30))
    return t


# 1. weights of the sans / 2. weights of the mono
stack([labelled(f"{w}  {s}", f, ["Rage Against The Machine"], 50, GREY) for w, s, f in fam("geist-rounded-by-nortics")],
      "weights-sans.png")
stack([labelled(f"{w}  {s}", f, ["const rate = a --> b;  // x != y"], 40, GREY) for w, s, f in fam("geist-rounded-mono-by-nortics")],
      "weights-mono.png")

# 3. rounded vs sharp
tiles = []
for label, d, lines, size in (
        ("Geist Rounded by Nortics - Regular", "geist-rounded-by-nortics", ["Rage Against The Machine", "EHKRtJjf  5:14 [1992]"], 56),
        ("Geist Sharp by Nortics - Regular", "geist-sharp-by-nortics", ["Rage Against The Machine", "EHKRtJjf  5:14 [1992]"], 56),
        ("Geist Rounded Mono by Nortics - Regular", "geist-rounded-mono-by-nortics", ["const EHKRtJjf = 5;  // 1992"], 44),
        ("Geist Sharp Mono by Nortics - Regular", "geist-sharp-mono-by-nortics", ["const EHKRtJjf = 5;  // 1992"], 44)):
    tiles.append(labelled(label, pick(d), lines, size))
stack(tiles, "rounded-vs-sharp.png")

# 4. arrows
arrow_lines = ["a->b  a-->b  a--->b", "a<-b  a<--b  a<---b", "a<->b  a<-->b  a<--->b"]
stack([labelled("Geist Rounded by Nortics", pick("geist-rounded-by-nortics"), arrow_lines, 52),
       labelled("Geist Rounded Mono by Nortics", pick("geist-rounded-mono-by-nortics"), arrow_lines + ["x => y   x == y   x != y   a <= b"], 44)],
      "arrows.png")

# 5. design changes vs the original Geist
rows = []
glyphs = ["a t l J j f   - \u2013 \u2014   ->"]
if a.geist_vf:
    rows.append(labelled("Geist (original, Vercel)", a.geist_vf, glyphs, 90, GREY))
rows.append(labelled("Geist Sharp by Nortics", pick("geist-sharp-by-nortics"), glyphs, 90))
rows.append(labelled("Geist Rounded by Nortics", pick("geist-rounded-by-nortics"), glyphs, 90))
stack(rows, "design-changes.png")
