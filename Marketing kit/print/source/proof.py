# Writes a preview PNG of every page of every kit PDF, cut to the trim size, into proofs/.
# usage: python -I proof.py [dpi] [only this file name part]
# An on-screen estimate of coated paper: MuPDF's own CMYK conversion, with black lifted to what ink on paper can reach.
import fitz, glob, os, sys
import numpy as np
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dpi = int(sys.argv[1]) if len(sys.argv) > 1 else 220
only = sys.argv[2] if len(sys.argv) > 2 else ''
os.makedirs(os.path.join(ROOT, 'proofs'), exist_ok=True)
for f in sorted(glob.glob(os.path.join(ROOT, '**', '*.pdf'), recursive=True)):
    name = os.path.splitext(os.path.basename(f))[0]
    if only not in name: continue
    doc = fitz.open(f)
    for i, page in enumerate(doc, 1):
        tb = page.trimbox
        pix = page.get_pixmap(dpi=dpi, clip=tb, alpha=False, colorspace=fitz.csRGB)
        a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).astype(np.float32) / 255
        black, white = np.array((21, 24, 33), np.float32), np.array((252, 252, 250), np.float32)
        Image.fromarray((black + a * (white - black) + .5).astype(np.uint8), 'RGB').save(os.path.join(ROOT, 'proofs', f'{name}-{i}.png'))
print('done')
