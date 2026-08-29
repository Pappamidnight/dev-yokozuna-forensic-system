# MAPA GERAL DA ARQUITETURA FORENSE (4 MUNDOS INDEPENDENTES)

**Versão Canónica**: 4.0.0 — Padrão Dev Yokozuna  
**Data**: 2026-08-29  
**Autoridade**: PROTOCOL.md e AGENTS.md

---

## ESTRUTURA GLOBAL E FLUXO UNIDIRECIONAL

```
┌───────────────────────────────┐
│   01_RECURSOS_ORIGINAIS       │  (Documentos Reais, Imutáveis, Read-Only, SHA-256)
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│   02_MOTOR_FORENSE            │  (Código, Agentes, Workflows, Regras, CORE-5)
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│   03_RESULTADOS               │  (Outputs Regeneráveis, Relatórios, Peças, PDFs)
└───────────────────────────────┘

        ▲
        │  (Governação e Navegação)
┌───────┴───────────────────────┐
│   04_CONTROLO_E_INDICES       │  (Mapa Geral, Índices, Workflows, Versões, Decisões)
└───────────────────────────────┘
```

---

## TABELA DE CORRESPONDÊNCIA E NAVEGAÇÃO

| Diretório | Função | Regra Operacional |
|---|---|---|
| [`01_RECURSOS_ORIGINAIS/`](file:///C:/Users/Yokozuna/Dev/01_RECURSOS_ORIGINAIS/) | Custódia e Arquivo de Provas | **NUNCA EDITAR**. Ficheiros são imutáveis e auditados por SHA-256. |
| [`02_MOTOR_FORENSE/`](file:///C:/Users/Yokozuna/Dev/02_MOTOR_FORENSE/) | Inteligência e Orquestração | Código e agentes versionados. Não armazena provas originais nem resultados finais. |
| [`03_RESULTADOS/`](file:///C:/Users/Yokozuna/Dev/03_RESULTADOS/) | Produção e Entrega | Ficheiros regeneráveis pelo motor a qualquer momento. |
| [`04_CONTROLO_E_INDICES/`](file:///C:/Users/Yokozuna/Dev/04_CONTROLO_E_INDICES/) | Gestão e Decisão | Responde a onde está cada coisa, que versões existem e qual workflow executar. |
