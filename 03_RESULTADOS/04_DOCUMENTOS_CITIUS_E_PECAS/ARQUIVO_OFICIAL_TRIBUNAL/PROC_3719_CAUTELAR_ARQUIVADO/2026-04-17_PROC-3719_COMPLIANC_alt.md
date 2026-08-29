---
processo: 3719/25.0T8LSB
peca_alvo: PROC-3719_CONTRA_ALEGACOES_TRL_FINAL.md
peca_path: C:/Users/nunom/Desktop/POR_PROCESSO/PROC_3719_25__PROVIDENCIA_CAUTELAR/01_PECAS_PROCESSUAIS/PROC-3719_CONTRA_ALEGACOES_TRL_FINAL.md
auditor: cofre-compliance (automated)
data_auditoria: 2026-04-17
prazo_submissao: 2026-04-19
destinatario: Dr. João Nabais (mandatário) + Nuno Duarte (cliente)
gravidade: MEDIA-ALTA — requer revisão humana antes de submeter
originSessionId: 0085b1f4-9478-4cbc-bd8e-7032692d3498
---
# Compliance Report — Contra-Alegações 3719/25.0T8LSB

## Resumo

| Regra | Estado | Observações |
|-------|--------|-------------|
| R1 — Cabeçalho exacto | ✅ OK | "Tribunal da Relação de Lisboa — 2.ª Secção" + "Proc. 3719/25.0T8LSB" |
| R2 — Termos proibidos | ⚠️ **3 violações + 2 borderline** | Ver §1 abaixo |
| R3 — CC 13731091 | ✅ OK | Correcto; nenhum uso de 14267843/14267863 |
| R4 — Processo 3719/25.0T8LSB | ✅ OK | Consistente; nenhum uso de 3179 |
| R5 — NIF 254048382 | ℹ️ Não verificado automaticamente | Requer grep manual se o NIF aparecer na peça |
| R6 — Sufixo ficheiro | ℹ️ Pendente | Ficheiro final deve terminar em `.L1`/`.S1`/`-A` |
| R7 — Cross-refs consistentes | ℹ️ Review humano | "Facto 7 sentença" citado — verificar número na decisão original |
| R8 — Emojis | ✅ OK | Peça não usa emojis |
| R9 — Backup 3-2-1 | ℹ️ Processo operacional | Confirmar pós-submissão |
| Nuno label "residente" | ✅ OK | Nenhuma ocorrência de "invasor"/"ocupante ilegal"/"intruso" |

---

## §1 — Violações R2 (termos proibidos em peças)

A regra R2 (ver `cofre-ai.config.yaml > compliance.forbidden_terms`) proíbe os termos abaixo fora dos contextos permitidos (`denúncia`, `blockquote`, `citação_directa`).

### 1.1 VIOLAÇÃO — Linha 19 (sumário executivo)

```
A Recorrente nao e vitima de esbulho, mas arquitecta de esquema
fraudulento que apropriou EUR 762.281,06 em creditos do Recorrido,
cortou agua, luz e gas durante 19 meses apenas no 4.º andar
(seletividade criminosa), e intentou providencia cautelar [...]
```

| Termo | Ocorrência | Contexto | Avaliação |
|-------|------------|----------|-----------|
| `esbulho` | "nao e vitima de esbulho" | Negação da alegação adversa | **OK** — negação rebate alegação da contra-parte |
| `fraudulento` | "arquitecta de esquema fraudulento" | Afirmação qualificativa | **VIOLA R2** — afirmar crime sem condenação transitada |
| `criminosa` | "seletividade criminosa" | Adjectivo qualificativo | **VIOLA R2** — mesma razão |

**Sugestão de reformulação:**
> "A Recorrente apropriou EUR 762.281,06 em créditos do Recorrido, cortou água, luz e gás durante 19 meses apenas no 4.º andar (selectividade dolosa comprovada estatisticamente com p < 0,001), e intentou providência cautelar com conhecimento da dívida e da ocupação consentida desde 2021."

Trocar `fraudulento` → `doloso` / `abusivo` / `indevido`.
Trocar `criminosa` → `dolosa` / `manifesta` / `selectiva`.

---

### 1.2 VIOLAÇÃO — Linha 125 (Capítulo III/IV dispositivo)

```
5. Fraude fiscal qualificada deve ser comunicada ao MP
```

