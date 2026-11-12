# Oficina de IA – Marketing, Colegio Americano de Guayaquil

Cuatro agentes (skills de Claude Code) trabajan para el **Coordinador de Marketing (director)**.
**Regla de oro: nada sale sin la aprobación del director.** Los agentes solo producen borradores. Ver [`reglas-del-director.md`](reglas-del-director.md).

## Los agentes

| # | Agente | Skill | Tipo | Horario (hora de Guayaquil) | Entrega |
|---|---|---|---|---|---|
| 1 | 📬 Asistente de Coordinación | [`asistente-coordinacion`](../.claude/skills/asistente-coordinacion/SKILL.md) | Programado + chat | Lun–Vie 7:00 | Correos clasificados con borradores en Gmail, agenda de coberturas, briefs para filmmaker y diseñadora |
| 2 | 🎬 Estratega de Contenido | [`estratega-contenido`](../.claude/skills/estratega-contenido/SKILL.md) | Programado + chat | Lunes 7:30 | Calendario semanal por red, 3 guiones, copies, briefs de producción |
| 3 | 📊 Analista de Pauta y KPIs | [`analista-pauta-kpis`](../.claude/skills/analista-pauta-kpis/SKILL.md) | Programado | Lun–Vie 8:00 (alertas) · Lunes (semanal) · Día 1 (mensual) | Alertas, formato de KPIs pre-llenado, recomendaciones, reporte para dirección |
| 4 | 💰 Control de Presupuesto | [`control-presupuesto`](../.claude/skills/control-presupuesto/SKILL.md) | Programado + chat | Viernes 15:00 · Último día hábil del mes | Semáforo por partida, proyección, borradores de órdenes de compra |

Al empezar, cada skill marca su encargo como **Trabajando** en el tablero; al terminar, deja la entrega en **Para revisar** ([`protocolo-tablero.md`](protocolo-tablero.md)).

## Rutina del director

| Cuándo | Qué revisa | Tiempo |
|---|---|---|
| Diario, 7:30–8:15 | Resumen del Asistente y alerta de pauta | 15 min |
| Lunes | Plan de contenido y reporte de KPIs | 30 min |
| Viernes | Corte de presupuesto y órdenes de compra | 10 min |
| Antes de publicar | Visto bueno final de cada pieza (👦 autorización de menores) | — |

## Cómo usarlos
- **Desde el tablero:** escribe en la caja del agente y pulsa Encargar.
- **Desde Claude Code** (sobre este repositorio), con la skill por nombre:
  - `/estratega-contenido guion de Reel para la casa abierta del sábado`
  - `/control-presupuesto orden de compra para la imprenta`
  - O en lenguaje natural: "revisa mis correos" activa el asistente-coordinacion.
- **Programados:** las tareas programadas invocan la skill a su hora.

## Puesta en marcha (checklist)
- [x] Definir los 4 agentes y las reglas
- [ ] Conectar **Gmail** y **Google Calendar** en claude.ai → Conectores
- [ ] Conectar un conector de pauta de **solo lectura** para Meta, Google y TikTok Ads (p. ej. Windsor.ai o Supermetrics)
- [ ] Pegar en `config.md` los enlaces de la hoja de KPIs, la hoja de presupuesto y el modelo de orden de compra
- [ ] Completar los datos del equipo y los umbrales de alerta en `config.md`
- [ ] Activar las tareas programadas

## Tablero "The Office"
Tablero en claude.ai con los 4 agentes, entregas para revisar (Aprobar / Pedir cambios) y pizarrón: https://claude.ai/artifact/GBpdy6epsKVRRBBtTBvd1M
Código: [`the-office/index.html`](the-office/index.html). Los agentes y encargos viven en su base de datos (`agents/*`, `tasks/*`).
