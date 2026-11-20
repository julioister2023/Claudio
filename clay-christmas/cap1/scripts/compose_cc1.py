"""Música original para "A CAG Clay Christmas · 1/4 — Hecho a mano" (60 s).

Fa mayor, 6/8 con negra con puntillo = 48 (un compás = 2,5 s; corchea = 0,4167 s).
Tema de la serie (5 notas, do-fa-mi-sol-fa) en el título, en el piano de la toma 11 y en el end card.
Piano solo e íntimo al principio; las cuerdas entran cuando crece (20 s); la orquesta completa
cuando le da la estrella (45-52,5 s); cierra otra vez con piano solo.
Instrumentos: GeneralUser GS (licencia libre, uso comercial permitido).
"""
import os, wave
import numpy as np
import tinysoundfont
from scipy.signal import fftconvolve, butter, sosfilt

SR = 48000
DUR = 61.0
SF = "/home/claude/music/sf/GeneralUser-GS.sf2"
OUT = "/home/claude/cc1/music/out"
os.makedirs(f"{OUT}/stems", exist_ok=True)
RNG = np.random.default_rng(20261120)
E = 2.5 / 6          # corchea
Q = 2 * E            # negra
DQ = 3 * E           # negra con puntillo (pulso)
BAR = 2.5

class Stem:
    def __init__(self, name):
        self.name, self.events, self.programs = name, [], {}
    def prog(self, ch, preset, bank=0, drums=False):
        self.programs[ch] = (bank, preset, drums)
    def note(self, t, dur, ch, key, vel):
        vel = int(max(1, min(127, vel + RNG.integers(-3, 4))))
        t = t + RNG.uniform(0, 0.012)                       # un poco humano
        self.events.append((t, 2, "on", ch, key, vel))
        self.events.append((t + dur, 0, "off", ch, key, 0))
    def chord(self, t, dur, ch, keys, vel, spread=0.0):
        for i, k in enumerate(keys):
            self.note(t + i * spread, dur, ch, k, vel)
    def cc(self, t, ch, ctl, val):
        self.events.append((t, 1, "cc", ch, ctl, int(max(0, min(127, val)))))
    def ramp(self, t0, t1, ch, v0, v1, ctl=11, step=0.03):
        n = max(1, int((t1 - t0) / step))
        for i in range(n + 1):
            self.cc(t0 + (t1 - t0) * i / n, ch, ctl, v0 + (v1 - v0) * i / n)

def render(stem):
    syn = tinysoundfont.Synth(samplerate=SR)
    sfid = syn.sfload(SF)
    for ch, (bank, preset, drums) in stem.programs.items():
        syn.program_select(ch, sfid, bank, preset, is_drums=drums)
        if not drums:
            syn.control_change(ch, 7, 110)
            syn.control_change(ch, 11, 127)
    total = int(DUR * SR)
    out = np.zeros((total, 2), dtype=np.float32)
    events = sorted(stem.events, key=lambda e: (e[0], e[1])) + [(DUR, 9, "end", 0, 0, 0)]
    pos = 0
    for t, _, kind, a, b, c in events:
        ts = min(total, max(0, int(round(t * SR))))
        if ts > pos:
            out[pos:ts] = np.frombuffer(syn.generate_simple(ts - pos), dtype=np.float32).reshape(-1, 2)
            pos = ts
        if kind == "on": syn.noteon(a, b, c)
        elif kind == "off": syn.noteoff(a, b)
        elif kind == "cc": syn.control_change(a, b, c)
    return out

# ------------------------------------------------------------- armonía (notas MIDI, do central = 60)
CH = {   # bajo, quinta, tercera, octava (para arpegios 6/8)
    "F":  [41, 48, 57, 53], "Bb": [46, 53, 62, 58], "C":  [36, 43, 52, 48], "Dm": [38, 45, 53, 50],
    "Am": [45, 52, 60, 57], "Gm": [43, 50, 58, 55], "F/A": [45, 48, 57, 53], "C/E": [40, 43, 52, 48],
}
PAD = {  # voces para cuerdas
    "F":  [53, 57, 60, 65, 69], "Bb": [53, 58, 62, 65, 70], "C":  [52, 55, 60, 64, 67], "Dm": [53, 57, 62, 65, 69],
    "Am": [52, 57, 60, 64, 69], "Gm": [50, 55, 58, 62, 67], "F/A": [53, 57, 60, 65, 69], "C/E": [52, 55, 60, 64, 67],
}
LOW = {"F": 41, "Bb": 34, "C": 36, "Dm": 38, "Am": 45, "Gm": 43, "F/A": 45, "C/E": 40}

