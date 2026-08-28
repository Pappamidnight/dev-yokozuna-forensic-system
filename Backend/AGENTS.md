# Regras de Agente: Backend

**Autoridade Global**: [DIRETRIZES-GLOBAIS-DEV.md](file:///c:/Users/Yokozuna/Dev/AI/DIRETRIZES-GLOBAIS-DEV.md)

---

## 1. Funcao do Diretorio
- Conter bibliotecas de infraestrutura, motores de modelos de dados (`pydantic-ai`) e adaptadores de armazenamento e base de dados.

## 2. Restricoes
- Os modelos Pydantic definidos em `Backend/pydantic-ai/src/` sao a fonte de verdade para a validacao semantica dos agentes.
- Nao armazenar documentos brutos ou relatorios no diretorio de codigo do backend.
