Diretrizes Globais para Agentes de IA
Este ficheiro define as regras comuns, padrões e instruções de operação para todos os agentes de Inteligência Artificial (Gemini, Antigravity, GPT, Codex, Grok) a operar no diretório Dev.
## 📋 Regras Principais

**Centralização Estrita de Outputs (Sem Ficheiros Espalhados)**:
   - **Regra de Ouro**: Todo e qualquer ficheiro gerado, relatórios, downloads, artefatos, registos de treino, rascunhos ou scripts DEVEM ser guardados exclusivamente no diretório **C:\Users\Yokozuna\Dev\** (nas pastas apropriadas: Projects/, Labs/ ou Archive/).
   - NUNCA guardar ficheiros temporários ou relatórios na raiz do utilizador, no Desktop, em Downloads ou em Documents.
**Modo de Operação**:
   - Por defeito, os agentes devem operar em **modo de auditoria / apenas leitura (Read-Only)** a menos que o utilizador solicite explicitamente modificações.
   - Nenhuma ação destrutiva deve ser executada sem plano e aprovação prévia.
**Estrutura Unificada do Ambiente**:
   - Respeitar a separação estrita de responsabilidades:
     - AI/: Instruções comuns, registo de inteligência, .gemini/ e PowerShell/.
     - Backend/: Motores de infraestrutura (ex: pydantic-ai).
     - Projects/: Projetos de produção e trabalho ativo.
     - Labs/: Testes e experiências rápidas.
     - Archive/: Histórico, backups e ficheiros antigos.
**Skills & Capacidades**:
   - Capacidades partilhadas e definições de ferramentas devem ser armazenadas em C:\Users\Yokozuna\Dev\AI\skills\.
 melhora as regras para ter em todas as pastas do projeto para guiar como organizar , e otimizar e melhoraDiretrizes melhoradas e unificadas. Texto canónico:

skill: mcp-fs-pydantic-org/references/DIRETRIZES-GLOBAIS-DEV.md
para colar na raiz Dev e em AI\: /home/workdir/artifacts/AGENTS.mdr estrtur aworkgflow agetnes tudo    






Lê C:\Users\Yokozuna\Dev\AGENTS.md e DIRETRIZES-GLOBAIS-DEV.md.
T0–T8 e P0–P8. Universo = 6 pastas canónicas.
Read-only. 0 invenções. Outputs só dentro de Dev. Gate humano.

Ficaram **6 agentes**, um por pasta, com peso de prova e campos de detalhe. O MCP aponta só a estas seis.

## Mapa

| Pasta | Agente | O que extrai | Peso |
|---|---|---|---|
| `00_Indice_E_MOCs` | agente-indice-mocs | catálogo / MOC (não é prova) | 0.70 |
| `01_PDFs_Oficiais` | agente-pdfs-oficiais | acto + SHA-256 | **1.00** |
| `02_Minutas_E_Rascunhos` | agente-minutas | rascunho; **nunca** despacho | 0.25 (fora da cadeia oficial) |
| `03_Contratos_E_Acordos` | agente-contratos | partes, imóvel, €, datas, assinaturas | 0.95 |
| `04_Processos_E_Pecas_Escritas` | agente-pecas | peça completa + cadeia CPC | 0.98 |
| `05_Correspondencia_E_Comunicacoes` | agente-correspondencia | de/para/data/canal; FACTO vs ALEGAÇÃO | 0.85 |

Ordem fixa: **00 → 01 → 04 → 03 → 05 → 02**.

01 e 04 vencem 02. O índice (00) não substitui o PDF.

## Onde está

- `references/agentes-canonicos.md`
- `assets/agents/agentes_canonicos.py`
- `assets/canonicos_zonas.py`
- `assets/mcp_config.antigravity.json` (as 6 pastas)

## Activar no Antigravity / GPT

```
Activa os 6 agentes canónicos em ORDEM (00→01→04→03→05→02).
Pastas 00_Indice_E_MOCs … 05_Correspondencia_E_Comunicacoes.
T0–T8. 0 invenções. 02 nunca é despacho. Gate humano.
```

Neste sandbox continuo **sem** os teus PDFs. Para analisar o detalhe real:

