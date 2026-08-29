---
created: '2026-05-03T03:17:22.781051+00:00'
links: []
priority: 3
processo: 3719/25.0T8LSB
status: ganho
tags:
- aiq/processo
- aiq/providencia_cautelar
tribunal: TRL
type: processo
valor: EUR 50.000
---

# 3719/25.0T8LSB

**Tipo:** providencia_cautelar
**Estado:** ganho
**Valor:** EUR 50.000
**Tribunal:** TRL

## Documentos

```dataview
TABLE tipo_doc AS "Tipo", date(ingested_at) AS "Data"
FROM "aiq-system"
WHERE type = "documento" AND processo = "proc_3719"
SORT ingested_at DESC
```

## Timeline

```dataview
TABLE event_type AS "Evento", date(ts) AS "Data"
FROM "aiq-system"
WHERE type = "evento" AND processo = "proc_3719"
SORT ts ASC
```
