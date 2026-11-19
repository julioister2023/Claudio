"""Arma "The Mighty Minis" v2: 14 tomas + cierre, locución, música con ducking y loudness.

Uso: python3 make_v2.py [--subs]
Salida en /home/claude/v2/edit/:
  mezcla_v2.wav                    mezcla final 48 kHz estéreo, -14 LUFS, pico real <= -1,5 dBTP
  mighty_minis_v2_master.mp4       1080x1920, 24 fps, 44,0 s, sin subtítulos
  mighty_minis_v2_subtitulado.mp4  igual, con subtítulos en español (con --subs)
"""
import glob
import json
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.signal import butter, sosfilt

D = "/home/claude/claudio/mighty-minis-edicion/v2/descargas"
VOZ = "/home/claude/claudio/mighty-minis-edicion/v2/voz/out"
MUSICA = "/home/claude/music_v2/mighty_minis_mix_raw.f32"
OUT = "/home/claude/v2/edit"
SR = 48000
DUR = 44.0
FPS = 24

# ------------------------------------------------------------------ montaje (cuadros a 24 fps)
# (toma, cuadro de entrada en la fuente, cuadros en el corte)
EDL = [
    ("toma_v2_01", 0, 96),    # 0,0-4,0   la mano deja al Mini; la cámara se acerca
    ("toma_v2_02", 0, 48),    # 4,0-6,0   la mochila: tropieza a los 5,08 s
    ("toma_v2_03", 12, 48),   # 6,0-8,0   detalle de la mochila cargada
    ("toma_v2_04", 0, 96),    # 8,0-12,0  saluda y la cámara entra a la cara
    ("toma_v2_05", 8, 60),    # 12,0-14,5 músculos; salto a los 13,5 s
    ("toma_v2_06", 5, 60),    # 14,5-17,0 flexiones
    ("toma_v2_07", 6, 48),    # 17,0-19,0 cenital: se arma el carro
    ("toma_v2_08", 12, 48),   # 19,0-21,0 maneja solo
    ("toma_v2_09", 14, 48),   # 21,0-23,0 se estaciona a los 22,5 s
    ("toma_v2_10", 0, 120),   # 23,0-28,0 giro de cámara; brazos 25,0-26,25 s
    ("toma_v2_11", 24, 48),   # 28,0-30,0 aletas y llama
    ("toma_v2_12", 0, 96),    # 30,0-34,0 despega y agarra la estrella (33,1 s)
    ("toma_v2_13", 24, 60),   # 34,0-36,5 baja en paracaídas; aterriza a los 35,45 s
    ("toma_v2_14", 7, 84),    # 36,5-40,0 bosteza y se duerme
]
assert sum(n for _, _, n in EDL) == 960

# ------------------------------------------------------------------ locución
# (archivo, inicio del habla en el corte en s, ganancia extra en dB)
VO = [
    ("l01__af_heart__1.00.wav", 0.55, 0.0),
    ("l02__af_heart__1.00.wav", 4.25, 0.0),
    ("l03__af_heart__1.00.wav", 6.60, 0.0),
    ("KID_HELLO", 8.25, -1.0),
    ("KID_HOLA", 9.00, -1.0),
    ("l04__af_heart__1.00.wav", 10.15, 0.0),
    ("l05__af_heart__1.00.wav", 12.10, 0.0),
    ("l06__af_heart__1.00.wav", 13.65, 0.0),
    ("l07__af_heart__1.00.wav", 15.20, 0.0),
    ("l08__af_heart__1.00.wav", 17.10, 0.0),
    ("l09__af_heart__1.00.wav", 18.95, 0.0),
    ("l10__af_heart__1.00.wav", 21.55, 0.0),
    ("l11__af_heart__1.00.wav", 23.20, 0.0),
    ("l12__af_heart__1.00.wav", 25.60, 0.0),
    ("l13__af_heart__1.00.wav", 28.20, 0.0),
    ("l14__af_heart__1.00.wav", 30.55, 0.0),
    ("KID_WOOHOO", 32.90, -1.0),   # "Yay!" al agarrar la estrella
    ("l15__af_heart__1.00.wav", 34.35, 0.0),
    ("w01__af_nicole__1.00.wav", 37.90, -2.0),
]
KIDS = json.load(open(f"{OUT}/voz_nino.json")) if glob.glob(f"{OUT}/voz_nino.json") else {}

