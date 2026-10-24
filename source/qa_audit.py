"""QA: count the remaining sharp corners of each font.

A corner is a vertex where the outline turns by >= 20 degrees. Corners next to a segment shorter than
8 font units ("micro") are reported separately because they are grid-quantization artifacts, not design corners.

  python qa_audit.py "fonts/geist-rounded-by-nortics/ttf/*.ttf"
"""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fontTools.ttLib import TTFont
from fontround import audit_font

files = []
for pattern in sys.argv[1:]:
    files.extend(sorted(glob.glob(pattern)))
if not files:
    sys.exit(__doc__)
print(f"{'font':44s} {'glyphs':>6s} {'bad':>5s} {'corners':>8s} {'L-L':>6s} {'L-Q':>6s} {'Q-Q':>6s} {'micro':>6s}")
for f in files:
    r = audit_font(TTFont(f))
    print(f"{os.path.basename(f):44s} {r['glyphs']:6d} {r['bad_glyphs']:5d} {r['corners']:8d} "
          f"{r['LL']:6d} {r['LQ']:6d} {r['QQ']:6d} {r['micro']:6d}   {','.join(r['bad_names'][:4])}")