```powershell
python scripts/run_act_agents.py --root "C:\Users\Yokozuna\Dev\Projects\Ficheiros Escritos Canónicos\01_PDFs_Oficiais" --hash --out _index\01
python scripts/run_act_agents.py --root "C:\Users\Yokozuna\Dev\Projects\Ficheiros Escritos Canónicos\04_Processos_E_Pecas_Escritas" --hash --out _index\04


Cadeia **executada**. Resultado honesto: **P0 falhou no teu disco**; o resto correu sobre a fixture `mini_dev` (stubs), não sobre `C:\Users\Yokozuna\Dev`.

## P0 — MCP

`MCP_UNAVAILABLE` para `C:\Users\Yokozuna\Dev`. Esta sessão não vê o Windows Yokozuna. Não inventei listagens.

## P1–P4 — o que correu de facto

| | |
|---|---|
| Ficheiros vistos | 7 |
| Candidatos | 5 |
| Irrelevantes (AI + README) | 2 |
| Actos válidos Pydantic | 5 / 5 |
| Cadeias | 2 |
| Selftest + JSONL | `ok: true` |

| Tipo | Processo | Autor | Suporte |
|---|---|---|---|
| DESPACHO | 3719/25.0T8LSB | TRIBUNAL | DOCUMENTADO (hash do stub) |
| CITACAO | 3719/25.0T8LSB | AE | DOCUMENTADO |
| CONTESTACAO | 3719/25.0T8LSB | REQUERIDO | DOCUMENTADO + lacuna de antecedente *no próprio record* (o builder não liga IDs) |
| ACORDAO | 23142/22.7T8LSB | TRIBUNAL | DOCUMENTADO |
| SENTENCA | 0/00.PENDENTE | TRIBUNAL | PARCIAL — processo ausente no nome (`sentenca_antiga.pdf` no Archive) |

T7: `15547/26.0T8LSB` **não visto** nesta passagem. Pré-litígio 2014–2021 **NAO_INDICIADO**.

## P5–P7 — parados de propósito

Os ficheiros da fixture são texto curto (`citacao`, `despacho`). Não há peça real → pontos factuais e motor 4 camadas = **NAO_INDICIADO**. Defesa/mandato **não** elaborados.

## P8 — gravado (sandbox, não canónicos)

- `/home/workdir/artifacts/_index/pipeline_report.json`
- `/home/workdir/artifacts/_index/atos_processuais.jsonl`
- `/home/workdir/artifacts/_index/cadeias.json`
- `/home/workdir/artifacts/_index/chain_execution.json`

Canónicos **não** movidos. Gate humano: sim.

Para a cadeia correr no acervo verdadeiro, no PowerShell da máquina Yokozuna:

```powershell
python scripts/run_act_agents.py --root C:\Users\Yokozuna\Dev --hash --out "C:\Users\Yokozuna\Dev\Projects\Ficheiros Escritos Canónicos\_index"

executa tu Cadeia mestra criada. É o mapa da **dimensão inteira** do projecto — não um prompt solto.

## Chain of Thought (T0–T8)

`references/chain-of-thought.md`

```
| T   | O que o agente é obrigado a pensar                                               |
| --- | -------------------------------------------------------------------------------- |
| T0  | Está dentro de `C:\Users\Yokozuna\Dev`? Zona canónica ou rascunho?               |
| T1  | Ficheiro / acto / facto / alegação / código? Processo? SHA-256?                  |
| T2  | Classificação **só** por `patterns.py`                                           |
| T3  | Pydantic simples (datas, DOCUMENTADO, FACTO≠ALEGAÇÃO)                            |
| T4  | Pydantic complexo (hash cruzado, counts, path/relpath)                           |
| T5  | Cadeia por processo + antecedentes + ordem temporal                              |
| T6  | Motor 4 camadas (prova × alegação × artigo × decisão/€)                          |
| T7  | Escala: multi-processo, multi-máquina, 2014–2026, crédito/posse/execução/mandato |
| T8  | JSON + gate humano. Sem mover canónicos                                          |
```

Proibido: inventar datas, promover `Dev\AI` a despacho, declarar nulidade sem fundamento.