SUBS = [  # (inicio, fin, texto) en español
    (1.20, 2.95, "Les presentamos al estudiante\nmás nuevo del CAG."),
    (4.20, 5.95, "Y su mochila nueva."),
    (6.55, 7.95, "Bien cargadita."),
    (8.20, 9.95, "Hello! ¡Hola, hola!"),
    (10.10, 11.95, "¿Dos idiomas? Obvio."),
    (12.05, 13.45, "Un poquito de deporte…"),
    (13.60, 14.95, "…y se pone fuerte."),
    (15.15, 16.90, "Pero fuerte, fuerte."),
    (17.05, 18.85, "Un poquito de robótica…"),
    (18.90, 21.40, "…y se arma un carro\nque se maneja solo."),
    (21.50, 22.95, "Y se parquea solo."),
    (23.15, 25.45, "IB, Cambridge, Programa Dual…"),
    (25.55, 27.90, "…va a necesitar\nunas manitos extra."),
    (28.15, 29.90, "Y cuando menos piensas…"),
    (30.50, 32.60, "…ya está alcanzando\nlas estrellas."),
    (32.85, 33.95, "¡Yupi!"),
    (34.30, 35.90, "Eso sí…"),
    (37.85, 39.95, "shhh… sigue siendo chiquito."),
]


def run(cmd):
    subprocess.run(cmd, check=True)


def load_audio(path, sr=SR, channels=1):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", str(channels),
                                   "-ar", str(sr), "-"])
    x = np.frombuffer(raw, np.float32)
    return x.reshape(-1, channels) if channels > 1 else x


def speech_bounds(x, sr=SR):
    win = int(sr * 0.01)
    n = len(x) // win
    e = np.sqrt((x[: n * win].reshape(n, win) ** 2).mean(1))
    db = 20 * np.log10(e + 1e-9)
    idx = np.where(db > db.max() - 35)[0]
    return idx[0] * win, (idx[-1] + 1) * win


# ------------------------------------------------------------------ audio
def build_audio():
    music = np.fromfile(MUSICA, dtype="<f4").reshape(-1, 2)[: int(DUR * SR)].copy()
    music /= np.abs(music).max()
    # nivel de la música: -20 dBFS RMS mientras suena
    act = np.sqrt((music.mean(1)[: len(music) // 2400 * 2400].reshape(-1, 2400) ** 2).mean(1))
    act = act[act > act.max() * 0.05]
    music *= 10 ** ((-20.0 - 20 * np.log10(np.sqrt((act ** 2).mean()))) / 20)

    vo = np.zeros(len(music), dtype=np.float32)
    hp = butter(2, 80, btype="high", fs=SR, output="sos")
    placed = []
    for name, t, gdb in VO:
        if name.startswith("KID_"):
            name = KIDS[name]
        x = sosfilt(hp, load_audio(name if name.startswith("/") else f"{VOZ}/{name}")).astype(np.float32)
        s0, s1 = speech_bounds(x)
        rms = np.sqrt((x[s0:s1] ** 2).mean())
        x *= 10 ** ((-19.0 + gdb - 20 * np.log10(rms)) / 20)
        start = int(round(t * SR)) - s0
        a, b = max(0, start), min(len(vo), start + len(x))
        vo[a:b] += x[a - start: b - start]
        placed.append((name, t, round((s1 - s0) / SR, 2)))

    # ducking: la música baja ~9 dB mientras hay voz (5 dB en la nana)
    win = int(0.02 * SR)
    n = len(vo) // win
    env = np.sqrt((vo[: n * win].reshape(n, win) ** 2).mean(1))
    active = (20 * np.log10(env + 1e-9) > -45).astype(np.float32)
    look = int(0.06 / 0.02)
    active = np.maximum(active, np.concatenate([active[look:], np.zeros(look)]))
    g = np.ones(n, dtype=np.float32)
    att, rel = np.exp(-1 / (0.05 / 0.02)), np.exp(-1 / (0.35 / 0.02))
    cur = 1.0
    for i in range(n):
        tt = i * 0.02
        depth = 10 ** (-(5.0 if tt >= 34.0 else 9.0) / 20)
        target = depth if active[i] else 1.0
        coef = att if target < cur else rel
        cur = target + (cur - target) * coef
        g[i] = cur
    gain = np.repeat(g, win)
    gain = np.concatenate([gain, np.full(len(vo) - len(gain), gain[-1])])
    mix = music * gain[:, None] + vo[:, None]

    raw = f"{OUT}/mezcla_v2_raw.wav"
    write_wav(raw, mix)
    # loudness en dos pasadas: -14 LUFS, pico real -1,5 dBTP
    p1 = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", raw, "-af",
                         "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                        capture_output=True, text=True).stderr
    m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", p1, re.S).group(0))
    run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af",
         f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
         f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true",
         "-ar", str(SR), "-c:a", "pcm_s16le", f"{OUT}/mezcla_v2.wav"])
    write_wav(f"{OUT}/stem_voz.wav", np.stack([vo, vo], 1))
    write_wav(f"{OUT}/stem_musica.wav", music * gain[:, None])
    return placed


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype("<i2").tobytes()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-",
                          "-c:a", "pcm_s16le", path], stdin=subprocess.PIPE)
    p.communicate(pcm)


