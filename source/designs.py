import math
from fontround import get_contours, build_glyph


def P(x, y): return (float(x), float(y))
def L(a, b): return ('L', a, None, b)


def ends(c): return [s[1] for s in c]


def area(c):
    pts = []
    for s in c:
        pts.append(s[1])
        if s[0] == 'Q':
            pts.append(s[2])
    a = 0.0
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        a += x0 * y1 - x1 * y0
    return a / 2


def reverse(c):
    return [(k, p1, cc, p0) for (k, p0, cc, p1) in reversed(c)]


def orient_like(new, old):
    return new if (area(new) < 0) == (area(old) < 0) else reverse(new)


def arc_quads(c, r, a0, a1, start, end):
    n = max(1, int(math.ceil(abs(a1 - a0) / 45.0)))
    step = (a1 - a0) / n
    out, prev = [], start
    for j in range(n):
        am = math.radians(a0 + step * (j + 0.5))
        k = r / math.cos(math.radians(step) / 2)
        ctrl = (c[0] + k * math.cos(am), c[1] + k * math.sin(am))
        if j == n - 1:
            e = end
        else:
            ae = math.radians(a0 + step * (j + 1))
            e = (c[0] + r * math.cos(ae), c[1] + r * math.sin(ae))
        out.append(('Q', prev, ctrl, e))
        prev = e
    return out


def translate(c, d):
    def tp(p): return None if p is None else (p[0] + d[0], p[1] + d[1])
    return [(k, tp(p0), tp(cc), tp(p1)) for (k, p0, cc, p1) in c]


def same_shape(a, b, tol=0.6):
    if len(a) != len(b):
        return None
    d = (b[0][1][0] - a[0][1][0], b[0][1][1] - a[0][1][1])
    for s, t in zip(a, b):
        if s[0] != t[0]:
            return None
        for i in (1, 2, 3):
            if (s[i] is None) != (t[i] is None):
                return None
            if s[i] is None:
                continue
            if abs(t[i][0] - s[i][0] - d[0]) > tol or abs(t[i][1] - s[i][1] - d[1]) > tol:
                return None
    return d


def top_x(c, tol=0.5):
    pts = ends(c)
    top = max(y for _, y in pts)
    xs = [x for x, y in pts if y >= top - tol]
    return min(xs), max(xs), top


def bottom_x(c, tol=0.5):
    pts = ends(c)
    xs = [x for x, y in pts if y <= tol]
    return (min(xs), max(xs)) if xs else None


def measure_th(allc):
    f = allc.get('f')
    if not f:
        return None
    best = None
    for s in f[0]:
        if s[0] == 'L' and abs(s[1][0] - s[3][0]) < 0.5 and abs(s[1][1] - s[3][1]) > 3:
            x = s[1][0]
            if best is None or x < best[0]:
                best = (x, abs(s[3][1] - s[1][1]))
    return best[1] if best else None


def measure_xh(allc):
    x = allc.get('x')
    return max(y for c in x for _, y in ends(c)) if x else None


# every design returns (new_contours, advance_delta, mark_dx) or None
def design_l(old, ctx, adv):
    if len(old) != 1:
        return None
    c = old[0]
    x0, x1, top = top_x(c)
    w = x1 - x0
    if not 15 < w < 300:
        return None
    th, ro, tl = ctx['th'], 0.95 * w, 0.94 * w
    xr = x1 + tl
    oldmax = max(x for x, _ in ends(c))
    segs = [L(P(x0, ro), P(x0, top)), L(P(x0, top), P(x1, top)), L(P(x1, top), P(x1, th)),
            L(P(x1, th), P(xr, th)), L(P(xr, th), P(xr, 0)), L(P(xr, 0), P(x0 + ro, 0))]
    segs += arc_quads((x0 + ro, ro), ro, 270, 180, P(x0 + ro, 0), P(x0, ro))
    return [orient_like(segs, c)], xr - oldmax, 0.0


