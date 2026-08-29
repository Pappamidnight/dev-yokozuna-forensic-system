---
name: Processo 3719 — Ledger API
description: FastAPI ledger financeiro idempotente para 3719/25.0T8LSB — recriado 2026-04-18
type: project
originSessionId: 927681e4-6853-4864-9e4f-d9e5a1e61173
---
Sistema recriado de raiz em 2026-04-18.
Path: `C:\Users\nunom\Desktop\processos\processo-3719\`

**Stack:** FastAPI 0.110 + PostgreSQL 16 + SQLAlchemy 2.0 + Alembic + Testcontainers

**Estado:** Ficheiros criados, git init pendente (utilizador rejeitou commit automático).

**Ficheiros criados:**
- `app/` completo: config, database, models, schemas, services, routes, main, verify_invariants
- `tests/` completo: conftest + 4 suites (models, idempotency, invariants, api)
- `ops/` completo: 7 scripts PowerShell
- `alembic/` completo: env.py, script.py.mako, versions/.gitkeep
- `CLAUDE.md` local enxuto

**Próximo passo:** `.\ops\bootstrap.ps1` → migration inicial → `pytest -q`

**Why:** Pasta foi apagada pelo utilizador; recriação completa aprovada via plan mode.
**How to apply:** Consultar `.claude/project.md` para contexto completo. CLAUDE.md local carregado automaticamente.
