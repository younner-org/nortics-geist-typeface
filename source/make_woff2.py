"""Convert every fonts/<family>/ttf/*.ttf into fonts/<family>/woff2/*.woff2 (needs fontTools + brotli).

  python make_woff2.py ../fonts
"""
import glob
import os
import sys
from fontTools.ttLib import TTFont

root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts")
n = 0
for ttf in sorted(glob.glob(os.path.join(root, "*", "ttf", "*.ttf"))):
    out_dir = os.path.join(os.path.dirname(os.path.dirname(ttf)), "woff2")
    os.makedirs(out_dir, exist_ok=True)
    font = TTFont(ttf)
    font.flavor = "woff2"
    font.save(os.path.join(out_dir, os.path.basename(ttf)[:-4] + ".woff2"))
    n += 1
print(f"{n} WOFF2 files written")