def design_t(old, ctx, adv):
    if len(old) != 1:
        return None
    c = old[0]
    x0, x1, top = top_x(c)
    w = x1 - x0
    pts = ends(c)
    xl, xr = min(x for x, _ in pts), max(x for x, _ in pts)
    th, xh = ctx['th'], ctx['xh']
    if not (15 < w < 300 and xl < x0 - 0.1 * w and xr > x1 + 0.2 * w):
        return None
    oldxr = xr
    xr = max(xr, x1 + 1.0 * w)
    ro = min(0.95 * w, xh - th - 5)
    segs = [L(P(x0, ro), P(x0, xh - th)), L(P(x0, xh - th), P(xl, xh - th)), L(P(xl, xh - th), P(xl, xh)),
            L(P(xl, xh), P(x0, xh)), L(P(x0, xh), P(x0, top)), L(P(x0, top), P(x1, top)),
            L(P(x1, top), P(x1, xh)), L(P(x1, xh), P(xr, xh)), L(P(xr, xh), P(xr, xh - th)),
            L(P(xr, xh - th), P(x1, xh - th)), L(P(x1, xh - th), P(x1, th)), L(P(x1, th), P(xr, th)),
            L(P(xr, th), P(xr, 0)), L(P(xr, 0), P(x0 + ro, 0))]
    segs += arc_quads((x0 + ro, ro), ro, 270, 180, P(x0 + ro, 0), P(x0, ro))
    return [orient_like(segs, c)], xr - oldxr, 0.0


def design_J(old, ctx, adv):
    if len(old) != 1:
        return None
    c = old[0]
    x0, x1, top = top_x(c)
    w = x1 - x0
    pts = ends(c)
    oldmin, oldmax = min(x for x, _ in pts), max(x for x, _ in pts)
    if not 15 < w < 300:
        return None
    th = ctx['th']
    ro, lf = 0.95 * w, 2.0 * w
    xl = 0.65 * w
    X0 = xl + lf
    X1 = X0 + w
    segs = [L(P(X0, top), P(X1, top)), L(P(X1, top), P(X1, ro))]
    segs += arc_quads((X1 - ro, ro), ro, 0, -90, P(X1, ro), P(X1 - ro, 0))
    segs += [L(P(X1 - ro, 0), P(xl, 0)), L(P(xl, 0), P(xl, th)), L(P(xl, th), P(X0, th)), L(P(X0, th), P(X0, top))]
    new_adv = X1 + (adv - oldmax)
    mark_dx = (xl + X1) / 2 - (oldmin + oldmax) / 2
    return [orient_like(segs, c)], new_adv - adv, mark_dx


def design_f(old, ctx, adv):
    if len(old) != 1:
        return None
    c = old[0]
    pts = ends(c)
    top = max(y for _, y in pts)
    xl, xt = min(x for x, _ in pts), max(x for x, _ in pts)
    b = bottom_x(c)
    if not b:
        return None
    x0, x1 = b
    w = x1 - x0
    th, xh = ctx['th'], ctx['xh']
    if not (15 < w < 300 and xl < x0 - 0.2 * w):
        return None
    ro = min(0.95 * w, top - xh - 10)
    if ro < 5:
        return None
    segs = [L(P(x0, 0), P(x0, xh - th)), L(P(x0, xh - th), P(xl, xh - th)), L(P(xl, xh - th), P(xl, xh)),
            L(P(xl, xh), P(x0, xh)), L(P(x0, xh), P(x0, top - ro))]
    segs += arc_quads((x0 + ro, top - ro), ro, 180, 90, P(x0, top - ro), P(x0 + ro, top))
    segs += [L(P(x0 + ro, top), P(xt, top)), L(P(xt, top), P(xt, top - th)), L(P(xt, top - th), P(x1, top - th)),
             L(P(x1, top - th), P(x1, xh)), L(P(x1, xh), P(xt, xh)), L(P(xt, xh), P(xt, xh - th)),
             L(P(xt, xh - th), P(x1, xh - th)), L(P(x1, xh - th), P(x1, 0)), L(P(x1, 0), P(x0, 0))]
    return [orient_like(segs, c)], 0.0, 0.0


