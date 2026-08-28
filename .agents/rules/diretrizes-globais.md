# Diretrizes Globais Unificadas - Regras para Agentes e Workflows

**Versao**: 2.1.0 (Otimizada para Maximizacao de Resultados e Determinismo)  
**Ambiente**: `C:\Users\Yokozuna\Dev\`  
**Autoridade**: [AI/DIRETRIZES-GLOBAIS-DEV.md](file:///c:/Users/Yokozuna/Dev/AI/DIRETRIZES-GLOBAIS-DEV.md) e [AGENTS.md](file:///c:/Users/Yokozuna/Dev/AGENTS.md)

---

## 1. Principios de Operacao Inegociaveis

1. **Centralizacao Estrita de Outputs**:
   - Todo e qualquer ficheiro gerado, relatorio, JSON, log, analise ou script DEVE ser guardado exclusivamente em `C:\Users\Yokozuna\Dev\` (preferencialmente em `_index/` ou subpastas autorizadas de projetos).
   - **Proibicao Absoluta**: Nao gravar na raiz do utilizador, Desktop, Downloads ou Documents.

2. **Modo Auditoria / Read-Only por Defeito**:
   - As 6 pastas canonicas (`00_Indice_E_MOCs` ate `05_Correspondencia_E_Comunicacoes`) sao imutaveis. Ficheiros originais nunca sao movidos, renomeados ou sobrescritos.
   - Escrita automatizada (`auto_safe=True`) so e permitida no diretorio `Projects/Ficheiros Escritos Canónicos/_index/`.

3. **Zero Invencoes e Zero Emojis**:
   - O que nao tiver suporte em documento com hash SHA-256 e classificado como `NAO_INDICIADO` ou `needs_review`.
   - Proibicao total de emojis em codigos, logs, relatorios e comunicacoes oficiais (conforme PROTOCOL.md).

4. **Gate Humano**:
   - Acoes de gravacao em massa exigem validacao previa e confirmacao explicita.

---

## 2. Mapa dos 6 Agentes e Precedencias Probatorias

$$\mathbf{00\_Indice} \longrightarrow \mathbf{01\_PDFs} \longrightarrow \mathbf{04\_Pecas} \longrightarrow \mathbf{03\_Contratos} \longrightarrow \mathbf{05\_Correspondencia} \longrightarrow \mathbf{02\_Minutas}$$

| Pasta | Agente | Funcao | Peso | Nivel Prova | Regra de Precedencia |
|---|---|---|---|---|---|
| `00_Indice_E_MOCs` | `agente-indice-mocs` | Catalogo e navegacao (MOC) | 0.70 | INDICE | Mapeia, mas nao e prova material. |
| `01_PDFs_Oficiais` | `agente-pdfs-oficiais` | Atos formais + hash SHA-256 | **1.00** | OFICIAL | **Prevalece sobre minutas e alegacoes**. |
| `02_Minutas_E_Rascunhos` | `agente-minutas` | Rascunhos e apontamentos | 0.25 | BAIXA | **Nunca e despacho judicial**. |
| `03_Contratos_E_Acordos` | `agente-contratos` | Partes, valores e clausulas | 0.95 | ALTA | Prevalece sobre minutas nao assinadas. |
| `04_Processos_E_Pecas_Escritas` | `agente-pecas` | Pecas e cadeia CPC | 0.98 | OFICIAL | **Prevalece sobre alegacoes unilaterais**. |
| `05_Correspondencia_E_Comunicacoes` | `agente-correspondencia` | De/Para/Data/Canal | 0.85 | MEDIA | FACTO (com aviso) $\neq$ ALEGACAO. |

---

## 3. Pipeline Deterministico: T0–T8 e P0–P8

- **T0**: Fronteira `C:\Users\Yokozuna\Dev\` e segregacao de zonas.
- **T1**: Identificacao de entidade e calculo de hash SHA-256.
- **T2**: Classificacao deterministica por padroes (`patterns.py`).
- **T3**: Validacao semantica Pydantic v2 (datas ISO-8601, consistencia semantica).
- **T4**: Validacao de integridade de grafos e relacoes cruzadas.
- **T5**: Construcao da cadeia temporal por processo judicial (CPC).
- **T6**: Motor de 4 Camadas: $\text{Prova Material (1.00)} \times \text{Alegacao} \times \text{Artigo CPC} \times \text{Decisao/Valor}$.
- **T7**: Enquadramento multi-processo e multi-ano (2014–2026).
- **T8**: Emissao estruturada em JSON/JSONL para `_index/` + Gate Humano.
