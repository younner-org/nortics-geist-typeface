"""QA: check that the arrow ligatures shape to a single ligature glyph with the expected advance.

Expected advance = number of characters x cell (580 = 600 - 20 tracking). Uses HarfBuzz (uharfbuzz).

  python qa_arrows.py fonts/geist-rounded-mono-by-nortics/ttf [--cell 580]
"""
import argparse
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_text import shape

SEQ = ["->", "-->", "--->", "<-", "<--", "<---", "<->", "<-->", "<--->"]

ap = argparse.ArgumentParser()
ap.add_argument("dir")
ap.add_argument("--cell", type=int, default=580)
a = ap.parse_args()
ok_all = True
for f in sorted(glob.glob(os.path.join(a.dir, "*.ttf"))):
    ok, bad = 0, []
    for s in SEQ:
        buf, names, upem = shape(f, s)
        adv = sum(p.x_advance for p in buf.glyph_positions)
        if len(names) == 1 and names[0].endswith(".liga") and adv == len(s) * a.cell:
            ok += 1
        else:
            bad.append((s, names, adv))
    ok_all &= not bad
    print(f"{os.path.basename(f):46s} {ok}/{len(SEQ)} {bad if bad else ''}")
print("ALL OK" if ok_all else "FAILURES")
sys.exit(0 if ok_all else 1)
