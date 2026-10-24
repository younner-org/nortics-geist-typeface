"""Generate web/webfonts.css and web/specimen.html from the fonts in fonts/.

  python gen_web.py            (run from the repository root or from source/)
"""
import glob
import html
import os
import urllib.parse
from fontTools.ttLib import TTFont

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FONTS = os.path.join(REPO, "fonts")
WEB = os.path.join(REPO, "web")
os.makedirs(WEB, exist_ok=True)

families = []  # (dir, family, kind, rows[(wc, sub, file)])
for fdir in sorted(os.listdir(FONTS)):
    ttfs = glob.glob(os.path.join(FONTS, fdir, "ttf", "*.ttf"))
    if not ttfs:
        continue
    rows, family = [], None
    for f in ttfs:
        t = TTFont(f)
        family = t['name'].getDebugName(16)
        rows.append((t['OS/2'].usWeightClass, t['name'].getDebugName(17), os.path.basename(f)[:-4]))
    rows.sort()
    families.append((fdir, family, "mono" if "mono" in fdir else "sans", rows))

css = ["/* Nortics Geist - web fonts (WOFF2). SIL Open Font License 1.1.",
       "   Link this file and use the family names below, e.g.  font-family: \"Geist Rounded by Nortics\"; font-weight: 250; */", ""]
for fdir, fam, kind, rows in families:
    css.append(f"/* {fam} */")
    for wc, sub, stem in rows:
        url = urllib.parse.quote(f"../fonts/{fdir}/woff2/{stem}.woff2")
        css.append(f'@font-face {{ font-family: "{fam}"; font-weight: {wc}; font-style: normal; '
                   f'font-display: swap; src: url("{url}") format("woff2"); }}')
    css.append("")
with open(os.path.join(WEB, "webfonts.css"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(css))

blocks = []
for fdir, fam, kind, rows in families:
    lines = ["Rage Against The Machine", "Killing In The Name 5:14 [1992]",
             "const a = b --> c;  x &lt;--&gt; y;  fn =&gt; z" if kind == "mono"
             else "Epic Associated ZAT-4842  a --&gt; b  c &lt;--&gt; d"]
    b = [f"<section><h2>{html.escape(fam)}</h2>"]
    for wc, sub, _ in rows:
        b.append(f'<div class="row"><span class="w">{wc} {sub}</span>'
                 f'<p style="font-family:\'{fam}\';font-weight:{wc}">' + "<br>".join(lines) + "</p></div>")
    b.append("</section>")
    blocks.append("\n".join(b))
page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nortics Geist - specimen</title>
<link rel="stylesheet" href="webfonts.css">
<style>
body{background:#0e0e0e;color:#f5f5f5;font:16px system-ui,sans-serif;margin:0;padding:48px}
h1{font:600 14px system-ui;letter-spacing:.08em;text-transform:uppercase;color:#9a9a9a;margin:0 0 8px}
h2{font:600 14px system-ui;letter-spacing:.08em;text-transform:uppercase;color:#7cc4ff;margin:56px 0 12px;border-top:1px solid #2a2a2a;padding-top:24px}
.row{display:flex;gap:32px;align-items:baseline;border-bottom:1px solid #1d1d1d;padding:10px 0}
.w{flex:0 0 150px;font:12px ui-monospace,monospace;color:#7a7a7a}
p{margin:0;font-size:34px;line-height:1.25}
</style></head><body><h1>Nortics Geist - by Andre Dorneles</h1>
""" + "\n".join(blocks) + "\n</body></html>\n"
with open(os.path.join(WEB, "specimen.html"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(page)
print("web/webfonts.css and web/specimen.html written for", sum(len(r[3]) for r in families), "fonts")
