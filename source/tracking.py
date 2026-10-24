from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates


def apply_tracking(font, t, mono, cell=600):
    """Tighten spacing by `t` font units per character.
    - plain glyphs: advance -t, outline shifted -t/2 (spacing removed evenly on both sides)
    - grid ligatures (N chars = N cells, and Geist Mono's 'hanging' ligatures): one uniform horizontal
      scale of (cell - t)/cell about the origin. Every cell shrinks by t, nothing is cut or sheared,
      so curves and arrow heads stay smooth.
    Run on simple (flattened) glyphs."""
    glyf, hmtx = font['glyf'], font['hmtx']
    s = (cell - t) / float(cell)
    changed = 0
    for name in font.getGlyphOrder():
        aw, lsb = hmtx.metrics[name]
        if aw <= 0:
            continue
        g = glyf[name]
        if g.numberOfContours <= 0:
            hmtx.metrics[name] = (aw - t, lsb)
            continue
        coords = list(g.coordinates)
        xs = [x for x, _ in coords]
        grid = name.endswith('.liga') and ((aw % cell == 0 and aw >= 2 * cell) or (mono and min(xs) < -40))
        if grid:
            new = [(x * s, y) for x, y in coords]
            newadv = aw * s
        else:
            new = [(x - t / 2.0, y) for x, y in coords]
            newadv = aw - t
        g.coordinates = GlyphCoordinates(new)
        g.recalcBounds(glyf)
        hmtx.metrics[name] = (int(round(newadv)), g.xMin)
        changed += 1
    return changed
