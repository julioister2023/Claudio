# Edición de "The Mighty Minis" — Colegio Americano de Guayaquil

Arma el comercial final de admisiones de 44 segundos, en vertical, a partir de las 8 tomas de plastilina que están en `clips/`. Usa HyperFrames en local.

El estilo es el del comercial de Apple "The Mighty Mac mini":
- set gris limpio,
- una mano real que deja el producto al centro,
- cámara fija,
- el producto se transforma en plastilina con cada beneficio,
- un narrador con humor seco,
- un remate cómico,
- y una placa final minimalista.

Aquí el "producto" es el Mini: un niño de preescolar de plastilina con el suéter rojo del uniforme del CAG.

## Reglas de trabajo

- Trabaja todo en local, con los archivos de esta carpeta. No uses URLs remotas para clips, audio, logo ni fuentes. Un intento anterior con el agente en la nube de HeyGen falló por eso: solo cargó la primera toma y el resto salió azul.
- Usa las skills de HyperFrames. Si no están instaladas, instálalas con `npx skills add heygen-com/hyperframes`.
- Crea el proyecto en `./edicion` con `npx hyperframes init edicion`.
- Mientras escribes, corre `npx hyperframes lint`. Antes de renderizar, corre `npx hyperframes check --json` y corrige todo lo que salga. No uses `validate` ni `inspect`: están obsoletos.
- No des el trabajo por terminado sin mostrarme capturas.
- Si estás en Claude Code en la nube, sigue también la sección "En la nube", al final.

## Material de esta carpeta

- **Clips:** `clips/toma_01_llega.mp4` a `clips/toma_08_siesta.mp4`. Son de 1080 × 1916 a 24 fps. Su audio no se usa.
- **Música:** `musica/mighty_minis_musica_120bpm.wav`. Es una pista original, libre de derechos, a 120 BPM, compuesta a la medida de estos cortes: 48 kHz, estéreo, 44,0 s, nivelada a −16 LUFS. Ya trae sus efectos (golpes y el whoosh del despegue), así que no agregues efectos extra salvo que te los pida.
- **Logo:** `marca/logo_CAG_horizontal_azul.png`, ya teñido de #001BB7 y con fondo transparente. La versión blanca original está en `marca/logo_CAG_horizontal_blanco.png`.
- **Fuente:** Poppins Regular, Medium y Bold en `fuentes/`, con su licencia OFL. Cópialas a `edicion/assets/fonts/` y cárgalas con @font-face. No uses Monument Extended: la copia que tengo es de uso personal.
- **Referencias del cierre:** `referencias/cierre_A_titulo.png` y `referencias/cierre_B_logo.png` muestran cómo deben verse las dos placas finales.
- **Previa:** `previa/mighty_minis_previa_con_musica.mp4` es un armado rápido sin voz, con los cortes, el efecto stop-motion, la música y el cierre. Úsala como guía de ritmo.

## El corte

Formato: 1080 × 1920, 24 fps, 44,0 segundos exactos, cortes secos y sin transiciones.

| Toma | Archivo | Entra (s) | Sale (s) | Momento clave (tiempo absoluto) |
| --- | --- | --- | --- | --- |
| 1 | toma_01_llega.mp4 | 0,0 | 4,0 | La mano deja al Mini; aterriza ≈ 1,25 s |
| 2 | toma_02_mochila.mp4 | 4,0 | 8,0 | La mano le pone la mochila ≈ 5,25 s |
| 3 | toma_03_hola.mp4 | 8,0 | 12,0 | Saluda con la mano |
| 4 | toma_04_musculos.mp4 | 12,0 | 17,0 | Le salen los músculos ≈ 13,0 s; posa ≈ 15,0 s |
| 5 | toma_05_carro.mp4 | 17,0 | 23,0 | El carro arranca ≈ 19,25 s y se estaciona solo ≈ 21,5 s |
| 6 | toma_06_manos.mp4 | 23,0 | 28,0 | Le brotan brazos ocupados entre 23,25 y 24,5 s |
| 7 | toma_07_despegue.mp4 | 28,0 | 34,0 | Despega ≈ 30,25 s; el fondo se vuelve cielo azul oscuro ≈ 31 s; llega al cielo ≈ 32,75 s |
| 8 | toma_08_siesta.mp4 | 34,0 | 40,0 | Baja con la estrella, bosteza ≈ 36,8 s y se duerme ≈ 39 s |
| Cierre | — | 40,0 | 44,0 | Placas finales |

Los momentos clave salen de medir el movimiento en cada clip.

Cada clip dura un cuadro de más (4,04, 5,04 o 6,04 s). Recórtalo a 4, 5 o 6 s exactos y escálalo a 1080 × 1920 llenando el cuadro; sobran 4 px de alto.

