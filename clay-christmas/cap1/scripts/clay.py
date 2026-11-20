# Sombreado de plastilina para máscaras (texto y estrella): hecho en código, no con IA.
import numpy as np, cv2
def _noise(rng, h, w, scale, amp):
    n = rng.standard_normal((h // scale + 2, w // scale + 2)).astype(np.float32)
    n = cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC)
    return amp * cv2.GaussianBlur(n, (0, 0), max(1, scale / 3))
def clay(mask, color, R=14.0, seed=1, light=(-0.45, -0.6, 0.66)):
    """mask: uint8 0/1. color: (r,g,b) 0-255. Devuelve RGBA float (0-1) y alfa."""
    rng = np.random.default_rng(seed)
    h, w = mask.shape
    d = cv2.distanceTransform(mask, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    d = cv2.GaussianBlur(d, (0, 0), 1.2)
    t = np.clip(d / R, 0, 1)
    height = R * (1 - (1 - t) ** 2.4) + 0.25 * cv2.GaussianBlur(d, (0, 0), R * 0.8)
    height += _noise(rng, h, w, max(8, int(R * 3)), R * 0.06) + _noise(rng, h, w, 6, R * 0.015)
    height *= mask
    height = cv2.GaussianBlur(height, (0, 0), 1.0)
    gy, gx = np.gradient(height)
    n = np.dstack([-gx, -gy, np.ones_like(height)]); n /= np.linalg.norm(n, axis=2, keepdims=True)
    L = np.array(light); L /= np.linalg.norm(L)
    diff = np.clip(((n * L).sum(2) + 0.35) / 1.35, 0, 1)
    Hh = L + np.array([0, 0, 1.0]); Hh /= np.linalg.norm(Hh)
    spec = np.clip((n * Hh).sum(2), 0, 1) ** 18 * 0.05
    ao = 0.86 + 0.14 * np.clip(d / (R * 0.8), 0, 1)
    base = np.array(color, np.float32) / 255
    mott = 1 + 0.03 * _noise(rng, h, w, 40, 1.0)[..., None]
    col = np.clip(base * mott * ((0.36 + 0.70 * diff) * ao)[..., None] + spec[..., None], 0, 1)
    alpha = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), 0.7)
    return col, alpha
def shadow(alpha, blur=10, opacity=0.35):
    return cv2.GaussianBlur(alpha, (0, 0), blur) * opacity
def paper(h, w, color=(240, 230, 214), seed=3):
    """Fondo crema de plastilina aplanada, mate, con huellas muy suaves."""
    rng = np.random.default_rng(seed)
    base = np.ones((h, w, 3), np.float32) * np.array(color, np.float32) / 255
    lum = 1 + _noise(rng, h, w, 160, 0.025) + _noise(rng, h, w, 30, 0.010) + _noise(rng, h, w, 4, 0.006)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    vign = 1 - 0.10 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    out = base * (lum * vign)[..., None]
    for k in range(4):   # huellas sutiles en el fondo
        cx, cy = rng.uniform(0.1, 0.9) * w, rng.uniform(0.1, 0.9) * h
        rx, ry, ang = rng.uniform(45, 70), rng.uniform(60, 90), rng.uniform(0, np.pi)
        ca, sa = np.cos(ang), np.sin(ang)
        u = ((xx - cx) * ca + (yy - cy) * sa) / rx; v = (-(xx - cx) * sa + (yy - cy) * ca) / ry
        r = np.sqrt(u * u + v * v)
        out *= (1 - 0.018 * np.cos(r * 2 * np.pi * 9) * np.clip(1 - r, 0, 1) ** 0.6 * (r < 1))[..., None]
    return np.clip(out, 0, 1)
