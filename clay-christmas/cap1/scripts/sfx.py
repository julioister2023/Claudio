# Efectos de sonido sintetizados (sin voces): plastilina, huellas, pasos, pito, aplausos, campana.
import numpy as np
from scipy.signal import butter, sosfilt
SR = 48000
rng = np.random.default_rng(77)
def _n(n): return rng.standard_normal(n).astype(np.float32)
def _bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype='band', fs=SR, output='sos'), x).astype(np.float32)
def _lp(x, f, order=2): return sosfilt(butter(order, f, btype='low', fs=SR, output='sos'), x).astype(np.float32)
def _env(n, a, r, shape=2.0):
    e = np.ones(n, np.float32); ai, ri = max(1, int(a * SR)), max(1, int(r * SR))
    e[:ai] = np.linspace(0, 1, ai); e[-ri:] *= np.linspace(1, 0, ri) ** shape
    return e
def squish(dur=0.35):
    """Plastilina que se aprieta: ruido grave y húmedo con pulsos."""
    n = int(dur * SR); x = _bp(_n(n), 120, 1400)
    am = 0.5 + 0.5 * np.abs(np.sin(np.linspace(0, np.pi * rng.uniform(3, 6), n))) ** 3
    return (x * am * _env(n, 0.03, 0.12) * 0.9).astype(np.float32)
def knead(dur=2.4):
    out = np.zeros(int(dur * SR), np.float32); t = 0.0
    while t < dur - 0.3:
        s = squish(rng.uniform(0.22, 0.38)); i = int(t * SR); out[i:i + len(s)] += s[:len(out) - i] * rng.uniform(0.6, 1.0)
        t += rng.uniform(0.3, 0.5)
    return out
def press():
    """Pulgar que deja una huella: golpe blando y corto."""
    n = int(0.16 * SR); x = _lp(_n(n), 600) * 3.0 + _bp(_n(n), 600, 2200) * 0.4
    return (x * _env(n, 0.004, 0.13, 3)).astype(np.float32)
def plink(f=1567.98):
    """Destello suave de cada huella (como una celesta lejana)."""
    n = int(1.2 * SR); t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * d) for m, a, d in [(1, 1, 4.5), (2.01, 0.35, 7), (3.0, 0.12, 10)])
    return (x * _env(n, 0.002, 0.3) * 0.5).astype(np.float32)
def pat():
    """Choque de manos de plastilina."""
    n = int(0.12 * SR); x = _bp(_n(n), 500, 4000) * 0.8 + _lp(_n(n), 500) * 1.5
    return (x * _env(n, 0.001, 0.1, 4)).astype(np.float32)
def splat():
    """Caída contra el pasto: golpe blando con aplastamiento."""
    n = int(0.45 * SR); t = np.arange(n) / SR
    thump = np.sin(2 * np.pi * 70 * t * (1 - t)) * np.exp(-t * 14) * 1.4
    x = thump + _lp(_n(n), 900) * np.exp(-t * 18) * 1.2 + _bp(_n(n), 200, 1200) * np.exp(-t * 9) * 0.5
    return (x * _env(n, 0.002, 0.2)).astype(np.float32)
def stretch(dur=0.9, up=True):
    """Plastilina que se estira: chirrido gomoso que sube."""
    n = int(dur * SR); t = np.arange(n) / SR
    f = (180 + 520 * (t / dur) ** 1.4) if up else (700 - 500 * (t / dur))
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = np.sin(ph) * 0.3 + np.sin(2 * ph) * 0.12
    x = _bp(_n(n), 300, 1800) * 0.25 * (1 + np.sin(ph * 0.5))
    return ((tone + x) * _env(n, 0.08, 0.25)).astype(np.float32)
def step():
    n = int(0.09 * SR); return (_lp(_n(n), 700) * _env(n, 0.002, 0.08, 4) * 1.3).astype(np.float32)
def whistle(dur=0.5):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 2650 + 90 * np.sin(2 * np.pi * 28 * t)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.6 + _bp(_n(n), 2000, 4000) * 0.15
    return (x * _env(n, 0.02, 0.08)).astype(np.float32)
def chime():
    """Timbre suave de colegio (ding-dong lejano)."""
    out = np.zeros(int(1.8 * SR), np.float32)
    for k, (f, t0) in enumerate([(659.25, 0.0), (523.25, 0.45)]):
        n = int(1.3 * SR); t = np.arange(n) / SR
        x = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 3)) * np.exp(-t * 2.2)
        i = int(t0 * SR); out[i:i + n] += (x * 0.35).astype(np.float32)
    return out
def applause(dur=3.5):
    n = int(dur * SR); out = np.zeros(n, np.float32)
    for k in range(int(dur * 70)):
        c = pat() * rng.uniform(0.05, 0.25); i = rng.integers(0, n - len(c))
        out[i:i + len(c)] += c
    return out * _env(n, 0.5, 1.2)
def scribble(dur=2.0):
    """Crayón sobre papel: trazos cortos y ásperos."""
    out = np.zeros(int(dur * SR), np.float32); t = 0.0
    while t < dur - 0.2:
        n = int(rng.uniform(0.12, 0.28) * SR); x = _bp(_n(n), 1800, 6000) * 0.5
        am = 0.6 + 0.4 * np.sin(np.linspace(0, np.pi * rng.uniform(4, 9), n)) ** 2
        i = int(t * SR); out[i:i + n] += (x * am * _env(n, 0.02, 0.05))[:len(out) - i]
        t += rng.uniform(0.16, 0.34)
    return out
def creak(dur=0.45):
    """Sillita de madera que cruje."""
    n = int(dur * SR); t = np.arange(n) / SR
    f = 160 + 60 * np.sin(2 * np.pi * 3 * t)
    pulses = (np.sin(2 * np.pi * np.cumsum(f) / SR) > 0.92).astype(np.float32)
    x = _bp(pulses + 0.05 * _n(n), 400, 2500)
    return (x * _env(n, 0.03, 0.15) * 1.2).astype(np.float32)