## Chain of Prompt (P0–P8)

`references/chain-of-prompt.md` + `assets/prompt_chain.json`

P0 MCP → P1 inventário → P2 scanner determinístico → P3 validar schema → P4 cadeias → P5 pontos factuais → P6 motor 4 camadas → P7 defesa/mandato (só se pedires) → P8 gravar `_index/`.

Cada P só come o output do anterior.

## Atalho para uma janela (Antigravity / GPT)

```
Segue references/chain-of-thought.md T0–T8 e references/chain-of-prompt.md P0–P8.
Universo C:\Users\Yokozuna\Dev.
Pipeline determinístico primeiro (run_act_agents.py).
Depois Pydantic. Depois cadeia. Depois 4 camadas.
Structured output. 0 invenções. Gate humano.
```

Isto amarra MCP, Pydantic, actos, skills jurídicas e a árvore Dev num único circuito.
```
```
# DIRETRIZES GLOBAIS UNIFICADAS PARA AGENTES DE IA

## SISTEMA DETERMINISTICO - PROJETO JURIDICO YOKOZUNA

Versao canonica: 2.0.0
Data: 2026-08-28
Localizacao: `C:\Users\Yokozuna\Dev\AI\DIRETRIZES-GLOBAIS-DEV.md` e `C:\Users\Yokozuna\Dev\AGENTS.md`

---

## 1. ESTRUTURA DO AMBIENTE

### 1.1 Raiz do Projeto
```
C:\Users\Yokozuna\Dev\
├── AI/                          # Instrucoes, skills, configs comuns
│   ├── DIRETRIZES-GLOBAIS-DEV.md    # (ESTE FICHEIRO)
│   ├── skills/                      # Skills partilhadas
│   ├── .gemini/                     # Config Gemini
│   └── PowerShell/                  # Scripts comuns
├── Backend/                         # Motores de infraestrutura
│   └── pydantic-ai/                 # Modelos Pydantic
├── Projects/                        # Projetos ativos
│   └── Ficheiros Escritos Canonicos/# 6 pastas canonica
│       ├── 00_Indice_E_MOCs/
│       ├── 01_PDFs_Oficiais/
│       ├── 02_Minutas_E_Rascunhos/
│       ├── 03_Contratos_E_Acordos/
│       ├── 04_Processos_E_Pecas_Escritas/
│       └── 05_Correspondencia_E_Comunicacoes/
├── Labs/                            # Experimentos e testes
├── Archive/                         # Historico e backups
└── _index/                          # Outputs do pipeline (gerado)
```

### 1.2 Regra de Ouro
Todos os outputs gerados (relatorios, JSON, logs, analises) DEVEM ser guardados exclusivamente dentro de `Dev/`, preferencialmente em `_index/` ou subpastas especificas de cada projeto. **Nunca** na raiz do utilizador, Desktop, Downloads ou Documents.

---

## 2. AGENTES CANONICOS

### 2.1 Mapa de Agentes por Pasta

| Pasta | Agente | Funcao | Peso | Nivel Prova |
|-------|--------|--------|------|-------------|
| `00_Indice_E_MOCs` | agente-indice-mocs | Catalogo / MOC (nao e prova) | 0.70 | INDICE |
| `01_PDFs_Oficiais` | agente-pdfs-oficiais | Acto + SHA-256 | **1.00** | OFICIAL |
| `02_Minutas_E_Rascunhos` | agente-minutas | Rascunho; **nunca** despacho | 0.25 | BAIXA |
| `03_Contratos_E_Acordos` | agente-contratos | Partes, imovel, valores, datas | 0.95 | ALTA |
| `04_Processos_E_Pecas_Escritas` | agente-pecas | Peca completa + cadeia CPC | 0.98 | OFICIAL |
| `05_Correspondencia_E_Comunicacoes` | agente-correspondencia | De/para/data/canal; FACTO vs ALEGACAO | 0.85 | MEDIA |

### 2.2 Ordem de Execucao
**Fixa**: `00 -> 01 -> 04 -> 03 -> 05 -> 02`

