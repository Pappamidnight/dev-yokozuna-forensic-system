# Contrato Formal dos Modelos Pydantic v2

**Autoridade**: [Backend/pydantic-ai/src/models_org.py](file:///c:/Users/Yokozuna/Dev/Backend/pydantic-ai/src/models_org.py)

---

## 1. Modelos Principais

### 1.1 `CanonicalRecord`
Registo atomico de ficheiro ou documento indexado.
- `path`: str (Caminho absoluto dentro de `C:\Users\Yokozuna\Dev\`)
- `relpath`: str (Caminho relativo a raiz)
- `sha256`: str (Hexadecimal de 64 caracteres)
- `kind`: `FACTO` | `ALEGACAO` | `DECISAO` | `PROVA_FISICA` | `FINANCEIRO` | `CODIGO` | `CONFIG` | `INDICE`
- `suporte`: `DOCUMENTADO` | `INDICIADO` | `NAO_INDICIADO`
- `process_id`: Optional[str] (Padrao `\d{1,6}/\d{2}\.\d[A-Z0-9]{2,8}`)
- `evidence_level`: `OFICIAL` | `ALTA` | `MEDIA` | `BAIXA` | `INDICE`
- `folder`: str
- `auto_safe`: bool (True apenas se gravado em `_index/`)

### 1.2 `AtoProcessual`
Ato juridico qualificado segundo o Código de Processo Civil (CPC).
- `tipo_cpc`: `CITACAO` | `NOTIFICACAO` | `DESPACHO` | `SENTENCA` | `ACORDAO` | `CONTESTACAO` | `RECURSO` | `AUTO_PENHORA` | `ATA_AUDIENCIA` | `CONTRATO` | `RASCUNHO` | `DOCUMENTO_DIVERSO`
- `process_id`: str
- `data_pratica`: Optional[str] (ISO-8601 `YYYY-MM-DD`)
- `autor_ato`: Optional[str] (ex: `TRIBUNAL`, `JUIZ`, `AGENTE_EXECUCAO`, `AUTOR`, `REU`)
- `antecedente_obrigatorio`: Optional[str]
- `lacuna_detetada`: bool
- `artigo_cpc`: Optional[str]

### 1.3 `OrganizationReport`
Relatorio global de execucao e metricas de auditoria.
- `total_files`: int
- `unique_hashes`: int
- `records`: List[CanonicalRecord]
- `counts_by_kind`: Dict[str, int]
- `counts_by_evidence_level`: Dict[str, int]
- `generated_at`: str (ISO-8601)
