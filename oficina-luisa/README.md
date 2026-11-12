# La Oficina de Luisa

Oficina de agentes de IA para la mesa de provincias de un noticiero de TV de Ecuador.
**Luisa es la jefa: nada sale sin su aprobación** ([`reglas.md`](reglas.md)).

**Tablero:** https://claude.ai/artifact/CXBJGzQ4Y7NUkFNfEg6PNK
Es una sala de redacción en pixel art: cada agente teclea cuando trabaja, hace fila en el escritorio de Luisa cuando tiene algo para revisar y descansa cuando está libre. Tiene modo demo (`#demo`).

## El equipo

| Agente | Hace | Cuándo | Skill |
|---|---|---|---|
| **Aldowise** | Noticias de provincias, verificadas, de interés nacional | Todos los días 5:45, con aviso al teléfono | [`aldowise-noticias`](../.claude/skills/aldowise-noticias/SKILL.md) |
| **Macarena** | Temas de color atemporales: fiestas, tradiciones, lugares, curiosidades | A pedido | [`macarena-color`](../.claude/skills/macarena-color/SKILL.md) |
| **Zendaya** | Temas para Ecuaterra: naturaleza visualmente impactante | A pedido | [`zendaya-ecuaterra`](../.claude/skills/zendaya-ecuaterra/SKILL.md) |
| **Niño Moi** | Revisa los textos de corresponsales; no procesa si faltan datos, salvo autorización | A pedido | [`nino-moi-revisor`](../.claude/skills/nino-moi-revisor/SKILL.md) |
| **Mamau** | Compara los reportes de corresponsales con el presupuesto; informe trimestral | A pedido · trimestral automático | [`mamau-liquidaciones`](../.claude/skills/mamau-liquidaciones/SKILL.md) |

## Dos formas de trabajar
- **Desde el tablero** (celular o computadora): Luisa toca a un agente, escribe o adjunta (PDF, Word, Excel o foto) y pulsa Encargar. El agente trabaja ahí mismo, sin internet.
- **Con internet y conectores** (Claude Code o tareas programadas): las skills buscan en la web, leen la hoja de presupuesto y dejan la entrega en el tablero.

## Biblioteca de estilos (Niño Moi)
En el tablero, sección "Biblioteca de estilos": Luisa pega o sube textos que ya salieron al aire, marcando su tipo (Ecuaterra, crónica, leída, en vivo…). Niño Moi los usa para imitar el estilo de cada formato. Lo ideal son 3 a 5 ejemplos por tipo.

## Pendiente
- [ ] Cargar textos de ejemplo en la biblioteca de Niño Moi.
- [ ] Completar la provincia de cada corresponsal en [`config.md`](config.md).
- [ ] Luisa: iniciar sesión con esta cuenta en la app de Claude de su teléfono para recibir los avisos.
- [ ] Opcional: una cuenta de la API de X para que Aldowise lea X directamente (hoy usa búsqueda web).

Detalles técnicos: [`protocolo-tablero.md`](protocolo-tablero.md) · [`config.md`](config.md)
