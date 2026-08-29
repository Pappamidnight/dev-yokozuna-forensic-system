# MANUAL DE ESTILO, TOM E LAYOUT UNIFORMIZADO PARA PEÇAS E RELATÓRIOS FORENSES

**Versão Canónica**: 1.0.0 — Padrão Oficial Dev Yokozuna  
**Data de Fixação**: 2026-08-28  
**Autoridade Máxima**: `PROTOCOL.md`, `AGENTS.md` e `INSTRUCOES_DETERMINISTICAS_MOTOR_IA.md`

---

## 1. O TOM E REGISTO REDATORIAL CANÓNICO

O tom oficial de qualquer peça judicial, requerimento ou relatório do sistema deve seguir escrupulosamente os seguintes 5 pilares:

```
                      OS 5 PILARES DO TOM FORENSE UNIFORMIZADO
                                         │
    ┌──────────────────┬─────────────────┼─────────────────┬──────────────────┐
    ▼                  ▼                 ▼                 ▼                  ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ 1. SÓBRIO &  │ │ 2. ZERO      │ │ 3. FACTOS    │ │ 4. JURISPRU- │ │ 5. DIÁLOGOS  │
│ INSTITUCIONAL│ │ EMOJIS       │ │ DOCUMENTADOS │ │ DÊNCIA STJ   │ │ LITERAIS     │
│ Serenidade e │ │ Proibição    │ │ Números de   │ │ Citação de   │ │ Transcrição  │
│ respeito     │ │ absoluta de  │ │ fatura, refs │ │ acórdãos com │ │ com data,    │
│ judicial.    │ │ símbolos.    │ │ Citius e €   │ │ data e proc. │ │ hora e nome. │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

1. **Linguagem Sóbria e Factual**:
   - Nunca usar adjetivos inflamados (*"odioso"*, *"criminosamente"*, *"vergonhoso"*).
   - Substituir por descrições técnicas de facto e de direito (*"conduta que configura preterição de formalidade essencial ao abrigo do art. 195.º do CPC"* ou *"imputação inidónea de despesas de prédio diverso"*).
2. **Citação Literal de Mensagens (WhatsApp / Emails)**:
   - Apresentar diálogos no formato cronológico estrito:
     > `[AAAA-MM-DD, HH:MM] Nome do Emissor`: *"Texto transcrito ipsis verbis."*
3. **Citação de Decisões e Jurisprudência**:
   - Identificar sempre o Tribunal Superior, a data e o processo:
     - Exemplo: *Como decidiu o Supremo Tribunal de Justiça no Acórdão de 2011-11-09 (Proc. 61/10), o direito de retenção é oponível erga omnes e prevalece sobre medidas cautelares (Art. 759.º, n.º 2 do CC).*

---

## 2. O LAYOUT UNIFORMIZADO (ESTRUTURA VISUAL PADRÃO)

Todas as peças geradas pelo sistema em **PDF**, **DOCX (LibreOffice)** e **Markdown** devem conter a seguinte arquitetura estrutural:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ TRIBUNAL JUDICIAL DA COMARCA DE LISBOA           PROCESSO N.º: [NÚMERO]      │
│ Juízo / Secção Competente                        Espécie: [Processo Comum]  │
│ Palácio da Justiça — Lisboa                      Valor da Causa: [€ VALOR]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DO [JUÍZO / TRIBUNAL]          │
│                                                                             │
│                                                                             │
│                        [TÍTULO DA PEÇA EM CAIXA ALTA]                       │
│                     (Subtítulo com as Exceções e Direitos)                  │
│                                                                             │
│                                                                             │
│ [QUALIFICAÇÃO DO RÉU / RECORRIDO COM NIF], vem apresentar o seu articulado: │
│                                                                             │
│ I. POR EXCEÇÃO DILATÓRIA: [TÍTULO DA EXCEÇÃO]                               │
│    1. Parágrafo numerado com o facto concreto...                            │
│    2. Parágrafo numerado com o artigo da lei violado...                     │
│                                                                             │
│ II. DA PROVA DOCUMENTAL E DAS CONFISSÕES ESCRITAS                           │
│    3. Parágrafo introdutório...                                             │
│    ┌───────────────────────────────────────────────────────────────────┐    │
│    │ [DATA, HORA] Emissor: "Transcrição literal da confissão..."       │    │
│    └───────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│ III. DO DIREITO DE RETENÇÃO E BENFEITORIAS (ART. 754.º DO CC)               │
│    4. Parágrafo descritivo do crédito de obras (€ 120.000,00)...            │
│                                                                             │
│ IV. DOS PEDIDOS                                                             │
│    a) Absolvição da instância por exceção dilatória;                        │
│    b) Reconhecimento do Direito de Retenção;                                │
│    c) Condenação da contraparte em custas e litigância de má-fé.            │
│                                                                             │
│ Junta: [Lista numerada de documentos anexos com Hashes SHA-256].            │
│                                                                             │
│                                           O Réu / Mandatário:               │
│                                           _________________________________ │
│                                           ([NOME COMPLETO])                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. ESPECIFICAÇÕES TÉCNICAS DE FORMATAÇÃO

| Elemento | DOCX (LibreOffice / Word) | PDF (ReportLab) | Markdown |
|---|---|---|---|
| **Margens** | Sup: 2.5cm \| Inf: 2.5cm \| Esq: 3.0cm \| Dir: 2.0cm | Margem: 1.8cm em A4 vertical | N/A |
| **Tipografia Principal** | Times New Roman / Garamond 11pt | Times-Roman 10pt (leading 14pt) | Fonte padrão Markdown |
| **Espaçamento de Linhas**| 1.3 a 1.5 linhas | Leading proporcional | N/A |
| **Parágrafos de Texto** | Justificado, avanço de 1.0cm na 1.ª linha | Justificado | Texto corrido com `1.`, `2.` |
| **Títulos de Secções** | Negrito, 12pt, numeração romana (`I.`, `II.`) | Helvetica-Bold 11pt (`I.`, `II.`) | `## I. TÍTULO` |
| **Caixas de Citação** | Tabela 1x1, fundo `#F1F5F9`, borda suave | Table 1x1, fundo cinzento, itálico | `> **[Data] Emissor**: *"Texto"*` |
| **Numeração de Páginas**| Rodapé centralizado: `Pág. X / Y` | Rodapé com numeração | `Pág. X` |
