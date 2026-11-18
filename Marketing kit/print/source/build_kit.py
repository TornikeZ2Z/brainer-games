# Builds the Brainer print kit: business cards in three directions, the A5 game sheet, stickers and T-shirt art.
# usage: python -I build_kit.py   (writes into the folder above this one)
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import pressfile as pf
from pressfile import Page, REGULAR, BOLD, BLACK, MM, PALETTE, write_pdf, lockup_h, lockup_v, visor, stage_strip, age_badge, qr

ROOT = os.path.dirname(HERE); SITE = os.path.join(ROOT, '..', '..', 'Website', 'assets')
RENDERS = os.path.join(HERE, 'renders')

NAME, ROLE = 'Tornike Kvinikadze', 'Founder'
PHONE, EMAIL, WEB = '+995 591 04 00 40', 'info@brainer.games', 'brainer.games'
DEMOS = 'https://brainer.games/games.html'
GAMES = [
    ('space-crash', 'Space Crash', 'Instant', 'Five shield drones block every row. Fire to find out if the shield breaks, then fly on or cash out.'),
    ('multi-charge', 'Multi Charge', 'Instant', 'Five charging pillars, one charge at a time. A safe charge levels your Brainer up. Cash out any time.'),
    ('plane-crash', 'Plane Crash', 'Crash', 'Fly on one step at a time while bombs fall ahead. Bail out with the parachute to cash out.'),
    ('fly-high', 'Fly High', 'Crash', 'Your Brainer takes off and the multiplier climbs. Cash out before it flies away.'),
    ('charge', 'Charge', 'Instant', 'Charge your Brainer to level it up and raise the multiplier. Overcharge its battery and it dozes off.'),
]
SHEET = [('Launch', 'HTML5, runs in an iframe'), ('Devices', 'Phone and desktop'), ('Distribution', 'Aggregators planned, direct API planned'),
         ('RTP', 'Up to 97%'), ('Bets / max win', '$0.10 to $200 / $10,000'), ('Currency', 'Per market (USD in the demo)'),
         ('Languages', 'English'), ('Certification', 'Not yet tested by a lab'), ('Licence', 'Not licensed yet')]

def out(*p):
    path = os.path.join(ROOT, *p); os.makedirs(os.path.dirname(path), exist_ok=True); return path

def robot(stage):   # the render cropped tight to the Brainer
    im = Image.open(os.path.join(RENDERS, f'stage-{stage}.png')).convert('RGBA')
    return im.crop(im.getchannel('A').point(lambda v: 255 if v > 6 else 0).getbbox())

def field(w, h, glows, ppi=300):
    # the night page as a picture, with soft violet light mixed in CMYK; flat night where there is no glow
    W, H = round(w * ppi / 25.4), round(h * ppi / 25.4)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); xx *= 25.4 / ppi; yy *= 25.4 / ppi
    t = np.zeros((H, W), np.float32)
    for cx, cy, r, a in glows: t += a * np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r))
    t = np.clip(t, 0, .92)[..., None]
    night, light = np.array(PALETTE['night'], np.float32), np.array((100, 90, 0, 0), np.float32)
    a = (night + (light - night) * t) * 2.55
    a += (np.random.default_rng(7).random(a.shape, np.float32) - .5) * (t > .004)   # a little dither, so the glow can't band
    return Image.fromarray(np.clip(a + .5, 0, 255).astype(np.uint8), 'CMYK')

def place(under, rgba, x_mm, y_mm, w_mm, ppi=300):   # lays a render over a CMYK picture, flattened
    w = round(w_mm * ppi / 25.4); h = round(w * rgba.height / rgba.width)
    top = Image.new('RGBA', under.size, (255, 255, 255, 0))
    top.paste(rgba.resize((w, h), Image.LANCZOS), (round(x_mm * ppi / 25.4), round(y_mm * ppi / 25.4)))
    return pf.blend_cmyk(top, under)

# ---------- business cards, 85 x 55 mm ----------
CW, CH = 85, 55

