# Regras de Resposta e Determinismo Operacional

**Autoridade**: [Projects/blindada-agent/docs/REGRAS.md](file:///c:/Users/Yokozuna/Dev/Projects/blindada-agent/docs/REGRAS.md) e [isntruçoes determionsiticas.txt](file:///c:/Users/Yokozuna/Dev/Projects/blindada-agent/docs/isntru%C3%A7oes%20determionsiticas.txt)

---

## 1. Padrao de Resposta do Agente

- **Conciso e Estruturado**: Maximo de 3 paragrafos por topico.
- **Listas Compactas**: Bullet points com no maximo 5 itens por bloco.
- **Codigo Funcional**: Apresentar codigo apenas quando essencial, completo e ja funcional ("Se nao for codigo pronto, nao digas nada").
- **Zero Emojis**: Proibicao absoluta de emojis em respostas, logs e documentos oficiais.
- **Confirmacoes Padronizadas**: `[STATUS]`, `[ACAO]`, `[CODIGO]`, `[PROXIMO]`.

---

## 2. Checklist Obrigatoria Pre-Resposta

Antes de emitir qualquer resposta, o agente valida internamente:
1. Li toda a conversa e requisitos do utilizador?
2. O codigo produzido e funcional e testado?
3. Fui direto ao ponto sem explicacoes prolixas?
4. A solucao e acionavel imediatamente sem exigir esforco manual do utilizador?

---

## 3. Protocolo de 4 Fases e Seguranca

1. **Fase 1 (Analise e Estrutura)**: Apresenta plano completo, arquitetura, pastas e testes sem alterar ficheiros reais.
2. **Fase 2 (Sandbox)**: Implementa e testa no ambiente isolado.
3. **Fase 3 (Execucao)**: Apenas sob expressao **"VALIDADO."** ou **"CONFIRMO EXECUCAO AGENTES"**.
4. **Fase 4 (Validacao Pos-Tool Use)**: Reporta evidencias, conformidade SHA-256 e status do Eval Pipeline.

---

## 4. Estrutura Canónica do Dataset (11 Secções)

- `00_INDEX`: Manifestos e índices principais.
- `01_PROCESSOS`: Dossiês por processo (`3719`, `10153`, `15547`, `23142`).
- `02_INTERVENIENTES`: Entidades, pessoas, tribunais e empresas.
- `03_CRONOLOGIAS`: Linhas temporais ordenadas por ato CPC.
- `04_ATOS_PROCESSUAIS`: Atos normalizados com SHA-256.
- `05_AGENTES`: Registo dos 7 agentes do `blindada-agent` e dos 6 agentes canónicos.
- `06_YKF_TOOLS`: Scripts YKF catalogados (`execution_allowed: false`).
- `07_CONFLITOS`: Tratamento explícito de colisões (`CONTEXT.md`, `PASTA_RULES.json`).
- `08_MELHORIAS`: Otimizações pendentes mantendo o eval verde.
- `09_VALIDACAO`: `frozen_judge.ps1`, `health_check_validator.ps1`, `goldenset.json`, `eval_pipeline.py`.
- `11_GRAPH_MEMORY`: Grafo relacional sem nós órfãos nem arestas duplicadas.
