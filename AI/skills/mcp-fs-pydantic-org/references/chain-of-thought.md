# Chain of Thought (T0 a T8) - Especificacao Operacional

Este documento detalha as etapas de raciocinio obrigatorias para todos os agentes de IA que operam no acervo canonico e no ecossistema Dev.

---

## Tabela Geral T0 a T8

| Etapa | Designacao | Raciocinio e Restricoes Obrigatorias |
|---|---|---|
| **T0** | **Fronteira e Zona** | O agente valida se o caminho reside em `C:\Users\Yokozuna\Dev\`. Identifica a zona (`00_Indice_E_MOCs` ate `05_Correspondencia_E_Comunicacoes` ou `_index/`). Ficheiros fora de `Dev/` sao imediatamente rejeitados. |
| **T1** | **Entidade e SHA-256** | O agente determina a natureza do ficheiro (Ato, Facto, Alegacao, Contrato, Codigo). Para ficheiros de prova, calcula ou recupera o hash SHA-256 hex de 64 caracteres. |
| **T2** | **Classificacao Deterministica** | A classificacao e feita estritamente com base em padroes de nomenclatura e conteudo formal (`patterns.py`), sem deducoes especulativas. |
| **T3** | **Validacao Pydantic Simples** | Aplicacao do modelo `CanonicalRecord`: validacao de datas ISO-8601, consistencia semantica (ex: `ALEGACAO` nunca pode ser `DOCUMENTADO`; `FACTO` exige suporte real). |
| **T4** | **Validacao Pydantic Complexa** | Verificacao de integridade cruzada de hashes, contagens globais de ficheiros e volumes de dados. Proibicao de `auto_safe=True` fora de `_index/`. |
| **T5** | **Cadeia Temporal e CPC** | Agrupamento de atos por processo judicial (ex: `3719/25.0T8LSB`), determinando ordem cronologica, notificacoes antecedentes e deteccao de lacunas procedimentais. |
| **T6** | **Motor de 4 Camadas** | Cruzamento quadridimensional: **Prova Material (1.00/0.95)** $\times$ **Alegacao da Parte** $\times$ **Artigo do CPC/Legislacao** $\times$ **Decisao / Prejuizo Financeiro**. |
| **T7** | **Escala e Conexao** | Integracao multi-processo e multi-temporal (2014–2026), rastreando conexoes de partes, garantias, arrestos e dividas conexas. |
| **T8** | **Output e Gate Humano** | Persistencia estrita em formato JSON/JSONL dentro de `_index/`. Ficheiros canonicos nunca sao movidos. Acoes de escrita em massa exigem validacao humana. |

---

## Proibicoes Expressas
1. **Zero Invencoes**: Proibido inventar datas, numeros de processo ou certidoes nao documentadas.
2. **Nao Promover Rascunhos**: Minutas em `02_Minutas_E_Rascunhos` nunca podem ser tratadas como despachos oficiais.
3. **Nao Declarar Nulidades sem Base**: Toda a alegacao de nulidade processual deve indicar expressamente a lacuna do ato ou vicio formal comprovado.
