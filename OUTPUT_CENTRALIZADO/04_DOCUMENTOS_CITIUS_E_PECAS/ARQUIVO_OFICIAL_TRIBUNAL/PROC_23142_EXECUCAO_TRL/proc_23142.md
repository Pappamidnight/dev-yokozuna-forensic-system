---
created: '2026-05-03T03:17:22.793065+00:00'
links: []
priority: 2
processo: '23142'
status: ganho
tags:
- aiq/processo
- aiq/execucao
tribunal: Centenario
type: processo
valor: EUR 180.000
---

# 23142

**Tipo:** execucao
**Estado:** ganho
**Valor:** EUR 180.000
**Tribunal:** Centenario

## Documentos

```dataview
TABLE tipo_doc AS "Tipo", date(ingested_at) AS "Data"
FROM "aiq-system"
WHERE type = "documento" AND processo = "proc_23142"
SORT ingested_at DESC
```

## Timeline

```dataview
TABLE event_type AS "Evento", date(ts) AS "Data"
FROM "aiq-system"
WHERE type = "evento" AND processo = "proc_23142"
SORT ts ASC
```
