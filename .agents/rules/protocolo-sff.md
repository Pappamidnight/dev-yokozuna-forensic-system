# Protocolo SFF de Instrucoes e Validacao

**Autoridade**: [AI/skills/mcp-fs-pydantic-org/references/protocolo-sff-workflows.md](file:///c:/Users/Yokozuna/Dev/AI/skills/mcp-fs-pydantic-org/references/protocolo-sff-workflows.md)

---

## 1. Estrutura de Pedidos SFF

Sempre que o utilizador enviar uma solicitacao estruturada no formato SFF, o agente deve seguir o fluxo:

```text
[FASE]: 1 / 2 / 3 / 4
[OBJETIVO]: Objetivo especifico
[PROCESSOS]: IDs dos processos (ex: 3719-25.0T8LSB, 10153-24.7T8LSB, 23142-22.7T8LSB, 15547-26.0T8LSB)
[FONTES]: Caminhos e ficheiros com niveis de suporte (OFICIAL, VALIDADO, EXTRAIDO, INFERIDO, HERDADO, NEEDS_REVIEW)
[DESTINO]: Caminho de gravacao em C:\Users\Yokozuna\Dev\
[MODELO]: SFF / Pydantic / Markdown / JSON / Grafo
[ORGANIZACAO]: Topicos de separacao pretendidos
[VALIDACAO]: Testes obrigatorios
[REGRAS]: Restricoes de seguranca e imutabilidade
[RESULTADO ESPERADO]: Entregavel final
```

---

## 2. Comandos de Controlo de Fases

- **Fase 1 (Analise)**: Cria o plano detalhado sem escrever em ficheiros de producao.
- **Fase 2 (Sandbox)**: Executa prototipos e testes isolados em `Sandbox/` ou `scratch/`.
- **Fase 3 (Execucao)**: So apos a expressao **"VALIDADO. Executa apenas o que foi aprovado no sandbox."**
- **Fase 4 (Validacao Pos-Execucao)**: Valida integridade SHA-256 e schema Pydantic, reportando evidencias concretas.

Comandos curtos autorizados:
- `Y` ou `SIM` $\rightarrow$ Avanca de fase.
- `VALIDADO.` $\rightarrow$ Autoriza execucao real.
