# Pone la estrella del CAG (render propio, no IA) sobre la pieza azul de plastilina que generó Kling.
import numpy as np, cv2
STAR = cv2.imread('/home/claude/cc1/star/estrella_cag.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255  # BGRA
def blue_mask(bgr, lax=False):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    if lax:
        m = ((hsv[..., 0] >= 96) & (hsv[..., 0] <= 126) & (hsv[..., 1] >= 110) & (hsv[..., 2] >= 90)).astype(np.uint8)
    else:
        m = ((hsv[..., 0] >= 98) & (hsv[..., 0] <= 125) & (hsv[..., 1] >= 140) & (hsv[..., 2] >= 110)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    return m
def find_disc(bgr, min_area=600, roi=None, max_frac=0.05, solidity=0.8, near=None):
    m = blue_mask(bgr)
    h, w = m.shape
    if roi is not None:
        x0, y0, x1, y1 = roi
        keep = np.zeros_like(m); keep[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)] = 1
        m = m * keep
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    good = []
    for c in cs:
        a = cv2.contourArea(c)
        if a < min_area or a > max_frac * h * w or len(c) < 6: continue
        sol = a / max(1.0, cv2.contourArea(cv2.convexHull(c)))
        if sol < solidity: continue
        good.append(c)
    if not good: return None
    if near is not None:
        c = min(good, key=lambda c: np.hypot(*(c.reshape(-1, 2).mean(0) - np.array(near))) - 0.002 * cv2.contourArea(c))
    else:
        c = max(good, key=cv2.contourArea)
    (cx, cy), (a1, a2), ang = cv2.fitEllipse(cv2.convexHull(c))
    major, minor = max(a1, a2), min(a1, a2)
    if a2 > a1: ang = ang - 90
    cm = np.zeros((h, w), np.uint8); cv2.drawContours(cm, [cv2.convexHull(c)], -1, 1, -1)
    return dict(cx=cx, cy=cy, major=major, minor=minor, ang=ang, mask=cm)
def remove_disc(bgr, d, grow=10):
    """Borra la pieza azul (inpainting) para que no asome detrás de la estrella."""
    m = cv2.dilate(d['mask'], np.ones((2 * grow + 1, 2 * grow + 1), np.uint8))
    ys, xs = np.where(m)
    if len(xs) == 0: return bgr
    pad = 30
    x0, x1 = max(0, xs.min() - pad), min(bgr.shape[1], xs.max() + pad)
    y0, y1 = max(0, ys.min() - pad), min(bgr.shape[0], ys.max() + pad)
    out = bgr.copy()
    out[y0:y1, x0:x1] = cv2.inpaint(bgr[y0:y1, x0:x1], m[y0:y1, x0:x1] * 255, 9, cv2.INPAINT_TELEA)
    return out
def skin_mask(bgr):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    return ((hsv[..., 0] >= 3) & (hsv[..., 0] <= 24) & (hsv[..., 1] >= 50) & (hsv[..., 1] <= 190) & (hsv[..., 2] >= 120)).astype(np.float32)
def draw_star(bgr, d, scale=1.5, mode='upright', tilt=0.0, min_aspect=0.7, keep_skin=None, alpha_mul=1.0):
    h, w = bgr.shape[:2]
    sh, sw = STAR.shape[:2]
    if mode == 'upright':
        size = d['major'] * scale
        sx, sy, ang = size / sw, size / sh, tilt
    else:
        asp = max(min_aspect, d['minor'] / max(d['major'], 1))
        sx = d['major'] * scale / sw; sy = d['major'] * asp * scale / sh
        ang = d['ang'] if abs(d['ang']) < 35 else 0.0
        ang += tilt
    M = cv2.getRotationMatrix2D((0, 0), -ang, 1.0)
    A = M[:, :2] @ np.array([[sx, 0], [0, sy]], np.float32)
    off = np.array([d['cx'], d['cy']]) - A @ np.array([sw / 2, sh / 2])
    Mf = np.hstack([A, off[:, None]]).astype(np.float32)
    st = cv2.warpAffine(STAR, Mf, (w, h), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    a = st[..., 3] * alpha_mul
    Ms = Mf.copy(); Ms[0, 2] += d['major'] * 0.04; Ms[1, 2] += d['major'] * 0.07
    sa = cv2.warpAffine(STAR[..., 3], Ms, (w, h), flags=cv2.INTER_LINEAR, borderValue=0)
    sa = cv2.GaussianBlur(sa, (0, 0), max(2, d['major'] * 0.05)) * 0.42 * alpha_mul
    img = bgr.astype(np.float32) / 255
    img *= (1 - sa[..., None])
    if keep_skin is not None:
        a = a * (1 - cv2.GaussianBlur(skin_mask(keep_skin), (0, 0), 1.2))
    col = np.clip(st[..., :3] * np.array([0.90, 0.98, 1.06], np.float32) + 0.025, 0, 1)  # tono cálido de la escena
    img = img * (1 - a[..., None]) + col * a[..., None]
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)
class Smoother:
    def __init__(self, k=0.5): self.k, self.s = k, None
    def __call__(self, d):
        if d is None: return None
        if self.s is None: self.s = dict(d); return self.s
        for key in ('cx', 'cy', 'major', 'minor'):
            self.s[key] = self.s[key] * self.k + d[key] * (1 - self.k)
        da = ((d['ang'] - self.s['ang'] + 90) % 180) - 90
        self.s['ang'] = self.s['ang'] + da * (1 - self.k)
        self.s['mask'] = d['mask']
        return self.s
