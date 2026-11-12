# Protocolo del tablero "The Office"

Toda skill de la oficina reporta su trabajo en el tablero del director:
https://claude.ai/artifact/GBpdy6epsKVRRBBtTBvd1M

- **Slug del tablero:** `7afbe00b-1a1c-4973-9f56-bf6f4e433a0c`
- **Herramientas:** `db_write` y `db_get` del servidor `claude-artifacts`. Si no están cargadas, búscalas con ToolSearch (`db_write`).
- **Colección:** `tasks`. Un documento por encargo: `tasks/<id>`.

## 1. Al empezar: marcar "Trabajando"
Antes de hacer cualquier otra cosa:

1. Obtén la hora actual en milisegundos: `date +%s%3N`. Ese valor es `AHORA`.
2. Crea el id: `<agentId>-<AAAAMMDD-HHMMSS>` con la hora de Guayaquil (`TZ=America/Guayaquil date +%Y%m%d-%H%M%S`). Ejemplo: `estratega-20261116-073000`.
3. Escribe el documento con `db_write`, op `set`, path `tasks/<id>`, **sin** `ifVersion`:

```json
{
  "agentId": "<asistente | estratega | analista | presupuesto>",
  "title": "<título corto del encargo, máx. 80 caracteres>",
  "brief": "<el encargo completo: lo que pidió el director o, si es programado, la tarea del día>",
  "attachments": [],
  "status": "trabajando",
  "version": 0,
  "deliverable": "",
  "feedback": "",
  "previous": null,
  "createdAt": AHORA,
  "updatedAt": AHORA,
  "approvedAt": null,
  "error": null,
  "source": "skill",
  "log": [{ "at": AHORA, "what": "Empezó a trabajar" }]
}
```

4. Guarda el `version` que devuelve `db_write`: lo necesitas para el paso final.

## 2. Al terminar: dejar la entrega en "Para revisar"
1. Toma `AHORA` otra vez con `date +%s%3N`.
2. `db_write`, op `update`, path `tasks/<id>`, `ifVersion` = la versión guardada:

```json
{
  "status": "revision",
  "deliverable": "<entrega completa en Markdown>",
  "version": 1,
  "updatedAt": AHORA,
  "log": [{ "at": <AHORA del inicio>, "what": "Empezó a trabajar" }, { "at": AHORA, "what": "Entregó la versión 1" }]
}
```

3. Si la escritura falla porque cambió la versión, lee el documento con `db_get`. Si el director ya lo borró, créalo de nuevo con `set`. Si no, reintenta el `update` una vez con la versión nueva.

### Formato de la entrega (`deliverable`)
- Markdown, sin preámbulo ni despedida.
- Empieza con `## Para aprobar`: una lista numerada y corta de las decisiones del director.
- Después va la entrega completa, con encabezados `##` y tablas cuando ayuden.
- Si faltan datos, termina con `## Datos que necesito`.
- Máximo unos 150 000 caracteres. Si es más largo, resume y deja el detalle en un Google Doc enlazado.

## 3. Si algo sale mal
No dejes el encargo colgado en "Trabajando". Haz un `update` con:

```json
{ "status": "error", "error": "<qué falló, en una línea>", "updatedAt": AHORA }
```

El director verá **Reintentar** en el tablero.

## 4. Rehacer con cambios
Si el director te pide rehacer una entrega del tablero (te da el id, o el título para que lo busques con `db_query`):

1. `db_get` en `tasks/<id>`. Toma `deliverable`, `version` y el `feedback`, o los cambios que te diga.
2. `update` con `{"status": "cambios", "feedback": "<cambios>", "previous": <deliverable actual>, "updatedAt": AHORA}`.
3. Rehaz la entrega completa aplicando los cambios.
4. `update` con `{"status": "revision", "deliverable": <nueva>, "version": <version + 1>, "previous": null, "updatedAt": AHORA}`. Empieza "Para aprobar" con una línea que diga qué cambiaste.

## 5. Si el tablero no está disponible
Si no tienes las herramientas `db_write` y `db_get`, dilo al inicio de tu respuesta y entrega el trabajo en el chat con el mismo formato. Nunca digas que lo dejaste en el tablero si no fue así.
