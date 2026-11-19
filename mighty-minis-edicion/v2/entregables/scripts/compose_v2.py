"""Música original para "The Mighty Minis" (CAG), compuesta a la medida del corte.

VERSIÓN 2 (corte de 14 tomas con cámara). 120 BPM (1 tiempo = 0,5 s), Fa mayor, 44 s.
Los golpes caen donde pasan las acciones medidas en los clips v2 (aterrizaje 1,08 s;
tropiezo con la mochila 5,08 s; salto de forzudo 13,5 s; "ta-DA" en el corte a las
flexiones 14,5 s; el carro se arma 17-19 s, maneja 19-21 s y se estaciona 22,5 s; brazos
25,0-26,25 s; despegue 30,0 s; corte cómico 34,0 s; nana 35-40 s; cierre 40-44 s).

Instrumentos: GeneralUser GS v2.0.3 (licencia libre, uso comercial permitido).
Salida: stems en music/stems/ y mezcla en bruto music/mighty_minis_mix_raw.wav (float32, 48 kHz).
"""
import os
import wave

import numpy as np
import tinysoundfont
from scipy.signal import fftconvolve, butter, sosfilt

SR = 48000
DUR = 44.0
SF = "/home/claude/music/sf/GeneralUser-GS.sf2"
OUT = "/home/claude/music_v2"
os.makedirs(f"{OUT}/stems", exist_ok=True)
RNG = np.random.default_rng(20261117)  # semilla fija: el resultado es reproducible


# ---------------------------------------------------------------- utilidades MIDI
class Stem:
    def __init__(self, name):
        self.name = name
        self.events = []
        self.programs = {}

    def prog(self, ch, preset, bank=0, drums=False):
        self.programs[ch] = (bank, preset, drums)

    def note(self, t, dur, ch, key, vel):
        vel = int(max(1, min(127, vel)))
        self.events.append((t, 2, "on", ch, key, vel))
        self.events.append((t + dur, 0, "off", ch, key, 0))

    def chord(self, t, dur, ch, keys, vel, spread=0.0):
        for i, k in enumerate(keys):
            self.note(t + i * spread, dur, ch, k, vel)

    def cc(self, t, ch, ctl, val):
        self.events.append((t, 1, "cc", ch, ctl, int(max(0, min(127, val)))))

    def bend(self, t, ch, value):
        self.events.append((t, 1, "bend", ch, int(max(0, min(16383, value))), 0))

    def ramp_cc(self, t0, t1, ch, ctl, v0, v1, step=0.02):
        n = max(1, int((t1 - t0) / step))
        for i in range(n + 1):
            self.cc(t0 + (t1 - t0) * i / n, ch, ctl, v0 + (v1 - v0) * i / n)

    def ramp_bend(self, t0, t1, ch, semis0, semis1, rng_semis=12, step=0.015):
        n = max(1, int((t1 - t0) / step))
        for i in range(n + 1):
            s = semis0 + (semis1 - semis0) * i / n
            self.bend(t0 + (t1 - t0) * i / n, ch, 8192 + s / rng_semis * 8191)


def render(stem):
    syn = tinysoundfont.Synth(samplerate=SR)
    sfid = syn.sfload(SF)
    for ch, (bank, preset, drums) in stem.programs.items():
        syn.program_select(ch, sfid, bank, preset, is_drums=drums)
        if not drums:
            syn.pitchbend_range(ch, 12)
            syn.control_change(ch, 7, 110)
            syn.control_change(ch, 11, 127)
    total = int(DUR * SR)
    out = np.zeros((total, 2), dtype=np.float32)
    events = sorted(stem.events, key=lambda e: (e[0], e[1])) + [(DUR, 9, "end", 0, 0, 0)]
    pos = 0
    for t, _, kind, a, b, c in events:
        ts = min(total, max(0, int(round(t * SR))))
        if ts > pos:
            buf = syn.generate_simple(ts - pos)
            out[pos:ts] = np.frombuffer(buf, dtype=np.float32).reshape(-1, 2)
            pos = ts
        if kind == "on":
            syn.noteon(a, b, c)
        elif kind == "off":
            syn.noteoff(a, b)
        elif kind == "cc":
            syn.control_change(a, b, c)
        elif kind == "bend":
            syn.pitchbend(a, b)
    return out


