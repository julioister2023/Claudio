# The Mighty Minis: notas de edición

Proyecto HyperFrames del comercial de 44 s (1080 × 1920, 24 fps).

## Estructura

- `index.html`: el corte. Tiene las 8 tomas con cortes secos, el texto "Hello! ¡Hola!" de la toma 3, la placa final (`compositions/cierre.html`), los subtítulos (`compositions/subtitulos.html`) y la mezcla (`assets/audio/mezcla.wav`).
- `assets/toma_01.mp4` … `toma_08.mp4`: las tomas ya pasadas a 12 fps "en dos", recortadas a 4, 5 o 6 s y llevadas a 1080 × 1920.
- `assets/audio/`:
  - `mezcla.wav`: master a −14 LUFS y pico ≤ −2 dBFS (medido con oversampling ×4).
  - `stem_voz.wav` y `stem_musica.wav`: la voz y la música, ya con el ducking, antes del limitador.
- `assets/fonts/`: Poppins (licencia OFL).
- `assets/gsap.min.js`: copia local; no se carga nada desde internet.

## Versión master y versión subtitulada

Los subtítulos están en el host `#subtitulos` de `index.html`:

- **Master:** agrega el atributo `data-hidden` al host.
- **Redes:** quítalo.

## Locución

- La voz es Kokoro `am_michael`, generada en local, porque la voz gratuita de HeyGen no estuvo disponible en esta sesión.
- Cada frase se generó por separado y se colocó en el tiempo de la tabla del brief. Los cortes no se movieron.
- "shh… they're little" se pasó por un vocoder LPC excitado con ruido para que suene susurrado.
- Kokoro no tiene voz de niño, así que "Hello! ¡Hola!" va como texto en pantalla.

Para cambiar la voz, reemplaza `assets/audio/mezcla.wav` por una mezcla nueva. Los tiempos de cada frase están en la tabla del brief.
