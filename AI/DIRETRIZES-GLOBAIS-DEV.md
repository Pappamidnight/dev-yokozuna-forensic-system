# DIRETRIZES GLOBAIS UNIFICADAS PARA AGENTES DE IA

## SISTEMA DETERMINISTICO - PROJETO JURIDICO YOKOZUNA

**Versao Canonica**: 2.1.0 (Otimizada)  
**Data**: 2026-08-28  
**Localizacao**: `C:\Users\Yokozuna\Dev\AI\DIRETRIZES-GLOBAIS-DEV.md` e `C:\Users\Yokozuna\Dev\AGENTS.md`

---

## 1. ESTRUTURA DO AMBIENTE DEV

### 1.1 Topologia Geral
```
C:\Users\Yokozuna\Dev\
|-- AI/                          # Instrucoes, skills, configs e PowerShell
|   |-- DIRETRIZES-GLOBAIS-DEV.md # (ESTE FICHEIRO CANONICO)
|   |-- AGENTS.md                # Regras para agentes na pasta AI
|   `-- skills/                  # Skills partilhadas (ex: mcp-fs-pydantic-org)
|-- Backend/                     # Motores de infraestrutura (pydantic-ai)
|-- Projects/                    # Projetos ativos e acervos canonicos
|   |-- Ficheiros Escritos Canonicos/
|   |   |-- 00_Indice_E_MOCs/
|   |   |-- 01_PDFs_Oficiais/
|   |   |-- 02_Minutas_E_Rascunhos/
|   |   |-- 03_Contratos_E_Acordos/
|   |   |-- 04_Processos_E_Pecas_Escritas/
|   |   |-- 05_Correspondencia_E_Comunicacoes/
|   |   `-- _index/              # Repositorio de outputs automatizados
|   |-- blindada-agent/          # Motor forense e grafo de memoria
|   `-- Instrucoes_Agents/       # Instrucoes especificas dos agentes
|-- Labs/                        # Experimentos e prototipos (Labs/Pydantic)
|-- Sandbox/                     # Testes isolados e investigacao cruzada
|-- Archive/                     # Historico e executaveis inativos
|-- PROTOCOL.md                  # Protocolo de 4 Fases e Regras Absolutas
`-- README.md                    # Mapa do ambiente
```

### 1.2 Regra de Ouro
Todos os outputs gerados DEVEM ser guardados exclusivamente dentro de `Dev/`, preferencialmente em `_index/` ou subpastas especificas. **Nunca** na raiz do utilizador, Desktop, Downloads ou Documents.

---

## 2. AGENTES CANONICOS

### 2.1 Mapa de Agentes por Pasta

| Pasta | Agente | Funcao | Peso | Nivel Prova |
|---|---|---|---|---|
| `00_Indice_E_MOCs` | `agente-indice-mocs` | Catalogo / MOC (nao e prova) | 0.70 | INDICE |
| `01_PDFs_Oficiais` | `agente-pdfs-oficiais` | Acto + SHA-256 | **1.00** | OFICIAL |
| `02_Minutas_E_Rascunhos` | `agente-minutas` | Rascunho; **nunca** despacho | 0.25 | BAIXA |
| `03_Contratos_E_Acordos` | `agente-contratos` | Partes, imovel, valores, datas | 0.95 | ALTA |
| `04_Processos_E_Pecas_Escritas` | `agente-pecas` | Peca completa + cadeia CPC | 0.98 | OFICIAL |
| `05_Correspondencia_E_Comunicacoes` | `agente-correspondencia` | De/para/data/canal; FACTO vs ALEGACAO | 0.85 | MEDIA |

### 2.2 Ordem de Execucao
**Fixa**: `00 -> 01 -> 04 -> 03 -> 05 -> 02`

**Regras de Precedencia**:
- `01` e `04` vencem `02` (documentos oficiais sobrepoem-se a minutas).
- `00` (indice) **nunca** substitui um PDF original.
- `02` (minuta) **nunca** e considerado despacho oficial.

---

## 3. PIPELINE DETERMINISTICO: T0–T8 E P0–P8

### 3.1 Reasoning Contract (T0 a T8)

| T | Raciocinio e Etapa Operacional Obrigatoria |
|---|---|
| **T0** | Esta dentro de `C:\Users\Yokozuna\Dev`? Zona canonica ou rascunho? |
| **T1** | Ficheiro / acto / facto / alegacao / codigo? Processo? SHA-256? |
| **T2** | Classificacao **so** por `patterns.py` e regras deterministicas. |
| **T3** | Pydantic simples (datas ISO, DOCUMENTADO, FACTO != ALEGACAO). |
| **T4** | Pydantic complexo (hash cruzado, contagens, path/relpath integridade). |
| **T5** | Cadeia por processo + antecedentes + ordem temporal CPC. |
| **T6** | Motor 4 camadas: **Prova $\times$ Alegacao $\times$ Norma $\times$ Decisao/Impacto**. |
| **T7** | Escala: multi-processo, multi-maquina, 2014–2026, credito/posse/execucao/mandato. |
| **T8** | JSON + gate humano. Sem mover ficheiros canonicos. |

### 3.2 Chain of Prompt (P0 a P8)

| P | Acao Executada |
|---|---|
| **P0** | MCP: Acesso ao sistema de ficheiros restrito as 6 pastas. |
| **P1** | Inventario: Listar todos os ficheiros reais sem extrapolar. |
| **P2** | Scanner Deterministico: Aplicar expressoes regulares e metadados. |
| **P3** | Validar Schema: Submeter dados aos modelos Pydantic v2. |
| **P4** | Cadeias: Interligar processos, antecedentes e notificacoes. |
| **P5** | Pontos Factuais: Extrair factos provados com referencia ao documento. |
| **P6** | Motor 4 Camadas: Prova $\times$ Alegacao $\times$ Norma $\times$ Decisao/Impacto. |
| **P7** | legal-strategy: Consolidar estrategia e teses juridicas (apenas se solicitado). |
| **P8** | Gravar `_index/`: Emitir JSON, JSONL e logs de execucao. |

---

## 4. LOOPS DE AGENTES: VALIDACAO, MELHORIA E OTIMIZACAO

```
[Entrada de Dados] -> [Loop A: Hashing SHA-256 & Dedup]
                             |
                             v
                      [Loop B: Pydantic Schema Cross-Validation]
                             |
                             v
                      [Loop C: Cadeias CPC & Detecao de Lacunas]
                             |
                             v
                      [Loop D: Score Probatorio & Otimizacao]
                             |
                             v
                      [Gravacao em _index/]
```

---

## 5. REFERENCIAS

- [reasoning-contract.md](file:///c:/Users/Yokozuna/Dev/AI/skills/mcp-fs-pydantic-org/references/reasoning-contract.md)
- [chain-of-prompt.md](file:///c:/Users/Yokozuna/Dev/AI/skills/mcp-fs-pydantic-org/references/chain-of-prompt.md)
- [agentes-canonicos.md](file:///c:/Users/Yokozuna/Dev/AI/skills/mcp-fs-pydantic-org/references/agentes-canonicos.md)
- [protocolo-sff-workflows.md](file:///c:/Users/Yokozuna/Dev/AI/skills/mcp-fs-pydantic-org/references/protocolo-sff-workflows.md)