# ---------------------------------------------------------------- armonía
ARP = {
    "F": [65, 69, 72, 77, 72, 69, 65, 69],
    "Bb": [65, 70, 74, 77, 74, 70, 65, 70],
    "C": [64, 67, 72, 76, 72, 67, 64, 67],
    "Dm": [65, 69, 74, 77, 74, 69, 65, 69],
}
CHORD = {"F": [53, 57, 60, 65, 69], "Bb": [58, 62, 65, 70], "C": [60, 64, 67, 72], "C7": [60, 64, 67, 70]}


def arp_8ths(stem, ch, t0, t1, chord, vel, dur=0.22):
    pat = ARP[chord]
    i, t = 0, t0
    while t < t1 - 1e-6:
        stem.note(t, dur, ch, pat[i % 8], vel + (6 if i % 2 == 0 else 0))
        i, t = i + 1, t + 0.25


def arp_16ths(stem, ch, t0, t1, chord, vel, dur=0.11):
    pat = ARP[chord]
    i, t = 0, t0
    while t < t1 - 1e-6:
        stem.note(t, dur, ch, pat[i % 8], vel + (8 if i % 4 == 0 else 0))
        i, t = i + 1, t + 0.125


# ================================================================ TECLADOS (marimba, xilófono, glock)
keys = Stem("keys")
keys.prog(0, 12)   # Marimba
keys.prog(6, 13)   # Xylophone
keys.prog(3, 9)    # Glockenspiel
# A · toma 1 (0-4): llega el Mini
arp_8ths(keys, 0, 0.0, 2.0, "F", 54)
arp_8ths(keys, 0, 2.0, 4.0, "Bb", 58)
# B · toma 2 (4-8): la mochila; el tema entra en el silbido
arp_8ths(keys, 0, 4.0, 6.0, "F", 62)
arp_8ths(keys, 0, 6.0, 8.0, "C", 62)
keys.note(6.0, 0.6, 3, 84, 78)                      # "ding" cuando se endereza orgulloso
# C · toma 3 (8-12): Hello / ¡Hola! (espacio para la voz del Mini)
arp_8ths(keys, 0, 8.0, 10.0, "Bb", 58)
arp_8ths(keys, 0, 10.0, 12.0, "C", 58)
keys.note(9.0, 0.4, 3, 89, 52)                      # saludos
keys.note(9.25, 0.4, 3, 86, 48)
for t, k in [(10.0, 91), (10.25, 88), (10.5, 84), (10.75, 86), (11.0, 88)]:
    keys.note(t, 0.45 if t == 11.0 else 0.22, 3, k, 58)
# E · tomas 7-9 (17-22,5): se arma el carro, maneja solo y se estaciona
arp_16ths(keys, 0, 17.0, 19.0, "F", 58)
arp_16ths(keys, 0, 19.0, 21.0, "Bb", 58)
arp_16ths(keys, 0, 21.0, 22.5, "C", 56)
keys.note(22.5, 0.5, 3, 91, 80)                     # se estaciona: ding-ding
keys.note(22.75, 0.8, 3, 96, 74)
# F · toma 10 (23-28): manos extra, una nota por cada brazo que aparece
arp_8ths(keys, 0, 23.0, 25.0, "F", 58)
arp_8ths(keys, 0, 25.0, 26.0, "Dm", 58)
arp_8ths(keys, 0, 26.0, 27.0, "Bb", 58)
arp_8ths(keys, 0, 27.0, 28.0, "C", 60)
for t, k in [(25.0, 77), (25.25, 81), (25.5, 84), (25.75, 86), (26.0, 89), (26.25, 93), (26.5, 96)]:
    keys.note(t, 0.15, 6, k, 88)
