# A small print-ready PDF writer: CMYK only, every word turned into outlines, no transparency, trim and bleed boxes set
# and a PDF/X-1a style output intent, so a print office's preflight has nothing to convert. Written by hand because a
# general PDF library would quietly bring in RGB, live fonts or transparency.
# Sizes are millimetres with the origin at the page's top left; a page knows its trim size and adds bleed and slug itself.
import datetime, hashlib, math, os, zlib
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.basePen import decomposeQuadraticSegment
from PIL import Image, ImageCms

MM = 72 / 25.4
SWOP = r'C:\Windows\System32\spool\drivers\color\RSWOP.icm'
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'Website', 'assets', 'fonts', 'firago')

# ---------- colour ----------
# CMYK builds in percent. Violet and screen blue are out of CMYK's gamut, so these keep their hue and go deeper. They lean
# on the known SWOP solids (100/90/0/0 is #21409A, 100/100/0/0 is #2E3192, 75/100/0/0 is #662D91): the only profile on this
# machine, RSWOP.icm, puts the blues about 20 degrees too red and can't be trusted for them. Black under small text stays K only.
PALETTE = {
    'violet': (90, 100, 0, 0), 'blue': (100, 90, 0, 0), 'night': (70, 50, 10, 100), 'ink': (90, 90, 0, 70),
    'k': (0, 0, 0, 100), 'white': (0, 0, 0, 0), 'tint': (5, 4, 0, 0), 'lilac': (40, 44, 0, 0), 'gold': (0, 25, 85, 0),
    'muted': (70, 65, 15, 10), 'rule': (14, 12, 0, 0),
}
STAGE_CMYK = [(65, 20, 0, 0), (75, 0, 50, 0), (0, 70, 85, 0), (0, 45, 100, 0), (0, 85, 5, 0),
              (75, 90, 0, 0), (90, 95, 0, 0), (100, 100, 10, 10), (30, 100, 35, 10), (85, 100, 0, 5)]

def col(c): return PALETTE[c] if isinstance(c, str) else c
def ops(c):
    return ' '.join(f'{v / 100:.3f}'.rstrip('0').rstrip('.') or '0' for v in col(c))