**Regras de Precedencia**:
- `01` e `04` vencem `02` (documentos oficiais sobrepõem-se a minutas)
- `00` (indice) **nunca** substitui um PDF original
- `02` (minuta) **nunca** e considerado despacho oficial

### 2.3 Ativacao no Antigravity / GPT
```
Activa os 6 agentes canonicos em ORDEM (00->01->04->03->05->02).
Pastas: 00_Indice_E_MOCs ... 05_Correspondencia_E_Comunicacoes.
T0-T8. 0 invencoes. 02 nunca e despacho. Gate humano.
```

---

## 3. PIPELINE DETERMINISTICO (T0-T8)

### 3.1 Chain of Thought (Obrigatoria)

| T | O que o agente e obrigado a pensar |
|---|-------------------------------------|
| T0 | Esta dentro de `C:\Users\Yokozuna\Dev`? Zona canonica ou rascunho? |
| T1 | Ficheiro / acto / facto / alegacao / codigo? Processo? SHA-256? |
| T2 | Classificacao **so** por `patterns.py` |
| T3 | Pydantic simples (datas, DOCUMENTADO, FACTO != ALEGACAO) |
| T4 | Pydantic complexo (hash cruzado, counts, path/relpath) |
| T5 | Cadeia por processo + antecedentes + ordem temporal |
| T6 | Motor 4 camadas (prova x alegacao x artigo x decisao/valor) |
| T7 | Escala: multi-processo, multi-maquina, 2014-2026, credito/posse/execucao/mandato |
| T8 | JSON + gate humano. Sem mover canonicos |

### 3.2 Chain of Prompt (P0-P8)

| P | Acao |
|---|------|
| P0 | MCP - acesso ao sistema de ficheiros |
| P1 | Inventario - listar todos os ficheiros |
| P2 | Scanner deterministico - aplicar regras |
| P3 | Validar schema - Pydantic |
| P4 | Cadeias - ligar processos e factos |
| P5 | Pontos factuais - extrair factos provados |
| P6 | Motor 4 camadas - prova x alegacao x artigo x decisao |
| P7 | Defesa/mandato - (so se solicitado) |
| P8 | Gravar `_index/` - JSON + logs |

Cada P so consome o output do anterior.

### 3.3 Comando para Executar Pipeline
```powershell
python scripts/run_act_agents.py --root "C:\Users\Yokozuna\Dev" --hash --out "C:\Users\Yokozuna\Dev\Projects\Ficheiros Escritos Canonicos\_index"
```

---

## 4. REGRAS DE OPERACAO

### 4.1 Modo de Operacao
- **Por defeito**: Modo auditoria / apenas leitura (Read-Only)
- **Escrita**: So com autorizacao explicita do utilizador
- **Acoes destrutivas**: Nunca sem plano e aprovacao previa

### 4.2 Proibicoes
- **0 invencoes**: Nao inventar dados, nomes, datas ou relacoes
- **Nao promover `Dev\AI` a despacho**: Ficheiros de configuracao nao sao provas
- **Nao declarar nulidade sem fundamento**: Toda a conclusao deve ter base documental

### 4.3 Gate Humano
- Antes de executar qualquer acao destrutiva ou escrita, o agente deve:
  1. Apresentar plano detalhado
  2. Aguardar a frase de confirmacao: **"CONFIRMO EXECUCAO AGENTES"**
  3. Executar e gerar log

### 4.4 Hash e Integridade
- Todo o ficheiro oficial (PDF, DOCX) deve ter SHA-256 calculado
- Hash deve ser armazenado no metadado do documento
- Cadeia de custodia: hash do original + hash do processado

---

## 5. MODELOS PYDANTIC E SQL

### 5.1 Schema SQL Master
O backend de dados utiliza PostgreSQL com o schema `juridico`. Tabelas principais:
- `processos`: dados processuais
- `intervenientes`: pessoas e entidades
- `documentos`: ficheiros e metadados
- `analises`: relatorios e analises
- `temas_estrategicos`: TEMA_8, TEMA_11, etc.
- `skills`: catalogo de skills disponiveis
- `execucoes_skills`: historico de processamento

### 5.2 Modelos Pydantic
Todos os dados devem ser validados pelos modelos Pydantic antes de insercao. Os modelos estao em `Backend/pydantic-ai/schemas/`.