keys.note(26.0, 0.3, 3, 89, 52)
keys.note(27.0, 0.3, 3, 91, 52)
# G · toma 7 (28-34): trémolo que sube y despegue
t, i = 28.0, 0
while t < 30.0 - 1e-6:
    keys.note(t, 0.1, 0, [72, 76, 79][i % 3], 36 + int(64 * (t - 28.0) / 2.0))
    t, i = t + 0.125, i + 1
arp_8ths(keys, 0, 30.0, 32.0, "F", 72)
arp_8ths(keys, 0, 32.0, 34.0, "C", 76)
for t, k in [(30.0, 84), (30.5, 81), (30.75, 84), (31.0, 86), (31.25, 84), (31.5, 81), (31.75, 86)]:
    keys.note(t, 0.2, 3, k, 64)                     # glock dobla el tema
for t, k in [(33.0, 91), (33.125, 96), (33.25, 100)]:
    keys.note(t, 0.3, 3, k, 70)                     # agarra la estrella (3,1 s de la toma 12)
# I · cierre (40-44)
keys.chord(40.0, 0.9, 0, [65, 69, 72, 77], 88, spread=0.03)
keys.note(40.5, 0.3, 3, 81, 62)
keys.note(40.75, 0.3, 3, 84, 66)
keys.chord(41.0, 0.8, 0, [64, 67, 70, 72], 80, spread=0.03)
keys.chord(42.0, 1.9, 0, [53, 60, 65, 69, 72, 77], 92, spread=0.035)
keys.note(42.0, 1.6, 3, 89, 70)
keys.note(42.125, 1.6, 3, 96, 64)

# ================================================================ BAJOS (pizzicato, bajo, tuba)
bass = Stem("bass")
bass.prog(1, 45)   # Pizzicato Strings
bass.prog(13, 33)  # Finger Bass
bass.prog(5, 58)   # Tuba
# A
bass.note(1.13, 0.35, 1, 41, 96)                    # aterriza: plop
bass.note(2.0, 0.3, 1, 46, 56)
bass.note(3.0, 0.3, 1, 41, 52)
# B, C
for t, k, v in [(4.0, 41, 86), (4.5, 48, 70), (5.0, 53, 80), (5.5, 48, 70),
                (6.0, 36, 86), (6.5, 43, 70), (7.0, 48, 80), (7.5, 43, 70),
                (8.0, 46, 80), (8.5, 53, 66), (9.0, 58, 74), (9.5, 53, 66),
                (10.0, 36, 80), (10.5, 43, 66), (11.0, 48, 74), (11.5, 43, 66)]:
    bass.note(t, 0.3, 1, k, v)
# D · músculos: tuba que se infla y oom-pah de forzudo
bass.note(12.5, 0.95, 5, 41, 108)
bass.ramp_bend(12.5, 13.0, 5, -12, 0)
for t, k in [(14.5, 34), (15.0, 36), (16.0, 36), (16.5, 31)]:
    bass.note(t, 0.38, 5, k, 100)
# E · carro: bajo en corcheas
t, i = 17.0, 0
while t < 22.5 - 1e-6:
    root = 41 if t < 19.0 else (46 if t < 21.0 else 48)
    bass.note(t, 0.2, 13, root + (12 if i % 2 else 0), 88 if i % 2 == 0 else 72)
    t, i = t + 0.25, i + 1
bass.note(22.5, 0.5, 13, 36, 72)                    # estacionado, relajado
# F · manos extra
for t, k in [(23.0, 41), (23.5, 48), (24.0, 41), (24.5, 48), (25.0, 50), (25.5, 45),
             (26.0, 46), (26.5, 41), (27.0, 48), (27.5, 43)]:
    bass.note(t, 0.3, 1, k, 82)
# G · despegue
bass.note(28.0, 1.95, 13, 36, 64)
t, i = 30.0, 0
while t < 34.0 - 1e-6:
    root = 41 if t < 32.0 else 48
    bass.note(t, 0.2, 13, root + (12 if i % 2 else 0), 96 if i % 2 == 0 else 80)
    t, i = t + 0.25, i + 1
