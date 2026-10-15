# PRD — Product Requirements Document: Acervo Forense V8

**Versao**: 8.0.0 Canónica  
**Data**: 2026-10-15  
**Autoridade**: Yokozuna / Dev Forensic System  
**Objetivo**: Sistema Integrado de Custodia, Deduplicacao Atomica, Inspecao Probatoria e Defesa Juridica

---

## 1. Visao Geral do Produto

O **Acervo Forense V8** e uma plataforma de computacao forense e gestao probatoria desenhada para operar sobre grandes volumes documentais (centenas de milhares de ficheiros), garantindo custodia criptografica estrita, segregação absoluta entre dados originais e derivados, deduplicacao atomica sem perda de metadados e geracao automatizada de pecas de defesa juridica de alta fidelidade.

---

## 2. Problema e Objetivos de Negocio

### 2.1. Desafios Existentes
1. **Dispersao de Evidencias**: Dispersao de faturas, comprovativos bancarios, licencas, contratos e comunicacoes de WhatsApp ao longo de 10 anos de operacao (2014-2024).
2. **Poluicao e Redundancia**: Proliferacao de copias e transferencias entre maquinas gerando gigabytes de redundancia desnecessaria.
3. **Litigios Judiciais Multi-Frente**: Necessidade de sustentar posicoes juridicas nos Processos 15547/26.0T8LSB, 3719/24.3T8LSB, 20203/24.0T8LSB, 10153/24.6T8LSB e 23142/24.0T8LSB com base factual irrefutavel.
4. **Cadeia de Custodia**: Cumprimento escrupuloso dos requisitos da norma ISO/IEC 27037 (recolha, preservacao e analise de evidencia digital).

### 2.2. Objetivos Principais
- Garantir 100% de integridade criptografica (SHA-256) em toda e qualquer evidencia.
- Assegurar a separacao atomica e conservacao dos ficheiros originais.
- Prover motor de pesquisa de latencia sub-milisegundo via Everything HTTP API.
- Gerar dossiers e matrizes de refutacao cabal contra alegacoes judiciais de terceiros.

---

## 3. Perfis de Utilizadores e Personas

- **Operador Forense**: Responsavel por acionar pipelines de inventario, extracao de entidades e sanitizacao de duplicados.
- **Auditor de Seguranca (Sentinel)**: Valida hashes, detecta alteracoes nao autorizadas e assegura o modo read-only de pastas sensiveis.
- **Mandatario Judicial / Agente-Pecas**: Extrai pecas, timelines, quadros comparativos e articulados processuais fundamentados.

---

## 4. Requisitos Funcionais (RF)

| ID | Requisito | Criterio de Aceitacao |
|---|---|---|
| **RF-01** | Inventario Everything HTTP | Comunicacao transparente com Everything 1.5 na porta 8080 em formato CSV/JSON; banimento definitivo de `es.exe`. |
| **RF-02** | Deduplicacao Atomica (1 Tipo = 1 Decisao) | O motor processa cada tipo documental (PDF, Imagens, Audio, Video, Excel, Word) de forma isolada, gerando `originais_<tipo>.csv`, `duplicados_<tipo>.csv` e `manifesto_<tipo>.json`. |
| **RF-03** | Preservacao de Metadados de Custodia | Registo imutavel de hash SHA-256, tamanho em bytes, data de criacao/modificacao e carimbo temporal ISO-8601. |
| **RF-04** | Protecao de Memorias e Altar Sensivel | O diretorio `00_ALTAR_MEMORIAS_PROTEGIDAS_FAMILIA_E_ANIMAIS` e blindado contra delecao, alteracao ou inclusao em repositorios de codigo. |
| **RF-05** | Compilacao de Pecas de Defesa | Integracao automatica entre schemas YAML de prova (`gestao_provas/`) e pecas processuais markdown (`caso_15547/docs/`). |

---

## 5. Requisitos Nao Funcionais (RNF)

- **RNF-01 (Seguranca)**: Politica Zero Emojis em relatorios, commits e pecas judiciais formais.
- **RNF-02 (Desempenho)**: Indexacao e filtragem de 50.000 ficheiros em menos de 10 segundos via Everything HTTP e Polars/Rust.
- **RNF-03 (Imutabilidade)**: Ficheiros de prova original residem em modo de leitura estrita (`Read-Only`).
- **RNF-04 (Resiliencia)**: Tratamento obrigatorio de excecoes I/O (`PermissionError`, `OSError`) com deflexao silenciosa sem abortar execucoes em lote.
- **RNF-05 (Compatibilidade)**: Operacao hibrida Windows 11 nativo e subprocessos WSL2 para ferramentas forenses especializadas.

---

## 6. Criterios de Sucesso e Metricas

- **Taxa de Falsos Positivos de Deduplicacao**: 0%. Nenhum ficheiro com conteudo distinto pode ser rotulado como duplicado.
- **Cobertura Factual nas Refutacoes**: 100% dos articulados juridicos suportados por documento com hash SHA-256 auditavel.
- **Zero Ficheiros Lixo em Git**: Repositorio de controlo de versoes restrito estritamente a codigo-fonte, configuracoes e documentacao estruturada.
