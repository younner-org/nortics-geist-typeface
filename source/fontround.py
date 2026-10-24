import math
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.basePen import BasePen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables.ttProgram import Program


class FlattenPen(BasePen):
    def __init__(self, glyphSet, outPen):
        super().__init__(glyphSet)
        self.outPen = outPen

    def _moveTo(self, pt): self.outPen.moveTo(pt)
    def _lineTo(self, pt): self.outPen.lineTo(pt)
    def _curveToOne(self, *pts): self.outPen.curveTo(*pts)
    def _qCurveToOne(self, *pts): self.outPen.qCurveTo(*pts)
    def _closePath(self): self.outPen.closePath()


# segment = (kind, p0, c, p1); kind 'L' (c is None) or 'Q'
def get_contours(glyphSet, name):
    rec = RecordingPen()
    glyphSet[name].draw(FlattenPen(glyphSet, rec))
    contours, cur, start, pos = [], None, None, None
    for cmd, pts in rec.value:
        if cmd == 'moveTo':
            start = pos = (float(pts[0][0]), float(pts[0][1]))
            cur = []
        elif cmd == 'lineTo' and cur is not None:
            p = (float(pts[0][0]), float(pts[0][1]))
            if p != pos:
                cur.append(('L', pos, None, p))
                pos = p
        elif cmd == 'qCurveTo' and cur is not None:
            if pts[-1] is None:
                cur = None
                continue
            c = (float(pts[0][0]), float(pts[0][1]))
            e = (float(pts[1][0]), float(pts[1][1]))
            if not (c == pos and e == pos):
                cur.append(('Q', pos, c, e))
                pos = e
        elif cmd in ('closePath', 'endPath'):
            if cur is not None:
                if pos != start:
                    cur.append(('L', pos, None, start))
                if len(cur) >= 2:
                    contours.append(cur)
            cur = None
    return contours


def sub(a, b): return (a[0] - b[0], a[1] - b[1])
def add(a, b): return (a[0] + b[0], a[1] + b[1])
def mul(a, k): return (a[0] * k, a[1] * k)
def cross(a, b): return a[0] * b[1] - a[1] * b[0]
def dot(a, b): return a[0] * b[0] + a[1] * b[1]
def norm(a): return math.hypot(a[0], a[1])


def unit(a):
    n = norm(a)
    return (0.0, 0.0) if n < 1e-9 else (a[0] / n, a[1] / n)


def tan_start(s):
    k, p0, c, p1 = s
    if k == 'Q':
        d = sub(c, p0)
        if norm(d) > 1e-9:
            return d
    return sub(p1, p0)


def tan_end(s):
    k, p0, c, p1 = s
    if k == 'Q':
        d = sub(p1, c)
        if norm(d) > 1e-9:
            return d
    return sub(p1, p0)


def turn_deg(ta, tb):
    ua, ub = unit(ta), unit(tb)
    if norm(ua) == 0 or norm(ub) == 0:
        return 0.0
    return math.degrees(math.acos(max(-1.0, min(1.0, dot(ua, ub)))))


def corners(contour, thr=20.0):
    out = []
    n = len(contour)
    for i in range(n):
        a, b = contour[i - 1], contour[i]
        t = turn_deg(tan_end(a), tan_start(b))
        if t >= thr:
            out.append((a[0] + b[0], t, contour[i][1], seg_len(a), seg_len(b)))
    return out


def audit_font(font, thr=20.0):
    gs = font.getGlyphSet()
    glyf = font['glyf']
    res = {'glyphs': 0, 'bad_glyphs': 0, 'corners': 0, 'LL': 0, 'LQ': 0, 'QQ': 0, 'micro': 0, 'bad_names': []}
    for name in font.getGlyphOrder():
        g = glyf[name]
        if g.numberOfContours == 0:
            continue
        cs = get_contours(gs, name)
        if not cs:
            continue
        res['glyphs'] += 1
        n = 0
        for c in cs:
            for kinds, t, p, la, lb in corners(c, thr):
                if min(la, lb) < 8.0:
                    res['micro'] += 1
                    continue
                n += 1
                if kinds == 'LL':
                    res['LL'] += 1
                elif kinds in ('LQ', 'QL'):
                    res['LQ'] += 1
                else:
                    res['QQ'] += 1
        if n:
            res['bad_glyphs'] += 1
            if len(res['bad_names']) < 12:
                res['bad_names'].append(name)
        res['corners'] += n
    return res


# ---------------- rounding ----------------
def quad_pt(p0, c, p1, t):
    u = 1 - t
    return (u * u * p0[0] + 2 * u * t * c[0] + t * t * p1[0],
            u * u * p0[1] + 2 * u * t * c[1] + t * t * p1[1])


def blossom(seg, u, v):
    _, p0, c, p1 = seg
    a, b, d = (1 - u) * (1 - v), (1 - u) * v + u * (1 - v), u * v
    return (a * p0[0] + b * c[0] + d * p1[0], a * p0[1] + b * c[1] + d * p1[1])


def seg_len(s, n=40):
    k, p0, c, p1 = s
    if k == 'L':
        return norm(sub(p1, p0))
    pts = [quad_pt(p0, c, p1, i / n) for i in range(n + 1)]
    return sum(norm(sub(pts[i + 1], pts[i])) for i in range(n))