def card_details(p, x, y, name, role, line):
    p.text(x, y, NAME, 10.5, BLACK, name, -.01)
    p.text(x, y + 4.5, ROLE, 8, REGULAR, role)
    yy = y + 12.6
    for t in (PHONE, EMAIL, WEB):
        p.text(x, yy, t, 8, REGULAR, line); yy += 4.2

def card_night():
    f = Page(CW, CH, label='front'); f.rect(-3, -3, CW + 6, CH + 6, 'night')
    lockup_v(f, CW / 2, 11.5, 36)
    b = Page(CW, CH, label='back'); b.rect(-3, -3, CW + 6, CH + 6, 'night')
    card_details(b, 6, 12, 'white', 'lilac', 'white')
    qr(b, 59, 7, 20, DEMOS)
    b.text(69, 31, 'Play the demos', 6, BOLD, 'white', align='center')
    age_badge(b, 73.2, 42.4, 5.8)
    stage_strip(b, -3, 51.5, CW + 6, 6.5)
    return [f, b]

def card_violet():
    f = Page(CW, CH, label='front'); f.rect(-3, -3, CW + 6, CH + 6, 'violet')
    lockup_v(f, CW / 2, 11.5, 36)
    b = Page(CW, CH, label='back'); b.rect(-3, -3, CW + 6, CH + 6, 'white')
    visor(b, 6, 6, 12, rim=False)
    card_details(b, 6, 19, 'k', 'muted', 'k')
    qr(b, 59, 7, 20, DEMOS, dark='k', light=None)
    b.text(69, 30, 'Play the demos', 6, BOLD, 'k', align='center')
    age_badge(b, 73.2, 44.2, 5.8, 'k', 'k')
    return [f, b]

def card_light():
    f = Page(CW, CH, label='front'); f.rect(-3, -3, CW + 6, CH + 6, 'tint')
    w = BLACK.width('Brainer', 1, pf.WORD_TRACK)
    h = 11.6; total = 80 * h / 44 + 10 * h / 38 + w * (28 * h / 38 * 72 / 25.4) / MM
    lockup_h(f, (CW - total) / 2, (CH - h) / 2, h, word='ink', rim=False)
    b = Page(CW, CH, label='back'); b.rect(-3, -3, CW + 6, CH + 6, 'white')
    card_details(b, 6, 12, 'k', 'muted', 'k')
    qr(b, 59, 7, 20, DEMOS, dark='k', light=None)
    b.text(69, 30, 'Play the demos', 6, BOLD, 'k', align='center')
    age_badge(b, 73.2, 42.4, 5.8, 'k', 'k')
    stage_strip(b, -3, 51.5, CW + 6, 6.5)
    return [f, b]

# ---------- A5 game sheet ----------
AW, AH = 148, 210

def rounded_picture(p, im, x, y, w, h, r):
    p.clip_rrect(x, y, w, h, r); p.image(im, x, y, w, h); p.unclip()

def sheet_front():
    p = Page(AW, AH, label='front')
    bg = field(AW + 6, AH + 6, [(112, 128, 46, .62), (128, 92, 24, .22)])
    hero = robot(5)
    bg = place(bg, hero, 57.5 + 3, 84 + 3, 86)
    p.image(bg, -3, -3, AW + 6, AH + 6)
    lockup_h(p, 10, 10, 8.6)
    age_badge(p, AW - 18, 9.6, 8.4)
    p.text(10, 33, 'FOR OPERATORS AND AGGREGATORS', 7.5, BOLD, 'lilac', .14)
    y = 46
    for line, c in (('Instant games', 'white'), ('your players', 'white'), ('come back to', 'lilac')):
        p.text(10, y, line, 33, BLACK, c, -.02); y += 13.2
    p.wrap(10, 88, 'Your players already know crash and mines games. Ours add the Brainer, one character that grows as they play.',
           10, 46.5, 4.9, REGULAR, 'white')
    y = 124
    for big, small in (('Up to 97%', 'RTP'), ('$0.10 to $200', 'Bets'), ('$10,000', 'Max win'), ('Five games', 'Demos to play now')):
        p.text(10, y, big, 15, BLACK, 'white', -.01); p.text(10, y + 4.6, small, 8, REGULAR, 'lilac'); y += 14.5
    qr(p, 10, 182, 20, DEMOS)
    p.text(34, 188, 'Play the demos', 11, BLACK, 'white', -.01)
    p.text(34, 193, WEB, 8.5, REGULAR, 'white')
    p.text(34, 199.6, '18+. Not licensed yet. Not yet tested by a lab. The demos use play money only.', 6.2, REGULAR, 'lilac')
    stage_strip(p, -3, 206.5, AW + 6, 6.5)
    return p

