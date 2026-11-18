# Makes the overview picture for choosing a card, and the zip that goes to the print office with the chosen card only.
# usage: python -I package.py [card direction: night, violet or light]
import io, os, sys, zipfile
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); P = os.path.join(ROOT, 'proofs')
card = sys.argv[1] if len(sys.argv) > 1 else 'night'

def font(file, size):
    t = TTFont(os.path.join(ROOT, '..', '..', 'Website', 'assets', 'fonts', 'firago', file)); t.flavor = None
    b = io.BytesIO(); t.save(b); b.seek(0)
    return ImageFont.truetype(b, size)
BOLD, SMALL = font('FiraGO-Bold.woff2', 34), font('FiraGO-Regular.woff2', 24)
INK, MUTED, NIGHT = (27, 24, 56), (91, 88, 128), (12, 15, 30)

def fit(name, h=None, w=None):
    im = Image.open(name).convert('RGB')
    s = h / im.height if h else w / im.width
    return im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)

W, g = 2200, 44
canvas = Image.new('RGB', (W, 2500), (244, 243, 250)); d = ImageDraw.Draw(canvas)
y = g
d.text((g, y), 'Business cards, 85 x 55 mm', font=BOLD, fill=INK); y += 56
cw = (W - 4 * g) // 3
for i, (key, label) in enumerate((('violet', 'A. Violet'), ('night', 'B. Night (recommended)'), ('light', 'C. Light'))):
    x = g + i * (cw + g)
    f, b = fit(os.path.join(P, f'brainer-card-{key}-1.png'), w=cw), fit(os.path.join(P, f'brainer-card-{key}-2.png'), w=cw)
    canvas.paste(f, (x, y)); canvas.paste(b, (x, y + f.height + 16))
    d.text((x, y + 2 * f.height + 30), label, font=SMALL, fill=INK)
y += 2 * f.height + 96
d.text((g, y), 'A5 game sheet', font=BOLD, fill=INK)
d.text((g + 1000 + g, y), 'Stickers (the pink line is the cut, it does not print)', font=BOLD, fill=INK); y += 56
top = y
a = fit(os.path.join(P, 'brainer-a5-game-sheet-1.png'), h=700); b = fit(os.path.join(P, 'brainer-a5-game-sheet-2.png'), h=700)
canvas.paste(a, (g, y)); canvas.paste(b, (g + a.width + 16, y))
x = g + 1000 + g; row = 0
for n, h in ((1, 196), (2, 245), (3, 310), (4, 294), (5, 372)):
    im = fit(os.path.join(P, f'brainer-stickers-{n}.png'), h=h)
    if x + im.width > W - g: x = g + 1000 + g; y += 330; row += 1
    canvas.paste(im, (x, y)); x += im.width + 22
y = top + 700 + 56
d.text((g, y), 'T-shirt, for a dark tee: chest 100 mm, back 280 mm', font=BOLD, fill=INK); y += 56
panel = Image.new('RGB', (W - 2 * g, 400), NIGHT)
c = Image.open(os.path.join(ROOT, 't-shirt', 'brainer-tee-chest-100mm.png')).convert('RGBA'); c = c.resize((400, round(c.height * 400 / c.width)), Image.LANCZOS)
t = Image.open(os.path.join(ROOT, 't-shirt', 'brainer-tee-back-280mm.png')).convert('RGBA'); t = t.resize((1000, round(t.height * 1000 / t.width)), Image.LANCZOS)
panel.paste(c, (200, (400 - c.height) // 2), c); panel.paste(t, (800, (400 - t.height) // 2), t)
canvas.paste(panel, (g, y)); y += 400 + g
canvas.crop((0, 0, W, y)).save(os.path.join(P, '00-kit-overview.png'))

zp = os.path.join(ROOT, 'Brainer-print-kit.zip')
with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
    files = ['00-print-spec.pdf', f'business-cards/brainer-card-{card}.pdf', 'brainer-a5-game-sheet.pdf', 'stickers/brainer-stickers.pdf',
             'logo/brainer-lockup-white.svg', 'logo/brainer-lockup-ink.svg'] + \
            [f't-shirt/brainer-tee-{n}.{e}' for n in ('chest-100mm', 'back-280mm') for e in ('svg', 'png')]
    for f in files: z.write(os.path.join(ROOT, f), 'Brainer print kit/' + f)
    print(*z.namelist(), sep='\n')
print(f'{os.path.getsize(zp) / 1e6:.1f} MB')
