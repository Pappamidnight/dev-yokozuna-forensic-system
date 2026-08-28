# Plano Final de Purga e Reorganização - C:\Users\Yokozuna\Dev

Plano ajustado para corresponder exatamente à **Estrutura Definida** pelo utilizador.

---

## 🎯 Estrutura Definida

```text
C:\Users\Yokozuna\Dev\
│
├── AI/                         # Instruções comuns às IAs
│   ├── AGENTS.md               # Diretrizes globais para as IAs
│   └── skills/                 # Skills e capacidades partilhadas
│
├── Backend/                    # Motor comum
│   └── pydantic-ai/            # Antigo pydantic-ai-backend (repositório motor)
│
├── Projects/                   # Projetos ativos
│   └── blindada-agent/         # Agente principal de produção
│
├── Labs/                       # Experiências e protótipos
│
├── Archive/                    # Retirado / histórico
│
└── README.md                   # Mapa e documentação do Dev
```

---

## 🧹 Etapas de Execução

### Etapa 1: Purga de Ficheiros e Pastas Temporárias
* **Apagar pastas vazias**:
  * `C:\Users\Yokozuna\Dev\New folder`
  * `C:\Users\Yokozuna\Dev\New folder (2)`
  * `C:\Users\Yokozuna\Dev\New folder (3)`
  * `C:\Users\Yokozuna\Dev\New folder (4)`
* **Apagar dumps temporários**:
  * `C:\Users\Yokozuna\Dev\tree_dirs.md`
  * `C:\Users\Yokozuna\Dev\tree_full.md`

### Etapa 2: Reestruturação dos Projetos e Motores
1. **Criar diretório `Backend/`**:
   * Mover `C:\Users\Yokozuna\Dev\Projects\pydantic-ai-backend` para `C:\Users\Yokozuna\Dev\Backend\pydantic-ai`.
2. **Criar diretório `AI/`**:
   * Criar subpastas `AI/skills/`.
   * Criar o ficheiro inicial `AI/AGENTS.md` com as diretrizes de trabalho para agentes.
3. **Organizar `Projects/`**:
   * Manter `Projects/blindada-agent/`.
4. **Criar `README.md` na raiz**:
   * Gerar o mapa explicativo do diretório `C:\Users\Yokozuna\Dev\`.
5. **Mover utilitários soltos**:
   * Mover `Antigravity-x64.exe` e `install.cmd` para `Archive/` (ou pasta de utilitários) para deixar a raiz 100% limpa.

---

## 🛡️ Verificação

1. Listar `C:\Users\Yokozuna\Dev\` e confirmar que a raiz contém apenas: `AI/`, `Backend/`, `Projects/`, `Labs/`, `Archive/`, `README.md`.
2. Testar que `Backend/pydantic-ai` e `Projects/blindada-agent` estão nos locais corretos.