def arp68(st, ch, t0, t1, chord, vel, dur=0.9):
    b, f, th, o = CH[chord]
    pat = [b, f, th, o, th, f]
    i, t = 0, t0
    while t < t1 - 1e-6:
        st.note(t, dur, ch, pat[i % 6], vel + (8 if i % 3 == 0 else 0))
        i, t = i + 1, t + E

def theme(st, ch, t0, vel, octave=0, last=1.6):
    """Tema de la serie: do-fa-mi-sol-fa."""
    seq = [(0, E * 0.95, 72), (E, Q + E * 0.4, 77), (DQ, E * 0.95, 76), (DQ + E, E * 0.95, 79), (DQ + 2 * E, last, 77)]
    for dt, d, k in seq:
        st.note(t0 + dt, d, ch, k + 12 * octave, vel + (6 if k == 77 else 0))

# ------------------------------------------------------------- piano
pno = Stem("piano"); pno.prog(0, 0)
pno.cc(0, 0, 64, 0)
# Título 0-2,5: tema solo
theme(pno, 0, 0.05, 58, last=1.9)
pno.chord(0.05, 1.25, 0, [41, 48, 57], 40); pno.chord(1.30, 0.8, 0, [46, 53, 62], 36); pno.chord(1.30 + 2 * E, 1.2, 0, [41, 48, 57], 38)
# 2,5-15: nana íntima (tomas 1-4)
prog1 = [(2.5, "F"), (5.0, "Bb"), (7.5, "F/A"), (8.75, "C"), (10.0, "Dm"), (12.5, "Bb"), (13.75, "C")]
for i, (t, c) in enumerate(prog1):
    t1 = prog1[i + 1][0] if i + 1 < len(prog1) else 15.0
    arp68(pno, 0, t, t1, c, 34)
mel1 = [(2.5, DQ, 69), (3.75, E, 67), (4.17, Q, 65), (5.0, Q, 74), (5.83, E, 72), (6.25, DQ, 70),
        (7.5, DQ, 69), (8.75, E, 67), (9.17, Q, 72), (10.0, Q, 69), (10.83, E, 65), (11.25, DQ, 62),
        (12.5, Q, 65), (13.33, E, 62), (13.75, DQ, 67)]
for t, d, k in mel1:
    pno.note(t, d * 0.97, 0, k, 50)
# 15-22,5: aula (tomas 5-7), un poco más luminoso
prog2 = [(15.0, "F"), (17.5, "Am"), (20.0, "Bb"), (21.25, "C")]
for i, (t, c) in enumerate(prog2):
    t1 = prog2[i + 1][0] if i + 1 < len(prog2) else 22.5
    arp68(pno, 0, t, t1, c, 38)
mel2 = [(15.0, E, 72), (15.42, E, 74), (15.83, E, 72), (16.25, DQ, 69), (17.5, Q, 72), (18.33, E, 76),
        (18.75, DQ, 72), (20.0, Q, 74), (20.83, E, 72), (21.25, DQ, 79)]
for t, d, k in mel2:
    pno.note(t, d * 0.97, 0, k, 54)
# 22,5-31,25: crece (tomas 8-10)
prog3 = [(22.5, "F"), (25.0, "Dm"), (27.5, "Bb"), (30.0, "C")]
for i, (t, c) in enumerate(prog3):
    t1 = prog3[i + 1][0] if i + 1 < len(prog3) else 31.25
    arp68(pno, 0, t, t1, c, 42 if t < 27.5 else 46)
mel3 = [(22.5, Q, 77), (23.33, E, 76), (23.75, DQ, 72), (25.0, E, 74), (25.42, E, 77), (25.83, E, 81),
        (26.25, DQ, 77), (27.5, DQ, 74), (28.75, DQ, 77), (30.0, DQ, 79), (30.62, E, 81)]