def sheet_back():
    p = Page(AW, AH, label='back'); p.rect(-3, -3, AW + 6, AH + 6, 'white')
    lockup_h(p, 10, 9.6, 6.6, word='ink', rim=False)
    age_badge(p, AW - 16, 9.2, 6.4, 'k', 'k')
    p.text(10, 28, 'Five games with playable demos', 17, BLACK, 'k', -.015)
    p.text(10, 33.4, 'Scan a code to open a game. The demos use play money only.', 8.5, REGULAR, 'muted')
    y = 37.5; rowh = 24.9
    for i, (gid, title, genre, line) in enumerate(GAMES):
        if i: p.line(10, y - 1.2, AW - 10, y - 1.2, .2, 'rule')
        art = Image.open(os.path.join(SITE, 'games', f'{gid}.webp')).convert('RGB').resize((262, 328), Image.LANCZOS)
        rounded_picture(p, pf.to_cmyk(art), 10, y, 18, 22.5, 1.7)
        p.text(32, y + 5.8, title, 12, BLACK, 'k', -.01)
        p.text(32, y + 9.9, genre.upper(), 6.2, BOLD, 'muted', .1)
        p.wrap(32, y + 14.6, line, 8, 84, 3.7, REGULAR, 'k')
        qr(p, AW - 10 - 19, y + 1.7, 19, f'https://brainer.games/game-{gid}.html', light=None, quiet=False)
        y += rowh
    p.rrect(10, y, AW - 20, 28, 2.4, 'tint')
    p.text(14, y + 5.6, 'Technical sheet', 8.5, BLACK, 'k')
    col_x = (14, 84); rows = 5
    for i, (k, v) in enumerate(SHEET):
        cx = col_x[0 if i < rows else 1]; ry = y + 10.2 + (i if i < rows else i - rows) * 3.75
        p.text(cx, ry, k, 6.6, REGULAR, 'muted'); p.text(cx + 18, ry, v, 6.6, BOLD, 'k')
    y += 31.2
    p.text(10, y, 'Up to 97%: the return is 97% before payouts round down to the cent and the $10,000 max win ends long rounds early.', 6.2, REGULAR, 'muted')
    p.text(10, y + 2.9, 'In Plane Crash, Space Crash and Multi Charge each step is fixed before the pick: no path, drone or pillar is better than another.', 6.2, REGULAR, 'muted')
    p.text(10, y + 5.8, 'Plane Crash, Fly High and Charge are working titles. Brain levels change the Brainer\u2019s look, never the odds or payouts.', 6.2, REGULAR, 'muted')
    p.text(10, y + 9.8, f'{EMAIL}  \u00b7  {WEB}', 8, BOLD, 'k')
    p.text(AW - 10, y + 9.8, '18+. Not licensed yet.', 6.2, REGULAR, 'muted', align='right')
    stage_strip(p, -3, 206.5, AW + 6, 6.5)
    return p

