# Protocolo del tablero "La Oficina de Luisa"

Toda skill de la oficina reporta su trabajo en el tablero de Luisa:
https://claude.ai/artifact/CXBJGzQ4Y7NUkFNfEg6PNK

- **Slug:** `5d4b2f44-88b1-4c28-b050-b4854f61a944`
- **Herramientas:** `db_write`, `db_get` y `db_query` del servidor `claude-artifacts`. Si no están cargadas, búscalas con ToolSearch (`db_write`).
- **Colecciones:**
  - `tasks`: los encargos.
  - `estilos`: la biblioteca de Niño Moi (`tipo`, `titulo`, `texto`).
  - `agents`: los agentes.
- **agentId:** `aldowise` · `macarena` · `zendaya` · `ninomoi` · `mamau`

## 1. Al empezar: marcar "Trabajando"
Antes de cualquier otra cosa:

1. `AHORA` = `date +%s%3N`.
2. id = `<agentId>-<AAAAMMDD-HHMMSS>`, con la hora de `TZ=America/Guayaquil date +%Y%m%d-%H%M%S`.
3. `db_write`, op `set`, path `tasks/<id>`, sin `ifVersion`:

```json
{
  "agentId": "<agentId>",
  "title": "<título corto, máx. 80 caracteres>",
  "brief": "<el encargo completo>",
  "attachments": [],
  "opts": {},
  "status": "trabajando",
  "version": 0,
  "deliverable": "",
  "feedback": "",
  "previous": null,
  "createdAt": AHORA,
  "updatedAt": AHORA,
  "approvedAt": null,
  "error": null,
  "enEspera": false,
  "source": "skill",
  "log": [{ "at": AHORA, "what": "Empezó a trabajar" }]
}
```

4. Guarda el `version` que devuelve `db_write`.

## 2. Al terminar: dejar la entrega en "Para revisar"
`db_write`, op `update`, path `tasks/<id>`, `ifVersion` = la versión guardada:

```json
{
  "status": "revision",
  "deliverable": "<entrega en Markdown>",
  "version": 1,
  "enEspera": false,
  "updatedAt": AHORA,
  "log": [{ "at": <inicio>, "what": "Empezó a trabajar" }, { "at": AHORA, "what": "Entregó la versión 1" }]
}
```

- Niño Moi pone `"enEspera": true` cuando no procesó el texto por falta de datos.
- Si la escritura falla por la versión, lee el documento con `db_get` y reintenta una vez. Si el documento ya no existe, créalo de nuevo con `set`.

### Formato de la entrega
- Markdown, sin preámbulo.
- Empieza con `## Para Luisa`.
- Lo que Luisa debe revisar va resaltado con `==así==` (se ve en amarillo).
- Los enlaces van como `[texto](https://...)`.
- Máximo unos 150 000 caracteres.

## 3. Si algo sale mal
`update` con `{ "status": "error", "error": "<qué falló>", "updatedAt": AHORA }`. Luisa verá **Reintentar** en el tablero.

## 4. Rehacer con cambios
1. `db_get` en `tasks/<id>`.
2. `update` con `{ "status": "cambios", "feedback": "<cambios>", "previous": <deliverable>, "updatedAt": AHORA }`.
3. Rehaz la entrega completa.
4. `update` con `{ "status": "revision", "deliverable": <nueva>, "version": <version+1>, "previous": null, "updatedAt": AHORA }`.

## 5. Si el tablero no está disponible
Dilo al inicio y entrega en el chat con el mismo formato. Nunca digas que lo dejaste en el tablero si no fue así.