for t, d, k in mel3:
    pno.note(t, d * 0.97, 0, k, 58)
# 31,25-33,75: el piano de la profe de música toca el tema (toma 11)
theme(pno, 0, 31.25, 64, last=2.0)
pno.chord(31.25, 2.4, 0, [41, 48, 57], 36)
# 33,75-40: amigo y ceremonia (tomas 12-13)
prog5 = [(33.75, "Bb"), (35.0, "C"), (36.25, "Dm"), (37.5, "Bb"), (38.75, "C")]
for i, (t, c) in enumerate(prog5):
    t1 = prog5[i + 1][0] if i + 1 < len(prog5) else 40.0
    arp68(pno, 0, t, t1, c, 46)
# 40-45: Navidad, otra vez íntimo (tomas 14-15)
prog6 = [(40.0, "F"), (42.5, "Bb")]
for i, (t, c) in enumerate(prog6):
    t1 = prog6[i + 1][0] if i + 1 < len(prog6) else 45.0
    arp68(pno, 0, t, t1, c, 32, dur=1.2)
mel6 = [(40.0, DQ, 81), (41.25, E, 79), (41.67, Q, 77), (42.5, Q, 82), (43.33, E, 81), (43.75, DQ, 77)]
for t, d, k in mel6:
    pno.note(t, d * 0.97, 0, k, 46)
# 45-52,5: la estrella (tomas 16-17), piano acompaña a la orquesta
prog7 = [(45.0, "Dm"), (46.25, "Bb"), (47.5, "Gm"), (48.75, "C"), (50.0, "F"), (51.25, "F")]
for i, (t, c) in enumerate(prog7):
    t1 = prog7[i + 1][0] if i + 1 < len(prog7) else 52.5
    arp68(pno, 0, t, t1, c, 50)
# 52,5-56,25: resuelve (toma 18)
for t, c in [(52.5, "Bb"), (53.75, "Bb"), (55.0, "F")]:
    arp68(pno, 0, t, t + 1.25, c, 36, dur=1.3)
# 56,25-60: end card, tema solo y acorde final
theme(pno, 0, 56.25, 56, last=1.5)
pno.chord(56.25, 1.2, 0, [41, 48, 57], 34); pno.chord(57.5, 0.8, 0, [46, 53, 62], 32)
pno.chord(58.35, 2.6, 0, [29, 41, 48, 57, 67, 72], 44, spread=0.045)

# ------------------------------------------------------------- celesta, glockenspiel y arpa
cel = Stem("celesta"); cel.prog(0, 8); cel.prog(1, 9); cel.prog(2, 46)
for t, d, k in mel2:
    if t < 20.0:
        cel.note(t, d, 0, k + 12, 34)
for t, d, k in mel6:
    cel.note(t, d, 0, k, 40)
# destello de la estrella (toma 15) y de la entrega
for i, k in enumerate([84, 89, 93, 96]):
    cel.note(43.95 + i * 0.09, 1.2, 1, k, 52 - i * 4)
for i, k in enumerate([89, 93, 96, 101]):
    cel.note(50.0 + i * 0.1, 1.5, 1, k, 50 - i * 4)
# glissando de arpa cuando se estira (toma 10) y en el clímax
for i, k in enumerate([53, 57, 60, 65, 69, 72, 77, 81, 84, 89]):
    cel.note(29.30 + i * 0.11, 1.6, 2, k, 46 + i * 2)
for i, k in enumerate([53, 57, 60, 65, 69, 72, 77, 81, 84]):
    cel.note(48.9 + i * 0.12, 1.8, 2, k, 50 + i * 2)

# ------------------------------------------------------------- cuerdas
strg = Stem("strings")
strg.prog(0, 48); strg.prog(1, 49); strg.prog(2, 42); strg.prog(3, 43); strg.prog(4, 45)
for ch in (0, 1, 2, 3):
    strg.cc(0, ch, 11, 0)
def pad(t0, t1, chord, vel=70, ch=1):
    strg.chord(t0, t1 - t0 + 0.08, ch, PAD[chord], vel)
    strg.note(t0, t1 - t0 + 0.08, 2, LOW[chord] + 12, vel - 6)
