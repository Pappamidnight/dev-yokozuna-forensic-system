# PROCESSO 10153/24.7T8LSB — Execucao (Unicre)

## 1. CABECALHO

| Campo | Valor | Fonte |
|-------|-------|-------|
| Numero | 10153/24.7T8LSB | `config_processamento.yaml:238` |
| Short | 10153 | `config_processamento.yaml:239` |
| Tribunal | Tribunal Judicial da Comarca de Lisboa | `config_processamento.yaml:240` |
| Tipo | Execucao Sentenca proprios autos | `config_processamento.yaml:241` |
| Valor | Nao especificado (diferente de 20203: EUR 3.605,21) | PENDENTE |
| Estado | **Pendente — Suspensa (Embargos)** | `config_processamento.yaml:242` |
| Periodo | 2024-04-18 a 2025-10-23 | `config_processamento.yaml:244-245` |
| Descricao | Execucao — Unicre (Exequente) vs Nuno Miguel Silva Duarte (Executado) | `config_processamento.yaml:246` |
| Apenso | 10153/24.7T8LSB-A — Embargos de Executado | `config_processamento.yaml:253-261` |

---

## 2. INTERVENIENTES PROCESSUAIS

### Partes Principais

| Nome | Qualidade | Representacao | NIF | Fonte |
|------|-----------|---------------|-----|-------|
| Unicre — Instituicao Financeira de Credito, S.A. | Exequente | — | unknown_unicre | `config_processamento.yaml:248-251` |
| Nuno Miguel Silva Duarte | Executado | — | 254048382 | `config_processamento.yaml:253-256` |

### Apenso A — Embargos de Executado

| Nome | Qualidade | Estado | Fonte |
|------|-----------|--------|-------|
| Nuno Miguel Silva Duarte | Embargante | Pendente | `config_processamento.yaml:258-261` |
| Unicre — Instituicao Financeira de Credito, S.A. | Embargado | Pendente | `config_processamento.yaml:258-261` |

---

## 3. MAPA DE DOCUMENTOS

**Nao existem documentos PDF deste processo no repositorio do projeto.**

O `_index.json` nao contem qualquer ficheiro com processo `10153`. O `config_processamento.yaml` e a unica fonte de dados.

---

## 4. CRONOLOGIA DE EVENTOS

| Data | Evento | Fonte | Nivel |
|------|--------|-------|-------|
| **2024-04-18** | Data primeiro documento do processo | `config_processamento.yaml:244` | CONFIRMADO |
| **2024** (estimado) | Instauracao da execucao com base na sentenca transitada de 20203/22.6T8LSB | `config_processamento.yaml:794-795` (GEROU_EXECUCAO) | INFERIDO |
| **2025-10-23** | Data ultimo documento — admissao liminar dos embargos de executado e suspensao da execucao | `config_processamento.yaml:242,245,258-261` | CONFIRMADO |

---

## 5. FACTOS COMPROVADOS

### Facto 1: Execucao da sentenca da acao 20203
A Unicre instaurou execucao contra Nuno Duarte com base na sentenca transitada do processo 20203/22.6T8LSB (chargebacks TPA, valor EUR 3.605,21). A execucao corre por apenso ao processo principal.
- **Fonte:** `config_processamento.yaml:219-261`; relacao GEROU_EXECUCAO em `config_processamento.yaml:794-795`

### Facto 2: Suspensa por embargos (23/10/2025)
A execucao foi suspensa por admissao liminar dos embargos de executado (apenso A, art. 733 CPC). Estado atual: Pendente.
- **Fonte:** `config_processamento.yaml:242,258-261`

### Facto 3: Embargos pendentes sem decisao
O apenso de embargos (10153/24.7T8LSB-A) encontra-se pendente desde 23/10/2025 sem atualizacao registada no repositorio. Nao ha documentos dos embargos.
- **Fonte:** `config_processamento.yaml:253-261`

---

## 6. RELACOES COM OUTROS PROCESSOS

| De | Para | Tipo | Fonte |
|----|------|------|-------|
| 10153/24.7T8LSB | 10153/24.7T8LSB-A | HAS_EMBARGOS | `config_processamento.yaml:796-797` |
| 20203/22.6T8LSB | 10153/24.7T8LSB | GEROU_EXECUCAO | `config_processamento.yaml:794-795` |
| 10153/24.7T8LSB | 23142/22.7T8LSB | MESMO_EXECUTADO (Nuno Duarte) | INFERIDO |

---

## 7. LACUNAS E PENDENTES

| Item | Descricao | Urgencia |
|------|-----------|----------|
| Documentos em falta | Nao existem PDFs — gap de digitalizacao total | ALTA |
| Estado dos embargos | Pendente desde 23/10/2025 sem atualizacao | MEDIA |
| Valor em execucao | Nao especificado — diferente do valor de 20203 (EUR 3.605,21) | BAIXO |
| Agente de Execucao | Nao identificado no YAML | BAIXO |

---

## 8. CHANGELOG

| Data | Versao | Alteracao | Fonte | Autor |
|------|--------|-----------|-------|-------|
| 2026-05-26 | v1 | Criacao inicial do dossier | — | opencode |
| 2026-05-26 | v2 | Adicionada cronologia, factos detalhados, relacoes, lacunas | `config_processamento.yaml` | opencode |
