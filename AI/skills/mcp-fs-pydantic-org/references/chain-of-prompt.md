# Chain of Prompt (P0 a P8) - Sequencia de Execucao

Este documento estabelece o pipeline sequencial de prompts onde cada estagio consome estritamente a saida estruturada do estagio anterior.

---

## Fluxo Sequencial P0 a P8

```
[P0: MCP Acesso] -> [P1: Inventario] -> [P2: Scanner] -> [P3: Validador Pydantic]
                                                                |
[P8: Gravacao _index] <- [P7: legal-strategy] <- [P6: 4 Camadas] <- [P5: Factos] <- [P4: Cadeias CPC]
```

---

## Detalhamento de Cada Prompt

### P0 - MCP e Conectividade
- **Objetivo**: Verificar a disponibilidade do sistema de ficheiros e listar as 6 pastas canónicas autorizadas.
- **Validacao**: Se MCP indisponivel, emitir `MCP_UNAVAILABLE` com zero registos (bloqueio de alucinacao).

### P1 - Inventario Exaustivo
- **Objetivo**: Coletar nomes, caminhos, tamanhos e extensoes de todos os ficheiros nas pastas alvo.
- **Saida**: Lista bruta de ficheiros existentes.

### P2 - Scanner Deterministico
- **Objetivo**: Extrair metadados, detetar padroes de processos judiciais e calcular hashes SHA-256 dos ficheiros.
- **Saida**: Dicionario preliminar de registos com hashes e categorias propostas.

### P3 - Validacao de Schema Pydantic
- **Objetivo**: Instanciar e validar os objetos `CanonicalRecord`.
- **Regra**: Qualquer violacao semantica (ex: alegacao como documentada) e corrigida ou marcada com erro de validacao.

### P4 - Construcao de Cadeias Processuais
- **Objetivo**: Ligar atos judiciais sequenciais, prazos e identificar lacunas processuais (ex: falta de citacao previa).
- **Saida**: Grafo relacional por numero de processo.

### P5 - Consolidacao de Pontos Factuais
- **Objetivo**: Extrair a lista de factos materiais provados (com SHA-256 e citacao de pagina/documento).

### P6 - Motor de 4 Camadas
- **Objetivo**: Mapear a matriz probatoria:
  $$\text{Prova Material / PDF (1.00)} \times \text{Alegacao da Parte} \times \text{Norma / Lei / CPC} \times \text{Decisao / Impacto}$$

### P7 - legal-strategy (Estrategia Juridica Opcional)
- **Objetivo**: Estruturar e redigir a estrategia juridica, teses ou articulados **apenas se solicitado formalmente pelo utilizador**.

### P8 - Gravacao Estruturada em `_index/`
- **Objetivo**: Escrever `pipeline_report.json`, `atos_processuais.jsonl`, `cadeias.json` e `chain_execution.json` em `Projects/Ficheiros Escritos Canónicos/_index/`.