# ---------- type ----------
class Face:
    def __init__(self, file):
        self.font = TTFont(os.path.join(FONT_DIR, file))
        self.upem = self.font['head'].unitsPerEm
        self.cmap = self.font.getBestCmap(); self.glyphs = self.font.getGlyphSet(); self.hmtx = self.font['hmtx']
        self.cache = {}; self.kerns = self._read_kerning()
        os2 = self.font['OS/2']; self.cap = getattr(os2, 'sCapHeight', 0) or 0.69 * self.upem

    def _read_kerning(self):   # the font's GPOS pair kerning: the browser applies it, so the outlines must too
        pairs, classes = {}, []
        if 'GPOS' not in self.font: return pairs, classes
        gpos = self.font['GPOS'].table
        ids = {i for f in gpos.FeatureList.FeatureRecord if f.FeatureTag == 'kern' for i in f.Feature.LookupListIndex}
        for i in sorted(ids):
            for sub in gpos.LookupList.Lookup[i].SubTable:
                sub = getattr(sub, 'ExtSubTable', sub)
                if sub.LookupType != 2: continue
                cov = sub.Coverage.glyphs
                if sub.Format == 1:
                    for g, ps in zip(cov, sub.PairSet):
                        for r in ps.PairValueRecord:
                            pairs.setdefault((g, r.SecondGlyph), (r.Value1.XAdvance if r.Value1 and hasattr(r.Value1, 'XAdvance') else 0))
                else:
                    classes.append((set(cov), sub.ClassDef1.classDefs, sub.ClassDef2.classDefs, sub.Class1Record))
        return pairs, classes

    def kern(self, a, b):
        pairs, classes = self.kerns
        if (a, b) in pairs: return pairs[(a, b)]
        for cov, c1, c2, rec in classes:
            if a in cov:
                v = rec[c1.get(a, 0)].Class2Record[c2.get(b, 0)].Value1
                if v is not None and getattr(v, 'XAdvance', 0): return v.XAdvance
                if (c1.get(a, 0), c2.get(b, 0)) != (0, 0): return 0
        return 0

    def name(self, ch):
        if ord(ch) not in self.cmap: raise KeyError(f'{ch!r} is not in the font')
        return self.cmap[ord(ch)]

    def outline(self, g):   # a glyph as moves, lines and cubics, in font units
        if g in self.cache: return self.cache[g]
        pen = DecomposingRecordingPen(self.glyphs); self.glyphs[g].draw(pen)
        out, cur = [], (0, 0)
        for op, a in pen.value:
            if op == 'moveTo': out.append(('m', a[0])); cur = a[0]
            elif op == 'lineTo': out.append(('l', a[0])); cur = a[0]
            elif op == 'curveTo': out.append(('c', a[0], a[1], a[2])); cur = a[2]
            elif op == 'qCurveTo':
                for q, p in decomposeQuadraticSegment(a):
                    c1 = (cur[0] + 2 / 3 * (q[0] - cur[0]), cur[1] + 2 / 3 * (q[1] - cur[1]))
                    c2 = (p[0] + 2 / 3 * (q[0] - p[0]), p[1] + 2 / 3 * (q[1] - p[1]))
                    out.append(('c', c1, c2, p)); cur = p
            elif op in ('closePath', 'endPath'): out.append(('h',))
        self.cache[g] = out
        return out

    def layout(self, text, size, track=0.0):   # glyphs with their pen positions in points; returns (glyphs, width)
        names = [self.name(c) for c in text]; x = 0.0; placed = []
        s = size / self.upem
        for i, g in enumerate(names):
            placed.append((g, x))
            x += self.hmtx[g][0] * s + track * size
            if i + 1 < len(names): x += self.kern(g, names[i + 1]) * s
        return placed, x - (track * size if names else 0)

    def width(self, text, size, track=0.0): return self.layout(text, size, track)[1]

REGULAR, BOLD, BLACK = Face('FiraGO-Regular.woff2'), Face('FiraGO-Bold.woff2'), Face('FiraGO-ExtraBold.woff2')
WORD_TRACK = -0.03   # the site's letter-spacing on the logo word

def fmt(v): return f'{v:.3f}'.rstrip('0').rstrip('.') or '0'