def bass(t0, t1, chord, vel=70):
    strg.note(t0, t1 - t0 + 0.08, 3, LOW[chord], vel)
# entran cuando crece (20 s)
for t0, t1, c in [(20.0, 21.25, "Bb"), (21.25, 22.5, "C"), (22.5, 25.0, "F"), (25.0, 26.6, "Dm"),
                  (27.5, 30.0, "Bb"), (30.0, 31.25, "C"), (31.25, 33.75, "F"), (33.75, 35.0, "Bb"),
                  (35.0, 36.25, "C"), (36.25, 37.5, "Dm"), (37.5, 38.75, "Bb"), (38.75, 40.0, "C")]:
    pad(t0, t1, c)
    if t0 >= 22.5:
        bass(t0, t1, c, 62)
for ch in (1, 2):
    strg.ramp(20.0, 22.5, ch, 0, 70)
    strg.ramp(22.5, 26.5, ch, 70, 84)
    strg.ramp(26.5, 26.75, ch, 84, 30)      # se cae: respiro
    strg.ramp(27.5, 31.25, ch, 50, 108)     # lo levantan y se estira
    strg.ramp(31.25, 31.6, ch, 108, 62)
    strg.ramp(31.6, 33.75, ch, 62, 58)
    strg.ramp(33.75, 39.9, ch, 66, 112)
    strg.ramp(39.9, 40.0, ch, 112, 0)        # corte suave a la Navidad
strg.ramp(22.5, 39.9, 3, 70, 100); strg.ramp(39.9, 40.0, 3, 100, 0)
# pizzicato del Sports Day (toma 9)
for i in range(4):
    for k in ([50, 57, 62] if i % 2 == 0 else [53, 57, 65]):
        strg.note(25.0 + i * E, 0.3, 4, k, 64)
# Navidad: colchón muy suave
for t0, t1, c in [(40.0, 42.5, "F"), (42.5, 45.0, "Bb")]:
    pad(t0, t1, c, 60, ch=0)
strg.ramp(40.0, 41.0, 0, 0, 52)
strg.ramp(41.0, 45.0, 0, 52, 60)
# la estrella: crescendo a la orquesta completa
for t0, t1, c in [(45.0, 46.25, "Dm"), (46.25, 47.5, "Bb"), (47.5, 48.75, "Gm"), (48.75, 50.0, "C"),
                  (50.0, 52.5, "F"), (52.5, 55.0, "Bb"), (55.0, 58.4, "F")]:
    pad(t0, t1, c, 80, ch=0)
    pad(t0, t1, c, 74, ch=1)
    bass(t0, t1, c, 74)
strg.ramp(45.0, 50.0, 0, 60, 120); strg.ramp(45.0, 50.0, 1, 0, 112); strg.ramp(45.0, 50.0, 2, 0, 110)
strg.ramp(45.0, 50.0, 3, 0, 110)
for ch in (0, 1, 2, 3):
    strg.ramp(50.0, 52.5, ch, 120 if ch == 0 else 112, 100)
    strg.ramp(52.5, 56.25, ch, 100, 58)
    strg.ramp(56.25, 58.6, ch, 58, 0)
# línea de violines en el clímax (el tema, aumentado)
for t, d, k in [(47.5, Q, 72), (48.33, E, 74), (48.75, DQ, 76), (50.0, DQ, 77), (51.25, E, 81), (51.67, Q, 79),
                (52.5, DQ, 77), (53.75, DQ, 74), (55.0, 2.6, 72)]:
    strg.note(t, d * 0.98, 0, k + 12, 92)

# ------------------------------------------------------------- metales y timbal
brs = Stem("brass"); brs.prog(0, 60); brs.prog(1, 47); brs.prog(9, 0, bank=128, drums=True)
brs.cc(0, 0, 11, 90)
# cornos con el tema en la ceremonia (toma 13)
for t, d, k in [(36.25, E, 60), (36.67, Q + E * 0.5, 65), (37.5, E, 64), (37.92, E, 67), (38.33, 1.6, 65)]:
    brs.note(t, d, 0, k, 82)
