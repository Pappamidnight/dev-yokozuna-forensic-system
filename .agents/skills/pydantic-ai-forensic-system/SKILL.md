---
name: pydantic-ai-forensic-system
description: Skill mestra para construir e orquestrar o ecossistema Pydantic AI, Golden Dataset, Eval Pipeline, Reasoning Contract (T0-T8), Chain of Prompt (P0-P8), Agentes Canonicos, Frozen Judge 100/100, Regras Globais e Output Centralizado.
---

# Pydantic AI Forensic System - Guia Mestre de Construcao e Execucao

Este skill define o protocolo deterministico completo para construir, validar e operar o ecossistema forense e juridico Yokozuna Dev.

---

## 1. Arquitetura Pydantic AI e Modelos de Dados

Todos os registos e transicoes de dados entre agentes devem ser validados por modelos **Pydantic v2** com validacao estrita de tipos e regras semanticas:

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from datetime import datetime

class CanonicalRecord(BaseModel):
    file_path: str = Field(..., description="Caminho relativo normalizado a partir da raiz Dev")
    rel_path: str = Field(..., description="Caminho relativo dentro da pasta canonica")
    filename: str = Field(..., description="Nome do ficheiro")
    folder: Literal[
        "00_Indice_E_MOCs",
        "01_PDFs_Oficiais",
        "02_Minutas_E_Rascunhos",
        "03_Contratos_E_Acordos",
        "04_Processos_E_Pecas_Escritas",
        "05_Correspondencia_E_Comunicacoes"
    ]
    process_id: Optional[str] = Field(None, description="Numero de processo judicial normalizado")
    tipo_cpc: str = Field(..., description="Classificacao de ato CPC")
    sha256: str = Field(..., min_length=64, max_length=64, description="Hash criptografico SHA-256")
    suporte: Literal["DOCUMENTADO", "INDICIADO", "NAO_INDICIADO"] = Field(...)
    weight: float = Field(..., ge=0.0, le=1.0)
    evidence_level: Literal["OFICIAL", "ALTA", "MEDIA", "INDICE", "BAIXA"]
    timestamp_iso: datetime = Field(default_factory=datetime.utcnow)
    pydantic_valid: bool = True
    is_duplicate: bool = False

    @field_validator("tipo_cpc")
    @classmethod
    def validar_minuta(cls, v: str, info):
        folder = info.data.get("folder")
        if folder == "02_Minutas_E_Rascunhos" and v == "DESPACHO":
            raise ValueError("Minuta nunca pode ser qualificada como DESPACHO")
        return v