# ---------- document ----------
class Page:
    def __init__(self, w, h, bleed=3.0, slug=8.0, marks=True, label=''):
        self.w, self.h, self.bleed, self.slug, self.marks, self.label = w, h, bleed, slug if marks else 0.0, marks, label
        self.ox = self.oy = self.bleed + self.slug
        self.W, self.H = w + 2 * self.ox, h + 2 * self.oy
        self.ops, self.images, self.spots = [], [], {}

    # page millimetres to PDF points (PDF's y runs upwards)
    def X(self, x): return (x + self.ox) * MM
    def Y(self, y): return (self.H - (y + self.oy)) * MM
    def emit(self, s): self.ops.append(s)

    def rect(self, x, y, w, h, fill):
        self.emit(f'{ops(fill)} k {fmt(self.X(x))} {fmt(self.Y(y + h))} {fmt(w * MM)} {fmt(h * MM)} re f')

    def rrect_path(self, x, y, w, h, r):
        k = 0.5522847 * r; X, Y = self.X, self.Y
        return ' '.join([
            f'{fmt(X(x + r))} {fmt(Y(y))} m', f'{fmt(X(x + w - r))} {fmt(Y(y))} l',
            f'{fmt(X(x + w - r + k))} {fmt(Y(y))} {fmt(X(x + w))} {fmt(Y(y + r - k))} {fmt(X(x + w))} {fmt(Y(y + r))} c',
            f'{fmt(X(x + w))} {fmt(Y(y + h - r))} l',
            f'{fmt(X(x + w))} {fmt(Y(y + h - r + k))} {fmt(X(x + w - r + k))} {fmt(Y(y + h))} {fmt(X(x + w - r))} {fmt(Y(y + h))} c',
            f'{fmt(X(x + r))} {fmt(Y(y + h))} l',
            f'{fmt(X(x + r - k))} {fmt(Y(y + h))} {fmt(X(x))} {fmt(Y(y + h - r + k))} {fmt(X(x))} {fmt(Y(y + h - r))} c',
            f'{fmt(X(x))} {fmt(Y(y + r))} l',
            f'{fmt(X(x))} {fmt(Y(y + r - k))} {fmt(X(x + r - k))} {fmt(Y(y))} {fmt(X(x + r))} {fmt(Y(y))} c h'])

    def rrect(self, x, y, w, h, r, fill):
        self.emit(f'{ops(fill)} k {self.rrect_path(x, y, w, h, r)} f')

    def ring(self, x, y, w, h, r, weight, stroke):
        self.emit(f'{ops(stroke)} K {fmt(weight * MM)} w {self.rrect_path(x, y, w, h, r)} S')

    def line(self, x1, y1, x2, y2, weight, stroke, cap=0):
        self.emit(f'{ops(stroke)} K {fmt(weight * MM)} w {cap} J {fmt(self.X(x1))} {fmt(self.Y(y1))} m {fmt(self.X(x2))} {fmt(self.Y(y2))} l S 0 J')

    def text(self, x, y, s, size, face=REGULAR, fill='k', track=0.0, align='left'):   # y is the baseline; size in points
        placed, width = face.layout(s, size, track)
        px = self.X(x) - (width if align == 'right' else width / 2 if align == 'center' else 0)
        py = self.Y(y); k = size / face.upem; out = []
        for g, gx in placed:
            for seg in face.outline(g):
                if seg[0] == 'h': out.append('h'); continue
                pts = seg[1:]
                out.append(' '.join(f'{fmt(px + gx + p[0] * k)} {fmt(py + p[1] * k)}' for p in pts) + (' ' + seg[0]))
        if out: self.emit(f'{ops(fill)} k ' + ' '.join(out) + ' f')
        return width / MM

    def wrap(self, x, y, s, size, width, leading, face=REGULAR, fill='k', track=0.0):   # returns the y below the block
        words, line = s.split(), ''
        for w in words:
            t = (line + ' ' + w).strip()
            if face.width(t, size, track) / MM > width and line:
                self.text(x, y, line, size, face, fill, track); y += leading; line = w
            else: line = t
        if line: self.text(x, y, line, size, face, fill, track); y += leading
        return y

    def image(self, im, x, y, w, h):   # im: a PIL CMYK image, drawn flat; never transparent
        assert im.mode == 'CMYK'
        self.images.append(im); n = len(self.images)
        self.emit(f'q {fmt(w * MM)} 0 0 {fmt(h * MM)} {fmt(self.X(x))} {fmt(self.Y(y + h))} cm /I{n} Do Q')

    def clip_rrect(self, x, y, w, h, r): self.emit(f'q {self.rrect_path(x, y, w, h, r)} W n')
    def unclip(self): self.emit('Q')

    def spot_path(self, name, path, weight=0.25):   # a die line: a named spot colour on overprint, the sticker cutter's layer
        self.spots[name] = True
        self.emit(f'q /GS1 gs /CS{name} CS 1 SCN {fmt(weight * MM)} w {path} S Q')

    def crop_marks(self):
        if not self.marks: return
        o, b, L = self.ox, self.bleed, self.slug - 2
        w, h = self.w, self.h; reg = '1 1 1 1 K 0.25 w'
        self.emit('q ' + reg)
        for xm in (0, w):
            for ys, ye in ((-b - 1 - L, -b - 1), (h + b + 1, h + b + 1 + L)):
                self.emit(f'{fmt(self.X(xm))} {fmt(self.Y(ys))} m {fmt(self.X(xm))} {fmt(self.Y(ye))} l S')
        for ym in (0, h):
            for xs, xe in ((-b - 1 - L, -b - 1), (w + b + 1, w + b + 1 + L)):
                self.emit(f'{fmt(self.X(xs))} {fmt(self.Y(ym))} m {fmt(self.X(xe))} {fmt(self.Y(ym))} l S')
        self.emit('Q')