# ------------------------------------------------------------------ subtítulos (PNG transparentes)
def subtitle_pngs():
    """Subtítulos arriba (la franja más limpia del set), sin caja. El color se adapta al fondo:
    tinta oscura con halo claro sobre el gris del set; blanco con sombra sobre pelo o primeros planos."""
    fpath = glob.glob("/home/claude/**/Poppins-SemiBold.ttf", recursive=True) or \
        glob.glob("/home/claude/**/Poppins-Medium.ttf", recursive=True)
    font = ImageFont.truetype(fpath[0], 52)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{OUT}/mighty_minis_v2_master.mp4", "-vf",
                          "fps=4,crop=780:170:150:200,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    band = np.frombuffer(raw, np.uint8).reshape(-1, 170, 780).astype(np.float32)
    paths = []
    for i, (a, b, text) in enumerate(SUBS):
        seg = band[int(a * 4): int(b * 4) + 1]
        luma = seg.mean()
        dark_frac = float(((seg < 110).mean(axis=(1, 2))).max())  # peor cuadro del intervalo
        dark_bg = True  # blanco con sombra en todos: el color no cambia entre líneas (medido: ver dark_frac)
        fill, halo = ((255, 255, 255, 255), (0, 0, 0, 190)) if dark_bg else ((29, 29, 31, 255), (255, 255, 255, 150))
        img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d, dg = ImageDraw.Draw(img), ImageDraw.Draw(glow)
        lines = text.split("\n")
        lh = 66
        y0 = 262 - (len(lines) - 1) * lh / 2
        for j, line in enumerate(lines):
            w = d.textlength(line, font=font)
            x, y = (1080 - w) / 2, y0 + j * lh
            dg.text((x, y + (3 if dark_bg else 0)), line, font=font, fill=halo)
            d.text((x, y), line, font=font, fill=fill)
        glow = glow.filter(ImageFilter.GaussianBlur(8 if dark_bg else 10))
        out = Image.alpha_composite(glow, img)
        pth = f"{OUT}/sub_{i:02d}.png"
        out.save(pth)
        paths.append(pth)
        print(f"sub {i:02d} {'blanco' if dark_bg else 'oscuro'} (luma {luma:.0f}, oscuro máx {dark_frac:.0%}) {text!r}")
    return paths


# ------------------------------------------------------------------ video
def build_video(subs=False):
    inputs, filters, labels = [], [], []
    for i, (name, s, n) in enumerate(EDL):
        inputs += ["-i", f"{D}/{name}.mp4"]
        filters.append(f"[{i}:v]trim=start_frame={s}:end_frame={s + n},setpts=PTS-STARTPTS,fps=12,fps={FPS},"
                       f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,"
                       f"format=yuv420p,trim=end_frame={n},setpts=PTS-STARTPTS[v{i}]")
        labels.append(f"[v{i}]")
    k = len(EDL)
    for j, card in enumerate(("cierre_v2_A.png", "cierre_v2_B.png")):
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", "2", "-i", f"{OUT}/{card}"]
        filters.append(f"[{k + j}:v]scale=1080:1920,setsar=1,format=yuv420p,trim=end_frame=48,"
                       f"setpts=PTS-STARTPTS[v{k + j}]")
        labels.append(f"[v{k + j}]")
    filters.append("".join(labels) + f"concat=n={len(labels)}:v=1:a=0[vcat]")
    last = "[vcat]"
    n_in = k + 2
    if subs:
        for i, (p, (a, b, _)) in enumerate(zip(subtitle_pngs(), SUBS)):
            inputs += ["-i", p]
            filters.append(f"{last}[{n_in}:v]overlay=0:0:enable='between(t,{a},{b})'[s{i}]")
            last = f"[s{i}]"
            n_in += 1
    inputs += ["-i", f"{OUT}/mezcla_v2.wav"]
    out = f"{OUT}/mighty_minis_v2_{'subtitulado' if subs else 'master'}.mp4"
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filters),
         "-map", last, "-map", f"{n_in}:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
         "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "256k", "-t", str(DUR),
         "-movflags", "+faststart", out])
    return out


if __name__ == "__main__":
    if "--solo-video" not in sys.argv:
        for row in build_audio():
            print("voz", row)
    print(build_video(subs=False))
    if "--subs" in sys.argv:
        print(build_video(subs=True))
