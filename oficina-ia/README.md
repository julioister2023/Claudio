# Oficina de IA – Marketing, Colegio Americano de Guayaquil

Cuatro agentes trabajan para el **Coordinador de Marketing (director)**.
**Regla de oro: nada sale sin la aprobación del director.** Los agentes solo producen borradores. Ver [`reglas-del-director.md`](reglas-del-director.md).

## Los agentes

| # | Agente | Archivo | Tipo | Horario (hora de Guayaquil) | Entrega |
|---|---|---|---|---|---|
| 1 | 📬 Asistente de Coordinación | [`asistente-coordinacion.md`](../.claude/agents/asistente-coordinacion.md) | Programado + chat | Lun–Vie 7:00 | Correos clasificados con borradores en Gmail, agenda de coberturas, briefs para filmmaker y diseñadora |
| 2 | 🎬 Estratega de Contenido | [`estratega-contenido.md`](../.claude/agents/estratega-contenido.md) | Programado + chat | Lunes 7:30 | Calendario semanal por red, 3 guiones, copies, briefs de producción |
| 3 | 📊 Analista de Pauta y KPIs | [`analista-pauta-kpis.md`](../.claude/agents/analista-pauta-kpis.md) | Programado | Lun–Vie 8:00 (alertas) · Lunes (semanal) · Día 1 (mensual) | Alertas, formato de KPIs pre-llenado, recomendaciones, reporte para dirección |
| 4 | 💰 Control de Presupuesto | [`control-presupuesto.md`](../.claude/agents/control-presupuesto.md) | Programado + chat | Viernes 15:00 · Último día hábil del mes | Semáforo por partida, proyección, borradores de órdenes de compra |

Todos los entregables llegan a la carpeta **Bandeja de aprobación** de Google Drive.

## Rutina del director

| Cuándo | Qué revisa | Tiempo |
|---|---|---|
| Diario, 7:30–8:15 | Resumen del Asistente y alerta de pauta | 15 min |
| Lunes | Plan de contenido y reporte de KPIs | 30 min |
| Viernes | Corte de presupuesto y órdenes de compra | 10 min |
| Antes de publicar | Visto bueno final de cada pieza (👦 autorización de menores) | — |

## Cómo usarlos por chat
En una sesión de Claude Code sobre este repositorio, pídelo por nombre:
- "Usa el **estratega-contenido** para un guion de Reel sobre la casa abierta del sábado"
- "Pídele al **control-presupuesto** una orden de compra para la imprenta"

## Puesta en marcha (checklist)
- [x] Definir los 4 agentes y las reglas
- [ ] Conectar **Gmail** y **Google Calendar** en claude.ai → Conectores
- [ ] Conectar un conector de pauta de **solo lectura** para Meta, Google y TikTok Ads (p. ej. Windsor.ai o Supermetrics)
- [ ] Crear la carpeta **Bandeja de aprobación** en Drive y pegar su enlace en [`config.md`](config.md)
- [ ] Pegar en `config.md` los enlaces de la hoja de KPIs, la hoja de presupuesto y el modelo de orden de compra
- [ ] Completar los datos del equipo y los umbrales de alerta en `config.md`
- [ ] Activar las tareas programadas
