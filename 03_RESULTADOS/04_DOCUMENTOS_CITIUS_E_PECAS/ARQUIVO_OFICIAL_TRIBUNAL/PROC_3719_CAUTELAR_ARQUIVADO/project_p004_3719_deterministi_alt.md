---
name: project-p004-3719-deterministic-arch
description: "P004/3719 — Arquitectura determinística, idempotente, com hooks inflexíveis, Archon harness e 6 processos paralelos"
metadata: 
  node_type: memory
  type: project
  originSessionId: 2340e883-06d1-4568-84d6-b539eb445534
---

# P004/3719 — Arquitectura Determinística

## Status
- **Fase**: PLANO pronto, aguardando aprovação para execução
- **Data início**: 2026-06-15
- **Checkpoint**: session_2026_06_15_p004_3719_architecture.md

## Objectivo
Construir sistema jurídico determinístico, idempotente e impossível de contornar para:
- Requerimento adiamento audiência processo 3719 (justo impedimento, substituição mandatário)
- 6 processos jurídicos paralelos (3719, 23142, 10153, 20203, 7620, AT)
- Ingestão massiva com classificação (liteLLM, spaCy, Tesseract, pandas)
- Observabilidade completa (audit, trace, rewind)

## Stack Técnica
- **Orquestração**: Archon harness (complementa workflow-planner)
- **LLM**: liteLLM routing (Haiku→Sonnet→Opus) — crítico desligado
- **NLP**: spaCy pt_core_news_lg
- **OCR**: Tesseract
- **Data**: pandas, data parsers (datas, números)
- **Persistência**: SQLite + NoSQL + GraphQL + FST5
- **Indexação**: pipeline_v2 (Postgres+pgvector, e5-base)

## Arquitetura

### Camada 1: Regras Imutáveis (Hooks)
```
pre_tool_call    → bloqueia ações proibidas
pre_write        → exige destino, backup, audit intent
pre_output       → valida fontes, SHA-256, guardrails, termos proibidos
post_write       → audit event + chain hash
quality_gate     → validações + testes + health check
rewind_hook      → plano reversão lógico
```

### Camada 2: Workflow Declarativo (13 estágios)
```
discover → hash → read → parse → normalize → classify → relate 
→ persist_sqlite → persist_nosql → persist_graph → index_vector 
→ review → report → quality_gate → stop
```

### Camada 3: Funções Determinísticas
- Pequenas, puras, sem side effects
- Input/output explícito
- Testáveis isoladamente
- Sem estado compartilhado
- Logs estruturados (JSON)

### Camada 4: Observabilidade
```
.kb/audit/audit.jsonl          # todas operações
.kb/trace/trace.jsonl          # eventos sequência
.kb/reports/hard_contract_review.md
.kb/reports/mission_control.json
.kb/reports/rewind_plan.json
```

## Idempotência Garantida
- **SHA-256 dedup**: bloqueia reingestão
- **Status field**: VALIDADO → CLASSIFICADO → INDEXADO
- **Upsert em SQLite**: nunca duplicate
- **Rerun seguro**: sem efeitos secundários

## 6 Processos Paralelos

| Processo | Número | Tipo | Intervenientes Chave |
|---|---|---|---|
| P_3719 | 3719/25.0T8LSB | Providência Cautelar | Nuno, Maria Teresa, Dr. Neto |
| P_23142 | 23142/22.7T8LSB | Execução Centenário | Exequente, executado, agente execução |
| P_10153 | 10153/24.7T8LSB | Embargos Unicre | Unicre, executado, tribunal |
| P_20203 | 20203/22.6T8LSB | Acção comum Unicre | Autor, réu |
| P_7620 | 7620/19.8T8LSB | Laboral Rent Exp | Trabalhador, Rent Experience |
| P_AT | 3263202001090798 | Execução Fiscal | NIF 254048382 |

## Workload (10 Fases)

| Fase | O quê | Ficheiros | Status |
|---|---|---|---|
| 1 | Audit estado | READ-ONLY | PENDING |
| 2 | Gap analysis | Comparação | PENDING |
| 3 | Contratos × 6 processos | 6 × hard_governance.yaml | PENDING |
| 4 | Workflows | core_workflow.yaml + Archon | PENDING |
| 5 | Permissões | agent_permissions.yaml | PENDING |
| 6 | Hooks | hard_hooks.yaml | PENDING |
| 7 | Schemas | 7 JSON v1.0 | PENDING |
| 8 | Observabilidade | audit/trace templates | PENDING |
| 9 | Relatório | hard_contract_review.md | PENDING |
| 10 | Aprovação | mission_control.json | PENDING |

## Riscos e Mitigações

| Risco | Impacto | Mitigação |
|---|---|---|
| Hooks bloqueadores se rules erradas | CRÍTICO | Review 3x antes apply |
| Conflito schemas × processos | ALTO | Template único parametrizado |
| Archon API incompatível | MÉDIO | Spec→test→deploy |
| Observabilidade volume | BAIXO | Streaming JSONL |
| LLM inventar factos | CRÍTICO | LLM desligado lógica crítica |

## Next Gates
1. **workflow-planner PLANO** para gerar contratos + review
2. **Aprovação utilizador** antes de execução
3. **Archon integration** e deployment

## Assessments (2026-06-15)
- Robustez: 8/10
- Determinismo: 9/10
- Idempotência: 9/10
- Completude: 5/10 (plano pronto)
- Risco: 6/10 (mitigado)

---

**Criado**: 2026-06-15
**Última actualização**: 2026-06-15
**Válido**: até revision posterior
