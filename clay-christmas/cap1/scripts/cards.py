# Título, end card y texto final del capítulo 1, hechos en edición (sin IA).
import numpy as np, cv2, os, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '/home/claude/cc1/cards')
from clay import clay, shadow, paper
W, H, FPS = 1080, 1920, 24
FONT = '/home/claude/claudio/mighty-minis-edicion/fuentes/Poppins-Bold.ttf'
NAVY, RED, CREAM = (32, 44, 112), (196, 32, 46), (247, 240, 228)
OUT = '/home/claude/cc1/cards'
rng = np.random.default_rng(5)

def sprite(text, size, color, R=None, seed=1):
    f = ImageFont.truetype(FONT, size)
    l, t, r, b = f.getbbox(text)
    pad = int(size * 0.25)
    m = Image.new('L', (r - l + 2 * pad, b - t + 2 * pad), 0)
    ImageDraw.Draw(m).text((pad - l, pad - t), text, font=f, fill=255)
    mask = (np.array(m) > 127).astype(np.uint8)
    col, a = clay(mask, color, R=R or size * 0.085, seed=seed)
    sh = shadow(a, blur=size * 0.07, opacity=0.38)
    return col, a, sh

def star_sprite(width):
    s = np.array(Image.open('/home/claude/cc1/star/estrella_cag.png').convert('RGBA')).astype(np.float32) / 255
    h = int(s.shape[0] * width / s.shape[1])
    s = cv2.resize(s, (width, h), interpolation=cv2.INTER_AREA)
    a = s[..., 3]
    return s[..., :3], a, shadow(a, blur=width * 0.05, opacity=0.38)

def place(canvas, spr, cx, cy, scale=1.0, ang=0.0, dx=0, dy=0, alpha_mul=1.0):
    col, a, sh = spr
    h, w = a.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, scale)
    M[0, 2] += cx - w / 2 + dx; M[1, 2] += cy - h / 2 + dy
    warp = lambda img, bv: cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=bv)
    shM = M.copy(); shM[0, 2] += 6; shM[1, 2] += 10
    s = cv2.warpAffine(sh, shM, (W, H), flags=cv2.INTER_LINEAR, borderValue=0) * alpha_mul
    canvas *= (1 - s)[..., None]
    c = warp(col, (0, 0, 0)); aa = warp(a, 0) * alpha_mul
    canvas[:] = canvas * (1 - aa[..., None]) + c * aa[..., None]

def pop(t, t0, dur=0.25):
    """Escala de entrada tipo stop motion: 0 -> 1.08 -> 1."""
    if t < t0: return 0.0
    x = (t - t0) / dur
    if x >= 1: return 1.0
    return 0.55 + 0.53 * np.sin(x * np.pi * 0.75) / np.sin(np.pi * 0.75) if x < 0.8 else 1.08 - 0.4 * (x - 0.8)