# ---------- stickers, on a night background with a die line (spot colour CutContour) ----------
def trace(mask):   # the outline of a filled mask, walking the pixel edges; returns (x, y) corners
    m = np.pad(mask, 1); H, W = m.shape
    ys, xs = np.nonzero(m); y0, x0 = ys[0], xs[0]
    x, y, d = int(x0), int(y0), 0   # 0 east, 1 south, 2 west, 3 north; the inside stays on the right
    start = (x, y, d); pts = []
    step = ((1, 0), (0, 1), (-1, 0), (0, -1))
    ahead = (((0, -1), (0, 0)), ((0, 0), (-1, 0)), ((-1, 0), (-1, -1)), ((-1, -1), (0, -1)))
    while True:
        pts.append((x, y))
        (ax, ay), (bx, by) = ahead[d]
        if m[y + ay, x + ax]: d = (d + 3) % 4
        elif not m[y + by, x + bx]: d = (d + 1) % 4
        x, y = x + step[d][0], y + step[d][1]
        if (x, y) == start[:2]: break
    return np.array(pts, float) - 1

def smooth_closed(pts, window, passes=3):
    n = len(pts); k = np.ones(window) / window
    for _ in range(passes):
        wrapped = np.vstack([pts[-window:], pts, pts[:window]])
        pts = np.stack([np.convolve(wrapped[:, i], k, 'same') for i in (0, 1)], 1)[window:window + n]
    return pts

def spline_path(p, pts):   # a closed Catmull-Rom curve through the points, as PDF cubics
    n = len(pts); P = lambda i: pts[i % n]
    s = [f'{pf.fmt(p.X(P(0)[0]))} {pf.fmt(p.Y(P(0)[1]))} m']
    for i in range(n):
        a, b, c, d = P(i - 1), P(i), P(i + 1), P(i + 2)
        c1, c2 = b + (c - a) / 6, c - (d - b) / 6
        s.append(' '.join(f'{pf.fmt(p.X(q[0]))} {pf.fmt(p.Y(q[1]))}' for q in (c1, c2, c)) + ' c')
    return ' '.join(s) + ' h'

def die_contour(rgba, offset_mm, w_mm, tag=None):
    # a smooth outline around a render, at a set distance, with no holes in it; tag (x, y, d in mm) is a circle it wraps too
    scale = 700 / max(rgba.size); w = round(rgba.width * scale); h = round(rgba.height * scale)
    px_mm = w / w_mm; pad = round(offset_mm * px_mm) + 8
    a = Image.new('L', (w + 2 * pad, h + 2 * pad), 0); a.paste(rgba.getchannel('A').resize((w, h)), (pad, pad))
    a = a.point(lambda v: 255 if v > 90 else 0)
    if tag:
        tx, ty, td = tag[0] * px_mm + pad, tag[1] * px_mm + pad, tag[2] * px_mm
        ImageDraw.Draw(a).ellipse((tx, ty, tx + td, ty + td), fill=255)
    r = offset_mm * px_mm
    blur = a.filter(ImageFilter.GaussianBlur(r * .9)).point(lambda v: 255 if v > 26 else 0).filter(ImageFilter.GaussianBlur(r * .25)).point(lambda v: 255 if v > 128 else 0)
    ImageDraw.floodfill(blur, (0, 0), 128)
    mask = np.asarray(blur) != 128
    pts = trace(mask)
    pts = smooth_closed(pts, max(5, round(r * .7)))[::6]
    return (pts - pad) / px_mm, pad / px_mm

def stickers():
    pages = []
    # 1. the visor, 70 x 48 mm
    w, h = 70, 48
    p = Page(w, h, label='visor'); p.rect(-3, -3, w + 6, h + 6, 'night')
    vw = 50; visor(p, (w - vw) / 2, 6.6, vw)
    age_badge(p, w / 2 - 2.6, 37.4, 5.2)
    p.spot_path('CutContour', p.rrect_path(0, 0, w, h, 13.5)); pages.append(p)
    # 2. round lockup, 60 mm
    d = 60
    p = Page(d, d, label='round'); p.rect(-3, -3, d + 6, d + 6, 'night')
    lockup_v(p, d / 2, 11.6, 31)
    age_badge(p, d / 2 - 3, 46.4, 6)
    p.spot_path('CutContour', p.rrect_path(0, 0, d, d, d / 2)); pages.append(p)
    # 3 to 5. the Brainer die-cut, on night; the die line wraps the 18+ mark too
    for stage, wide, tag in ((5, 62, (53.5, 61, 6.4)), (3, 58, (50, 56, 6.4)), (10, 70, (63, 72, 6.4))):
        art = robot(stage); art_h = wide * art.height / art.width
        pts, _ = die_contour(art, 3.2, wide, tag)
        x0, y0 = pts[:, 0].min(), pts[:, 1].min(); W, H = pts[:, 0].max() - x0, pts[:, 1].max() - y0
        p = Page(round(W + .5), round(H + .5), label=f'brainer {stage}')
        dx, dy = (p.w - W) / 2 - x0, (p.h - H) / 2 - y0
        p.rect(-3, -3, p.w + 6, p.h + 6, 'night')
        scale = 600 / 25.4
        art2 = art.resize((round(wide * scale), round(art_h * scale)), Image.LANCZOS)
        p.image(pf.flatten(art2, 'night'), dx, dy, wide, art_h)
        age_badge(p, dx + tag[0], dy + tag[1], tag[2])
        p.spot_path('CutContour', spline_path(p, pts + (dx, dy))); pages.append(p)
    return pages

