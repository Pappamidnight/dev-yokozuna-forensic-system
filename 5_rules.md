# Regras Operacionais e Governanca Forense: Acervo V8

**Versao**: 8.0.0 Canónica  
**Data**: 2026-10-15  
**Autoridade**: Yokozuna / Antigravity Forensic Engine  

---

## 1. As 10 Leis Inquebraveis do Ecossistema

1. **Lei 1: Politica Mandatoria Zero Emojis**:
   - E expressamente proibido o uso de emojis, icones decorativos ou grafismos informais em logs, codigos, mensagens operacionais, relatorios e pecas juridicas.

2. **Lei 2: Modo Auditoria e Custodia de Provas (Read-Only)**:
   - Pastas de prova original (`00_PROVA_ORIGINAL`, `01_CITIUS_CONGELADO`, etc.) sao imutaveis.
   - Proibido qualquer comando de eliminacao, renomeacao ou sobrescrita (`rm`, `del`, `mv`, `>`, `>>`) em areas de prova.

3. **Lei 3: Grounding Criptografico e Anti-Alucinacao**:
   - Todo e qualquer facto alegado deve ser suportado por ficheiro real com hash SHA-256 verificado.
   - Informacao sem correspondencia documental e classificada categoricamente como `[LACUNA_PROBATORIA]` ou `[ALEGACAO_PENDENTE]`.

4. **Lei 4: Banimento Definitivo de `es.exe`**:
   - O inventario e a pesquisa de ficheiros realizam-se exclusivamente via Everything HTTP API (`http://127.0.0.1:8080/`) ou varreduras protegidas por `try...except OSError`.

5. **Lei 5: Heuristica Atomica Tipo-a-Tipo**:
   - O motor processa estritamente `1 Tipo de Cada Vez`:
   - `1 CSV de Originais = 1 CSV de Duplicados = 1 Resumo JSON de Manifesto = 1 Decisao de Conservacao`.

6. **Lei 6: Reserva Jurisdicional para Decisoes Financeiras**:
   - O agente jamais substitui a autoridade do juiz na liquidacao de montantes controvertidos.
   - Apresenta-se o quadro documental de factos auditados para determinacao oficiosa pelo tribunal.

7. **Lei 7: Protecao do Altar de Memorias**:
   - O diretorio `00_ALTAR_MEMORIAS_PROTEGIDAS_FAMILIA_E_ANIMAIS` nao pode ser apagado, alterado ou versionado no Git. Constitui arquivo inviolavel.

8. **Lei 8: Centralizacao Estrita de Artefactos**:
   - Toda a saida e relatorio gerado reside exclusivamente nas pastas autorizadas (`reports/`, `caso_15547/docs/`, `data/`). E proibido poluir a raiz do utilizador, Desktop ou Downloads.

9. **Lei 9: Padrao Six Sigma em Codigo Python no Windows**:
   - Uso obrigatorio de `pathlib.Path` com raw strings (`r"..."`).
   - Leitura e escrita com `encoding="utf-8"` explicito em todos os I/O.
   - Isolamento de pacotes e execucao via `uv`.

10. **Lei 10: Assinatura e Rastreabilidade de Intervenientes**:
    - Cada artefacto ou peca formal emitida deve conter: Autor/Funcao, Timestamp ISO-8601 e Hash SHA-256 de integridade.