def _stream(data, extra=''):
    z = zlib.compress(data, 9)
    return f'<< /Length {len(z)} /Filter /FlateDecode {extra} >>\nstream\n'.encode() + z + b'\nendstream'

def write_pdf(path, pages, title):
    objs = {}
    def add(body):
        n = len(objs) + 1; objs[n] = body if isinstance(body, bytes) else body.encode(); return n
    catalog = add(b''); pages_id = add(b'')
    with open(SWOP, 'rb') as f: icc = add(_stream(f.read(), '/N 4 /Alternate /DeviceCMYK'))
    gs_over = add('<< /Type /ExtGState /OP true /op true /OPM 1 >>')
    kids = []
    for p in pages:
        p.crop_marks()
        res_img, res_cs = [], []
        for i, im in enumerate(p.images, 1):
            data = im.tobytes()
            n = add(_stream(data, f'/Type /XObject /Subtype /Image /Width {im.width} /Height {im.height} /ColorSpace /DeviceCMYK /BitsPerComponent 8'))
            res_img.append(f'/I{i} {n} 0 R')
        for name in p.spots:
            tint = add(_stream(b'{dup 0 mul exch dup 1 mul exch dup 0 mul exch 0 mul}', '/FunctionType 4 /Domain [0 1] /Range [0 1 0 1 0 1 0 1]'))
            res_cs.append(f'/CS{name} [/Separation /{name} /DeviceCMYK {tint} 0 R]')
        content = add(_stream(('\n'.join(p.ops)).encode()))
        res = '<< /ProcSet [/PDF /ImageC]'
        if res_img: res += ' /XObject << ' + ' '.join(res_img) + ' >>'
        if res_cs: res += ' /ColorSpace << ' + ' '.join(res_cs) + f' >> /ExtGState << /GS1 {gs_over} 0 R >>'
        res += ' >>'
        ox, oy = p.ox, p.oy
        box = lambda m: f'[{fmt((ox - m) * MM)} {fmt((oy - m) * MM)} {fmt((ox + p.w + m) * MM)} {fmt((oy + p.h + m) * MM)}]'
        kids.append(add(f'<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {fmt(p.W * MM)} {fmt(p.H * MM)}] '
                        f'/TrimBox {box(0)} /BleedBox {box(p.bleed)} /Resources {res} /Contents {content} 0 R >>'))
    objs[pages_id] = f'<< /Type /Pages /Count {len(kids)} /Kids [{" ".join(f"{k} 0 R" for k in kids)}] >>'.encode()
    intent = (f'<< /Type /OutputIntent /S /GTS_PDFX /OutputConditionIdentifier (CGATS TR 001) /RegistryName (http://www.color.org) '
              f'/Info (U.S. Web Coated SWOP) /DestOutputProfile {icc} 0 R >>')
    objs[catalog] = f'<< /Type /Catalog /Pages {pages_id} 0 R /OutputIntents [{intent}] >>'.encode()
    now = datetime.datetime.now().strftime("D:%Y%m%d%H%M%S+04'00'")
    info = add(f'<< /Title ({title}) /Author (Brainer) /Creator (Brainer print kit) /Producer (Brainer pressfile) /CreationDate ({now}) '
               f"/ModDate ({now}) /Trapped /False /GTS_PDFXVersion (PDF/X-1:2001) /GTS_PDFXConformance (PDF/X-1a:2001) >>")
    out = bytearray(b'%PDF-1.3\n%\xe2\xe3\xcf\xd3\n'); offs = {}
    for n in sorted(objs):
        offs[n] = len(out); out += f'{n} 0 obj\n'.encode() + objs[n] + b'\nendobj\n'
    xref = len(out); out += f'xref\n0 {len(objs) + 1}\n0000000000 65535 f \n'.encode()
    for n in sorted(objs): out += f'{offs[n]:010d} 00000 n \n'.encode()
    uid = hashlib.md5(bytes(out[:4096]) + title.encode()).hexdigest()
    out += f'trailer\n<< /Size {len(objs) + 1} /Root {catalog} 0 R /Info {info} 0 R /ID [<{uid}> <{uid}>] >>\nstartxref\n{xref}\n%%EOF\n'.encode()
    with open(path, 'wb') as f: f.write(out)

