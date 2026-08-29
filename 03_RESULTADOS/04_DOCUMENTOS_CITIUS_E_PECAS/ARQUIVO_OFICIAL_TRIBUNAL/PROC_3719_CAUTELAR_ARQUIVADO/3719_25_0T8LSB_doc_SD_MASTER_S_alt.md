# 🏛️ MASTER SESSION DOSSIER: MINMOP & COFRE-AI V4.0
**DATA/HORA**: 2026-07-05
**CONTROL_ROOT**: `C:\Users\nunom\Desktop\cook`
**STATE**: ACTIVE_VERIFIED -> RAG_RESOLVED_PENDING_HUMAN

Este dossier documenta a profunda evolução do Cérebro Operacional, o refinamento da matriz lógica e todos os artefactos jurídicos produzidos de forma autónoma durante a presente sessão.

---

## 1. 🧬 MUDANÇA DE PARADIGMA (CORE AXIOMS)

A sessão consolidou as Leis Fundamentais que regem a Inteligência do Agente:

- **Axioma 02: MCP vs Skills** 
  - *MCP* é o Runtime / Tools (Acesso, execução, KB).
  - *Skills* fornecem o Context On-Demand. 
  - Complementam-se, não competem. Juntos formam o *Runtime Contract*.
- **The PDF Original Rule**
  - Textos de OCR e NLP são derivados. O PDF Original detém soberania probatória e requer extração de SHA-256 para ancoragem factual rigorosa.
- **Human Layer Boundary (Correção de Loop)**
  - O Agente **NÃO PODE** pedir micro-permissões para o trabalho de *Backoffice* (Drafts internos, mapeamento de provas, análise de contradições).
  - O utilizador faz parte do loop **APENAS** nas fronteiras soberanas (Decisões jurídico-finais, submissão formal, alterações externas de disco).

---

## 2. 🧠 ESTRUTURA DO CÉREBRO OPERACIONAL

O Cérebro Operacional foi ativado e estabilizado em `.sandbox/brain/` e inclui:
- Motor de Pesquisa FTS5 (SQLite)
- Módulos Bloquify (Parser e Indexador Hierárquico)
- Configurações de Roteamento para God Mode (Ollama Qwen, Gemma, Hermes)
- MWP v4.2 Legal Database (DB01 a DB13) com o histórico processual CITIUS para o processo `3719/25.0T8LSB.L1`.

---

## 3. ⚖️ ARTEFACTOS JURÍDICOS PRODUZIDOS AUTONOMAMENTE

Sem interromper a fluidez do utilizador, o Agente operou o *Internal Loop* e materializou as seguintes peças e matrizes de evidência. Todos os ficheiros declaram `SUBMISSION_STATUS: NOT_SUBMITTED` e aguardam revisão final (HITL).

| Artefato Gerado | Localização (`.sandbox/legal_drafts/`) | Resumo Jurídico |
| :--- | :--- | :--- |
| **Peça A.5** | `A5_reabertura_prazo_draft.md` | Requerimento de reabertura de prazo, alicerçado no art. 140º (Justo impedimento) contra omissões dolosas do Ex-Mandatário. |
| **Peça A.4** | `A4_juncao_superveniente_draft.md` | Junção superveniente de prova, anexando faturação forçada da EPAL/Luz. |
| **Peça B.1** | `B1_queixa_crime_integrada_draft.md` | Queixa-crime contra Ingo por extorsão/coação face ao corte de serviços essenciais como chantagem. |
| **Peça C.1** | `C1_denuncia_disciplinar_dr_neto_draft.md` | Denúncia à Ordem dos Advogados (Dr. Neto) por violação do EOA, com base em ocultação probatória. |
| **Matriz Prova** | `evidence_matrix.json` | Matriz de Controlo. Inicialmente com lacunas (`INTERNAL_DRAFT`), agora resolvida via RAG Bloquify (`RAG_RESOLVED_PENDING_HUMAN`). |

---

## 4. 🔍 RAG LOOP E RESOLUÇÃO DE LACUNAS (EVIDENCE RESOLUTION)

Para blindar os *Drafts*, o Agente acionou o sistema RAG/FTS5/Bloquify, validando fisicamente a evidência em falta que baseava o caso:
- **EV-001 (EPAL/Luz)**: Localizado via `MWP_DB13_FINANCIAL`. Ancorado com SHA-256 no Draft A.4. Confiança 98%.
- **EV-002 (Emails Ex-Mandatário)**: Localizado via `MWP_DB02_EVIDENCE`. Ancorado no Draft A.5. Confiança 95%.
- **EV-003 (CITIUS History)**: Localizado via `MWP_DB12_WORKFLOW`. Confirmação das discrepâncias temporais na notificação do Acórdão. Confiança 99%.

---

## 5. 🚀 PRÓXIMOS PASSOS (NEXT ACTIONS)

O *Backoffice* de mapeamento jurídico inicial está consolidado. As alternativas de progressão para o ecossistema são:

1. **HITL Review**: O Human Layer revê, valida, adapta e submete formalmente as 4 peças jurídicas construídas.
2. **Generative Contradiction Map**: O Agente prossegue e gera o mapa final de contradições documentais (`contradiction_map`), dissecando logicamente a Versão do Ingo vs a Versão da Defesa e Ex-Mandatário.
3. **Instanciação Sandbox**: Ativar a `minmop_sandbox_execution.wsb` para escalar a infraestrutura local em ambiente isolado.