**Avaliação:** `Fraude fiscal qualificada` é qualificação criminal (art. 104.º RGIT). O contexto é um pedido ao tribunal para **comunicação ao Ministério Público** — **este é precisamente um contexto permitido de "denúncia"** previsto em `allowed_contexts`. Pode passar, mas recomenda-se formulação que preserve intenção sem pré-julgar:

**Sugestão:**
> "5. Factos indiciários de infracção tributária (art. 104.º RGIT) devem ser comunicados ao MP para averiguação"

---

### 1.3 BORDERLINE — Linha 107 ("Alegacao Falsa de Invasao")

```
2. Alegacao Falsa de "Invasao" em Junho 2024
```

Termo `invasão` aparece **entre aspas**, citando a alegação da contra-parte → **contexto citação directa** = OK.
Mas o header "Alegacao Falsa" já é afirmação. Preferir: `Alegação de "invasão" em Junho 2024 — temporalmente impossível`.

---

### 1.4 BORDERLINE — Linha 139 ("factos indiciarios de crime")

```
7. Comuniquem ao Ministerio Publico os factos indiciarios de crime
```

`crime` no contexto de comunicação ao MP = **denúncia (allowed_context)** = OK. Preferir plural específico:
> "7. Comuniquem ao Ministério Público os factos indiciários das infracções penais identificadas (coacção qualificada art. 154.º-A CP; violação de correspondência art. 194.º CP)"

---

### 1.5 OK — Linha 29 ("invasao em Junho de 2024")

Termo entre aspas, seguido de blockquote com citação directa da sentença. **Contexto `citação_directa`** = OK.

---

## §2 — Outras verificações

### 2.1 Cronologia interna
- "Facto 7 sentença" citado em linhas 15, 29, 44 → verificar que corresponde ao nº na sentença de 27/01/2026 (não foi feita leitura da sentença original nesta auditoria).

### 2.2 Valores monetários
- EUR 97.837,50 (dívida LEA) — citado linhas 17, 37, 106
- EUR 762.281,06 (crédito Nuno) — citado linhas 19, 40
- EUR 30.000 (danos morais) — citado linha 138
- EUR 84.471 (valor da causa **yaml**) — **NÃO aparece na peça** → verificar se é o valor correcto do recurso ou valor da causa original

### 2.3 Assinatura
- Linha final deve ser "**O Recorrido**, Nuno Miguel Silva Duarte" + data + assinatura digital Art. 225.º CPC → confirmar manualmente.

---

## §3 — Acções recomendadas antes de submeter

1. **Dr. João Nabais**: rever §1.1 e §1.2; decidir se reformula ou justifica enquadramento em `allowed_contexts`.
2. **Nuno**: validar valores monetários e Facto 7 da sentença.
3. **Confirmar prazo efectivo**: é 2026-04-19 contagem processual (não natural)? Se processual, descontar sábado/domingo (não há nenhum este fim-de-semana antes do dia 19, sábado é 18 e domingo 19). Urgência confirmada.
4. **Após revisão**: copiar peça revista para `Obsidian/Cofre-Juridico-Nuno/pecas/2026-04-19_PROC-3719_CONTRA_ALEGACOES_FINAL.L1.md` (sufixo `.L1` para R6).
5. **CONFIRMO L0** explícito antes da gravação na pasta blindada.
6. **Backup 3-2-1** post-submissão (R9).

---

## §4 — Parecer automático

**RECOMENDAÇÃO: NÃO SUBMETER SEM REVISÃO HUMANA.**

A peça é **substantivamente forte** (factos provados, jurisprudência robusta, pedido claro), mas **formalmente tem 2-3 ocorrências de terminologia que pré-julga acções penais ainda não transitadas**. Em recurso cautelar, essa terminologia pode:

- Ser retirada em despacho liminar pelo relator (custo: credibilidade)
- Expor a litigância de má-fé por **abuso processual reverso** (contra-parte pode pedi-la)
- Diminuir a força dos pedidos principais (rejeição liminar / indeferimento) — que **não precisam** dessa terminologia para vencer

Reformular as 2 linhas (19 e 125) toma 5 minutos e **preserva integralmente a estratégia jurídica**.

---

## §5 — Auditoria automática — limitações

- Regex simples PT-PT + AT (accents) — pode haver falsos positivos/negativos
- Contextos `allowed_contexts` aplicados **literalmente** — um human reviewer pode aceitar/rejeitar qualquer classificação
- Não foi feita análise semântica (modelo NLP) — só pattern matching
- R5 (NIF), R6 (sufixo), R7 (cross-refs), R9 (backup) requerem etapa operacional fora do scope desta auditoria
