# Diretrizes Globais Unificadas para Agentes de IA

## Sistema Deterministico - Projeto Dev Yokozuna
**Versao Canonica**: 2.1.0  
**Data**: 2026-08-28  
**Autoridade**: `C:\Users\Yokozuna\Dev\AI\DIRETRIZES-GLOBAIS-DEV.md` e `C:\Users\Yokozuna\Dev\AGENTS.md`

---

## 1. Regras Absolutas e Principais

1. **Centralizacao Estrita de Outputs (Regra de Ouro)**:
   - Todo e qualquer ficheiro gerado, relatorios, JSON, logs, analises e artefatos DEVEM ser guardados exclusivamente em `C:\Users\Yokozuna\Dev\` (preferencialmente em `_index/` ou subpastas de saida autorizadas).
   - E expressamente proibido gravar em `Desktop`, `Downloads`, `Documents` ou raiz do utilizador.

2. **Modo de Operacao Read-Only / Auditoria**:
   - Agentes operam por defeito em modo de leitura estrita.
   - Ficheiros canonicos sao imutaveis (sem mover, renomear ou sobrescrever ficheiros originais).
   - Nenhuma acao destrutiva ou de escrita e permitida sem plano validado e autorizacao explicita.

3. **Zero Invencoes e Zero Emojis**:
   - Proibido alucinar dados, datas, partes ou numeros de processo.
   - O que nao tiver suporte documental e classificado como `NAO_INDICIADO` ou `needs_review`.
   - Proibicao total de emojis em logs, codigos e documentos oficiais (conforme [PROTOCOL.md](file:///c:/Users/Yokozuna/Dev/PROTOCOL.md)).

4. **Gate Humano**:
   - Acoes de gravacao em massa exigem validacao e confirmacao explicita do utilizador.

---

## 2. Mapa dos 6 Agentes Canonicos e Precedencias

| Pasta | Agente | Funcao | Peso | Nivel Prova |
|---|---|---|---|---|
| `00_Indice_E_MOCs` | `agente-indice-mocs` | Catalogo e navegacao (MOC) | 0.70 | INDICE |
| `01_PDFs_Oficiais` | `agente-pdfs-oficiais` | Atos formais + hash SHA-256 | **1.00** | OFICIAL |
| `02_Minutas_E_Rascunhos` | `agente-minutas` | Rascunhos e notas (nunca despacho) | 0.25 | BAIXA |
| `03_Contratos_E_Acordos` | `agente-contratos` | Partes, clausulas, valores, datas | 0.95 | ALTA |
| `04_Processos_E_Pecas_Escritas` | `agente-pecas` | Pecas integrais + cadeia CPC | 0.98 | OFICIAL |
| `05_Correspondencia_E_Comunicacoes` | `agente-correspondencia` | De/Para/Data/Canal; FACTO vs ALEGACAO | 0.85 | MEDIA |

### Ordem de Execucao Deterministica
$$\mathbf{00\_Indice} \longrightarrow \mathbf{01\_PDFs} \longrightarrow \mathbf{04\_Pecas} \longrightarrow \mathbf{03\_Contratos} \longrightarrow \mathbf{05\_Correspondencia} \longrightarrow \mathbf{02\_Minutas}$$

**Regras de Precedencia**:
- `01_PDFs_Oficiais` e `04_Processos_E_Pecas_Escritas` prevalecem sobre qualquer minuta (`02`).
- `00_Indice_E_MOCs` mapeia o acervo mas **nunca substitui a prova original**.
- `02_Minutas_E_Rascunhos` **nunca e promovido a despacho ou documento judicial**.

---

## 3. Pipeline Deterministico: Reasoning Contract (T0 a T8)

| Fase | Raciocinio e Etapa Operacional Obrigatoria |
|---|---|
| **T0** | Verificacao de fronteira (`C:\Users\Yokozuna\Dev`) e segregacao de zona (canonica vs rascunho). |
| **T1** | Identificacao de entidade: Ficheiro / Ato / Facto / Alegacao / Codigo / SHA-256. |
| **T2** | Classificacao deterministica estrita por padroes (`patterns.py`). |
| **T3** | Validacao de schema Pydantic simples (datas ISO, DOCUMENTADO, FACTO != ALEGACAO). |
| **T4** | Validacao de schema Pydantic complexo (hashes cruzados, contagens, integridade de caminhos). |
| **T5** | Construcao da cadeia temporal por processo + antecedentes CPC. |
| **T6** | Motor de 4 Camadas: **Prova $\times$ Alegacao $\times$ Norma $\times$ Decisao/Impacto**. |
| **T7** | Enquadramento em escala multi-processo e multi-ano (2014–2026). |
| **T8** | Emissao estruturada em JSON/JSONL para `_index/` com Gate Humano. |

---

## 4. Pipeline Deterministico: Chain of Prompt (P0 a P8)

- **P0 - MCP**: Verificacao de acesso ao sistema de ficheiros nas 6 pastas canonicas.
- **P1 - Inventario**: Listagem exaustiva de ficheiros sem invencoes.
- **P2 - Scanner Deterministico**: Extracao de metadados e calculo de SHA-256.
- **P3 - Validar Schema**: Aplicacao dos modelos Pydantic v2 com bloqueio semantico.
- **P4 - Cadeias Processuais**: Interligacao de atos, notificacoes e prazos.
- **P5 - Pontos Factuais**: Consolidacao de factos provados documentados.
- **P6 - Motor 4 Camadas**: Cruzamento Prova vs Alegacao vs Norma vs Decisao/Impacto.
- **P7 - legal-strategy**: Elaboracao de estrategia juridica (unicamente quando solicitado).
- **P8 - Gravacao**: Persistencia em `Projects/Ficheiros Escritos Canonicos/_index/`.

---

## 5. Loop de Validacao e Otimizacao de Agentes

O pipeline incorpora um ciclo de melhoria continua estruturado em 4 estagios:
1. **Auditoria e Extracao**: Coleta e hashing SHA-256.
2. **Validacao Cruzada Pydantic**: Deteccao de inconsistencias e conflitos semanticos.
3. **Refinamento e Enriquecimento**: Reconciliacao de lacunas, cruzamento de intervenientes e ordenacao temporal.
4. **Relatorio de Qualidade e Score**: Calculo do indice de confianca probatoria.

---

## 6. Referencias e Skills

- Skill Canonica: [`AI/skills/mcp-fs-pydantic-org/`](file:///c:/Users/Yokozuna/Dev/AI/skills/mcp-fs-pydantic-org)
- Reasoning Contract: [`AI/skills/mcp-fs-pydantic-org/references/reasoning-contract.md`](file:///c:/Users/Yokozuna/Dev/AI/skills/mcp-fs-pydantic-org/references/reasoning-contract.md)
- Modelos Pydantic: [`Backend/pydantic-ai/src/models_org.py`](file:///c:/Users/Yokozuna/Dev/Backend/pydantic-ai/src/models_org.py)
- Protocolo Obrigatorio: [`PROTOCOL.md`](file:///c:/Users/Yokozuna/Dev/PROTOCOL.md)