def param_at_length(s, d, n=80):
    k, p0, c, p1 = s
    pts = [quad_pt(p0, c, p1, i / n) for i in range(n + 1)]
    acc = 0.0
    for i in range(n):
        step = norm(sub(pts[i + 1], pts[i]))
        if acc + step >= d:
            f = 0 if step == 0 else (d - acc) / step
            return (i + f) / n
        acc += step
    return 1.0


def trim(seg, a, b, L):
    k, p0, c, p1 = seg
    if k == 'L':
        d = unit(sub(p1, p0))
        return ('L', add(p0, mul(d, a)), None, sub(p1, mul(d, b)))
    s = param_at_length(seg, a) if a > 0 else 0.0
    e = param_at_length(seg, L - b) if b > 0 else 1.0
    if e <= s + 1e-3:
        e = min(1.0, s + 1e-3)
    return ('Q', blossom(seg, s, s), blossom(seg, s, e), blossom(seg, e, e))


def fillet(a_t, b_t, a_orig, b_orig, t_used, turn):
    T1, T2 = a_t[3], b_t[1]
    if norm(sub(T2, T1)) < 0.01:
        return []
    tin = unit(tan_end(a_t))
    tout = unit(tan_start(b_t))
    if a_orig[0] == 'L' and b_orig[0] == 'L':
        reff = t_used / math.tan(math.radians(turn) / 2)
        sgn = 1 if cross(tin, tout) > 0 else -1
        nrm = (-tin[1] * sgn, tin[0] * sgn)
        O = add(T1, mul(nrm, reff))
        a1 = math.atan2(T1[1] - O[1], T1[0] - O[0])
        sweep = math.radians(turn) * sgn
        n = max(1, int(math.ceil(turn / 45.0)))
        step = sweep / n
        out, prev = [], T1
        for j in range(n):
            amid = a1 + step * (j + 0.5)
            ctrl = (O[0] + reff / math.cos(step / 2) * math.cos(amid),
                    O[1] + reff / math.cos(step / 2) * math.sin(amid))
            aend = a1 + step * (j + 1)
            end = T2 if j == n - 1 else (O[0] + reff * math.cos(aend), O[1] + reff * math.sin(aend))
            out.append(('Q', prev, ctrl, end))
            prev = end
        return out
    den = cross(tin, tout)
    if abs(den) > 1e-6:
        d = sub(T2, T1)
        aa = cross(d, tout) / den
        bb = cross(d, tin) / den
        if aa > 0 and bb < 0 and aa < 4 * t_used + 5 and -bb < 4 * t_used + 5:
            return [('Q', T1, add(T1, mul(tin, aa)), T2)]
    return [('L', T1, None, T2)]


def round_contour(segs, R, min_turn=12.0):
    n = len(segs)
    if n < 3:
        return segs, 0
    lens = [seg_len(s) for s in segs]
    turns, ts = [0.0] * n, [0.0] * n
    for i in range(n):
        turns[i] = turn_deg(tan_end(segs[i - 1]), tan_start(segs[i]))
        if turns[i] >= min_turn:
            ts[i] = min(R * math.tan(math.radians(turns[i]) / 2), 3.0 * R)
    for _ in range(8):
        for k in range(n):
            j = (k + 1) % n
            tot = ts[k] + ts[j]
            lim = 0.92 * lens[k]
            if tot > lim > 0:
                f = lim / tot
                ts[k] *= f
                ts[j] *= f
    for i in range(n):
        if ts[i] < 0.8:
            ts[i] = 0.0
    if not any(ts):
        return segs, 0
    trimmed = [trim(segs[k], ts[k], ts[(k + 1) % n], lens[k]) for k in range(n)]
    out, count = [], 0
    for i in range(n):
        out.append(trimmed[i])
        j = (i + 1) % n
        if ts[j] > 0:
            out.extend(fillet(trimmed[i], trimmed[j], segs[i], segs[j], ts[j], turns[j]))
            count += 1
    return out, count


def build_glyph(contours):
    pen = TTGlyphPen(None)
    for segs in contours:
        pen.moveTo(segs[0][1])
        last = len(segs) - 1
        for i, (k, p0, c, p1) in enumerate(segs):
            if k == 'L':
                if i != last:
                    pen.lineTo(p1)
            else:
                pen.qCurveTo(c, p1)
        pen.closePath()
    g = pen.glyph()
    g.program = Program()
    return g


def round_font_glyphs(font, R, adv_scale=1.0):
    gs = font.getGlyphSet()
    glyf = font['glyf']
    hmtx = font['hmtx']
    total = 0
    for name in font.getGlyphOrder():
        if glyf[name].numberOfContours == 0:
            aw, lsb = hmtx.metrics[name]
            hmtx.metrics[name] = (int(round(aw * adv_scale)), lsb)
            continue
        cs = get_contours(gs, name)
        if not cs:
            continue
        new = []
        for c in cs:
            r, k = round_contour(c, R) if R > 0 else (c, 0)
            total += k
            new.append(r)
        g = build_glyph(new)
        glyf[name] = g
        g.recalcBounds(glyf)
        aw, lsb = hmtx.metrics[name]
        hmtx.metrics[name] = (int(round(aw * adv_scale)), g.xMin)
    return total