# ---------- T-shirts: flat vector art at actual size, no bleed, for a dark tee ----------
def text_path(s, x, y, size_mm, face=BLACK, track=pf.WORD_TRACK, align='left'):   # text as SVG path data, baseline at x, y
    k = size_mm / face.upem; placed, width = face.layout(s, size_mm, track); d = []
    x -= width if align == 'right' else width / 2 if align == 'center' else 0
    for g, gx in placed:
        for seg in face.outline(g):
            if seg[0] == 'h': d.append('Z'); continue
            pts = ' '.join(f'{x + gx + q[0] * k:.3f} {y - q[1] * k:.3f}' for q in seg[1:])
            d.append(seg[0].upper() + pts)
    return ' '.join(d)

def rrect_svg(x, y, w, h, r, fill):   # rounded corners as true curves: some tools draw rx as chamfers
    k = 0.5522847 * r
    d = (f'M{x + r:.3f} {y:.3f}H{x + w - r:.3f}C{x + w - r + k:.3f} {y:.3f} {x + w:.3f} {y + r - k:.3f} {x + w:.3f} {y + r:.3f}'
         f'V{y + h - r:.3f}C{x + w:.3f} {y + h - r + k:.3f} {x + w - r + k:.3f} {y + h:.3f} {x + w - r:.3f} {y + h:.3f}'
         f'H{x + r:.3f}C{x + r - k:.3f} {y + h:.3f} {x:.3f} {y + h - r + k:.3f} {x:.3f} {y + h - r:.3f}'
         f'V{y + r:.3f}C{x:.3f} {y + r - k:.3f} {x + r - k:.3f} {y:.3f} {x + r:.3f} {y:.3f}Z')
    return f'<path d="{d}" fill="{fill}"/>'

def visor_svg(x, y, w, rim=True, rim_col='#fff'):
    u = w / 80; e = []
    if rim:
        e.append(rrect_svg(x, y, 80 * u, 44 * u, 15.5 * u, rim_col))
        e.append(rrect_svg(x + 3 * u, y + 3 * u, 74 * u, 38 * u, 12.5 * u, '#3550F0'))
    else:
        e.append(rrect_svg(x, y, 80 * u, 44 * u, 15.5 * u, '#3550F0'))
    e.append(rrect_svg(x + 22.5 * u, y + 8.5 * u, 35 * u, 3 * u, 1.5 * u, '#fff'))   # the line above the eyes, M24 10H56 with round caps
    for ex in (21.6, 48.4):
        e.append(rrect_svg(x + ex * u, y + 15 * u, 10 * u, 17 * u, 4.6 * u, '#fff'))
    return e

def svg_file(path, w, h, body, title):
    with open(path, 'w', encoding='utf8') as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.3f} {h:.3f}" width="{w:.3f}mm" height="{h:.3f}mm"><title>{title}</title>\n' + '\n'.join(body) + '\n</svg>\n')