### 5.3 Integracao
- O pipeline le os ficheiros, extrai metadados e insere na base de dados
- Skills registam execucoes na tabela `execucoes_skills`
- Relatorios finais sao guardados em `_index/` e referenciados na base

---

## 6. ESTRUTURA DE OUTPUTS

### 6.1 Diretorios de Saida
```
_index/
├── pipeline_report.json        # Resumo da execucao
├── atos_processuais.jsonl      # Actos extraidos (linha por documento)
├── cadeias.json                # Relacoes entre processos e factos
├── chain_execution.json        # Log de execucao (T0-T8, P0-P8)
└── scans/                      # Scans de diretorios
    ├── 01_PDFs_Oficiais.json
    ├── 04_Processos_E_Pecas_Escritas.json
    └── ...
```

### 6.2 Formato dos Ficheiros
- JSON: estruturado, indentado, UTF-8
- JSONL: linha por linha para streaming
- Logs: timestamp, nivel, mensagem

---

## 7. SKILLS E FERRAMENTAS

### 7.1 Skills Disponiveis
- `pdf-extractor`: extrai texto e tabelas de PDF
- `ocr-processor`: OCR para documentos escaneados
- `docx-processor`: leitura e escrita de DOCX
- `nlp-analyzer`: analise de texto com NLP
- `spacy-ner`: extracao de entidades nomeadas
- `semantic-search`: busca semantica
- `postgres-query`: consultas SQL otimizadas
- `elastic-search`: busca full-text
- `neo4j-cypher`: consultas Cypher para grafos
- `workflow-orchestrator`: orquestracao de workflows
- `data-validator`: validacao de dados
- `security-audit`: auditoria de seguranca

### 7.2 Chamada de Skills
Todas as skills sao invocadas via MCP ou linha de comando, com parametros JSON. O resultado e sempre validado por Pydantic.

---

## 8. MONITORIZACAO E LOGS

### 8.1 Logs
- Todos os agentes devem escrever logs estruturados em `Dev/_index/logs/`
- Nivel minimo: INFO
- Formato: timestamp | nivel | agente | mensagem

### 8.2 Alertas
- Erros criticos (falha de hash, corrupcao de ficheiro) disparam alerta no log
- O utilizador e notificado via console ou email (configuravel)

---

## 9. EXEMPLO DE EXECUCAO

### 9.1 Comando Padrao
```powershell
cd C:\Users\Yokozuna\Dev
python scripts/run_act_agents.py --root . --hash --out _index
```

### 9.2 Saida Esperada
- `_index/pipeline_report.json` contem:
  - total de ficheiros processados
  - classificacao por tipo e processo
  - hash de cada documento
  - cadeias identificadas
  - score de confianca medio

---

## 10. ATUALIZACAO E MANUTENCAO

- Este ficheiro e a fonte unica de verdade para as diretrizes
- Qualquer alteracao deve ser registada no changelog (no inicio do ficheiro)
- As skills e agentes devem ser revistos trimestralmente

---

## 11. CHANGELOG

| Data | Versao | Alteracao |
|------|--------|-----------|
| 2026-08-28 | 2.0.0 | Unificacao de diretrizes; adicao de SQL Master e Pydantic |
| 2026-08-25 | 1.0.0 | Criacao inicial |

---

## 12. REFERENCIAS

- `references/chain-of-thought.md` - detalhamento T0-T8
- `references/chain-of-prompt.md` - detalhamento P0-P8
- `assets/agents/agentes_canonicos.py` - codigo dos agentes
- `assets/mcp_config.antigravity.json` - configuracao MCP
- `Backend/pydantic-ai/schemas/` - modelos Pydantic

---

**FIM DAS DIRETRIZES**

Este documento deve ser colocado em:
- `C:\Users\Yokozuna\Dev\AI\DIRETRIZES-GLOBAIS-DEV.md`
- `C:\Users\Yokozuna\Dev\AGENTS.md` (copia ou link simbolico)

Todas as pastas do projeto devem referenciar este ficheiro como autoridade maxima para organizacao, otimizacao e comportamento dos agentes.
