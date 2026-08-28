# DIRETRIZES GLOBAIS UNIFICADAS PARA AGENTES DE IA

## SISTEMA DETERMINISTICO - PROJETO JURIDICO YOKOZUNA

**Versao Canonica**: 2.0.0  
**Data**: 2026-08-28  
**Localizacao**: `C:\Users\Yokozuna\Dev\AI\DIRETRIZES-GLOBAIS-DEV.md`

---

## 1. ESTRUTURA DO AMBIENTE DEV

### 1.1 Raiz do Projeto
```
C:\Users\Yokozuna\Dev\
|-- AI/                          # Instrucoes, skills, configs comuns
|   |-- DIRETRIZES-GLOBAIS-DEV.md
|   |-- AGENTS.md
|   `-- skills/
|-- Backend/                     # Motores de infraestrutura (pydantic-ai)
|-- Projects/                    # Projetos ativos
|   |-- Ficheiros Escritos Canonicos/
|   |   |-- 00_Indice_E_MOCs/
|   |   |-- 01_PDFs_Oficiais/
|   |   |-- 02_Minutas_E_Rascunhos/
|   |   |-- 03_Contratos_E_Acordos/
|   |   |-- 04_Processos_E_Pecas_Escritas/
|   |   |-- 05_Correspondencia_E_Comunicacoes/
|   |   `-- _index/
|   |-- blindada-agent/
|   `-- Instrucoes_Agents/
|-- Labs/
|-- Sandbox/
|-- Archive/
|-- PROTOCOL.md
`-- README.md
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

## 3. PIPELINE DETERMINISTICO (T0-T8 E P0-P8)

Consulte:
- [chain-of-thought.md](file:///c:/Users/Yokozuna/Dev/AI/skills/mcp-fs-pydantic-org/references/chain-of-thought.md)
- [chain-of-prompt.md](file:///c:/Users/Yokozuna/Dev/AI/skills/mcp-fs-pydantic-org/references/chain-of-prompt.md)
- [agent-loops-optimizer.md](file:///c:/Users/Yokozuna/Dev/AI/skills/mcp-fs-pydantic-org/references/agent-loops-optimizer.md)