def lockup_svg(height, word, rim):   # the horizontal lockup at the site's proportions: outlined, ready for any vector tool
    u = height / 38; vw = 80 * height / 44; size = 28 * u
    cap = BLACK.cap / BLACK.upem * size; tw = BLACK.width('Brainer', size, pf.WORD_TRACK)
    body = visor_svg(0, 0, vw, rim) + [f'<path d="{text_path("Brainer", vw + 10 * u, height / 2 + cap / 2, size)}" fill="{word}"/>']
    return vw + 10 * u + tw, height, body

def svg_png(svg, png, ppi=300):   # a transparent picture of the SVG, for direct-to-film printers
    import fitz
    fitz.open(svg)[0].get_pixmap(dpi=ppi, alpha=True).save(png)

def build_tees():
    for name, word, rim in (('brainer-lockup-white', '#fff', True), ('brainer-lockup-ink', '#1B1838', False)):
        w, h, body = lockup_svg(38, word, rim)
        for folder in ('logo', os.path.join('..', 'logo')):
            svg_file(out(folder, f'{name}.svg'), w, h, body, 'Brainer')
    # chest: the visor, 100 mm wide
    chest = out('t-shirt', 'brainer-tee-chest-100mm.svg')
    svg_file(chest, 100, 55, visor_svg(0, 0, 100), 'Brainer tee, chest print')
    # back: the lockup 280 mm wide with the address and the 18+ mark under it
    w, h, body = lockup_svg(38, '#fff', True); s = 280 / w
    scaled = [f'<g transform="scale({s:.5f})">'] + body + ['</g>']
    size = 15.5; base = h * s + 24; d = 13
    cy = base - BOLD.cap / BOLD.upem * size / 2
    badge = [f'<circle cx="{280 - d / 2:.3f}" cy="{cy:.3f}" r="{d / 2 - .45:.3f}" fill="none" stroke="#fff" stroke-width=".9"/>',
             f'<path d="{text_path("18+", 280 - d / 2, cy + BOLD.cap / BOLD.upem * 4.6 / 2, 4.6, BOLD, -.01, "center")}" fill="#fff"/>']
    address = f'<path d="{text_path(WEB, 0, base, size, BOLD, -.01)}" fill="#fff"/>'
    back = out('t-shirt', 'brainer-tee-back-280mm.svg')
    svg_file(back, 280, base + size * .26, scaled + [address] + badge, 'Brainer tee, back print')   # room for the g's tail
    for svg in (chest, back): svg_png(svg, svg[:-3] + 'png')

