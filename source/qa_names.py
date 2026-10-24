"""QA: check naming / weight consistency of a family directory (or any set of .ttf files).

Checks: unique PostScript names, unique weight classes per family, RIBBI rules (nameID 1/2),
fsSelection / macStyle bits, designer, vendor ID.

  python qa_names.py "fonts/*/ttf/*.ttf"
"""
import glob
import os
import sys
from collections import defaultdict
from fontTools.ttLib import TTFont

files = []
for pattern in sys.argv[1:]:
    files.extend(sorted(glob.glob(pattern)))
if not files:
    sys.exit(__doc__)
problems = []
by_family_wc, by_ps = defaultdict(list), defaultdict(list)
for f in files:
    t = TTFont(f)

    def nm(i):
        return next((r.toUnicode() for r in t['name'].names if r.nameID == i and r.platformID == 3), "")

    fam, sub, wc = nm(16), nm(17), t['OS/2'].usWeightClass
    sel, mac = t['OS/2'].fsSelection, t['head'].macStyle
    by_family_wc[(fam, wc)].append(f)
    by_ps[nm(6)].append(f)
    ribbi = sub in ("Regular", "Bold")
    if nm(2) != (sub if ribbi else "Regular"):
        problems.append((f, "nameID 2 breaks the RIBBI rule", nm(2)))
    if nm(1) != (fam if ribbi else f"{fam} {sub}"):
        problems.append((f, "nameID 1 breaks the RIBBI rule", nm(1)))
    if bool(sel & 0x40) != (sub == "Regular") or bool(sel & 0x20) != (sub == "Bold"):
        problems.append((f, "fsSelection REGULAR/BOLD bits", hex(sel)))
    if not sel & 0x80:
        problems.append((f, "fsSelection USE_TYPO_METRICS not set", hex(sel)))
    if bool(mac & 1) != (sub == "Bold"):
        problems.append((f, "head.macStyle bold bit", mac))
    if nm(9) != "Andre Dorneles":
        problems.append((f, "designer", nm(9)))
    if t['OS/2'].achVendID.strip() != "NRTC":
        problems.append((f, "vendor id", t['OS/2'].achVendID))
for k, v in by_family_wc.items():
    if len(v) > 1:
        problems.append((k, "duplicate weight class", [os.path.basename(x) for x in v]))
for k, v in by_ps.items():
    if len(v) > 1:
        problems.append((k, "duplicate PostScript name", [os.path.basename(x) for x in v]))
print(f"{len(files)} fonts checked")
print("problems:", problems if problems else "none")
sys.exit(1 if problems else 0)
