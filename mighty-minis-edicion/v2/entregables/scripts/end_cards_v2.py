"""Cierre v2 de The Mighty Minis, al estilo del anuncio de Apple.

A (40-42 s): el último cuadro de la toma 14 (el Mini dormido en el set) con el titular
   "The Mighty Minis." arriba, como el producto enmarcado por su titular.
B (42-44 s): el mismo gris del set, con el logo del CAG en azul y la línea de admisiones.

Uso: python3 end_cards_v2.py <ultimo_cuadro_t14.png> <logo_azul.png> <carpeta_salida>
"""
import glob
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ultimo, logo_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
FONT = {n: glob.glob(f"/home/claude/**/Poppins-{n}.ttf", recursive=True)[0] for n in ("Bold", "Medium", "Regular")}
W, H = 1080, 1920
INK = (29, 29, 31)          # #1D1D1F
INK_SOFT = (43, 48, 72)     # #2B3048


def centered(draw, y, text, font, fill):
    w = draw.textlength(text, font=font)
    draw.text(((W - w) / 2, y), text, font=font, fill=fill)


# A · titular sobre el último cuadro (encuadre 1080x1920)
frame = Image.open(ultimo).convert("RGB")
s = max(W / frame.width, H / frame.height)
frame = frame.resize((round(frame.width * s), round(frame.height * s)), Image.LANCZOS)
x0, y0 = (frame.width - W) // 2, (frame.height - H) // 2
frame = frame.crop((x0, y0, x0 + W, y0 + H))
a = frame.copy()
centered(ImageDraw.Draw(a), 250, "The Mighty Minis.", ImageFont.truetype(FONT["Bold"], 92), INK)
a.save(f"{out}/cierre_v2_A.png")

# Gris del set: muestra de la franja superior del cuadro, en degradado vertical suave
top = np.asarray(frame)[40:300].reshape(-1, 3).mean(0)
grad = np.linspace(1.06, 0.93, H)[:, None, None]
bg = np.clip(top[None, None, :] * grad, 0, 255).repeat(W, axis=1).astype(np.uint8)
b = Image.fromarray(bg, "RGB")

# B · logo azul + admisiones
logo = Image.open(logo_path).convert("RGBA")
lw = 560
logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
ly = 760
b.paste(logo, ((W - lw) // 2, ly), logo)
d = ImageDraw.Draw(b)
centered(d, ly + logo.height + 70, "Admisiones 2027 · Preescolar", ImageFont.truetype(FONT["Medium"], 38), INK)
centered(d, ly + logo.height + 130, "colegioamericano.edu.ec", ImageFont.truetype(FONT["Regular"], 32), INK_SOFT)
b.save(f"{out}/cierre_v2_B.png")
print("gris del set", top.round(), "logo alto", logo.height)
