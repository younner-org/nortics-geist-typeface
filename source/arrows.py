from fontTools.ttLib.tables import otTables
from fontround import get_contours, build_glyph
from designs import translate


def liga_subtables(font):
    gsub = font['GSUB'].table
    idx = set()
    for fr in gsub.FeatureList.FeatureRecord:
        if fr.FeatureTag == 'liga':
            idx.update(fr.Feature.LookupListIndex)
    out = []
    for li in sorted(idx):
        lk = gsub.LookupList.Lookup[li]
        for st in lk.SubTable:
            if lk.LookupType == 7:
                st = st.ExtSubTable
            if hasattr(st, 'ligatures'):
                out.append(st)
    return out


def liga_lengths(font):
    n = {}
    for st in liga_subtables(font):
        for first, ligs in st.ligatures.items():
            for lg in ligs:
                n.setdefault(lg.LigGlyph, len(lg.Component) + 1)
    return n


def fix_mono_ligatures(font, cell=600):
    """Geist Mono draws an N-char ligature glyph hanging back N-1 cells but advances a single cell.
    Rebase the outline to the glyph origin and advance N cells so columns stay aligned."""
    gs = font.getGlyphSet()
    glyf, hmtx = font['glyf'], font['hmtx']
    fixed = []
    for name, n in liga_lengths(font).items():
        if n < 2 or name not in glyf.keys() or glyf[name].numberOfContours == 0:
            continue
        cs = get_contours(gs, name)
        xs = [p[0] for c in cs for s in c for p in (s[1], s[2], s[3]) if p]
        if not xs or min(xs) > -40:
            continue
        glyf[name] = build_glyph([translate(c, ((n - 1) * cell, 0)) for c in cs])
        aw, lsb = hmtx.metrics[name]
        hmtx.metrics[name] = (n * cell, lsb)
        fixed.append(name)
    return fixed


def add_arrow(font, new_name, base, delta, chars):
    """Create a longer arrow by stretching the shaft of an existing ligature, and register the rule."""
    gs = font.getGlyphSet()
    glyf, hmtx = font['glyf'], font['hmtx']
    if base not in glyf.keys():
        return False
    cs = get_contours(gs, base)
    adv = hmtx[base][0]
    cut = adv / 2.0
    xs = [p[0] for c in cs for s in c for p in (s[1], s[2], s[3]) if p]
    for off in (0, 60, -60, 120, -120, 180, -180):
        if not any(abs(x - (cut + off)) < 30 for x in xs):
            cut += off
            break

    def sp(p):
        return None if p is None else ((p[0] + delta if p[0] > cut else p[0]), p[1])

    new = [[(k, sp(a), sp(b), sp(c)) for (k, a, b, c) in cont] for cont in cs]
    g = build_glyph(new)
    glyf[new_name] = g
    order = list(font.getGlyphOrder())
    if new_name not in order:
        order.append(new_name)
    font.setGlyphOrder(order)
    g.recalcBounds(glyf)
    hmtx.metrics[new_name] = (int(round(adv + delta)), g.xMin)
    if 'GDEF' in font and font['GDEF'].table.GlyphClassDef:
        font['GDEF'].table.GlyphClassDef.classDefs[new_name] = 2
    for st in liga_subtables(font):
        if chars[0] in st.ligatures:
            lg = otTables.Ligature()
            lg.LigGlyph = new_name
            lg.Component = list(chars[1:])
            lg.CompCount = len(chars)
            st.ligatures[chars[0]].append(lg)
            st.ligatures[chars[0]].sort(key=lambda l: -len(l.Component))
            return True
    return False


SANS_ARROWS = (
    ('less_hyphen_hyphen_greater.liga', 'less_hyphen_greater.liga', 600, ['less', 'hyphen', 'hyphen', 'greater']),
    ('less_hyphen_hyphen_hyphen_greater.liga', 'less_hyphen_greater.liga', 1200, ['less', 'hyphen', 'hyphen', 'hyphen', 'greater']),
)
MONO_ARROWS = (
    ('less_hyphen_hyphen_hyphen.liga', 'less_hyphen_hyphen.liga', 600, ['less', 'hyphen', 'hyphen', 'hyphen']),
    ('less_hyphen_hyphen_greater.liga', 'less_hyphen_greater.liga', 600, ['less', 'hyphen', 'hyphen', 'greater']),
    ('less_hyphen_hyphen_hyphen_greater.liga', 'less_hyphen_greater.liga', 1200, ['less', 'hyphen', 'hyphen', 'hyphen', 'greater']),
)
