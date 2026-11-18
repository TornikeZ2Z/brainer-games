# Checks every kit PDF the way a print office's preflight would: page boxes, bleed, colour spaces, fonts, transparency,
# picture resolution and total ink. Prints one line per page and FAIL for anything a printer would bounce.
# usage: python -I preflight.py
import glob, os, re, sys, zlib
import numpy as np
from pypdf import PdfReader
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MM = 72 / 25.4; bad = 0

def fail(msg):
    global bad; bad += 1; print('   FAIL', msg)

def inside(a, b):   # box a sits inside box b
    return a[0] >= b[0] - .01 and a[1] >= b[1] - .01 and a[2] <= b[2] + .01 and a[3] <= b[3] + .01

for f in sorted(glob.glob(os.path.join(ROOT, '**', '*.pdf'), recursive=True)):
    r = PdfReader(f); info = r.metadata; raw = open(f, 'rb').read()
    print(os.path.relpath(f, ROOT), f'{len(raw) / 1e6:.1f} MB', raw[:8].decode(), info.get('/GTS_PDFXConformance'), 'Trapped', info.get('/Trapped'))
    for name, pat in (('RGB', b'/DeviceRGB'), ('font', b'/Font'), ('soft mask', b'/SMask'), ('transparency group', b'/Group'), ('alpha', b'/ca '), ('blend', b'/BM ')):
        if pat in raw: fail(f'{name} found')
    if b'/OutputIntents' not in raw: fail('no output intent')
    for n, page in enumerate(r.pages, 1):
        media = [float(v) for v in page.mediabox]; trim = [float(v) for v in page.trimbox]; bleed = [float(v) for v in page.bleedbox]
        tw, th = (trim[2] - trim[0]) / MM, (trim[3] - trim[1]) / MM; bl = (trim[0] - bleed[0]) / MM
        if not inside(trim, bleed) or not inside(bleed, media): fail('boxes do not nest')
        content = page.get_contents().get_data().decode('latin1')
        if re.search(r'\brg\b|\bRG\b|\bg\b(?!s)', content): fail('RGB or grey operator in content')
        worst, low = 0, 1e9
        xo = page['/Resources'].get('/XObject', {})
        for m in re.finditer(r'([\d.]+) 0 0 ([\d.]+) ([\d.-]+) ([\d.-]+) cm /(I\d+) Do', content):
            im = xo['/' + m[5]].get_object(); wpt, hpt = float(m[1]), float(m[2])
            ppi = min(im['/Width'] / (wpt / 72), im['/Height'] / (hpt / 72)); low = min(low, ppi)
            if im['/ColorSpace'] != '/DeviceCMYK': fail('picture is not CMYK')
            a = np.frombuffer(im.get_data(), np.uint8).reshape(im['/Height'], im['/Width'], 4)
            worst = max(worst, int(np.percentile(a.astype(np.uint16).sum(2), 99.99)) * 100 // 255)
        fills = [tuple(float(x) * 100 for x in c) for c in re.findall(r'([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) k\b', content)]
        flat = max((sum(c) for c in fills), default=0)
        if low < 280 and low < 1e9: fail(f'picture only {low:.0f} ppi')
        if max(worst, flat) > 300: fail(f'ink {max(worst, flat):.0f}%')
        spot = '/CutContour' if '/CSCutContour' in content else ''
        print(f'   p{n}: {tw:.1f} x {th:.1f} mm, bleed {bl:.1f} mm, ink max {max(worst, flat):.0f}%, pictures {"none" if low == 1e9 else f"{low:.0f} ppi"} {spot}')
# every QR code on the page, read back module by module from the drawn PDF and compared with its link
import fitz, segno
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_kit import GAMES, DEMOS, AW
def check_qr(path, page, x, y, size, url, quiet):
    d = fitz.open(os.path.join(ROOT, path))[page]; t = d.trimbox; dpi = 1200
    box = fitz.Rect(t.x0 + x * MM, t.y0 + y * MM, t.x0 + (x + size) * MM, t.y0 + (y + size) * MM)
    pix = d.get_pixmap(dpi=dpi, clip=box, colorspace=fitz.csGRAY, alpha=False)
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width)
    m = np.array([list(r) for r in segno.make(url, error='m', boost_error=False).matrix], bool); n = len(m); pad = 4 if quiet else 0
    u = pix.width / (n + 2 * pad); wrong = 0
    for r in range(n):
        for c in range(n):
            wrong += (a[int((r + pad + .5) * u), int((c + pad + .5) * u)] < 128) != m[r, c]
    print(f'   QR {os.path.basename(path)} p{page + 1} {url}: {n} modules, {size / (n + 2 * pad):.2f} mm each, {wrong} wrong')
    if wrong: fail('QR does not match its link')
for name in ('night', 'violet', 'light'): check_qr(f'business-cards/brainer-card-{name}.pdf', 1, 59, 7, 20, DEMOS, True)
check_qr('brainer-a5-game-sheet.pdf', 0, 10, 182, 20, DEMOS, True)
for i, g in enumerate(GAMES): check_qr('brainer-a5-game-sheet.pdf', 1, AW - 29, 37.5 + i * 24.9 + 1.7, 19, f'https://brainer.games/game-{g[0]}.html', False)
print('ALL CLEAR' if not bad else f'{bad} problem(s)')
sys.exit(1 if bad else 0)
