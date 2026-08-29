---
name: yokozuna-os-3719-export
description: Bash exporter que materializa estrutura YOKOZUNA-OS focada no processo 3719_TRL (charter, KB L0/L1, hooks, skills, config)
type: project
originSessionId: eef51390-a122-4d8a-bae3-26a9fab9e41b
---
# yokozuna-os-3719-export

**Path:** `C:/Users/nunom/dev-environment/yokozuna-os-3719-export/`
**Remote:** https://github.com/TIOOOOOOOOOOO/yokozuna-os-3719-export (PRIVATE) · commit `630776e`

## Componentes
- `export-session.sh` — Bash exporter (saneado: brace-expansion fix, INVARIANTS reescrito, GITHUB_USER=Pappamidnight)
- `README.md`, `.gitignore`, `KNOWN_ISSUES.md`

## Output do script
- `00-charter/` (CHARTER, INVARIANTS)
- `core/kb/L0-immutable-facts/processes.md` (3719/25.0T8LSB, 23142/24.0T8LSB)
- `core/kb/L1-domain-knowledge/legal/civil-procedure-pt/process_3719.md`
- `03-hooks-dev/` (secrets-scanner.sh, legal-language-gate.sh)
- `02-skills-dev/` (task-spec-writer.yaml, self-critic.yaml)
- `_config/` (settings.json, PROTECTED_PATHS)
- ZIP `yokozuna-os-3719-export-<TIMESTAMP>.zip`

## Caveats (ver KNOWN_ISSUES.md)
- Requer `jq` (so WSL/Linux/macOS — Windows nativo nao tem)
- KB tem PII real (nº processo, tribunais) — OK em repo privado, rever antes de tornar publico
- Charter diz "7 processos"; MEMORY.md diz 6 — inconsistencia menor

**Why:** Distribuir snapshot da estrutura YOKOZUNA-OS focada no 3719_TRL como single-script bash, util para reconstituir lab num novo workstation.
**How to apply:** Em WSL/Linux: `chmod +x export-session.sh && ./export-session.sh`.
