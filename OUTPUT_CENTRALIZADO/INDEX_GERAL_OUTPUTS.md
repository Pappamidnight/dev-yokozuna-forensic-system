# Painel Geral de Outputs Centralizados - Dev Yokozuna

**Ultima Atualizacao**: 2026-08-28 07:05:05  
**Pasta Central**: `C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO`  
**Status do Workflow**: `APPROVED`  

---

## 1. Relatorios de Auditoria e Qualidade (`01_INDEX_E_RELATORIOS/`)

| Ficheiro | Descricao | Status / Score |
|---|---|---|
| [`frozen_judge_report.json`](file:///C:/Users/Yokozuna/Dev/OUTPUT_CENTRALIZADO/01_INDEX_E_RELATORIOS/frozen_judge_report.json) | Relatorio do Frozen Judge v2.5 | **100/100 [PASS]** |
| [`workflow_controller_status.json`](file:///C:/Users/Yokozuna/Dev/OUTPUT_CENTRALIZADO/01_INDEX_E_RELATORIOS/workflow_controller_status.json) | Controlador de Entregaveis | **APPROVED** |
| [`eval_report.json`](file:///C:/Users/Yokozuna/Dev/OUTPUT_CENTRALIZADO/01_INDEX_E_RELATORIOS/eval_report.json) | Avaliacao Golden Dataset | **PASS (100% F1)** |
| [`quality_factuality_report.json`](file:///C:/Users/Yokozuna/Dev/OUTPUT_CENTRALIZADO/01_INDEX_E_RELATORIOS/quality_factuality_report.json) | Agente de Factualidade | **95.00% [PASS]** |
| [`sanitization_report.json`](file:///C:/Users/Yokozuna/Dev/OUTPUT_CENTRALIZADO/01_INDEX_E_RELATORIOS/sanitization_report.json) | Higienizacao de Estrutura | **COMPLETED** |
| [`error_remediation_report.json`](file:///C:/Users/Yokozuna/Dev/OUTPUT_CENTRALIZADO/01_INDEX_E_RELATORIOS/error_remediation_report.json) | Auto-Correcao de Erros | **HEALTHY** |
| [`relevance_matrix.json`](file:///C:/Users/Yokozuna/Dev/OUTPUT_CENTRALIZADO/01_INDEX_E_RELATORIOS/relevance_matrix.json) | Matriz Probatoria (0.00 a 1.00) | **47.698 Factos** |
| [`pipeline_report.json`](file:///C:/Users/Yokozuna/Dev/OUTPUT_CENTRALIZADO/01_INDEX_E_RELATORIOS/pipeline_report.json) | Scanner dos 6 Agentes | **COMPLETED** |
| [`tree_dirs.md`](file:///C:/Users/Yokozuna/Dev/OUTPUT_CENTRALIZADO/01_INDEX_E_RELATORIOS/tree_dirs.md) | Mapa Estrutural do Acervo | **Atualizado** |

---

## 2. Dados Estruturados e Bases JSONL (`02_DADOS_ESTRUTURADOS/`)

- [`atos_processuais.jsonl`](file:///C:/Users/Yokozuna/Dev/OUTPUT_CENTRALIZADO/02_DADOS_ESTRUTURADOS/atos_processuais.jsonl): Atos processuais normalizados CPC.
- [`pontos_factuais.jsonl`](file:///C:/Users/Yokozuna/Dev/OUTPUT_CENTRALIZADO/02_DADOS_ESTRUTURADOS/pontos_factuais.jsonl): Factos provados e alegacoes unilaterais.
- [`cronologia_mestre.jsonl`](file:///C:/Users/Yokozuna/Dev/OUTPUT_CENTRALIZADO/02_DADOS_ESTRUTURADOS/cronologia_mestre.jsonl): Cronologia mestre ISO-8601 ordenada.
- [`audit_ledger.jsonl`](file:///C:/Users/Yokozuna/Dev/OUTPUT_CENTRALIZADO/02_DADOS_ESTRUTURADOS/audit_ledger.jsonl): Ledger criptografico de auditoria.
- [`error_remediation.jsonl`](file:///C:/Users/Yokozuna/Dev/OUTPUT_CENTRALIZADO/02_DADOS_ESTRUTURADOS/error_remediation.jsonl): Registo historico de auto-correcoes.

---

## 3. Logs de Auditoria e Execucao (`03_LOGS_AUDITORIA/`)

- [`errors.log`](file:///C:/Users/Yokozuna/Dev/OUTPUT_CENTRALIZADO/03_LOGS_AUDITORIA/errors.log): Registo central de erros e excecoes.
- [`auto_system.log`](file:///C:/Users/Yokozuna/Dev/OUTPUT_CENTRALIZADO/03_LOGS_AUDITORIA/auto_system.log): Log de eventos do daemon continuo.
- [`session_15min.log`](file:///C:/Users/Yokozuna/Dev/OUTPUT_CENTRALIZADO/03_LOGS_AUDITORIA/session_15min.log): Log da sessao intensiva de 15 minutos.

---

## 4. Documentos Citius e Pecas Oficiais (`04_DOCUMENTOS_CITIUS_E_PECAS/`)

- Destinado a pecas processuais finais, articulados juridicos e manifestos Citius gerados pelo pipeline.
