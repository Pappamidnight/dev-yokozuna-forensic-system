# WORKFLOW — PC 3719/25.0T8LSB (TRL)
# Prioridade: ★ MAXIMO
# Tipo: Contra-alegacoes ao recurso de Teresa

---

## ESTADO

| Campo | Valor |
|:---|:---|
| Sentenca | 27/01/2026 — TOTALMENTE IMPROCEDENTE |
| Sentenca reconhece | "ocupacao antiga, consentida e estavel" (p. 10) |
| Teresa recorreu | Sim — TRL |
| Contra-alegacoes | Respondidas 17/03/2026 (§1-§16 completados) |
| Mandatario | JNA (Dr. Nabais) |

---

## 3 LINHAS DEFESA (independentes)

### LINHA 1 — FORMAL (rejeicao recurso)
- Art. 640. CPC — onus especificacao nao cumprido
- Referencias temporalmente impossiveis
- Conclusoes = mera repeticao motivacao
- Argumentos: ARG-3719-F1/F2/F3

### LINHA 2 — CONTRADITORIO
- 48 recibos retroactivos (15/12/2023) → reconhecimento
- WhatsApp 18/06/2024 → Teresa reconhece residente
- Discrepancias renda/impostos
- 2 apartamentos vazios → sem urgencia real
- Alegacao roubo electricidade/gatos sem prova
- Sentenca p. 10: ocupacao consentida
- Argumentos: ARG-3719-C1 a C6

### LINHA 3 — SUBSTANTIVA
- Credito €274.699,32 documentado
- Direito retencao art. 754. CC
- 7 tipos credito (bd/FINANCEIRO.md)
- Nuno credor liquido +€584.970
- Argumentos: ARG-3719-S1 a S4

---

## PIPELINE MWP (4 stages)

### Stage 1 — Pesquisa
Inputs: bd/CRONOLOGIA.md, bd/PROVAS.md, bd/FINANCEIRO.md
Output: Factos seleccionados + refs documentais
Estado: COMPLETO

### Stage 2 — Argumentacao
Inputs: skills/LEGISLACAO.md, bd/JURISPRUDENCIA.md, bd/ARGUMENTOS.md
Output: Esqueleto 3 linhas + normas + jurisprudencia
Estado: COMPLETO

### Stage 3 — Redaccao
Inputs: config/ESTRUTURA_PECA.md, config/VOZ_TRIBUNAL.md, config/TERMOS_PROIBIDOS.md
Output: §1-§16 redigidos
Estado: COMPLETO (17/03/2026)

### Stage 4 — Revisao
Inputs: hooks/SEGURANCA.md, hooks/VALIDACAO.md
Output: Peca validada
Estado: EM COORDENACAO COM JNA

---

## CROSS-STAGE VERIFY

Apos cada stage, verificar:
- Consistencia com sentenca (p. 1-15)
- Zero termos proibidos
- Varela constraint (R7) respeitado
- Cada facto com ref

---

## PROXIMOS PASSOS

1. Coordenacao com JNA para versao final
2. Submissao TRL
3. Preparar resposta a eventuais questoes TRL

---

## DEPENDENCIAS

- WF_ARRESTO.md — preparar em paralelo (★★)
- WF_CENTENARIO.md — contra-alegacoes entregues 18/03
- bd/FINANCEIRO.md — valores credito actualizados

Versao: 9.0
