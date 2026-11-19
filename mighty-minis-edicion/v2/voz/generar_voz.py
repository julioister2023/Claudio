"""Genera la locución v2 con Kokoro-82M (Apache 2.0) y la verifica con faster-whisper.

Lee guion.json y escribe en out/:
  <id>__<voz>__<velocidad>.wav  (24 kHz, mono)
  reporte.json                  (duración y transcripción de cada archivo)
"""
import json
import pathlib

import numpy as np
import soundfile as sf
from kokoro import KPipeline

AQUI = pathlib.Path(__file__).resolve().parent
SALIDA = AQUI / "out"
SALIDA.mkdir(exist_ok=True)

guion = json.loads((AQUI / "guion.json").read_text(encoding="utf-8"))
pipelines = {}
archivos = []

for linea in guion["lineas"]:
    lang = linea["lang"]
    if lang not in pipelines:
        pipelines[lang] = KPipeline(lang_code=lang, repo_id="hexgrad/Kokoro-82M")
    for vel in guion["velocidades"]:
        partes = [audio for _, _, audio in pipelines[lang](linea["texto"], voice=linea["voz"], speed=vel)]
        audio = np.concatenate([np.asarray(p, dtype=np.float32) for p in partes])
        nombre = f"{linea['id']}__{linea['voz']}__{vel:.2f}.wav"
        sf.write(SALIDA / nombre, audio, 24000)
        archivos.append({"archivo": nombre, "id": linea["id"], "voz": linea["voz"], "velocidad": vel,
                         "lang": lang, "duracion_s": round(len(audio) / 24000, 3)})
        print("ok", nombre, archivos[-1]["duracion_s"], "s", flush=True)

# Voz del Mini: subir tono y formantes para que suene a niño de 4 años.
import subprocess
for a in list(archivos):
    if a["id"].startswith("k"):
        nino = a["archivo"].replace(".wav", "__nino.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SALIDA / a["archivo"]),
                        "-af", "rubberband=pitch=1.32:formant=shifted", "-ar", "24000", str(SALIDA / nino)], check=True)
        archivos.append({**a, "archivo": nino, "nino": True})

# Verificación: transcribir cada archivo para confirmar que se entiende.
from faster_whisper import WhisperModel

modelo = WhisperModel("small", device="cpu", compute_type="int8")
for a in archivos:
    segmentos, _ = modelo.transcribe(str(SALIDA / a["archivo"]), language="es" if a["lang"] == "e" else "en",
                                     word_timestamps=True)
    palabras = []
    texto = []
    for s in segmentos:
        texto.append(s.text.strip())
        for w in s.words or []:
            palabras.append({"w": w.word.strip(), "ini": round(w.start, 2), "fin": round(w.end, 2)})
    a["transcripcion"] = " ".join(texto)
    a["palabras"] = palabras
    print(a["archivo"], "->", a["transcripcion"], flush=True)

(SALIDA / "reporte.json").write_text(json.dumps(archivos, ensure_ascii=False, indent=1), encoding="utf-8")
