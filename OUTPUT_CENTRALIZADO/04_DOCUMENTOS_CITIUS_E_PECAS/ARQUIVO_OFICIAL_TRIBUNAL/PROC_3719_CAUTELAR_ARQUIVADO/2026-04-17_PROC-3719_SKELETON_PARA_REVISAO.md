---
processo: 3719/25.0T8LSB
label: Centenário — Providência Cautelar (recurso)
tipo_peca: CONTRA-ALEGAÇÕES AO RECURSO (TRL 2.ª Secção)
prazo_submissao: 2026-04-19
status: PEÇA FINAL JÁ EXISTE — este ficheiro é pre-submission checklist
peca_final_existe: C:/Users/nunom/Desktop/POR_PROCESSO/PROC_3719_25__PROVIDENCIA_CAUTELAR/01_PECAS_PROCESSUAIS/PROC-3719_CONTRA_ALEGACOES_TRL_FINAL.md
compliance_report: 2026-04-17_PROC-3719_COMPLIANCE_REPORT.md
originSessionId: 0085b1f4-9478-4cbc-bd8e-7032692d3498
---
# Pre-submission Checklist — Contra-Alegações 3719/25.0T8LSB

## AVISO

O skeleton anterior (para redacção from-scratch) foi **superseded**: investigação em POR_PROCESSO revelou que a peça final já existe como `PROC-3719_CONTRA_ALEGACOES_TRL_FINAL.md` (+ versões datadas 2026-03-19 e 2026-04-08). Este ficheiro passa a ser **checklist pre-submissão**.

---

## Dados canónicos extraídos da peça final

| Campo | Valor | Fonte |
|-------|-------|-------|
| **Tribunal ad quem** | Tribunal da Relação de Lisboa — 2.ª Secção | Linha 2 peça final |
| **Tribunal a quo** | Juízo Cível de Lisboa (Juiz 4) | Contexto cronológico |
| **Processo** | 3719/25.0T8LSB | Confirmado |
| **Recorrido** | Nuno Miguel Silva Duarte (CC 13731091) | Linha 3 |
| **Recorrente** | Maria Teresa Castro Bangueses Ribeiro | Linha 4 (**não é LEA directamente — é representante individual**) |
| **Sentença a quo** | 27/01/2026 (indeferimento providência — favorável a Nuno) | Facto 7 |
| **Audiência TRL** | 2026-05-30 | Calendário processual |
| **Mandatário** | Dr. João Nabais (jnabais-advogados.pt) | Constituído 2026-03-02 |
| **Valor causa** | Rever — YAML diz €84.471; peça não explicita | ⚠️ discrepância a validar |
| **Crédito conexo invocado** | €762.281,06 | Base do direito de retenção |
| **Dívida adversa invocada** | €97.837,50 (balancete LEA 31/08/2022) | Má-fé processual |
| **Danos morais pedidos** | €30.000 | Capítulo IV dispositivo |

## Descoberta crítica do cruzamento

O YAML master dizia "LEA" como contra-parte do 3719. A peça final tem **Maria Teresa Castro Bangueses Ribeiro** como Recorrente pessoal. Pode ser:
- Teresa = sócia/representante da LEA que accionou pessoalmente
- Ou processo foi reconfigurado — confirmar com Dr. Nabais

## Checklist imperativa antes de submeter

### Compliance R1-R9 (ver `COMPLIANCE_REPORT.md` detalhado)

- [x] R1 — Cabeçalho exacto ("Tribunal da Relação de Lisboa — 2.ª Secção — Proc. 3719/25.0T8LSB")
- [ ] **R2 — ⚠️ 2 reformulações obrigatórias**: linhas 19 (`fraudulento`, `criminosa`) e 125 (`Fraude fiscal`) — ver Compliance Report §1
- [x] R3 — CC 13731091 correcto
- [x] R4 — processo 3719/25.0T8LSB correcto
- [ ] R5 — confirmar que NIF 254048382 aparece onde deve
- [ ] R6 — sufixo `.L1` no ficheiro final
- [ ] R7 — "Facto 7 sentença" confere com decisão de 27/01/2026
- [x] R8 — sem emojis
- [ ] R9 — backup 3-2-1 pós-submissão

### Validações factuais

- [ ] Valor da causa: €84.471 (YAML) vs valor efectivo no recurso
- [ ] Facto 7 da sentença = "residência permanente 4.º andar desde 2021" (citado linhas 15, 29, 44)
- [ ] EUR 97.837,50 (balancete LEA 31/08/2022) — comprovativo disponível
- [ ] EUR 762.281,06 (crédito total) — decomposição em PRV-EXTR-001 e afins
- [ ] Citação AE Luísa Santos ref. 437217551 de 20/09/2024 — cópia disponível
- [ ] Procuração Cleber 19/09/2022 vs acto 09/12/2021 — disponível em anexos

### Operacional

- [ ] Assinatura digital Art. 225.º CPC confirmada
- [ ] Anexos da peça (Anexo A-F) todos presentes em `02_PROVAS_DOCUMENTAIS/`
- [ ] Cópia da procuração actual de Dr. Nabais junta
- [ ] Comprovativo de taxa de justiça

### Submissão

- [ ] Upload via Citius no prazo 2026-04-19 (sábado dia 18, domingo dia 19 — **confirmar se prazo natural ou processual**, porque se processual pode ser 20-04 segunda)
- [ ] Notificação automática à contraparte (Dr. representante da Recorrente)
- [ ] Backup local + Obsidian/Cofre + OneDrive (3-2-1)
- [ ] Emissão `CONFIRMO L0` antes de gravar versão submetida em `pecas/`

## Próximas invocações recomendadas

1. **Dr. Nabais** recebe:
   - `2026-04-17_PROC-3719_COMPLIANCE_REPORT.md` (este)
   - `PROC-3719_CONTRA_ALEGACOES_TRL_FINAL.md` (peça)
2. **Nuno** valida factos materiais
3. Aplica-se `cofre-compliance` skill + `juridico-critic` agent em loop até zero violações R2
4. `CONFIRMO L0` + cópia para `Obsidian/Cofre-Juridico-Nuno/pecas/2026-04-19_PROC-3719_CONTRA_ALEGACOES.L1.md`
5. Submissão via Citius pelo mandatário
6. Post-submissão: actualizar YAML master `processos.3719.prazo: null` + `last_updated: 2026-04-19` + criar nova entry para prazo de audiência `2026-05-30`

## Links

- Peça final: `POR_PROCESSO/PROC_3719_25__PROVIDENCIA_CAUTELAR/01_PECAS_PROCESSUAIS/PROC-3719_CONTRA_ALEGACOES_TRL_FINAL.md`
- Versão 2026-03-19: `01_PECAS_PROCESSUAIS/2026-03-19__PROC-3719__...CONTRA_ALEGACOES_23142_DEFINITIVO.md`
- Versão 2026-04-08: `01_PECAS_PROCESSUAIS/2026-04-08__PROC-3719__2026-04-08_PROC-3719_CONTRA_ALEGACOES.md`
- Compliance report: `dev-environment/drafts/2026-04-17_PROC-3719_COMPLIANCE_REPORT.md`
- Investigação cronologia: relatório Explore agent 2026-04-17
