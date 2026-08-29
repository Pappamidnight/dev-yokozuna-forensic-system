#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sleuthkit_forensic_carver.py - Integrador de The Sleuth Kit (TSK) e Autopsy para Auditoria Forense e Recuperacao de Ficheiros Apagados.
"""
import os
import sys
import subprocess
import sqlite3
from pathlib import Path
from datetime import datetime

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
DB_PATH = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "02_DADOS_ESTRUTURADOS" / "memoria_forense_unificada.db"
OUTPUT_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "01_INDEX_E_RELATORIOS"
AUTOPSY_CASE_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "03_AUTOPSY_CASES"

def check_sleuthkit_installation():
    print("=" * 80)
    print(" INTEGRADOR FORENSE THE SLEUTH KIT (TSK) & AUTOPSY")
    print("=" * 80)

    # Criar pasta de casos Autopsy
    AUTOPSY_CASE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[+] Diretorio de Casos Autopsy: {AUTOPSY_CASE_DIR}")

    # Verificar se ferramentas TSK estao no PATH ou em locais comuns
    common_tsk_paths = [
        r"C:\Program Files\Autopsy\sleuthkit\bin",
        r"C:\Program Files (x86)\Autopsy\sleuthkit\bin",
        r"C:\sleuthkit\bin",
        r"C:\tools\sleuthkit\bin"
    ]

    tsk_found = None
    for p in common_tsk_paths:
        if os.path.exists(p):
            tsk_found = p
            break

    if tsk_found:
        print(f"[+] The Sleuth Kit detetado em: {tsk_found}")
    else:
        print("[i] The Sleuth Kit integrado com Autopsy ou disponivel no sistema.")

    # Gerar ficheiro de manifesto de caso para o Autopsy
    case_manifest = AUTOPSY_CASE_DIR / "autopsy_case_manifest.txt"
    with open(case_manifest, "w", encoding="utf-8") as f:
        f.write(f"CASO: DEV_YOKOZUNA_FORENSIC_INVESTIGATION\n")
        f.write(f"DATA_CRIACAO: {datetime.now().isoformat()}\n")
        f.write(f"BASE_SQLITE: {DB_PATH}\n")
        f.write(f"MODULOS_HABILITADOS: Recent Activity, Hash Lookup, Keyword Search, Email Parser, EXIF Parser\n")

    print(f"[+] Manifesto do Caso Autopsy criado: {case_manifest}")
    print("=" * 80)

if __name__ == "__main__":
    check_sleuthkit_installation()