# I · cierre
bass.note(40.0, 0.8, 13, 41, 96)
bass.note(40.0, 0.5, 1, 41, 90)
bass.note(41.0, 0.5, 13, 48, 84)
bass.note(42.0, 1.8, 13, 41, 100)
bass.note(42.0, 0.6, 1, 41, 92)

# ================================================================ MELODÍA (silbido, píccolo, clarinete)
lead = Stem("lead")
lead.prog(2, 78)   # Whistle
lead.prog(11, 72)  # Piccolo
lead.prog(7, 71)   # Clarinet
HOOK_A = [(0.0, 84, 0.45), (0.5, 81, 0.22), (0.75, 84, 0.22), (1.0, 86, 0.22),
          (1.25, 84, 0.22), (1.5, 81, 0.22), (1.75, 77, 0.22),
          (2.0, 79, 0.45), (2.5, 81, 0.45), (3.0, 84, 0.9)]
for dt, k, d in HOOK_A:                             # tema en la toma 2
    lead.note(4.0 + dt, d, 2, k, 86)
for t, k in [(26.0, 77), (26.25, 74), (26.5, 70), (26.75, 74), (27.0, 76), (27.25, 79), (27.5, 84)]:
    lead.note(t, 0.2, 7, k, 66)
# riser: silbido de émbolo que sube una octava en 2 s
lead.cc(27.99, 2, 11, 40)
lead.note(28.0, 1.98, 2, 84, 96)
lead.ramp_bend(28.0, 29.98, 2, -12, 0)
lead.ramp_cc(28.0, 29.98, 2, 11, 40, 127)
lead.bend(29.99, 2, 8192)
# clímax: tema en píccolo y carrerita "woohoo" hasta el corte
for dt, k, d in [(0.0, 84, 0.45), (0.5, 81, 0.22), (0.75, 84, 0.22), (1.0, 86, 0.22),
                 (1.25, 84, 0.22), (1.5, 81, 0.22), (1.75, 86, 0.22),
                 (2.0, 84, 0.11), (2.125, 86, 0.11), (2.25, 88, 0.11), (2.375, 89, 0.11)]:
    lead.note(30.0 + dt, d, 11, k, 102)
lead.note(32.5, 1.49, 11, 91, 108)
# cierre: cadencia del tema (Do Si♭ La Sol → Fa)
for t, k in [(41.0, 84), (41.25, 82), (41.5, 81), (41.75, 79)]:
    lead.note(t, 0.22, 2, k, 84)
lead.note(42.0, 1.6, 2, 77, 88)

# ================================================================ METALES Y TIMBALES
brass = Stem("brass")
brass.prog(4, 61)   # Brass Section
brass.prog(12, 47)  # Timpani
brass.note(5.13, 0.7, 12, 41, 108)                  # la mochila pesa: tropieza
brass.chord(13.625, 0.75, 4, CHORD["F"], 114)         # ¡BWAAM! salto de forzudo
brass.note(13.625, 0.9, 12, 41, 118)
brass.chord(14.0, 0.15, 4, [57, 60, 65], 70)        # pah
brass.chord(14.5, 0.9, 4, CHORD["C"], 116)          # ¡DA! justo al terminar "strong" (corte a las flexiones)
brass.note(14.5, 0.9, 12, 48, 112)
brass.chord(15.5, 0.15, 4, [58, 62, 65], 70)
t = 16.0
while t < 17.0 - 1e-6:                              # redoble de timbal al carro
    brass.note(t, 0.12, 12, 48, 50 + int(55 * (t - 16.0)))
    t += 0.0625
brass.chord(17.0, 0.22, 4, CHORD["F"], 100)
brass.chord(19.0, 0.18, 4, CHORD["Bb"], 86)        # arranca solo
brass.chord(21.0, 0.18, 4, CHORD["C"], 86)          # maniobra para estacionarse
# riser y despegue
brass.cc(27.99, 4, 11, 30)
brass.chord(28.0, 1.97, 4, [48, 55, 60, 64, 67], 108)
brass.ramp_cc(28.0, 29.97, 4, 11, 30, 127)
t = 28.0
while t < 30.0 - 1e-6:
    brass.note(t, 0.1, 12, 48, 40 + int(70 * (t - 28.0) / 2.0))
    t += 0.0625
