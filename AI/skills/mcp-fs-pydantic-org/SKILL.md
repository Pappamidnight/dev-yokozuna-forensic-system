---
name: mcp-fs-pydantic-org
description: Skill de governanca, auditoria deterministica e loops de validacao/otimizacao para acervos juridicos e agentes canonicos no diretorio Dev.
---

# MCP FS Pydantic Org Skill

Esta skill orquestra o pipeline deterministico de 6 agentes canonicos sobre as 6 pastas de acervo em `C:\Users\Yokozuna\Dev\Projects\Ficheiros Escritos Canónicos\`.

## 1. Ativacao e Sintaxe Rapida

Para ativar a cadeia deterministica no Antigravity ou GPT:
```
Activa os 6 agentes canonicos em ORDEM (00->01->04->03->05->02).
Pastas: 00_Indice_E_MOCs ... 05_Correspondencia_E_Comunicacoes.
T0-T8. 0 invencoes. 02 nunca e despacho. Gate humano.
```

## 2. Mapa dos Agentes e Precedencias

1. `00_Indice_E_MOCs`: `agente-indice-mocs` (Peso 0.70)
2. `01_PDFs_Oficiais`: `agente-pdfs-oficiais` (Peso **1.00**, SHA-256)
3. `04_Processos_E_Pecas_Escritas`: `agente-pecas` (Peso 0.98, cadeia CPC)
4. `03_Contratos_E_Acordos`: `agente-contratos` (Peso 0.95, clausulas e partes)
5. `05_Correspondencia_E_Comunicacoes`: `agente-correspondencia` (Peso 0.85, FACTO vs ALEGACAO)
6. `02_Minutas_E_Rascunhos`: `agente-minutas` (Peso 0.25, rascunho apenas)

## 3. Ficheiros de Referencia

- [references/DIRETRIZES-GLOBAIS-DEV.md](file:///c:/Users/Yokozuna/Dev/AI/skills/mcp-fs-pydantic-org/references/DIRETRIZES-GLOBAIS-DEV.md)
- [references/reasoning-contract.md](file:///c:/Users/Yokozuna/Dev/AI/skills/mcp-fs-pydantic-org/references/reasoning-contract.md)
- [references/chain-of-prompt.md](file:///c:/Users/Yokozuna/Dev/AI/skills/mcp-fs-pydantic-org/references/chain-of-prompt.md)
- [references/agentes-canonicos.md](file:///c:/Users/Yokozuna/Dev/AI/skills/mcp-fs-pydantic-org/references/agentes-canonicos.md)
- [references/agent-loops-optimizer.md](file:///c:/Users/Yokozuna/Dev/AI/skills/mcp-fs-pydantic-org/references/agent-loops-optimizer.md)
- [references/protocolo-sff-workflows.md](file:///c:/Users/Yokozuna/Dev/AI/skills/mcp-fs-pydantic-org/references/protocolo-sff-workflows.md)

## 4. Scripts e Avaliacao

- `scripts/run_act_agents.py`: Auditoria deterministica, calculo de SHA-256, validacao Pydantic e relatorios em `_index/`.
- `scripts/optimize_and_validate_loop.py`: Loop iterativo de deteccao de lacunas e enriquecimento.
- `scripts/eval_pipeline.py`: Pipeline de avaliacao e metricas com Golden Dataset.
- `scripts/watchdog_indexer.py`: Watchdog em tempo real.
