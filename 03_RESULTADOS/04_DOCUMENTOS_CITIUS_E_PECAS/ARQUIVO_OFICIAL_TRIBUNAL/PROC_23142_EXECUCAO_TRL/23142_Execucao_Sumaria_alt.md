# PROCESSO 23142/22.7T8LSB — Execucao Sumaria (Ag. Execucao)

## 1. CABECALHO

| Campo | Valor | Fonte |
|-------|-------|-------|
| Numero | 23142/22.7T8LSB | `config_processamento.yaml:162` |
| Short | 23142 | `config_processamento.yaml:163` |
| Tribunal | Tribunal Judicial da Comarca de Lisboa — Juiz 4 | `config_processamento.yaml:164`; `Logs/outputs/lacunas_cronologicas_20260516_180635.json:248` |
| Tipo | Execucao Sumaria (Ag. Execucao) | `config_processamento.yaml:166` |
| Valor | EUR 31.855,00 | `config_processamento.yaml:168` |
| Estado | Com Decisao — Recurso TRL | `config_processamento.yaml:167` |
| Periodo documentos | 2022-10-05 a 2026-03-18 | `config_processamento.yaml:169-170` |
| Juiz de Direito | Carla Matos | `Logs/outputs/lacunas_cronologicas_20260516_180635.json:240-250` |
| Recurso | 23142/22.7T8LSB.L1 — TRL 2a Seccao | `config_processamento.yaml:186-190` |
| Agente Execucao | Luisa Santos (Cedula 5840) | `irregularities_report.json:13,47-48` |

---

## 2. INTERVENIENTES PROCESSUAIS

### Partes

| Nome | Qualidade | Representacao | NIF/CC | Fonte |
|------|-----------|---------------|--------|-------|
| Centenario Unipessoal, Lda. | Exequente / Credora / Recorrente | Dr. Varela de Matos (Ced. 9878L) | NIF 510016723 | `config_processamento.yaml:172-180,612-641` |
| Nuno Miguel Silva Duarte | Executado / Recorrido | Dr. Nuno Ferreira Leite Rua (FLRP) | NIF 254048382, CC 13731091 | `config_processamento.yaml:172-190,280-285` |
| Lisbon Experience — Adm. Imoveis, Lda. (LEA) | Executada | — | NIF 510287549 | `config_processamento.yaml:172-180,293-299` |
| Filipe Jose Rodrigues Delgado | Executado | — | unknown_filipe | `config_processamento.yaml:172-180,288-291` |

### Mandatarios

| Nome | Funcao | Cedula | Email | Representa | Fonte |
|------|--------|--------|-------|------------|-------|
| Varela de Matos | Advogado | 9878L | varela.de.matos@adv.oa.pt | Centenario | `config_processamento.yaml:612-641` |
| Nuno Ferreira Leite Rua | Advogado (FLRP) | — | nflrua@flrp.pt | Nuno Duarte | `config_processamento.yaml:633-641` |
| Luisa Santos | Agente Execucao | 5840 | 5840@solicitador.net | — | `config_processamento.yaml:618-631` |

---

## 3. MAPA DE DOCUMENTOS

### Documentos Originais (raiz do projeto)

| ID | Nome Ficheiro | Tipo | Data | Tamanho | SHA-256 | has_text | Fonte |
|----|--------------|------|------|---------|---------|----------|-------|
| 011 | PROC_23142-22.7T8LSB_SENTENCA_DATA_2023-04-24_CENTENRIO_UNIPESSOAL_LDA_NUNO_MIGUEL_SILVA_DUARTE_E_OUTROS_011.pdf | SENTENCA | 2023-04-24 | 1.554.765 | c10b444b | Sim | `_index.json:160-173` |

### Duplicados em PROCESSOS/23142/

| Nome | SHA-256 | Original |
|------|---------|----------|
| PROC_23142_SENTENCA_DATA_2023-04-24_c10b444b.pdf | c10b444b | DOC 011 |

### Documentos Relacionados (fora de 23142 mas com factos do processo)

| ID | Nome | Tipo | Processo Indexado | Relevancia |
|----|------|------|-------------------|------------|
| 009 | DOC_FATURARECIBO_009.pdf | FATURA_RECIBO | (vazio) | Possivel fatura LEA EUR 82.722 (IR-E.1) |
| 010 | DOC_FATURARECIBO_010.pdf | FATURA_RECIBO | (vazio) | Possivel fatura LEA |

### Documentos SCAN (sem OCR, sem texto extraivel)

31 PDFs SCAN_060-090 com 8 hashes unicos. Nenhum atribuido a 23142.

---

## 4. CRONOLOGIA DE EVENTOS

### Legenda: `[NIVEL]` = CONFIRMADO / INFERIDO / PENDENTE

