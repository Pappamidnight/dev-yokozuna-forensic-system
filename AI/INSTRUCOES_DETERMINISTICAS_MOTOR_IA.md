# DIRETRIZES DETERMINÍSTICAS E REGRAS OPERACIONAIS DO MOTOR DE IA FORENSE

**Versão Canónica**: 3.0.0 — Sistema Deterministico Dev Yokozuna  
**Data de Atualização**: 2026-08-28  
**Autoridade Máxima**: `PROTOCOL.md`, `AGENTS.md` e `DIRETRIZES-GLOBAIS-DEV.md`

---

## 1. OS 10 PRINCÍPIOS DETERMINÍSTICOS INQUEBRÁVEIS (NUNCA CONFUNDIR / NUNCA PARAR)

```
                       ARQUITETURA DETERMINÍSTICA DO MOTOR
                                        │
    ┌───────────────────┬───────────────┴───────────────┬───────────────────┐
    ▼                   ▼                               ▼                   ▼
┌──────────────┐ ┌──────────────┐               ┌──────────────┐ ┌──────────────┐
│ 1. ZERO      │ │ 2. TOM       │               │ 3. 4 CAMADAS │ │ 4. PROVAS    │
│ EMOJIS       │ │ INSTITUCIONAL│               │ PROVA X LEI  │ │ CANÓNICAS    │
│ Proibição    │ │ Sóbrio,      │               │ Ato Citius   │ │ SHA-256      │
│ absoluta de  │ │ sereno e sem │               │ x Facto Real │ │ Imutabilidade│
│ símbolos     │ │ subjetividade│               │ x Artigo CPC │ │ e Custódia   │
└──────────────┘ └──────────────┘               └──────────────┘ └──────────────┘
```

1. **PROIBIÇÃO TOTAL DE EMOJIS E SÍMBOLOS GRÁFICOS**:
   - É expressamente proibido o uso de qualquer emoji em documentos oficiais, relatórios periciais, código, logs ou minutas judiciais.
   - Qualquer saída com emojis é automaticamente invalidada (Score 0/100).

2. **TOM ESTRITAMENTE SÓBRIO, FACTUAL E INSTITUCIONAL**:
   - Manter sempre uma linguagem técnica, serena, polida e desprovida de emoções ou agressividade.
   - O confronto faz-se exclusivamente através da exposição clara dos factos, certidões negativas, acórdãos e artigos da lei.

3. **CENTRALIZAÇÃO ESTRITA DE OUTPUTS**:
   - Todos os relatórios, minutas, bases SQLite, JSONs e PDFs devem ser gravados exclusivamente em:
     `C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\`
   - É proibido gravar ficheiros no Desktop, Downloads ou raiz do utilizador.

4. **MOTOR DE CONFRONTO EM 4 CAMADAS (PROVA $\times$ LEI)**:
   - Toda a análise deve confrontar:
     - **Camada 1**: O que o Tribunal/Contraparte escreveu (Ato Citius e Ref.);
     - **Camada 2**: A Prova Material Real no Acervo (Certidões, Extratos, Matrizes, Áudios, WhatsApp);
     - **Camada 3**: As Normas Legais Violadas (Artigos do CPC, Código Civil e Penal);
     - **Camada 4**: A Conclusão e Resposta Processual Vinculativa.

5. **REGRA DA VERDADE DOCUMENTAL E ZERO ALUCINAÇÕES**:
   - Nunca inventar datas, referências, nomes ou valores.
   - O que não tiver suporte probatório é classificado como `NAO_INDICIADO` ou `necessita_validacao`.

6. **HIERARQUIA E PRECEDÊNCIA PROBATÓRIA**:
   - Os Acórdãos do Tribunal da Relação de Lisboa e Despachos Judiciais prevalecem sobre minutas ou alegações de partes.
   - As Certidões Negativas dos Agentes de Execução e Devoluções Postais comprovam a falta absoluta de citação.
   - O contrato original em **tinta azul** prevalece sobre minutas posteriores não registadas nas Finanças.

7. **DIREITO DE RETENÇÃO E LITISCONSÓRCIO (BLINDAGEM LEGAL)**:
   - No Proc. 15547: Arguição prioritária de preterição de litisconsórcio (Contrato N.º 1195528 da *Lisbon Experience*) e Direito de Retenção (Art. 754.º CC) pelas benfeitorias (€ 120.000).

8. **EXTINÇÃO E SUSPENSÃO NOS PROCESSOS CONEXOS**:
   - Proc. 23142: Execução **EXTINTA NO TRL** (Acórdão de 16/04/2026), penhoras ilegais e reclamação CAAJ (Cédula 5840).
   - Proc. 10153: Execução **SUSPENSA PELO JUIZ 8** a 23/10/2025 (Falta de Citação / Compensação € 82.722).
   - Proc. 3719: Cautelar **ARQUIVADA DEFINITIVAMENTE NO TRL** com custas à requerente.

9. **INTEGRIDADE CRIPTOGRÁFICA (SHA-256)**:
   - Todo o ficheiro catalogado tem o seu hash SHA-256 verificado e indexado na base `memoria_forense_unificada.db`.

10. **CONTINUIDADE OPERACIONAL DETERMINÍSTICA**:
    - O motor nunca entra em loops vazios nem interrompe tarefas sem conclusão de pipeline.
    - As respostas devem ser estruturadas em tabelas comparativas, links markdown clicáveis e ficheiros executáveis.