## Efecto stop-motion

Antes de componer, pasa cada clip a 12 cuadros por segundo "en dos", es decir, cada cuadro dura dos. Así se siente plastilina animada a mano. Ejemplo para la toma 1:

```
ffmpeg -i clips/toma_01_llega.mp4 -t 4 -vf "fps=12,fps=24,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" -an -c:v libx264 -crf 16 -pix_fmt yuv420p edicion/assets/toma_01.mp4
```

Repite lo mismo con las demás tomas, usando `-t 5` o `-t 6` según la tabla. En la composición usa esas versiones procesadas.

## Estilo Apple: reglas

- Las tomas cuentan la historia. No pongas nada encima: ni stickers, ni emojis, ni barras de progreso, ni marcos, ni zooms, ni transiciones.
- No apliques gradación de color ni filtros: las tomas van tal como vienen.
- La tipografía es mínima y centrada, con mucho aire alrededor. Nunca lleva cajas ni píldoras detrás.
- La paleta es el gris del set, una tinta casi negra (#1D1D1F) y el azul del CAG (#001BB7), este último solo en el logo.

## Locución (en inglés americano)

El tono es el de un narrador de Apple: cálido, juguetón, con humor seco y pausas cómicas. La última línea va susurrada.

| Tiempo (s) | Línea |
| --- | --- |
| 0,2–3,6 | Say hello to the newest student at CAG. |
| 4,2–7,4 | And their brand-new backpack. Fully loaded. |
| 8,3–9,5 | (Lo dice el Mini, con voz de niño) Hello! ¡Hola! |
| 9,8–11,6 | Two languages? Obviously. |
| 12,2–16,6 | Add a little sport… and they get strong. Like, really strong. |
| 17,3–22,8 | Add robotics, and they'll build a car that drives itself. … And parks itself. ("And parks itself" cae justo cuando se estaciona, ≈ 21,6 s) |
| 23,3–27,6 | IB, Cambridge, Dual Program… they'll need a few extra hands. |
| 28,3–33,6 | Before you know it, they're reaching for the stars. Woohoo! ("Woohoo!" ≈ 32,5 s) |
| 34,4–39,5 | But still, you know… (susurrando) shh… they're little. |
| 40,0–44,0 | Sin locución |

- Si encuentras un archivo `locucion.wav` en esta carpeta, úsalo y transcríbelo con `npx hyperframes transcribe` para sacar los tiempos de cada palabra.
- Si no hay archivo, genera la voz con la skill `/media-use` usando Voice Turbo de HeyGen; con la cuenta gratis alcanza, porque son unos 40 s. Antes, revisa con `npx hyperframes auth status` si inicié sesión. Si no: en mi computadora, pídeme que escriba `! npx hyperframes auth login`; en la nube, inicia sesión tú como dice la sección "En la nube". En los dos casos, espera a que te confirme.
- Ajusta cada línea a la tabla, moviendo solo la voz, nunca los cortes.
- Si no consigues una voz de niño que suene bien para "Hello! ¡Hola!", deja esa línea solo como texto en pantalla, pequeño y centrado.

## Música

El anuncio de Apple usa "Pili Pili" de Polo & Pan. No la uses, porque tiene derechos.

Usa `musica/mighty_minis_musica_120bpm.wav` desde el segundo 0,0, sin moverla. Ya trae los golpes compuestos en estos momentos:
- 1,25 · 5,25 · 13,0 · 15,0 · 17,0 · 19,25 · 20,5 · 21,5,
- de 23,25 a 24,5 (los brazos),
- una subida de 28 a 30 y el despegue en 30,0,
- un corte en seco a silencio en 34,0,
- una nana de 35 a 40,
- y los golpes del cierre en 40,0 y 42,0.

Si te digo que esta pista no me gusta, busca otra en el catálogo de HeyGen con `/media-use` (necesita la misma sesión de HeyGen). Tiene que tener ese espíritu: electro-pop alegre y juguetón, entre 110 y 120 BPM. Edítala a los cortes con `npx hyperframes beats`.

Mezcla:
- Baja la música entre 8 y 10 dB mientras habla la voz (ducking) y súbela en las pausas.
- El master final va a −14 LUFS integrados, con pico real de −1 dBTP o menos.
- Mide el render con `npx hyperframes audio <video> --json`: que haya sonido, que los golpes caigan con la imagen y que el volumen esté en rango.

## Placa final (40,0–44,0 s), como la de Apple

- Fondo #ECEEF1, un gris muy claro, con corte seco desde la toma 8.
- De 40,0 a 42,0: "The Mighty Minis." centrado, en Poppins Bold de unos 92 px y color #1D1D1F. Aparece de golpe con el golpe de la música.
- De 42,0 a 44,0, entrando con el acorde final:
  - `marca/logo_CAG_horizontal_azul.png`, de unos 560 px de ancho y centrado;
  - debajo, "Admisiones 2027 · Preescolar" en Poppins Medium 38 px, color #1D1D1F;
  - y "colegioamericano.edu.ec" en Poppins Regular 32 px, color #3A4060.
- Todo va dentro de la franja segura vertical, entre y = 168 px y y = 1330 px. Guíate por `referencias/`.

## Subtítulos

- **Versión master:** sin subtítulos, como en Apple.
- **Versión para redes:** subtítulos en español con estas reglas:
  - máximo dos líneas, de unos 30 caracteres cada una;
  - Poppins Medium 42 px en #1D1D1F, sin caja;
  - arriba, centrados en y ≈ 265 px (entre y = 200 y y = 330), sobre la cabeza del niño. No los pongas a media altura: entre y ≈ 1100 y 1330 tapan la cintura y las manos del niño en casi todas las tomas;
  - si en alguna captura un subtítulo toca al niño o la estrella grande de la toma 7, mueve solo ese al lugar libre más cercano, siempre entre y = 168 y y = 1330;
  - en la toma 7, desde que el fondo se vuelve cielo azul oscuro (≈ 31 s), van en blanco;
  - entrada y salida de 0,1 s;
  - sincronizados con la locución real.

  El texto es este:
  - Les presentamos al estudiante más nuevo del CAG.
  - Y su mochila nueva. Bien cargadita.
  - Hello! ¡Hola!
  - ¿Dos idiomas? Obvio.
  - Un poquito de deporte… / …y se pone fuerte. Pero fuerte, fuerte.
  - Un poquito de robótica… / …y se arma un carro que se maneja solo. / Y se parquea solo.
  - IB, Cambridge, Programa Dual… / …va a necesitar unas manitos extra.
  - Y cuando menos piensas… / …ya está alcanzando las estrellas. / ¡Wiii!
  - Eso sí… / shhh… sigue siendo chiquito.

## Entregables (en `./entregables`)

1. `mighty_minis_master.mp4`: sin subtítulos.
2. `mighty_minis_subtitulado.mp4`: con subtítulos en español.
3. `mighty_minis_mezcla.wav`: voz más música, y además los stems por separado.
4. El proyecto en `./edicion`, listo para seguir editando.
5. Opcional, si todo lo anterior sale bien: `mighty_minis_15s.mp4` para pauta. Usa estos tramos del corte largo: la toma 1 de 0 a 3 s, la toma 4 de 13 a 16 s, la toma 7 de 29,5 a 33,5 s, la toma 8 de 37 a 40 s y la placa del logo durante 2 s. Ajusta la música a esos cortes.

## Control de calidad antes de entregar

- El video dura exactamente 44,0 s, en 1080 × 1920 y a 24 fps.
- Saca capturas del render en 1,25 · 5,25 · 9,0 · 13,0 · 15,0 · 21,5 · 30,25 · 33,0 · 34,0 · 39,0 · 40,5 y 43,0 s, de las dos versiones.
- El volumen medido da −14 LUFS ±1 y el pico real queda en −1 dBTP o menos. Aclárame que lo mediste, no que lo escuchaste.
- No hay ningún texto debajo de y = 1330 px.
- Al terminar, dime qué decidiste en cada punto y muéstrame las capturas.

## En la nube

Esto aplica si trabajas en Claude Code en la nube y yo te escribo desde el celular.

- Yo no tengo terminal: corre tú todos los comandos.
- Node 22 ya viene instalado. Instala FFmpeg con `apt-get update && apt-get install -y ffmpeg`.
- Instala las skills de HyperFrames en este repositorio. Si después no aparecen como skills en esta sesión, lee sus `SKILL.md` directamente y síguelos.
- Para iniciar sesión en HeyGen, corre `npx hyperframes auth login --device`. Pásame el enlace y el código, y espera a que te diga que ya lo aprobé. Si la red no deja llegar a HeyGen, avísame: tengo que cambiar el acceso a internet del entorno a Full.
- Corre los renders en segundo plano y revisa su avance, porque un comando en primer plano se corta a los 10 minutos.
- No subas `node_modules` ni archivos de más de 90 MB.
- Al terminar, deja los entregables en `entregables/`, haz commit y push de tu rama. Al final de tu mensaje, dame un enlace de descarga directa para cada archivo, con este formato: `https://github.com/<dueño>/<repo>/raw/<rama>/<ruta del archivo en el repo>`.
