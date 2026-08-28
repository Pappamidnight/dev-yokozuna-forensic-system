# PROTOCOLO DE OPERACAO E REGRAS ABSOLUTAS

Este documento estabelece as regras obrigatorias e o fluxo de trabalho em 4 Fases para todas as interacoes e operacoes dos agentes de IA no ambiente Dev.

---

## REGRAS ABSOLUTAS

1. ZERO EMOJIS: Proibicao total do uso de emojis em todas as respostas, logs e documentos.
2. NUNCA PULAR FASES: O fluxo obrigatorio de 4 Fases deve ser seguido sequencialmente sem excecoes.
3. NUNCA EXECUTAR SEM VALIDACAO: Nenhuma alteracao, criacao ou comando no computador real pode ser executado sem autorizacao previa e explicita do utilizador.
4. TRANSPARENCIA TOTAL: Reportar sempre o que sera feito antes de executar qualquer acao.

---

## FLUXO DE TRABALHO - 4 FASES

### FASE 1: ANALISE E ESTRUTURA
- Receber input do utilizador em bullet points.
- Analisar requisitos.
- Apresentar estrutura/arquitetura completa.
- Listar pastas, ficheiros e funcionalidades envolvidas.
- Descrever o plano de testes e dry run.
- AGUARDAR VALIDACAO EXPLICITA DO UTILIZADOR.

### FASE 2: SANDBOX (APOS VALIDACAO DA FASE 1)
- Escrever codigo/conteudo no ambiente isolado (scratch).
- Implementar funcionalidades validadas.
- Executar testes e verificacoes no sandbox.
- Apresentar os resultados do dry run ao utilizador.
- AGUARDAR VALIDACAO EXPLICITA DO UTILIZADOR.

### FASE 3: EXECUCAO (APOS VALIDACAO DA FASE 2)
- Executar no computador real.
- Criar/modificar ficheiros e pastas no sistema.
- Executar aplicacoes ou comandos autorizados.
- AGUARDAR VALIDACAO POS-EXECUCAO DO UTILIZADOR.

### FASE 4: VALIDACAO POS-TOOL USE (APOS EXECUCAO DA FASE 3)
- Verificar resultados no sistema real.
- Apresentar evidencias concretas de sucesso.
- Confirmar determinismo e integridade.
- AGUARDAR VALIDACAO FINAL DO UTILIZADOR.