brass.cc(30.0, 4, 11, 127)
brass.chord(30.0, 0.55, 4, [53, 57, 60, 65, 69, 72], 122)
brass.note(30.0, 1.0, 12, 41, 127)
brass.chord(31.0, 0.15, 4, [57, 60, 65], 90)
brass.chord(31.5, 0.15, 4, [57, 60, 65], 90)
brass.cc(31.99, 4, 11, 92)
brass.chord(32.0, 1.99, 4, [48, 60, 64, 67, 72], 106)
brass.ramp_cc(32.0, 33.98, 4, 11, 92, 127)
# cierre
brass.cc(39.9, 4, 11, 110)
brass.chord(40.0, 0.6, 4, [53, 57, 60, 65], 90)
brass.chord(41.0, 0.4, 4, CHORD["C7"], 76)
brass.chord(42.0, 1.85, 4, [53, 57, 60, 65, 69], 96)
brass.ramp_cc(42.4, 43.85, 4, 11, 110, 40)
brass.note(42.0, 1.4, 12, 41, 100)

# ================================================================ BATERÍA
dr = Stem("drums")
dr.prog(9, 0, bank=128, drums=True)
KICK, SNARE, CLAP, HH, OHH, CRASH, CRASH2, MARACAS, WOOD, TAMB, TRI = 36, 38, 39, 42, 46, 49, 57, 70, 76, 54, 81


def hit(t, k, v):
    dr.note(t, 0.1, 9, k, v)


for i in range(2, 16):                              # A: maracas
    hit(i * 0.25, MARACAS, 44 if i % 2 else 32)
hit(1.13, WOOD, 78)                                 # aterrizaje
for bar_start in (4.0, 6.0, 8.0, 10.0):             # B y C: groove suave
    for b in range(4):
        tb = bar_start + b * 0.5
        if b % 2 == 0:
            hit(tb, KICK, 74 if bar_start < 8 else 64)
        else:
            hit(tb, CLAP, 80)
    for e in range(8):
        hit(bar_start + e * 0.25, MARACAS, 46 if e % 2 else 34)
        if bar_start >= 8.0 and e % 2:
            hit(bar_start + e * 0.25, HH, 48)
# D: forzudo y flexiones
for tb in (13.625, 14.5, 15.0, 16.0):
    hit(tb, KICK, 100)
for tb in (14.0, 15.5):
    hit(tb, SNARE, 72)
hit(13.625, CRASH, 96)
hit(14.5, CRASH2, 102)
for i in range(8):
    hit(16.0 + i * 0.125, SNARE, 40 + i * 9)
# E: carro (las piezas encajan una a una, luego maneja y se estaciona)
hit(17.0, CRASH, 88)
for tb, v in [(17.17, 70), (17.42, 66), (17.58, 72), (17.75, 68), (18.08, 74), (18.33, 80)]:
    hit(tb, WOOD, v)
t = 17.0
while t < 22.5 - 1e-6:
    k = round((t - 17.0) / 0.125)
    hit(t, HH, 58 if k % 2 == 0 else 40)
    if k % 4 == 0:
        hit(t, KICK, 96)
    if k % 8 == 4:
        hit(t, CLAP, 86)
    t += 0.125
hit(22.5, KICK, 92)
hit(22.5, CRASH, 72)
# F: manos extra
for i in range(10):
    tb = 23.0 + i * 0.5
    hit(tb, KICK if i % 2 == 0 else CLAP, 76)
for i in range(20):
    hit(23.0 + i * 0.25, MARACAS, 44 if i % 2 else 32)
# G: redoble, despegue y clímax
hit(28.0, KICK, 60)
for i in range(16):
    hit(28.0 + i * 0.125, SNARE, 30 + int(i * 6))