def design_j(old, ctx, adv):
    # base = dotless j ('uni0237'); j, jcircumflex, jcaron inherit by contour match
    if len(old) != 1:
        return None
    c = old[0]
    x0, x1, top = top_x(c)
    w = x1 - x0
    pts = ends(c)
    ymin, xl = min(y for _, y in pts), min(x for x, _ in pts)
    if not (15 < w < 300 and xl < x0 - 0.3 * w and ymin < -50):
        return None
    th, ro = ctx['th'], 0.95 * w
    segs = [L(P(x0, top), P(x1, top)), L(P(x1, top), P(x1, ymin + ro))]
    segs += arc_quads((x1 - ro, ymin + ro), ro, 0, -90, P(x1, ymin + ro), P(x1 - ro, ymin))
    segs += [L(P(x1 - ro, ymin), P(xl, ymin)), L(P(xl, ymin), P(xl, ymin + th)),
             L(P(xl, ymin + th), P(x0, ymin + th)), L(P(x0, ymin + th), P(x0, top))]
    return [orient_like(segs, c)], 0.0, 0.0


def design_J_mono(old, ctx, adv):
    # cell is fixed-width: keep the J centred in it
    if len(old) != 1:
        return None
    c = old[0]
    x0, x1, top = top_x(c)
    w = x1 - x0
    pts = ends(c)
    oldmin, oldmax = min(x for x, _ in pts), max(x for x, _ in pts)
    if not 15 < w < 300:
        return None
    th, ro, lf = ctx['th'], 0.95 * w, 2.2 * w
    xl = adv / 2.0 - (lf + w) / 2.0
    X0 = xl + lf
    X1 = X0 + w
    segs = [L(P(X0, top), P(X1, top)), L(P(X1, top), P(X1, ro))]
    segs += arc_quads((X1 - ro, ro), ro, 0, -90, P(X1, ro), P(X1 - ro, 0))
    segs += [L(P(X1 - ro, 0), P(xl, 0)), L(P(xl, 0), P(xl, th)), L(P(xl, th), P(X0, th)), L(P(X0, th), P(X0, top))]
    return [orient_like(segs, c)], 0.0, (xl + X1) / 2 - (oldmin + oldmax) / 2


def design_j_mono(old, ctx, adv):
    # dotless j with the typewriter flag at x-height; only the foot is redrawn
    if len(old) != 1:
        return None
    c = old[0]
    pts = ends(c)
    top = max(y for _, y in pts)
    ymin = min(y for _, y in pts)
    xl, x1 = min(x for x, _ in pts), max(x for x, _ in pts)
    th, xh = ctx['th'], ctx['xh']
    vert = [(abs(s[3][1] - s[1][1]), s[1][0]) for s in c
            if s[0] == 'L' and abs(s[1][0] - s[3][0]) < 0.5 and s[1][0] < x1 - 5]
    if not vert or ymin > -50:
        return None
    x0 = max(vert)[1]
    w = x1 - x0
    slab = [x for x, y in pts if xh - th - 0.5 <= y <= xh + 0.5]
    sl = min(slab) if slab else x0
    if not (15 < w < 300 and xl < x0 - 0.3 * w and sl < x0 - 5 and abs(top - xh) < 1):
        return None
    ro = 0.95 * w
    segs = [L(P(xl, ymin), P(xl, ymin + th)), L(P(xl, ymin + th), P(x0, ymin + th)),
            L(P(x0, ymin + th), P(x0, xh - th)), L(P(x0, xh - th), P(sl, xh - th)),
            L(P(sl, xh - th), P(sl, xh)), L(P(sl, xh), P(x1, xh)), L(P(x1, xh), P(x1, ymin + ro))]
    segs += arc_quads((x1 - ro, ymin + ro), ro, 0, -90, P(x1, ymin + ro), P(x1 - ro, ymin))
    segs += [L(P(x1 - ro, ymin), P(xl, ymin))]
    return [orient_like(segs, c)], 0.0, 0.0


def make_dash(factor, cap=None):
    """Lengthen a plain rectangular dash. Sans: grow to the right and widen the advance.
    Mono (cap given): keep it centred in the fixed cell and never exceed `cap`."""
    def f(old, ctx, adv):
        if len(old) != 1 or len(old[0]) != 4:
            return None
        c = old[0]
        pts = ends(c)
        xs, ys = [x for x, _ in pts], [y for _, y in pts]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        ln = x1 - x0
        if ln < 100 or (y1 - y0) > 150:
            return None
        nl = factor * ln
        if cap is not None:
            nl = min(nl, cap)
            nx0, nx1, dadv = adv / 2.0 - nl / 2.0, adv / 2.0 + nl / 2.0, 0.0
        else:
            nx0, nx1, dadv = x0, x0 + nl, nl - ln
        segs = [L(P(nx0, y0), P(nx0, y1)), L(P(nx0, y1), P(nx1, y1)),
                L(P(nx1, y1), P(nx1, y0)), L(P(nx1, y0), P(nx0, y0))]
        return [orient_like(segs, c)], dadv, 0.0
    return f


