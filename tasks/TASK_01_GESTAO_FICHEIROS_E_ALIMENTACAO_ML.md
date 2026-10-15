# TASK 01: Analise, Gestao de Ficheiros e Alimentacao Correta de Machine Learning

**Ramo de Trabalho**: `tasks-gestao-ficheiros-ml`  
**Autoridade**: Yokozuna / Acervo Forense V8  
**Data**: 2026-10-15  
**Objetivo**: Protocolo estruturado de saneamento, inventario e extracao controlada de dados para alimentar com 100% de integridade os modelos de NLP, Classificadores e Memoria Vetorial.

---

## 1. Diagnostico e Causa Raiz das Falhas na Alimentacao de ML

A tentativa de alimentacao cega do motor de Machine Learning encontrou bloqueios operacionais decorrentes de:
1. **Dependencia Exclusiva da Porta HTTP 8080**:
   - O servidor HTTP do Everything pode encontrar-se inativo, congelado ou a sofrer timeouts de socket em varreduras massivas, bloqueando scripts dependentes de `urllib.request`.
   - **Solucao Mandatoria**: Adotar arquitetura resiliente tripla: `Everything MCP SDK (DLL nativa)` -> `ripgrep / fd local` -> `HTTP 8080` (apenas se online).
2. **Heterogeneidade de Formatos e Ficheiros Bloqueados**:
   - A leitura direta de pastas de sistema ou nuvem (Google Drive, OneDrive) sem pré-filtragem aciona bloqueios de I/O (`PermissionError`, `OSError: [Errno 13]`).
   - Ficheiros binarios pesados (scans de 140 MB, PDFs protegidos com senha) nao podem ser injetados em modelos de NLP sem parsing previo.
3. **Ausencia de Pipeline de Saneamento Pre-ML**:
   - O Machine Learning nao deve ler ficheiros brutos em disco, mas sim um **Dataset Curado e Auditado** com hashes SHA-256 e texto normalizado.

---

## 2. Roteiro Operacional em 4 Fases

```
[FASE 1: Inventario Resiliente]
       (fd + ripgrep + Everything MCP DLL)
                     |
                     v
[FASE 2: Gestao e Sanitizacao de Ficheiros]
       (Filtro de Ruido + Hash BLAKE3/SHA-256 + Deduplicacao)
                     |
                     v
[FASE 3: Engenharia de Features Estruturadas]
       (Extracao de Entropia + Magic Bytes + Tokens Juridicos)
                     |
                     v
[FASE 4: Alimentacao e Treino de Modelos]
       (TF-IDF NLP + Naive Bayes/XGBoost + Embeddings Qdrant)
```

---

## 3. Detalhamento das Tarefas de Execucao

### Fase 1: Inventario e Rastreio de Alta Performance
- **T-1.1**: Utilizar `fd` e `ripgrep` (`rg`) nativos no host ou WSL2 (`wsl -d Ubuntu-26.04`) com credenciais administrativas para varrer as unidades `C:\ACERVO`, `Desktop` e `Google Drive`.
- **T-1.2**: Mapear os ficheiros estritamente por litígio atraves dos helpers dedicados em `helpers/` (`proc_15547.py`, `proc_3719.py`, `proc_20203.py`, `proc_10153.py`, `proc_23142.py`, `proc_7620.py`).
- **T-1.3**: Gerar lista indexada de ficheiros candidatos em formato JSONL leve (`data/inventario_candidatos_ml.jsonl`).

### Fase 2: Gestao, Limpeza e Custodia Documental
- **T-2.1**: Excluir compulsoriamente lixo de build (`node_modules`, `target`, `__pycache__`, `.venv`, `.git`, `$Recycle.Bin`).
- **T-2.2**: Calcular hashes duplos (BLAKE3 para indexacao em microssegundos + SHA-256 para custodia legal ISO/IEC 27037).
- **T-2.3**: Segregar duplicados exatos para que nao poluam nem enviesem a distribuicao estatistica do treino de ML.

### Fase 3: Engenharia de Features e Normalizacao de Texto
- **T-3.1**: Executar extrator binario Rust `crates/forensic_ml` para calcular a Entropia de Shannon (0.0 a 8.0) e inspecionar os primeiros 16 Magic Bytes de cada ficheiro.
- **T-3.2**: Processar articulados juridicos (`caso_15547/docs/*.md`) fatiando o texto em blocos coerentes (seccoes de 100 a 500 palavras), removendo stop-words juridicas e extraindo unigramas e bigramas.
- **T-3.3**: Mapear cada bloco para uma categoria juridica supervisionada:
  - `DIREITO_RETENCAO_BENFEITORIAS` (Processo 15547)
  - `RECURSO_RELACAO_PROVISORIA` (Processo 3719)
  - `NULIDADE_CITACAO_INOPONIBILIDADE` (Processo 20203)
  - `OPOSICAO_DESPEJO_BENFEITORIAS` (Processo 10153)
  - `RESTITUICAO_DINHEIROS_RETIDOS` (Processo 23142)
  - `FRAUDE_FISCAL_SIMULACAO` (Processo 7620)

### Fase 4: Treino, Validacao e Exportacao de Modelos
- **T-4.1**: Ajustar a matriz TF-IDF com vocabulario fixo e calcular as probabilidades condicionais do classificador Naive Bayes / Regressao Logistica.
- **T-4.2**: Executar validacao cruzada (K-Fold ou Split Treino/Teste 80/20) e calcular metricas de precisao, recall e F1-Score por classe.
- **T-4.3**: Persistir os pesos do modelo em `data/ml/modelo_classificador_forense.json` para permitir inferencia instantanea sem re-treino.
- **T-4.4**: Gerar relatorio formal de auditoria em `reports/relatorio_machine_learning_verdadeiro.md`.

---

## 4. Matriz de Controlo e Estado das Tarefas

| Codigo | Descricao da Tarefa | Responsavel | Estado |
|---|---|---|---|
| **T-1.1** | Configuracao dos Helpers por Processo (`helpers/`) | Antigravity | Concluido |
| **T-1.2** | Motor Rust de Features e Hashing BLAKE3 (`crates/forensic_ml`) | Antigravity | Concluido |
| **T-1.3** | Fallback de I/O contra timeouts HTTP | Antigravity | Concluido |
| **T-2.1** | Sanitizacao de lista de ficheiros reais | Operador / Script | Em Curso |
| **T-3.1** | Extracao de texto de documentos Citius e pecas | Pipeline | Pendente |
| **T-4.1** | Execucao do treino supervisionado e exportacao | Pipeline | Pendente |
| **T-4.2** | Validacao e emissao de relatorio com F1-Score | Sentinel | Pendente |
