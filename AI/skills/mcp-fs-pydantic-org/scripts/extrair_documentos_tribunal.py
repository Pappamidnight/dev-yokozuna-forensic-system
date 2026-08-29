#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extrair_documentos_tribunal.py - Extrator e Compilador de Todos os Ficheiros e Documentos Oficiais do Tribunal (Citius).
Varre o sistema de ficheiros e centraliza por processos: 23142, 3719, 10153, 20203 e 15547.
"""

import os
import sys
import shutil
from pathlib import Path

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
TRIBUNAL_DEST = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "04_DOCUMENTOS_CITIUS_E_PECAS" / "ARQUIVO_OFICIAL_TRIBUNAL"

SEARCH_ROOTS = [
    DEV_ROOT / "Projects" / "Ficheiros Escritos Canónicos" / "04_Processos_E_Pecas_Escritas",
    Path(r"C:\Users\Yokozuna\OneDrive\GESTAO\00_OBSIDIAN_VAULT\01_PROCESSOS_JUDICIAIS"),
    DEV_ROOT / "backendgoogleinges" / "data" / "processed",
    DEV_ROOT / "OUTPUT_CENTRALIZADO" / "04_DOCUMENTOS_CITIUS_E_PECAS"
]

PROCESSOS_MAP = {
    "PROC_23142_EXECUCAO_TRL": ["23142", "centenario", "luisa santos", "penhora"],
    "PROC_3719_CAUTELAR_ARQUIVADO": ["3719", "cautelar", "teresa", "bangueses"],
    "PROC_10153_UNICRE_SUSPENSO": ["10153", "redunicre", "unicre", "piscarreta", "athayde"],
    "PROC_20203_DECLARATIVO_UNICRE": ["20203", "catrau"],
    "PROC_15547_REIVINDICACAO": ["15547", "reivindicacao", "nuno forra", "ricardo miranda"]
}

def extrair_docs_tribunal():
    print("=" * 80)
    print(" EXTRATOR DE DOCUMENTOS OFICIAIS DO TRIBUNAL (CITIUS)")
    print(f" Destino: {TRIBUNAL_DEST}")
    print("=" * 80)

    TRIBUNAL_DEST.mkdir(parents=True, exist_ok=True)
    for pdir in PROCESSOS_MAP.keys():
        (TRIBUNAL_DEST / pdir).mkdir(parents=True, exist_ok=True)

    total_copiados = 0

    for sroot in SEARCH_ROOTS:
        if not sroot.exists():
            continue
        print(f"\n[+] A varrer: {sroot}")
        for root, dirs, files in os.walk(str(sroot)):
            if "ARQUIVO_OFICIAL_TRIBUNAL" in root:
                continue

            for f in files:
                f_lower = f.lower()
                fp = os.path.join(root, f)

                # Identificar a qual processo pertence
                for proc_folder, keywords in PROCESSOS_MAP.items():
                    if any(kw in f_lower or kw in root.lower() for kw in keywords):
                        dest_proc = TRIBUNAL_DEST / proc_folder
                        dest_file = dest_proc / f
                        if not dest_file.exists():
                            try:
                                shutil.copy2(fp, dest_file)
                                total_copiados += 1
                                print(f"  -> [{proc_folder}] Copiado: {f} ({os.path.getsize(fp)} bytes)")
                            except Exception:
                                pass
                        break

    print("\n" + "=" * 80)
    print(f" COMPILAÇÃO CONCLUÍDA:")
    print(f" - Total de Documentos do Tribunal Centralizados: {total_copiados}")
    print(f" - Pasta de Destino: {TRIBUNAL_DEST}")
    print("=" * 80)

if __name__ == "__main__":
    extrair_docs_tribunal()