# ---------- pictures ----------
_srgb = ImageCms.createProfile('sRGB'); _swop = ImageCms.getOpenProfile(SWOP)
_to_cmyk = ImageCms.buildTransform(_srgb, _swop, 'RGB', 'CMYK', ImageCms.Intent.RELATIVE_COLORIMETRIC, ImageCms.Flags.BLACKPOINTCOMPENSATION)

# magenta per cyan that holds a blue's or violet's hue on press, by sRGB hue, from the same SWOP solids
HUES, RATIOS = (207, 232, 252, 273), (.59, .90, 1.11, 1.33)

def to_cmyk(rgb):   # sRGB picture to CMYK, with saturated blues and violets rebuilt on the palette's mixes, so the robot's screen matches the logo
    rgb = rgb.convert('RGB')
    a = np.asarray(ImageCms.applyTransform(rgb, _to_cmyk)).astype(np.float32) / 255
    r, g, b = np.moveaxis(np.asarray(rgb).astype(np.float32) / 255, -1, 0)
    hi, lo = np.max([r, g, b], 0), np.min([r, g, b], 0); delta = np.maximum(hi - lo, 1e-4)
    sat, hue = delta / np.maximum(hi, 1e-4), 240 + 60 * (r - g) / delta
    C, M, K = a[..., 0], a[..., 1], a[..., 3]
    ratio = np.interp(hue, HUES, RATIOS)
    w = np.clip((sat - .25) / .25, 0, 1) * np.clip((hue - 197) / 12, 0, 1) * np.clip((300 - hue) / 15, 0, 1) * np.clip(1 - K / .6, 0, 1) * (b >= hi)
    M2 = np.minimum(ratio * C, 1); C2 = np.minimum(C, M2 / ratio)
    a[..., 0], a[..., 1] = C + (C2 - C) * w, M + (M2 - M) * w
    return Image.fromarray((a * 255 + .5).astype(np.uint8), 'CMYK')

def flatten(rgba, bg):   # a transparent render flattened onto a flat CMYK colour, so its edge disappears into the page
    rgba = rgba.convert('RGBA')
    fg = np.asarray(to_cmyk(rgba.convert('RGB'))).astype(np.float32)
    al = np.asarray(rgba.getchannel('A')).astype(np.float32)[..., None] / 255
    under = np.array(col(bg), dtype=np.float32) * 2.55
    return Image.fromarray((fg * al + under * (1 - al) + .5).astype(np.uint8), 'CMYK')

def blend_cmyk(top_rgba, under_cmyk):   # the same, over a CMYK picture
    top_rgba = top_rgba.convert('RGBA')
    fg = np.asarray(to_cmyk(top_rgba.convert('RGB'))).astype(np.float32)
    al = np.asarray(top_rgba.getchannel('A')).astype(np.float32)[..., None] / 255
    un = np.asarray(under_cmyk).astype(np.float32)
    return Image.fromarray((fg * al + un * (1 - al) + .5).astype(np.uint8), 'CMYK')