| Data | Evento | Documento / Fonte | Nivel |
|------|--------|-------------------|-------|
| **2021-12-09** | Contrato entre Centenario e Executados. Valor EUR 11.094,00 em prestacoes de EUR 995,47. Varela certificou presenca de Renato Gil. | `Logs/outputs/lacunas_cronologicas_20260516_180635.json:287-289,302-304` | CONFIRMADO |
| **2021-12-09** | Varela certificou presenca de Renato Gil. Renato so assinou a 22/01/2022 (44 dias depois). | `config_processamento.yaml:527-607` (IR-A.2) | CONFIRMADO |
| **2021-12-30** | 1a prestacao (EUR 995,47) vencida e nao paga. Nenhuma prestacao foi paga. | `Logs/outputs/lacunas_cronologicas_20260516_180635.json:302-304` | CONFIRMADO |
| **2022-09-19** | Procuracao datada retroativamente 283 dias para ato de 09/12/2021. | `config_processamento.yaml:527-607` (IR-A.3) | CONFIRMADO |
| **2022-09-21** | Registo de entrada (valor taxa: EUR 51,00). Fim da lacuna de 265 dias. | `Logs/outputs/lacunas_cronologicas_20260516_180635.json:15-16,302` | CONFIRMADO |
| **2022-10-05** | Data primeiro documento do processo (YAML). | `config_processamento.yaml:169` | CONFIRMADO |
| **2022-10-12** | Varela apresentou requerimento executivo SEM titulo executivo e SEM procuracao. | `config_processamento.yaml:527-607` (IR-A.1) | CONFIRMADO |
| **2022-10-13** | Varela confessou "por lapso" a falta de titulo/procuracao. | `config_processamento.yaml:527-607` (IR-A.1) | CONFIRMADO |
| **2023-03-16** | Conclusao — indeferimento liminar do requerimento executivo. Assinado por Carla Matos, Juiz de Direito. | `Logs/outputs/lacunas_cronologicas_20260516_180635.json:268-274,278-282` | CONFIRMADO |
| **2023-04-20** | Conclusao — despacho. Assinado por Carla Matos. | `Logs/outputs/lacunas_cronologicas_20260516_180635.json:240-250` | CONFIRMADO |
| **2023-04-21** | Conclusao — despacho "o recurso como para os da causa. Notifique." Assinado por Carla Matos. | `Logs/outputs/lacunas_cronologicas_20260516_180635.json:253-266` | CONFIRMADO |
| **2023-04-24** | Certificacao Citius — notificacao da sentenca. Doc 011 (1.5MB). | `Logs/outputs/lacunas_cronologicas_20260516_180635.json:207-209`; `_index.json:165` | CONFIRMADO |
| **2023-07-04** | AE Luisa Santos: citacao Ref. Citius 36425114. Citou Filipe Delgado (co-executado, interesses antagonico) em vez de Nuno. Confessou "por lapso" Ref.437217551. | `config_processamento.yaml:527-607` (IR-C.1, IR-C.2) | CONFIRMADO |
| **2023-07-04** | Filipe Delgado interceptou citacao e ocultou de Nuno. | `config_processamento.yaml:527-607` (IR-D.1) | CONFIRMADO |
| **2023-07-19** | Varela admitiu em reuniao (audio gravado) ter redigido contrato com ambiguidade deliberada. | `config_processamento.yaml:527-607` (IR-A.4) | CONFIRMADO |
| **2024-01** | Fim da ocultacao — Filipe entregou citacao a Nuno (6 meses depois). | `config_processamento.yaml:527-607` (IR-D.1) | INFERIDO |
| **2026-03-18** | Data ultimo documento do processo (YAML). | `config_processamento.yaml:170` | CONFIRMADO |

### Emails Extraidos

| Email | Contexto | Fonte |
|-------|----------|-------|
| lisboa.execucao@tribunais.org.pt | Tribunal — 23142 | `emails_manipulados_20260516_180635.json:14-72` |
| varela.de.matos-9878l@advogados.oa.pt | Mandatario Centenario | `emails_manipulados_20260516_180635.json:74-78` |
| 5840@solicitador.net | AE Luisa Santos | `emails_manipulados_20260516_180635.json:86-90` |

---

## 5. FACTOS COMPROVADOS

### Facto 1: Contrato de prestacoes nao pagas
Em 09/12/2021, Centenario celebrou com os Executados um acordo no valor de EUR 11.094,00, dividido em prestacoes de EUR 995,47 cada. A primeira prestacao venceria a 30/12/2021. Nenhuma prestacao foi paga.
- **Fonte:** `Logs/outputs/lacunas_cronologicas_20260516_180635.json:287-289,302-304`

### Facto 2: Indeferimento liminar (16/03/2023)
A Juiz Carla Matos proferiu indeferimento liminar do requerimento executivo a 16/03/2023, por nao contender documento que importasse constituicao ou... (texto truncado).
- **Fonte:** `Logs/outputs/lacunas_cronologicas_20260516_180635.json:268-274,278-282`

### Facto 3: Decisao de 20-21/04/2023
A Juiz Carla Matos proferiu dois despachos: um a 20/04/2023 e outro a 21/04/2023 determinando "o recurso como para os da causa. Notifique."
- **Fonte:** `Logs/outputs/lacunas_cronologicas_20260516_180635.json:240-266`