brs.chord(38.75, 1.2, 0, [60, 64, 67], 78)
# cornos en el clímax
for t0, t1, keys in [(47.5, 48.75, [55, 62, 67]), (48.75, 50.0, [55, 60, 64]), (50.0, 52.5, [53, 60, 65]),
                     (52.5, 55.0, [53, 58, 62])]:
    brs.chord(t0, t1 - t0 + 0.05, 0, keys, 84)
brs.ramp(47.5, 50.0, 0, 60, 120); brs.ramp(50.0, 55.0, 0, 120, 60)
# timbal: redoble antes del clímax y golpe en el pico
for i in range(14):
    brs.note(48.9 + i * 0.075, 0.2, 1, 41, 30 + i * 4)
brs.note(50.0, 1.4, 1, 41, 100)
brs.note(30.0 + 1.25, 1.0, 1, 36, 62)      # golpe suave cuando termina de estirarse
# platillo suspendido (redoble suave) hacia el pico
for i in range(16):
    brs.note(48.8 + i * 0.07, 0.3, 9, 51, 20 + i * 3)
brs.note(50.0, 2.0, 9, 57, 70)

stems = {}
for st in (pno, cel, strg, brs):
    stems[st.name] = render(st)
    print("render", st.name, "peak", round(float(np.abs(stems[st.name]).max()), 3))

# ------------------------------------------------------------- reverb y mezcla
def make_ir(seconds=2.4, rt60=1.9):
    n = int(seconds * SR); t = np.arange(n) / SR
    decay = np.exp(-6.91 * t / rt60)
    sos = butter(1, 5000, btype="low", fs=SR, output="sos")
    ir = np.stack([sosfilt(sos, RNG.standard_normal(n)) * decay, sosfilt(sos, RNG.standard_normal(n)) * decay], axis=1)
    ir[: int(0.018 * SR)] = 0
    return (ir / np.sqrt((ir ** 2).sum(axis=0))).astype(np.float32)
IR = make_ir()
def reverb(x, send):
    wet = np.stack([fftconvolve(x[:, c], IR[:, c])[: len(x)] for c in range(2)], axis=1)
    return x + send * wet.astype(np.float32)
def active_rms_db(x):
    mono = x.mean(axis=1); fr = int(0.05 * SR)
    m = mono[: len(mono) // fr * fr].reshape(-1, fr)
    rms = np.sqrt((m ** 2).mean(axis=1)); act = rms[rms > rms.max() * 0.05]
    return 20 * np.log10(np.sqrt((act ** 2).mean()) + 1e-12)
PLAN = {"piano": (-21.0, 0.30), "celesta": (-27.0, 0.40), "strings": (-23.0, 0.34), "brass": (-26.0, 0.30)}
mix = np.zeros((int(DUR * SR), 2), dtype=np.float32)
for name, x in stems.items():
    target, send = PLAN[name]
    g = 10 ** ((target - active_rms_db(x)) / 20)
    y = reverb(x * g, send)
    mix += y
    with wave.open(f"{OUT}/stems/{name}.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y / max(1e-9, np.abs(y).max()) * 0.9, -1, 1) * 32767).astype(np.int16).tobytes())
    print(f"stem {name:8s} gain {20*np.log10(g):+6.1f} dB")
# Arco dinámico: íntimo al principio, crece con él, respira en la música y en la Navidad, clímax en la estrella
BP = [(0.0, -4), (2.4, -4), (2.6, -8), (14.8, -8), (15.2, -6), (19.8, -6), (22.5, -3), (26.5, -1), (26.8, -5), (27.5, -4),
      (31.1, 0), (31.4, -7), (33.6, -7), (33.9, -4), (39.8, 0), (40.1, -8), (44.9, -8), (45.1, -6), (49.8, 0),
      (52.4, 0), (56.1, -5), (56.4, -7), (61.0, -7)]
tt = np.arange(len(mix)) / SR
env_db = np.interp(tt, [b[0] for b in BP], [b[1] for b in BP])
mix *= (10 ** (env_db / 20)).astype(np.float32)[:, None]
f0, f1 = int(59.2 * SR), int(60.0 * SR)
mix[f0:f1] *= np.linspace(1, 0, f1 - f0)[:, None] ** 1.6
mix[f1:] = 0
mix = mix / float(np.abs(mix).max()) * 0.89
with wave.open(f"{OUT}/musica_cap1.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("ok", len(mix) / SR)