# ---------- brand marks ----------
def visor(p, x, y, w, rim=True, rim_col='white', screen='blue', face='white'):
    # the visor logo, exact: 80 x 44 units; the rim and the line above the eyes always share one weight
    u = w / 80
    if rim:
        p.rrect(x, y, 80 * u, 44 * u, 15.5 * u, rim_col)
        p.rrect(x + 3 * u, y + 3 * u, 74 * u, 38 * u, 12.5 * u, screen)
    else:
        p.rrect(x, y, 80 * u, 44 * u, 15.5 * u, screen)
    p.line(x + 24 * u, y + 10 * u, x + 56 * u, y + 10 * u, 3 * u, face, cap=1)
    p.rrect(x + 21.6 * u, y + 15 * u, 10 * u, 17 * u, 4.6 * u, face)
    p.rrect(x + 48.4 * u, y + 15 * u, 10 * u, 17 * u, 4.6 * u, face)

def lockup_h(p, x, y, height, word='white', rim=True, rim_col='white', screen='blue', face='white'):
    # the site's header logo: visor 38 high, gap 10, word 28 px, tracked -.03em; returns the total width in mm
    u = height / 38; vw = 80 * height / 44
    visor(p, x, y, vw, rim, rim_col, screen, face)
    size = 28 * u * 72 / 25.4
    cap = BLACK.cap / BLACK.upem * size / MM
    tx = x + vw + 10 * u
    tw = p.text(tx, y + height / 2 + cap / 2, 'Brainer', size, BLACK, word, WORD_TRACK)
    return vw + 10 * u + tw

def lockup_v(p, cx, y, width, word='white', rim=True, rim_col='white', screen='blue', face='white'):
    # stacked: the card's lockup, the word's cap height sized off the visor; returns the bottom y
    visor(p, cx - width / 2, y, width, rim, rim_col, screen, face)
    h = width * 44 / 80; size = width * .33 * 72 / 25.4
    cap = BLACK.cap / BLACK.upem * size / MM; base = y + h + width * .14 + cap
    p.text(cx, base, 'Brainer', size, BLACK, word, WORD_TRACK, 'center')
    return base

def stage_strip(p, x, y, w, h):   # the ten stage colours, one thread through every printed piece
    n = len(STAGE_CMYK)
    for i, c in enumerate(STAGE_CMYK):
        p.rect(x + w * i / n, y, w / n + (0.02 if i < n - 1 else 0), h, c)

def age_badge(p, x, y, d, stroke='white', fill='white'):   # the 18+ mark; x, y is its top left
    p.emit(f'{ops(stroke)} K {fmt(d * .07 * MM)} w {p.rrect_path(x + d * .035, y + d * .035, d * .93, d * .93, d * .465)} S')
    size = .6 * d * MM / BOLD.width('18+', 1)
    cap = BOLD.cap / BOLD.upem * size / MM
    p.text(x + d / 2, y + d / 2 + cap / 2, '18+', size, BOLD, fill, -0.01, 'center')

def qr(p, x, y, size, data, dark='k', light='white', quiet=True):   # a QR code as vector squares; x, y and size include its quiet zone
    import segno
    q = segno.make(data, error='m', boost_error=False)
    m = [list(r) for r in q.matrix]; n = len(m); pad = 4 if quiet else 0
    u = size / (n + 2 * pad)
    if light: p.rrect(x, y, size, size, u * 2.2, light)
    d = u
    out = []
    for r in range(n):
        c = 0
        while c < n:
            if m[r][c]:
                s = c
                while c < n and m[r][c]: c += 1
                xx, yy = x + (s + pad) * u, y + (r + pad) * u
                out.append(f'{fmt(p.X(xx))} {fmt(p.Y(yy + d))} {fmt((c - s) * u * MM)} {fmt(d * MM + .02)} re')
            else: c += 1
    p.emit(f'{ops(dark)} k ' + ' '.join(out) + ' f')
