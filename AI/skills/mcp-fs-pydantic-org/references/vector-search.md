# Motor de Busca Vetorial Factual (P4b)

O motor de busca vetorial factual complementa a validacao de atos processuais atraves de recuperacao semantica direcionada, sem substituir a identidade criptografica por hash SHA-256.

---

## 1. Topologia do Pipeline Vetorial

```
[P4: Cadeias Processuais] -> [P4b: Vector Indexing & Search] -> [P5: Pontos Factuais] -> [P6: 4 Camadas]
```

### 1.1 `VectorChunk`
- `chunk_id`: Identificador unico
- `process_id`: Numero do processo judicial (ex: `3719/25.0T8LSB`)
- `tipo_cpc`: Tipo de ato processual
- `sha256`: Hash de integridade do documento original
- `texto`: Conteudo textual indexado
- `embedding`: Vetor deterministico de 256 dimensoes

### 1.2 Regras de Filtragem
- **Similaridade Semantica $\neq$ Prova Material**: Um resultado de busca vetorial sem suporte documental e classificado como `PARCIAL` ou `INDICIADO`.
- **Filtros Rigorosos**: A pesquisa prioriza documentos de `01_PDFs_Oficiais` e `04_Processos_E_Pecas_Escritas` antes de consultar correspondencia ou minutas.
