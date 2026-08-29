---
created: '2026-05-03T03:17:22.794066+00:00'
links: []
priority: 3
processo: '10153'
status: pendente
tags:
- aiq/processo
- aiq/execucao
tribunal: Unicre
type: processo
valor: EUR 82.000
---

# 10153

**Tipo:** execucao
**Estado:** pendente
**Valor:** EUR 82.000
**Tribunal:** Unicre

## Documentos

```dataview
TABLE tipo_doc AS "Tipo", date(ingested_at) AS "Data"
FROM "aiq-system"
WHERE type = "documento" AND processo = "proc_10153"
SORT ingested_at DESC
```

## Timeline

```dataview
TABLE event_type AS "Evento", date(ts) AS "Data"
FROM "aiq-system"
WHERE type = "evento" AND processo = "proc_10153"
SORT ts ASC
```
