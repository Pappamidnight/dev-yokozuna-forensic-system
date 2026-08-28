#!/usr/bin/env python3
"""
Scaffolding Deterministico de Estrutura de Pastas e Ficheiros SFF (scaffold_process_structures.py).
Garante que os 4 processos judiciais centrais possuem a estrutura padronizada SFF com AGENTS.md e PASTA_RULES.json:
- 01_INICIAL
- 02_CONTESTACAO
- 03_PROVAS (input/, output/, processed/)
- 04_ALEGACOES
- 05_SENTENCA
- 06_RECURSOS
"""
import os
import sys
import json
from typing import Dict, List

DEV_ROOT = "C:\\Users\\Yokozuna\\Dev"
CANONICAL_PROCS_ROOT = os.path.join(DEV_ROOT, "Projects", "Ficheiros Escritos Canónicos", "04_Processos_E_Pecas_Escritas", "04.01_Processos_Gerais")

TARGET_PROCESSES = [
    {
        "id": "3719-25.0T8LSB",
        "nome": "Providencia Cautelar e Tutela de Posse / Habitacao",
        "jurisdicao": "Comarca de Lisboa - Juizo Local Civel"
    },
    {
        "id": "10153-24.7T8LSB",
        "nome": "Oposicao a Execucao / Retencao TPA Unicre",
        "jurisdicao": "Comarca de Lisboa - Juizo de Execucao"
    },
    {
        "id": "23142-22.7T8LSB",
        "nome": "Nulidade Absoluta da Citacao e Domicilio Fiscal Ativo",
        "jurisdicao": "Comarca de Lisboa - Juizo de Execucao"
    },
    {
        "id": "15547-26.0T8LSB",
        "nome": "Propriedade Plena e Litisconsorcio Necessario",
        "jurisdicao": "Comarca de Lisboa - Juizo Central Civel"
    }
]

SFF_STAGES = [
    "01_INICIAL",
    "02_CONTESTACAO",
    "03_PROVAS/input",
    "03_PROVAS/output",
    "03_PROVAS/processed",
    "04_ALEGACOES",
    "05_SENTENCA",
    "06_RECURSOS"
]


def scaffold_processes():
    print("==================================================================")
    print("INICIANDO SCAFFOLDING DETERMINISTICO DE PASTAS SFF")
    print(f"Raiz Processual: {CANONICAL_PROCS_ROOT}")
    print("==================================================================")

    created_dirs = 0
    created_files = 0

    for proc in TARGET_PROCESSES:
        proc_dir = os.path.join(CANONICAL_PROCS_ROOT, proc["id"])
        os.makedirs(proc_dir, exist_ok=True)

        # 1. Criar subpastas SFF
        for stage in SFF_STAGES:
            stage_dir = os.path.join(proc_dir, stage.replace("/", os.sep))
            if not os.path.exists(stage_dir):
                os.makedirs(stage_dir, exist_ok=True)
                created_dirs += 1

        # 2. Criar AGENTS.md no processo
        proc_agents_md = os.path.join(proc_dir, "AGENTS.md")
        if not os.path.exists(proc_agents_md):
            with open(proc_agents_md, "w", encoding="utf-8") as f:
                f.write(f"""# Diretrizes do Processo {proc['id']}

**Designacao**: {proc['nome']}  
**Jurisdicao**: {proc['jurisdicao']}  
**Autoridade**: `AI/DIRETRIZES-GLOBAIS-DEV.md` e `AGENTS.md`  

---

## 1. Regras Operacionais
- Modo estrito Read-Only sobre os ficheiros originais.
- Factualidade comprovada: Proibido inventar dados. Factos sem hash sao `NAO_INDICIADO`.
- Segregacao de estagios: Pecas nos estagios `01_INICIAL` a `06_RECURSOS`.
""")
                created_files += 1

        # 3. Criar PASTA_RULES.json
        proc_rules_json = os.path.join(proc_dir, "PASTA_RULES.json")
        if not os.path.exists(proc_rules_json):
            rules_data = {
                "process_id": proc["id"],
                "process_name": proc["nome"],
                "jurisdiction": proc["jurisdicao"],
                "allowed_stages": ["01_INICIAL", "02_CONTESTACAO", "03_PROVAS", "04_ALEGACOES", "05_SENTENCA", "06_RECURSOS"],
                "evidence_policy": "DOCUMENTADO_ONLY_WITH_SHA256",
                "human_gate_required_for_writes": True
            }
            with open(proc_rules_json, "w", encoding="utf-8") as f:
                json.dump(rules_data, f, ensure_ascii=False, indent=2)
                created_files += 1

    print(f"[INFO] Diretorios SFF verificados/criados : {created_dirs}")
    print(f"[INFO] Ficheiros de regras gerados       : {created_files}")
    print("==================================================================\n")


if __name__ == "__main__":
    scaffold_processes()
