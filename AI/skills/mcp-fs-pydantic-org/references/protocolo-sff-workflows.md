# Protocolo SFF e Estrutura de Instrucoes para Agentes de IA

**Versao**: 2.0.0  
**Autoridade**: [DIRETRIZES-GLOBAIS-DEV.md](file:///c:/Users/Yokozuna/Dev/AI/DIRETRIZES-GLOBAIS-DEV.md)  
**Ambiente**: `C:\Users\Yokozuna\Dev\`

---

## 1. Como Dar Instrucoes Eficazes aos Agentes (Formato SFF)

Para garantir determinismo maximo, 0 alucinacoes e cumprimento integral das tarefas, os pedidos devem ser estruturados no formato de **Ficha Forense (SFF)**:

### 1.1 Formato Padrao SFF
```text
[FASE]: 1 / 2 / 3 / 4
[OBJETIVO]: Objetivo claro e sem ambiguidade
[PROCESSOS]: Lista de IDs de processos (ex: 3719/25.0T8LSB, 10153/24.7T8LSB)
[FONTES]: Caminhos ou ficheiros com nivel probatorio (OFICIAL, VALIDADO, EXTRAIDO, INFERIDO, HERDADO, NEEDS_REVIEW)
[DESTINO]: Caminho absoluto dentro de Dev (ex: Projects/blindada-agent/data/processos/3719-25.0T8LSB ou _index/)
[MODELO]: SFF / Pydantic / Markdown / JSON / Grafo
[ORGANIZACAO]:
- resumo do processo
- atos processuais
- intervenientes
- cronologia
- provas
- conflitos
- defesa
[VALIDACAO]: Testes obrigatorios (ex: todos os JSON validos, nenhum ato sem fonte, SHA-256 validado)
[REGRAS]: Limites, proibicoes e seguranca (ex: nao alterar ficheiros canonicos, modo read-only)
[RESULTADO ESPERADO]: Entregavel final especificado
```

---

## 2. Niveis de Classificacao de Fontes

| Nivel | Significado | Peso Probatorio | Exemplo |
|---|---|---|---|
| `OFICIAL` | Documentos autenticados, sentencas, certidoes, despachos judiciais | **1.00** | `01_PDFs_Oficiais`, Citius |
| `VALIDADO` | Instrumentos contratuais assinados e pecas processuais completas | **0.95 - 0.98** | `03_Contratos_E_Acordos`, `04_Processos` |
| `EXTRAIDO` | Dados recolhidos diretamente via OCR ou parsing de emails com aviso | **0.85** | `05_Correspondencia_E_Comunicacoes` |
| `INFERIDO` | Conclusoes logicas derivadas sem documento direto explicito | **0.50** | Relacoes entre partes nao documentadas |
| `HERDADO` | Metadados herdados de processos anexos ou bases anteriores | **0.40** | Registos de processos dependentes |
| `NEEDS_REVIEW` | Dados com conflito temporal ou sem suporte probatorio | **0.10** | Rascunhos, minutas de `02_Minutas` |

---

## 3. Fluxo de Trabalho em 4 Fases (Conforme PROTOCOL.md)

1. **FASE 1: ANALISE E PLANO**
   - Comando curto: `FASE 1: cria plano SFF completo para [processo], usando [fontes], sem executar.`
   - O agente analisa, cria o plano e aguarda aprovacao.

2. **FASE 2: SANDBOX (Apos 'Y' ou 'SIM')**
   - O agente gera prototipos ou testa em ambiente isolado (`Sandbox/` ou `scratch/`).
   - Apresenta os resultados do teste e aguarda validacao.

3. **FASE 3: EXECUCAO (Apos 'VALIDADO.')**
   - O agente persiste os dados em pastas de producao autorizadas (`Projects/` ou `_index/`).

4. **FASE 4: VALIDACAO POS-EXECUCAO**
   - O agente valida integridade via Pydantic e hashing SHA-256, reportando o resultado final.

---

## 4. Comandos de Controlo Rapido

- `Y` ou `SIM` $\rightarrow$ Avancar para a fase seguinte.
- `VALIDADO. Executa apenas o que foi aprovado no sandbox.` $\rightarrow$ Autorizacao para gravacao real.
