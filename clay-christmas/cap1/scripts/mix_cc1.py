"""Efectos (sin voces) + música del capítulo 1, mezclados y normalizados."""
import sys, wave, numpy as np, subprocess
sys.path.insert(0, '/home/claude/cc1/sfx')
import sfx
from sfx import SR
DUR = 60.0
N = int(DUR * SR)
fx = np.zeros((N, 2), np.float32)
def put(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR); e = min(N, i + len(sig))
    lg, rg = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    fx[i:e, 0] += sig[:e - i] * gain * lg; fx[i:e, 1] += sig[:e - i] * gain * rg
# notas de las huellas: el tema de la serie (do-fa-mi-sol-fa-do)
C6, F6, E6, G6, C7 = 1046.5, 1396.9, 1318.5, 1568.0, 2093.0
# título y end card: cada letra entra con un "plop" suave
for t in (0.05, 0.18, 0.30, 0.42, 0.62): put(sfx.press(), t, 0.35)
for t in (0.0, 0.10, 0.22, 0.70, 1.00): put(sfx.press(), 56.25 + t, 0.35)
# 1-2: amasan la bolita
put(sfx.knead(2.4), 2.55, 0.55, -0.1); put(sfx.knead(1.6), 5.05, 0.45, 0.1)
# 3: timbre lejano del colegio y palmaditas en la mochila
put(sfx.chime(), 9.0, 0.30, 0.3); put(sfx.pat(), 10.35, 0.35); put(sfx.pat(), 10.62, 0.3)
# 4: primera huella (mamá)
put(sfx.press(), 11.85, 0.6); put(sfx.plink(C6), 11.9, 0.55)
# 5: crayón
put(sfx.scribble(2.0), 15.3, 0.35)
# 6: choca la mano y le deja una sonrisa
put(sfx.pat(), 18.6, 0.7); put(sfx.press(), 19.4, 0.45); put(sfx.plink(F6), 19.45, 0.5)
# 7: crece a los 6
put(sfx.stretch(0.55), 20.75, 0.45)
# 8: cruza con el guardia y crece a los 10
for k in range(7): put(sfx.step(), 22.6 + k * 0.36, 0.30, 0.2 * (-1) ** k)
put(sfx.stretch(1.2), 23.2, 0.35); put(sfx.plink(E6), 24.6, 0.5)
# 9: Sports Day: pito, carrera y caída
put(sfx.whistle(0.45), 25.05, 0.28, 0.4)
for k in range(7): put(sfx.step(), 25.1 + k * 0.2, 0.32, 0.2 * (-1) ** k)
put(sfx.splat(), 26.55, 0.8)
# 10: el entrenador lo levanta y se estira a los 14
put(sfx.stretch(1.4), 28.9, 0.5); put(sfx.plink(G6), 30.4, 0.5)
# 12: amigos caminando, crecen a los 17
for k in range(7): put(sfx.step(), 33.85 + k * 0.3, 0.26, 0.15 * (-1) ** k)
put(sfx.stretch(0.9), 34.6, 0.35); put(sfx.plink(F6), 35.3, 0.45)
# 13: aplausos en la ceremonia y la mano de papá
put(sfx.applause(3.5), 36.35, 0.42); put(sfx.plink(C7), 37.6, 0.45)
# 14: la sillita cruje
put(sfx.creak(), 40.35, 0.4)
# 15: amasa la plastilina azul
put(sfx.knead(1.3), 42.55, 0.45)
# 16: un pasito de la niña
put(sfx.step(), 48.1, 0.3)
# 17: su primera huella
put(sfx.press(), 49.55, 0.7); put(sfx.plink(F6), 49.6, 0.75)
# reverb corta para los efectos
from scipy.signal import fftconvolve
ir_n = int(0.6 * SR); t = np.arange(ir_n) / SR
ir = (np.random.default_rng(3).standard_normal(ir_n) * np.exp(-t * 9)).astype(np.float32); ir /= np.sqrt((ir ** 2).sum())
fx = fx + 0.18 * np.stack([fftconvolve(fx[:, c], ir)[:N] for c in range(2)], 1)
# música
w = wave.open('/home/claude/cc1/music/out/musica_cap1.wav')
mus = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768
mus = mus[:N]
mix = mus + fx * 0.55
mix = mix / np.abs(mix).max() * 0.9
def wav(path, x):
    with wave.open(path, 'wb') as o:
        o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR)
        o.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
wav('/home/claude/cc1/sfx/mezcla_raw.wav', mix)
wav('/home/claude/cc1/sfx/stem_efectos.wav', fx / max(1e-9, np.abs(fx).max()) * 0.9)
print('ok')