### Facto 4: Agente de Execucao designada — Luisa Santos
A AE Luisa Santos (NIF 218469632, BI 11039123, Cedula 5840, Email: 5840@solicitador.net) aceitou a designacao.
- **Fonte:** `irregularities_report.json:13,47-48`

### Facto 5: Lacuna de 265 dias sem registos
Entre 2021-12-30 (vencimento da 1a prestacao) e 2022-09-21 (registo de entrada), nao existem documentos no repositorio.
- **Fonte:** `Logs/outputs/lacunas_cronologicas_20260516_180635.json:15-16`

---

## 6. IRREGULARIDADES

### Do YAML (config_processamento.yaml:527-607)

| ID | Facto | Data | Responsavel | Gravidade | Artigos |
|----|-------|------|-------------|-----------|---------|
| IR-A.1 | Requerimento executivo 12/10/2022 sem titulo executivo nem procuracao. Confessou "por lapso" 13/10/2022. | 2022-10-12 | Varela de Matos | ALTA | — |
| IR-A.2 | Varela certificou presenca de Renato Gil em 09/12/2021. Renato assinou 44 dias depois (22/01/2022). | 2021-12-09 | Varela de Matos | ALTA | — |
| IR-A.3 | Procuracao datada 19/09/2022 para ato notarial de 09/12/2021 (283 dias retroativa). | 2022-09-19 | Varela de Matos | ALTA | — |
| IR-A.4 | Varela admitiu em reuniao (19/07/2023 — audio gravado) ter redigido contrato com ambiguidade deliberada. | 2023-07-19 | Varela de Matos | ALTA | — |
| IR-C.1 | AE Luisa Santos: citacao 04/07/2023 (Citius 36425114) sem alegacoes recurso. Confessou "por lapso" Ref.437217551. | 2023-07-04 | Luisa Santos (AE) | ALTA | — |
| IR-C.2 | AE Luisa Santos entregou citacao a Filipe Delgado (co-executado, interesses antagonico, nao co-residente) em vez de Nuno. | 2023-07-04 | Luisa Santos (AE) | ALTA | — |
| IR-D.1 | Filipe interceptou citacao 04/07/2023 e ocultou de Nuno durante ~6 meses (Jul/2023 a Jan/2024). | 2023-07-04 | Filipe Delgado | ALTA | — |
| IR-E.1 | LEA emitiu fatura 1000002/2021 no valor de EUR 82.722 no NIF de Nuno sem conhecimento deste. | 2021-01-12 | LEA / Teresa Ribeiro | CRITICA | — |
| IR-E.3 | LEA emitiu 48 recibos retroativos de 2021-2023 num unico dia (15/12/2023). | 2023-12-15 | LEA | CRITICA | — |

### Da analise automatica (patrimonial_20260516_180635.json)

| ID | Tipo | Descricao | Gravidade | Artigos | Fonte |
|----|------|-----------|-----------|---------|-------|
| IR-2d6a4d89 | AUSENCIA_ATIVOS | Sentenca sem referencia a ativos para execucao | ALTA | 735 CPC | doc 011 |
| IR-fd330d0a | ASSINATURAS_MULTIPLAS | 3 assinaturas: 16/03, 20/04, 21/04/2023 no mesmo documento | MEDIA | 376 CC | doc 011 |

---

## 7. LACUNAS E PENDENTES

| Item | Descricao | Impacto |
|------|-----------|---------|
| Lacuna 265 dias | 2021-12-30 a 2022-09-21 — sem documentos no repositorio | MEDIO |
| Audio reuniao 19/07/2023 | Referido no YAML (IR-A.4) mas nao existe no repositorio | ALTO — prova de confissao |
| Faturas LEA EUR 82.722 | DOC_FATURARECIBO_009+010 — processo nao atribuido (3263?) | ALTO — documento financeiro critico |
| Abandono mandato Dr. Neto | 05/11/2025 (referido pelo utilizador, nao confirmado em docs do projeto) | PENDENTE — aguarda ficheiro externo |
| Indeferimento liminar completo | Texto do despacho de 16/03/2023 parcialmente extraido | BAIXO |

---

## 8. RELACOES COM OUTROS PROCESSOS

| De | Para | Tipo | Fonte |
|----|------|------|-------|
| 23142/22.7T8LSB | 23142/22.7T8LSB.L1 (TRL 2a Sec) | APPEALED_TO | `config_processamento.yaml:792-793` |
| 23142 | 3263202001090798? | FATURAS (possivel) | DOC_009+010 relacionados a LEA |

---

## 9. CHANGELOG

| Data | Versao | Alteracao | Fonte | Autor |
|------|--------|-----------|-------|-------|
| 2026-05-26 | v1 | Criacao inicial do dossier | — | opencode |
| 2026-05-26 | v2 | Corrigidas 13 refs partidas: `lacunas_cronologicas.json` -> `Logs/outputs/lacunas_cronologicas_20260516_180635.json` | `Logs/outputs/lacunas_cronologicas_20260516_180635.json` | opencode |
