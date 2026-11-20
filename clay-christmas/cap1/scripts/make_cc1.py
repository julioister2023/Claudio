"""Montaje del capítulo 1 "Hecho a mano" (60 s, 1080x1920, 24 fps con movimiento a 12 cuadros por segundo)."""
import os, sys, json, subprocess, numpy as np, cv2, wave
sys.path.insert(0, '/home/claude/cc1/edit'); sys.path.insert(0, '/home/claude/cc1/sfx')
from star_track import find_disc, draw_star, remove_disc, Smoother
W, H, FPS = 1080, 1920, 24
CLIPS = '/home/claude/claudio/clay-christmas/cap1/descargas'
CARDS = '/home/claude/cc1/cards'
OUT = '/home/claude/cc1/edit/out'; os.makedirs(OUT, exist_ok=True)
FR = '/home/claude/cc1/edit/frames'; os.makedirs(FR, exist_ok=True)
EDL = json.load(open('/home/claude/cc1/edit/edl.json'))   # [{"clip":"V1","start":f,"n":f, "star":{...}}...]

def read_clip(name):
    cap = cv2.VideoCapture(f'{CLIPS}/{name}.mp4'); fr = []
    while True:
        ok, f = cap.read()
        if not ok: break
        fr.append(f)
    return fr

def fit(f):
    h, w = f.shape[:2]; s = max(W / w, H / h)
    f = cv2.resize(f, (round(w * s), round(h * s)), interpolation=cv2.INTER_LANCZOS4)
    y0, x0 = (f.shape[0] - H) // 2, (f.shape[1] - W) // 2
    return f[y0:y0 + H, x0:x0 + W]

rng = np.random.default_rng(9)
def grain(f, i, amount=3.2):
    r = np.random.default_rng(1000 + i // 2)
    g = r.normal(0, amount, (H // 2, W // 2, 1)).astype(np.float32)
    g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    return np.clip(f.astype(np.float32) + g, 0, 255).astype(np.uint8)

idx = 0
def emit(f):
    global idx
    cv2.imwrite(f'{FR}/{idx:05d}.png', f); idx += 1

# título
for i in range(60):
    emit(grain(cv2.imread(f'{CARDS}/titulo/{i:04d}.png'), i))
texto = sorted(os.listdir(f'{CARDS}/texto'))
for e in EDL:
    fr = read_clip(e['clip'])
    srcs = []
    for a, b in e['segs']:
        srcs += [min(a + (j // 2) * 2, len(fr) - 1) for j in range(b - a)]
    srcs += [srcs[-1]] * e.get('hold', 0)
    sm = Smoother(0.5)
    st = e.get('star')
    last, lost, held = None, 99, None
    for k, s in enumerate(srcs):
        f = fr[s]
        if st and k >= st.get('from', 0):
            if k % 2 == 0 or held is None:
                prev = (last['cx'], last['cy']) if last is not None else None
                d = find_disc(f, st.get('min_area', 600), tuple(st['roi']), solidity=st.get('sol', 0.8), near=prev)
                if d is not None:
                    last, lost = sm(d), 0
                else:
                    lost += 1
                held = (last, lost)
            last_d, lost_n = held
            if last_d is not None and lost_n < 4:
                fade = min(1.0, (k - st.get('from', 0) + 1) / max(1, st.get('fade', 1))) * (1 - lost_n / 4)
                g = remove_disc(f, last_d) if lost_n == 0 else f
                f = draw_star(g, last_d, scale=st.get('scale', 1.55), mode=st.get('mode', 'upright'), tilt=st.get('tilt', 0),
                              min_aspect=st.get('min_aspect', 0.7), keep_skin=(f if st.get('skin') else None), alpha_mul=fade)
        f = fit(f)
        if e.get('texto') is not None:
            j = k - e['texto']
            if 0 <= j < len(texto):
                ov = cv2.imread(f'{CARDS}/texto/{texto[j]}', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
                a = ov[..., 3:4]
                f = (f.astype(np.float32) * (1 - a) + ov[..., :3] * 255 * a).astype(np.uint8)
        emit(grain(f, idx))
    print(e['clip'], len(srcs), 'cuadros; acumulado', round(idx / FPS, 2), 's', flush=True)
for i in range(90):
    emit(grain(cv2.imread(f'{CARDS}/final/{i:04d}.png'), i))
print('cuadros', idx, 'segundos', idx / FPS)
