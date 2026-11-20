# Estrella del CAG en plastilina, hecha a partir del logo (no la dibuja la IA).
import numpy as np, cv2
from PIL import Image
rng = np.random.default_rng(11)
logo = np.array(Image.open('/home/claude/claudio/mighty-minis-edicion/marca/logo_CAG_horizontal_azul.png').convert('RGBA')).astype(np.float32)
H, W = logo.shape[:2]
blue = (logo[..., 3] > 128) & (logo[..., 2] > 120) & (logo[..., 0] < 90)
# Solo la parte izquierda (la estrella con sus dos trazos), sin el texto
cols = np.where(blue.any(axis=0))[0]
# el texto empieza después de un hueco grande de columnas vacías
gaps = np.where(np.diff(cols) > 15)[0]
x_end = cols[gaps[0]] + 1 if len(gaps) else cols[-1] + 1
m = blue[:, :x_end].copy()
ys, xs = np.where(m)
m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
pad = 60
m = np.pad(m, pad)
S = 1400 / max(m.shape)
m = cv2.resize(m.astype(np.uint8) * 255, (int(m.shape[1] * S), int(m.shape[0] * S)), interpolation=cv2.INTER_AREA)
mask = (m > 127).astype(np.uint8)
# Bordes suavizados, como amasados
mask = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), 3.0)
mask = (mask > 0.5).astype(np.uint8)
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (19, 19))
mask = cv2.morphologyEx(cv2.morphologyEx(mask, cv2.MORPH_OPEN, k), cv2.MORPH_CLOSE, k)
h, w = mask.shape
d = cv2.distanceTransform(mask, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
d = cv2.GaussianBlur(d, (0, 0), 2.5)
R = 62.0
t = np.clip(d / R, 0, 1)
height = R * (1 - (1 - t) ** 2.4)              # borde de almohada, redondeado
# Bulto suave en el centro de cada parte
big = cv2.GaussianBlur(d, (0, 0), 25)
height += 0.32 * big
# Irregularidad de hecho a mano
def noise(scale, amp):
    n = rng.standard_normal((h // scale + 2, w // scale + 2)).astype(np.float32)
    n = cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC)
    return amp * cv2.GaussianBlur(n, (0, 0), scale / 3)
height += noise(120, 4.5) + noise(40, 1.6) + noise(14, 0.25)
# Marcas de herramienta: surcos alargados
for k in range(6):
    cy, cx = np.argwhere(d > 50)[rng.integers((d > 50).sum())]
    ang = rng.uniform(0, np.pi); ln = rng.uniform(80, 180)
    ca, sa = np.cos(ang), np.sin(ang)
    yy0, xx0 = np.mgrid[0:h, 0:w].astype(np.float32)
    u = ((xx0 - cx) * ca + (yy0 - cy) * sa) / ln
    v = (-(xx0 - cx) * sa + (yy0 - cy) * ca) / 5.0
    height -= 1.4 * np.exp(-(u ** 2) * 2 - v ** 2)
# Huellas digitales: crestas concéntricas elípticas
yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
def huella(cx, cy, rx, ry, ang, amp):
    ca, sa = np.cos(ang), np.sin(ang)
    u = ((xx - cx) * ca + (yy - cy) * sa) / rx
    v = (-(xx - cx) * sa + (yy - cy) * ca) / ry
    r = np.sqrt(u * u + v * v)
    ridges = np.cos(r * 2 * np.pi * 9) * np.clip(1 - r, 0, 1) ** 0.7
    dent = -1.8 * np.clip(1 - r, 0, 1) ** 2
    return amp * (0.35 * ridges + dent) * (r < 1)
inside = np.argwhere(d > 70)
for k in range(5):
    cy, cx = inside[rng.integers(len(inside))]
    height += huella(cx, cy, rng.uniform(55, 80), rng.uniform(70, 100), rng.uniform(0, np.pi), 1.6)
height *= mask
height = cv2.GaussianBlur(height, (0, 0), 1.6)
# Normales e iluminación
gy, gx = np.gradient(height)
nz = np.ones_like(height)
n = np.dstack([-gx, -gy, nz]); n /= np.linalg.norm(n, axis=2, keepdims=True)
L = np.array([-0.45, -0.6, 0.66]); L /= np.linalg.norm(L)
wrap = 0.35
diff = np.clip(((n * L).sum(2) + wrap) / (1 + wrap), 0, 1)
Hh = (L + np.array([0, 0, 1])); Hh /= np.linalg.norm(Hh)
spec = np.clip((n * Hh).sum(2), 0, 1) ** 18 * 0.05
ao = np.clip(1 - 0.010 * (cv2.GaussianBlur(height, (0, 0), 12) - height), 0.8, 1) * (0.86 + 0.14 * np.clip(d / 40, 0, 1))
base = np.array([30, 64, 200], np.float32) / 255.0   # azul plastilina, cercano al del logo
mott = 1 + 0.035 * noise(60, 1.0)[..., None]
shade = (0.34 + 0.72 * diff)[..., None] * ao[..., None]
bounce = np.clip(n[..., 1], 0, 1)[..., None] * np.array([0.05, 0.04, 0.02])
col = base * mott * shade + spec[..., None] + bounce
col = np.clip(col, 0, 1)
alpha = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), 0.8)
rgba = np.dstack([col * 255, alpha * 255]).astype(np.uint8)
Image.fromarray(rgba, 'RGBA').save('/home/claude/cc1/star/estrella_cag.png')
# Sombra suave aparte (para componer)
sh = cv2.GaussianBlur(alpha, (0, 0), 18)
shadow = np.zeros((h, w, 4), np.uint8); shadow[..., 3] = (sh * 150).astype(np.uint8)
Image.fromarray(shadow, 'RGBA').save('/home/claude/cc1/star/estrella_sombra.png')
# Vista previa sobre crema
bg = Image.new('RGBA', (w + 80, h + 80), (238, 228, 212, 255))
s = Image.fromarray(shadow, 'RGBA'); bg.alpha_composite(s, (52, 64))
bg.alpha_composite(Image.fromarray(rgba, 'RGBA'), (40, 40))
bg.convert('RGB').resize(((w + 80) // 2, (h + 80) // 2)).save('/home/claude/cc1/star/preview.jpg', quality=88)
print(w, h)