hit(30.0, CRASH, 116)
hit(30.0, CRASH2, 100)
for i in range(8):
    tb = 30.0 + i * 0.5
    hit(tb, KICK, 102)
    if i % 2:
        hit(tb, CLAP, 94)
for i in range(16):
    hit(30.0 + i * 0.25, HH, 62 if i % 2 == 0 else 48)
hit(32.0, CRASH, 92)
for i, v in enumerate((92, 100, 108, 116)):
    hit(33.5 + i * 0.125, SNARE, v)
# I: cierre
hit(40.0, KICK, 96)
hit(40.0, CRASH, 70)
hit(40.0, TRI, 70)
hit(41.0, CLAP, 70)
hit(42.0, KICK, 100)
hit(42.0, CRASH, 76)
hit(42.0, TRI, 82)

# ================================================================ NANA (arpa y caja de música)
lull = Stem("lullaby")
lull.prog(10, 46)  # Harp
lull.prog(8, 10)   # Music Box
for t, k in [(35.0, 84), (35.15, 81), (35.3, 77), (35.45, 72)]:
    lull.note(t, 0.9, 10, k, 66)                    # baja flotando (toma 13)
lull.note(35.45, 1.2, 10, 53, 50)                   # aterriza suavecito (35,45 s)
for dt, k, d in [(0.0, 84, 0.9), (1.0, 81, 0.45), (1.5, 84, 0.45), (2.0, 86, 0.45),
                 (2.5, 84, 0.45), (3.0, 81, 0.45), (3.5, 77, 0.6)]:
    lull.note(36.0 + dt, d, 8, k, 72 - int(dt * 4))
lull.chord(36.0, 2.0, 10, [53, 60, 65, 69], 46, spread=0.045)
lull.chord(38.0, 1.0, 10, [58, 62, 65, 70], 42, spread=0.045)
lull.chord(39.0, 1.2, 10, [53, 57, 60, 65], 38, spread=0.045)

# ---------------------------------------------------------------- render de stems MIDI
stems = {}
for st in (keys, bass, lead, brass, dr, lull):
    stems[st.name] = render(st)
    print("render", st.name, "peak", float(np.abs(stems[st.name]).max()))


# ---------------------------------------------------------------- efectos de sonido (ruido filtrado)
def noise(n):
    return RNG.standard_normal(n).astype(np.float32)


def sweep_band(n, f0, f1, q_bw=0.6):
    """Ruido filtrado con un pasabanda que barre de f0 a f1 (por bloques)."""
    out = np.zeros(n, dtype=np.float32)
    x = noise(n)
    block = 480
    for s in range(0, n, block):
        frac = s / max(1, n - 1)
        fc = f0 * (f1 / f0) ** frac
        lo, hi = fc * (1 - q_bw / 2), min(fc * (1 + q_bw / 2), SR / 2 - 100)
        sos = butter(2, [lo, hi], btype="band", fs=SR, output="sos")
        seg = x[max(0, s - 2048):s + block]
        y = sosfilt(sos, seg)[-min(block, n - s):]
        out[s:s + len(y)] = y
    return out


sfx = np.zeros((int(DUR * SR), 2), dtype=np.float32)


def place(sig, t, pan=0.0, gain=1.0):
    s = int(t * SR)
    e = min(len(sfx), s + len(sig))
    lg, rg = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    sfx[s:e, 0] += sig[:e - s] * lg * gain
    sfx[s:e, 1] += sig[:e - s] * rg * gain


def env(n, attack, release):
    a, r = int(attack * SR), int(release * SR)
    e = np.ones(n, dtype=np.float32)
    e[:a] = np.linspace(0, 1, a)
    e[n - r:] = np.linspace(1, 0, r) ** 2
    return e