DASHES_SANS = (('hyphen', make_dash(1.5)), ('endash', make_dash(1.5)), ('emdash', make_dash(1.5)))
DASHES_MONO = (('hyphen', make_dash(1.5, 540)), ('endash', make_dash(1.5, 580)), ('emdash', make_dash(1.5, 600)))

DESIGNS = (('l', design_l), ('t', design_t), ('J', design_J), ('f', design_f), ('uni0237', design_j))
DESIGNS_MONO = (('t', design_t), ('J', design_J_mono), ('f', design_f), ('uni0237', design_j_mono))


def capture_components(font):
    glyf = font['glyf']
    info = {}
    for n in font.getGlyphOrder():
        g = glyf[n]
        if g.numberOfContours < 0:
            ok, comps = True, []
            for c in g.components:
                tr = getattr(c, 'transform', None)
                if tr is not None and [list(r) for r in tr] != [[1, 0], [0, 1]]:
                    ok = False
                comps.append((c.glyphName, c.x, c.y))
            if ok:
                info[n] = comps
    return info


def apply_designs(font, comp=None, designs=None, verbose=True):
    designs = designs or DESIGNS
    gs = font.getGlyphSet()
    glyf, hmtx = font['glyf'], font['hmtx']
    names = [n for n in font.getGlyphOrder() if glyf[n].numberOfContours != 0]
    allc = {n: get_contours(gs, n) for n in names}
    ctx = {'th': measure_th(allc), 'xh': measure_xh(allc)}
    if not ctx['th'] or not ctx['xh']:
        if verbose:
            print("   designs: medidas falharam", ctx)
        return {}
    cur = {n: list(cs) for n, cs in allc.items()}
    advd, changed, report, newbases = {}, set(), {}, {}
    for base, fn in designs:
        if base not in allc:
            continue
        res = fn(allc[base], ctx, hmtx[base][0])
        if res is None:
            report[base] = None
            continue
        newc, adv_delta, mark_dx = res
        newbases[base] = res
        hits = []
        for n in list(cur):
            out, flags = [], []
            for ct in cur[n]:
                d = same_shape(allc[base][0], ct)
                if d is None:
                    out.append(ct); flags.append(False)
                else:
                    out.append(translate(newc[0], d)); flags.append(True)
            if any(flags):
                if mark_dx and n != base:
                    out = [ct if fl else translate(ct, (mark_dx, 0)) for ct, fl in zip(out, flags)]
                cur[n] = out
                advd[n] = advd.get(n, 0) + adv_delta
                changed.add(n)
                hits.append(n)
        report[base] = hits
    for n in changed:
        glyf[n] = build_glyph(cur[n])
        aw, lsb = hmtx.metrics[n]
        hmtx.metrics[n] = (int(round(aw + advd.get(n, 0))), lsb)
    rebuilt = []
    for n, comps in (comp or {}).items():
        if n in changed or n not in hmtx.metrics:
            continue
        bases = [cn for cn, _, _ in comps if cn in newbases]
        if not bases:
            continue
        contours, delta = [], 0.0
        for cn, x, y in comps:
            if cn in newbases:
                nc, ad, mk = newbases[cn]
                contours += [translate(c, (x, y)) for c in nc]
                delta += ad
            elif cn in allc:
                mk = 0.0
                for b in bases:
                    mk = newbases[b][2] or mk
                contours += [translate(c, (x + mk, y)) for c in allc[cn]]
        if contours:
            glyf[n] = build_glyph(contours)
            aw, lsb = hmtx.metrics[n]
            hmtx.metrics[n] = (int(round(aw + delta)), lsb)
            rebuilt.append(n)
    if verbose:
        print("   designs th=%.0f xh=%.0f ->" % (ctx['th'], ctx['xh']),
              {k: (None if v is None else len(v)) for k, v in report.items()}, "recompostos:", rebuilt)
    report['_rebuilt'] = rebuilt
    return report