def boil(i, k):
    r = np.random.default_rng(1000 * (i // 2) + k)   # cambia cada 2 cuadros: 12 por segundo
    return r.uniform(-2.2, 2.2), r.uniform(-2.2, 2.2), r.uniform(-0.7, 0.7)

def render(name, n, items, bg):
    os.makedirs(f'{OUT}/{name}', exist_ok=True)
    for i in range(n):
        t = i / FPS
        c = bg.copy()
        for k, (spr, cx, cy, t0, base_ang) in enumerate(items):
            s = pop(t, t0)
            if s <= 0: continue
            dx, dy, da = boil(i, k)
            place(c, spr, cx, cy, scale=s, ang=base_ang + da, dx=dx, dy=dy)
        Image.fromarray((np.clip(c, 0, 1) * 255).astype(np.uint8)).save(f'{OUT}/{name}/{i:04d}.png')

bg = paper(H, W)
# ---------------- título (2,5 s)
star = star_sprite(170)
t_items = [(star, W / 2, 520, 0.05, -4),
           (sprite('A CAG', 170, NAVY, seed=2), W / 2, 760, 0.18, -1.5),
           (sprite('Clay', 170, RED, seed=3), W / 2, 960, 0.30, 1.0),
           (sprite('Christmas', 150, RED, seed=4), W / 2, 1150, 0.42, -0.8),
           (sprite('1/4', 92, NAVY, seed=5), W / 2, 1380, 0.62, 0)]
render('titulo', int(2.5 * FPS), t_items, bg)
# ---------------- end card (3,75 s)
logo = np.array(Image.open('/home/claude/claudio/mighty-minis-edicion/marca/logo_CAG_horizontal_azul.png').convert('RGBA')).astype(np.float32) / 255
lw = 600; lh = int(logo.shape[0] * lw / logo.shape[1])
logo = cv2.resize(logo, (lw, lh), interpolation=cv2.INTER_AREA)
e_items = [(star_sprite(150), W / 2, 470, 0.0, -4),
           (sprite('Merry', 150, RED, seed=7), W / 2, 680, 0.10, -1.2),
           (sprite('Christmas', 150, RED, seed=8), W / 2, 860, 0.22, 0.8),
           (sprite('be TOGETHER.', 92, NAVY, seed=9), W / 2, 1090, 0.70, 0),
           (sprite('be CAG.', 92, NAVY, seed=10), W / 2, 1210, 1.00, 0)]
os.makedirs(f'{OUT}/final', exist_ok=True)
render('final', int(3.75 * FPS), e_items, bg)
# logo plano (exacto), entra con fundido a 1,4 s
for i in range(int(3.75 * FPS)):
    t = i / FPS
    a = np.clip((t - 1.4) / 0.4, 0, 1)
    if a <= 0: continue
    p = f'{OUT}/final/{i:04d}.png'
    c = np.array(Image.open(p)).astype(np.float32) / 255
    x0, y0 = (W - lw) // 2, 1500
    la = logo[..., 3:4] * a
    c[y0:y0 + lh, x0:x0 + lw] = c[y0:y0 + lh, x0:x0 + lw] * (1 - la) + logo[..., :3] * la
    Image.fromarray((np.clip(c, 0, 1) * 255).astype(np.uint8)).save(p)
# ---------------- texto final sobre la toma 18 (RGBA)
os.makedirs(f'{OUT}/texto', exist_ok=True)
l1, l2 = sprite('No one is', 92, CREAM, seed=11), sprite('shaped alone.', 92, CREAM, seed=12)
n = int(3.25 * FPS)
for i in range(n):
    t = i / FPS
    rgb = np.zeros((H, W, 3), np.float32); acc = np.zeros((H, W), np.float32)
    for k, (spr, cy, t0) in enumerate([(l1, 300, 0.15), (l2, 420, 0.45)]):
        s = pop(t, t0)
        if s <= 0: continue
        dx, dy, da = boil(i, k + 20)
        col, a, sh = spr; h, w = a.shape
        M = cv2.getRotationMatrix2D((w / 2, h / 2), da, s); M[0, 2] += W / 2 - w / 2 + dx; M[1, 2] += cy - h / 2 + dy
        shM = M.copy(); shM[0, 2] += 5; shM[1, 2] += 9
        s_a = np.clip(cv2.warpAffine(sh, shM, (W, H)) * 1.6, 0, 0.75)
        rgb = rgb * (1 - s_a[..., None]); acc = acc + s_a * (1 - acc)
        c = cv2.warpAffine(col, M, (W, H)); aa = cv2.warpAffine(a, M, (W, H))
        rgb = rgb * (1 - aa[..., None]) + c * aa[..., None]; acc = acc + aa * (1 - acc)
    out = np.dstack([np.where(acc[..., None] > 1e-4, rgb / np.maximum(acc[..., None], 1e-4), 0), acc])
    Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8), 'RGBA').save(f'{OUT}/texto/{i:04d}.png')
print('ok')