# zumbidos del carro (pico un cuadro después de la imagen)
n = int(0.38 * SR)
place(sweep_band(n, 700, 3200) * env(n, 0.12, 0.2), 19.05, pan=-0.4, gain=0.9)
place(sweep_band(n, 3200, 700) * env(n, 0.12, 0.2), 21.2, pan=0.4, gain=0.9)
# riser 28-30 s
n = int(2.0 * SR)
r = sweep_band(n, 300, 6000, q_bw=0.9) * (np.linspace(0, 1, n) ** 2.2)
r[-int(0.004 * SR):] *= np.linspace(1, 0, int(0.004 * SR))
place(r, 28.0, gain=1.1)
# despegue: retumbo + soplido que baja
n = int(1.3 * SR)
sos = butter(2, 260, btype="low", fs=SR, output="sos")
rumble = sosfilt(sos, noise(n)) * np.exp(-np.linspace(0, 4.5, n))
place((rumble * 3.0 + sweep_band(n, 4000, 500, q_bw=1.0) * np.exp(-np.linspace(0, 3.2, n))).astype(np.float32), 30.02, gain=1.0)
stems["sfx"] = sfx


# ---------------------------------------------------------------- reverb sintética (convolución)
def make_ir(seconds=1.4, rt60=1.1):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    decay = np.exp(-6.91 * t / rt60)
    sos = butter(1, 5500, btype="low", fs=SR, output="sos")
    ir = np.stack([sosfilt(sos, noise(n)) * decay, sosfilt(sos, noise(n)) * decay], axis=1)
    ir[: int(0.012 * SR)] = 0  # pre-delay
    return (ir / np.sqrt((ir ** 2).sum(axis=0))).astype(np.float32)


IR = make_ir()


def reverb(x, send):
    if send <= 0:
        return x
    wet = np.stack([fftconvolve(x[:, c], IR[:, c])[: len(x)] for c in range(2)], axis=1)
    return x + send * wet.astype(np.float32)


def active_rms_db(x):
    mono = x.mean(axis=1)
    frame = int(0.05 * SR)
    m = mono[: len(mono) // frame * frame].reshape(-1, frame)
    rms = np.sqrt((m ** 2).mean(axis=1))
    act = rms[rms > rms.max() * 0.05]
    return 20 * np.log10(np.sqrt((act ** 2).mean()) + 1e-12)


# objetivo de nivel (RMS mientras suena, dBFS) y envío de reverb por stem
PLAN = {"drums": (-21.0, 0.05), "bass": (-21.5, 0.0), "keys": (-23.0, 0.20), "lead": (-20.5, 0.22),
        "brass": (-21.0, 0.16), "lullaby": (-22.0, 0.32), "sfx": (-27.0, 0.10)}
mix = np.zeros((int(DUR * SR), 2), dtype=np.float32)
for name, x in stems.items():
    target, send = PLAN[name]
    g = 10 ** ((target - active_rms_db(x)) / 20)
    y = reverb(x * g, send)
    if name != "lullaby":
        # corte cómico seco a los 34 s y vuelta para el cierre a los 40 s
        e = np.ones(len(y), dtype=np.float32)
        a, b = int(33.99 * SR), int(34.0 * SR)
        e[a:b] = np.linspace(1, 0, b - a)
        e[b:int(39.995 * SR)] = 0
        c = int(39.995 * SR)
        e[c:int(40.0 * SR)] = np.linspace(0, 1, int(40.0 * SR) - c)
        y *= e[:, None]
    mix += y
    with wave.open(f"{OUT}/stems/{name}.wav", "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(y / max(1e-9, np.abs(y).max()) * 0.9, -1, 1) * 32767).astype(np.int16).tobytes())
    print(f"stem {name:8s} gain {20*np.log10(g):+6.1f} dB  send {send}")

# fundido final 43,4-44 s
f0 = int(43.4 * SR)
mix[f0:] *= np.linspace(1, 0, len(mix) - f0)[:, None] ** 1.5
peak = float(np.abs(mix).max())
mix = mix / peak * 0.89
mix.astype("<f4").tofile(f"{OUT}/mighty_minis_mix_raw.f32")
print("mix peak before norm", peak, "samples", len(mix))
