# Loops de Agentes: Validacao, Melhoria e Otimizacao de Dados

Este documento especifica a arquitetura dos loops de auto-correcao, validacao cruzada e otimizacao continua de informacoes entre os agentes de IA.

---

## 1. Arquitetura em Loop Fechado

```text
       +-------------------------------------------------------------+
       |                                                             |
       v                                                             |
[1. Coleta e Hashing]                                                |
       |                                                             |
       v                                                             |
[2. Validacao Semantica Pydantic] ---> (Erros detetados?) ---------> [Auto-Correcao]
       |                                      |                      (ou flag needs_review)
       v (Valido)                             |
[3. Cruzamento Relacional e Cadeias] <--------+
       |
       v
[4. Deteccao de Lacunas e Otimizacao]
       |
       v
[5. Calculo de Score de Confianca] ---> (Score < Limiar?) ---------> [Refinamento Iterativo]
       |                                                             (max 3 passagens)
       v (Aprovado)
[6. Emissao Estruturada em _index/]
```

---

## 2. As 4 Etapas do Loop

### Loop A: Auditoria e Integridade Criptografica
- Para cada ficheiro analisado, o agente calcula o hash SHA-256.
- Se o ficheiro ja constar do inventario com hash identico, e marcado como `duplicado_verificado` para evitar reprocessamento desnecessario.

### Loop B: Validacao Cruzada e Inferencia de Tipos
- O agente `data-validator` executa o modelo `CanonicalRecord`.
- Se um registo for classificado como `ALEGACAO`, mas estiver com `support_level: DOCUMENTADO`, o validador corrige automaticamente para `INDICIADO`.
- Se um ato processual referenciar um processo sem formato padrao, o loop normaliza o identificador.

### Loop C: Deteccao de Lacunas e Reconciliacao
- O agente compara a sequencia temporal de cada processo.
- Se existir uma *Penhora* sem *Notificacao Previa* ou *Citacao*, o validador regista uma `lacuna_processual` no relatorio.
- Cruza dados com correspondencias em `05_Correspondencia_E_Comunicacoes` para verificar se houve citacao postal posterior.

### Loop D: Otimizacao de Indice e Score de Confianca
- Calcula a pontuacao ponderada de evidencia do processo:
  $$\text{Score} = \frac{\sum (\text{Atos} \times \text{Peso})}{\text{Total de Atos}} \times (1 - \text{Penalizacao por Lacunas})$$
- O relatorio final consolida as metricas em `_index/pipeline_report.json`.