```

---

## 2. Golden Dataset e Ground-Truth Forense

O Golden Dataset reside em `AI/skills/mcp-fs-pydantic-org/assets/eval/goldenset.json` e contem a verdade de referencia imutavel:

1. **4 Processos Centrais**:
   - `10153/24.7T8LSB`: Inexigibilidade de € 105.633 face a retencao na fonte TPA de € 52.285 (Art. 729 CPC e Art. 847 CC).
   - `23142/22.7T8LSB`: Nulidade da citacao perante morada fiscal ativa e descontos SS (Art. 188 e 191 CPC).
   - `15547/26.0T8LSB`: Propriedade plena e litisconsorcio necessario de Teresa de Jesus Martins (Art. 1311, 892 CC e Art. 33 CPC).
   - `3719/25.0T8LSB`: Tutela cautelar urgente e primazia da habitacao/posse (Art. 362 CPC e Art. 65 CRP).
2. **Casos Negativos de Bloqueio**:
   - Proibicao de promover minutas a despachos judiciais.
   - Proibicao de utilizar indices como prova documental.
   - Proibicao de alegacoes unilaterais marcadas como `DOCUMENTADO`.
   - Regra 0 Criptografica: 100% de suporte por hash SHA-256.

---

## 3. Eval Pipeline Deterministico

O pipeline de avaliacao compara a saida do scanner contra o Golden Dataset com 5 metricas obrigatorias:

- **Precision**: $\ge 0.95$
- **Recall**: $\ge 0.90$
- **F1-Score**: $\ge 0.92$
- **Pydantic Validity**: $1.00$ ($100\%$)
- **Zero Rule Violations**: $0$ violacoes negativas permitidas

---

## 4. Reasoning Contract (T0 a T8) e Chain of Prompt (P0 a P8)

### Reasoning Contract (Etapas Operacionais Obrigatorias)
- **T0**: Verificacao de fronteira (`C:\Users\Yokozuna\Dev`) e modo Read-Only.
- **T1**: Identificacao de entidade: Ficheiro / Ato / Facto / Codigo / SHA-256.
- **T2**: Classificacao deterministica estrita por padroes (`patterns.py`).
- **T3**: Validacao de schema Pydantic simples.
- **T4**: Validacao de schema Pydantic complexo (hashes cruzados e caminhos).
- **T5**: Construcao da cadeia temporal por processo + antecedentes CPC.
- **T6**: Motor de 4 Camadas: **Prova $\times$ Alegacao $\times$ Norma $\times$ Decisao/Impacto**.
- **T7**: Enquadramento em escala multi-processo e multi-ano (2014-2026).
- **T8**: Emissao estruturada para `OUTPUT_CENTRALIZADO/` e `_index/`.

### Chain of Prompt
- **P0**: MCP Filesystem Access Verification.
- **P1**: Inventario Exaustivo sem Invencoes.
- **P2**: Scanner Deterministico e Calculo de SHA-256.
- **P3**: Validacao Pydantic com Bloqueio Semantico.
- **P4**: Cadeias Processuais e Antecedentes.
- **P5**: Consolidacao de Pontos Factuais (`FACTO` vs `ALEGACAO`).
- **P6**: Motor de 4 Camadas de Relevancia Probatoria.
- **P7**: `legal-strategy` (ativada unicamente quando solicitado).
- **P8**: Gravacao e Sincronizacao Centralizada.

---

## 5. Os 6 Agentes Canonicos e Precedencias

| Pasta | Agente | Funcao | Peso | Nivel Prova |
|---|---|---|---|---|
| `00_Indice_E_MOCs` | `agente-indice-mocs` | Catalogo e navegacao (MOC) | 0.70 | INDICE |
| `01_PDFs_Oficiais` | `agente-pdfs-oficiais` | Atos formais + hash SHA-256 | **1.00** | OFICIAL |
| `02_Minutas_E_Rascunhos` | `agente-minutas` | Rascunhos e notas (nunca despacho) | 0.25 | BAIXA |
| `03_Contratos_E_Acordos` | `agente-contratos` | Partes, clausulas, valores, datas | 0.95 | ALTA |
| `04_Processos_E_Pecas_Escritas` | `agente-pecas` | Pecas integrais + cadeia CPC | 0.98 | OFICIAL |
| `05_Correspondencia_E_Comunicacoes` | `agente-correspondencia` | De/Para/Data/Canal; FACTO vs ALEGACAO | 0.85 | MEDIA |

---

## 6. Frozen Judge (100/100) e MCP Gateway

O **Frozen Judge** (`frozen_judge.py`) audita o sistema sob 5 criterios de 20 pontos cada:
1. **Regra 0 Criptografica**: 100% de cobertura por hash SHA-256.
2. **Ordenacao Cronologica Mestre**: Datas normalizadas ISO-8601 em `_index/cronologia_mestre.jsonl`.
3. **Isolamento Estrito de Minutas**: Zero minutas qualificadas como despacho ou documento provado.
4. **Cobertura dos 4 Processos Centrais**: `3719`, `10153`, `23142`, `15547`.
5. **Validacao das 5 Clausulas Petreas Juridicas**: Inexigibilidade, nulidade, propriedade, tutela e integridade material.

Toda decisao aprovada gera registo no [`audit_ledger.jsonl`](file:///c:/Users/Yokozuna/Dev/OUTPUT_CENTRALIZADO/02_DADOS_ESTRUTURADOS/audit_ledger.jsonl) com veredito `APPROVED_ROUTING_AUTHORIZED`.

---

## 7. Output Centralizado e Scripts de Execucao

Todos os outputs sao unificados em:
[`C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\`](file:///c:/Users/Yokozuna/Dev/OUTPUT_CENTRALIZADO/)
- `01_INDEX_E_RELATORIOS/`
- `02_DADOS_ESTRUTURADOS/`
- `03_LOGS_AUDITORIA/`
- `04_DOCUMENTOS_CITIUS_E_PECAS/`
- `INDEX_GERAL_OUTPUTS.md`

### Como Executar

```powershell
# Sessao de 15 Minutos de Reuniao e Consolidacao (PowerShell)
.\AI\PowerShell\Scripts\Start-15MinSession.ps1

# Daemon Continuo (Watchdog + Fatos + Otimizacao)
.\AI\PowerShell\Scripts\Start-AutoSystem.ps1

# Painel Interativo Batch
.\iniciar_agentes_workflows.bat
```
