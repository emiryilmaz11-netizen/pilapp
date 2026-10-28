# Generates Android launcher/splash resources and the Play Store icon
# from the PİL mark (three rounded bars on #241B2B).
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, 'android/app/src/main/res')
STORE = os.path.join(ROOT, 'store')
BG = (36, 27, 43, 255)
CREAM = (245, 244, 240, 255)
LILAC = (201, 167, 232, 255)
SPLASH_BG = (248, 246, 243, 255)
# Bars from icon-maskable-512.png, in 512-unit coordinates: (x0, y0, x1, y1, color)
BARS = [(143, 180, 370, 212, CREAM), (143, 240, 307, 272, LILAC), (143, 300, 343, 332, CREAM)]


def mark(size, bg, scale=1.0, ss=4):
    """Bars centered on a size×size canvas; scale enlarges them around the center."""
    n = size * ss
    im = Image.new('RGBA', (n, n), bg)
    d = ImageDraw.Draw(im)
    k = n / 512 * scale
    off = n / 2 - 256 * k
    for x0, y0, x1, y1, c in BARS:
        box = [off + x0 * k, off + y0 * k, off + x1 * k, off + y1 * k]
        d.rounded_rectangle(box, radius=(y1 - y0) / 2 * k, fill=c)
    return im.resize((size, size), Image.LANCZOS)


def save(im, *parts):
    p = os.path.join(*parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    im.save(p, optimize=True)


DENS = {'mdpi': 1, 'hdpi': 1.5, 'xhdpi': 2, 'xxhdpi': 3, 'xxxhdpi': 4}
for name, f in DENS.items():
    legacy = int(48 * f)
    fg = int(108 * f)
    # Adaptive foreground: transparent, same proportions as the maskable icon
    save(mark(fg, (0, 0, 0, 0)), RES, f'mipmap-{name}', 'ic_launcher_foreground.png')
    # Legacy square icon (API 24-25) with rounded corners
    sq = mark(legacy, BG, scale=1.25)
    m = Image.new('L', (legacy * 4, legacy * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, legacy * 4 - 1, legacy * 4 - 1], radius=legacy * 4 * 0.18, fill=255)
    sq.putalpha(m.resize((legacy, legacy), Image.LANCZOS))
    save(sq, RES, f'mipmap-{name}', 'ic_launcher.png')
    rd = mark(legacy, BG, scale=1.25)
    m = Image.new('L', (legacy * 4, legacy * 4), 0)
    ImageDraw.Draw(m).ellipse([0, 0, legacy * 4 - 1, legacy * 4 - 1], fill=255)
    rd.putalpha(m.resize((legacy, legacy), Image.LANCZOS))
    save(rd, RES, f'mipmap-{name}', 'ic_launcher_round.png')

# Pre-Android-12 splash: cream background with the dark icon tile centered
for orient, (w, h) in {'port': (320, 480), 'land': (480, 320)}.items():
    for name, f in DENS.items():
        W, H = int(w * f), int(h * f)
        im = Image.new('RGBA', (W, H), SPLASH_BG)
        t = int(96 * f)
        tile = mark(t, BG, scale=1.25)
        m = Image.new('L', (t * 4, t * 4), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, t * 4 - 1, t * 4 - 1], radius=t * 4 * 0.22, fill=255)
        tile.putalpha(m.resize((t, t), Image.LANCZOS))
        im.alpha_composite(tile, ((W - t) // 2, (H - t) // 2))
        save(im.convert('RGB'), RES, f'drawable-{orient}-{name}', 'splash.png')
        if orient == 'port' and name == 'mdpi':
            save(im.convert('RGB'), RES, 'drawable', 'splash.png')

# Play Store icon: 512×512, 32-bit PNG. Play rounds the corners itself.
save(mark(512, BG, scale=1.25), STORE, 'icon-512.png')
print('icons done')
