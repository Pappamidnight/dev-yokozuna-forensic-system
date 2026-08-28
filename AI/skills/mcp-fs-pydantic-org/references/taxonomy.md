# Taxonomia e Destino Logico por Tipo de Ficheiro

Este documento define o mapeamento deterministico da triagem de ficheiros de origem para o ecossistema canonico.

---

## 1. Tabela de Mapeamento Taxonomico

| Tipo de Conteudo / Extensao | Categoria Logica | Destino Canonico em Dev | Nivel de Prova |
|---|---|---|---|
| PDFs autenticados, sentencas Citius, autos | `DECISAO` / `PROVA_FISICA` | `Projects/.../01_PDFs_Oficiais` | `OFICIAL` (1.00) |
| Pecas processuais, oposicoes, recursos | `PROVA_FISICA` | `Projects/.../04_Processos_E_Pecas_Escritas` | `OFICIAL` (0.98) |
| Contratos assinados, acordos, cessoes | `FINANCEIRO` / `FACTO` | `Projects/.../03_Contratos_E_Acordos` | `ALTA` (0.95) |
| Emails, cartas registadas, comprovativos de envio | `FACTO` / `ALEGACAO` | `Projects/.../05_Correspondencia_E_Comunicacoes` | `MEDIA` (0.85) |
| Indices, MOCs Markdown, mapas | `INDICE` | `Projects/.../00_Indice_E_MOCs` | `INDICE` (0.70) |
| Minutas, rascunhos, anotacoes | `ALEGACAO` | `Projects/.../02_Minutas_E_Rascunhos` | `BAIXA` (0.25) |
| Codigo Python, scripts de automacao | `CODIGO` | `Projects/blindada-agent/` ou `AI/` | N/A |
| Modelos Pydantic, validadores | `CODIGO` | `Backend/pydantic-ai/` | N/A |
| Relatorios de auditoria e JSONL | `CONFIG` / `INDICE` | `Projects/.../_index/` | N/A |