# ---------- notes for the print office, one A4 page ----------
def spec_sheet():
    p = Page(210, 297, bleed=0, marks=False, label='spec'); m = 16
    lockup_h(p, m, 14, 8, word='ink', rim=False)
    p.text(m, 36, 'Notes for the print office', 20, BLACK, 'k', -.015)
    p.text(m, 42, f'Questions: {EMAIL}, {PHONE}', 9, REGULAR, 'muted')

    def heading(y, t): p.text(m, y, t, 10.5, BLACK, 'k'); return y + 5.5
    y = heading(53, 'What to print')
    cols = (m, m + 36, m + 72, m + 100)
    for x, t in zip(cols, ('Item', 'Trim size', 'Print', 'Paper and finish')): p.text(x, y, t, 7.5, BOLD, 'muted')
    y += 1.6; p.line(m, y, 210 - m, y, .25, 'rule'); y += 4.4
    rows = [('Business cards', '85 x 55 mm', '4/4', '350 gsm coated board, matt lamination both sides. Suggested: 200.'),
            ('A5 game sheet', '148 x 210 mm', '4/4', '170 gsm silk coated. Short digital run, 150: game names may still change.'),
            ('Stickers, 5 designs', 'See below', '4/0', 'White vinyl, matt laminate, die-cut on the CutContour line. Suggested: 100 of each.'),
            ('T-shirts', 'Chest 100 mm wide, back 280 mm wide', 'White and blue', 'Dark navy or black tee. Screen print from the SVG, or direct-to-film from the PNG.')]
    for name, size, sides, stock in rows:
        p.text(cols[0], y, name, 8.5, BOLD, 'k')
        ybot = p.wrap(cols[1], y, size, 8.5, 33, 3.9, REGULAR, 'k')
        p.text(cols[2], y, sides, 8.5, REGULAR, 'k')
        ybot = max(ybot, p.wrap(cols[3], y, stock, 8.5, 210 - m - cols[3], 3.9, REGULAR, 'k'))
        y = ybot + 1.6
    p.text(m, y, 'Sticker sizes: visor 70 x 48 mm, round 60 mm, Brainers 67 x 76, 65 x 72 and 76 x 91 mm. Each is one page of the PDF.', 8, REGULAR, 'muted')
    y += 10

    y = heading(y, 'How the files are set up')
    for t in ('CMYK only, text turned into outlines, no transparency, 3 mm bleed, crop marks, trim and bleed boxes set.',
              'Built to PDF/X-1a rules with a SWOP coated output intent. Pictures are 300 ppi or better. Highest total ink is 254%.',
              'CutContour is a spot colour on overprint: it is the cutter\u2019s line and must not print.',
              'T-shirt SVGs are vector at actual size. The white is real white ink, so please keep it as a printing colour.'):
        p.text(m, y, '\u2022', 8.5, REGULAR, 'k'); y = p.wrap(m + 4, y, t, 8.5, 210 - 2 * m - 4, 4.1, REGULAR, 'k') + .5
    y += 5

    y = heading(y, 'Please')
    for t in ('Show us a printed proof before the run. Violet and screen blue are outside CMYK and print deeper than on screen, so judge them on paper.',
              'Keep the CMYK numbers as they are. If you print to another condition, such as FOGRA, tell us first rather than converting.',
              'Keep Night as the rich black it is built from. Flattening it to black only will lose its depth.',
              'If a brighter blue is possible for the logo, for example a spot colour matched to #3550F0, tell us the cost.'):
        p.text(m, y, '\u2022', 8.5, REGULAR, 'k'); y = p.wrap(m + 4, y, t, 8.5, 210 - 2 * m - 4, 4.1, REGULAR, 'k') + .5
    y += 5

    y = heading(y, 'Colours')
    swatches = [('Brainer violet', '#532AFF', 'violet'), ('Screen blue', '#3550F0', 'blue'), ('Night', '#0B0F1E', 'night'), ('Ink', '#1B1838', 'ink'),
                ('Tint', '#F5F4FF', 'tint'), ('Win gold', '#FFC147', 'gold')]
    w = (210 - 2 * m - 5 * 3) / 6
    for i, (name, hx, key) in enumerate(swatches):
        x = m + i * (w + 3); p.rrect(x, y, w, 12, 1.4, key)
        p.text(x, y + 16, name, 7.5, BOLD, 'k'); p.text(x, y + 19.4, hx, 7, REGULAR, 'muted')
        p.text(x, y + 22.8, '/'.join(str(v) for v in PALETTE[key]), 7, REGULAR, 'k')
    y += 29
    stage_strip(p, m, y, 210 - 2 * m, 6)
    w = (210 - 2 * m) / 10
    for i, c in enumerate(pf.STAGE_CMYK):
        p.text(m + i * w, y + 9.6, '/'.join(str(v) for v in c), 5.8, REGULAR, 'k')
    p.text(m, y + 14.2, 'The ten stage colours, CMYK in percent. The screen colours are the brand\u2019s; CMYK is how they go on paper.', 7, REGULAR, 'muted')
    return p

def main():
    for name, make in (('night', card_night), ('violet', card_violet), ('light', card_light)):
        write_pdf(out('business-cards', f'brainer-card-{name}.pdf'), make(), f'Brainer business card, {name}')
    write_pdf(out('brainer-a5-game-sheet.pdf'), [sheet_front(), sheet_back()], 'Brainer A5 game sheet')
    write_pdf(out('stickers', 'brainer-stickers.pdf'), stickers(), 'Brainer stickers')
    build_tees()
    write_pdf(out('00-print-spec.pdf'), [spec_sheet()], 'Brainer print kit, notes for the print office')
    print('built')

if __name__ == '__main__': main()
