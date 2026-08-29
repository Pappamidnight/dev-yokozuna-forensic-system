#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
descompactar_dossier_filesystem.py - Extrai e sincroniza a arvore de pastas organizada do Dossier Forense diretamente no sistema de ficheiros.
"""

import os
import sys
import zipfile
from pathlib import Path

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
OUTPUT_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO"
ZIP_FILE = OUTPUT_DIR / "DOSSIER_FORENSE_COMPLETO_DEV_YOKOZUNA.zip"
TARGET_DIR = OUTPUT_DIR / "DOSSIER_FORENSE_ORGANIZADO"

def extrair_dossier():
    print("=" * 80)
    print(" A SINCRONIZAR DOSSIER FORENSE DIRETAMENTE NO SISTEMA DE FICHEIROS")
    print(f" Origem ZIP: {ZIP_FILE}")
    print(f" Destino:    {TARGET_DIR}")
    print("=" * 80)

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    if not ZIP_FILE.exists():
        print(f"[-] Erro: Ficheiro {ZIP_FILE} nao existe.")
        return

    with zipfile.ZipFile(ZIP_FILE, "r") as zipf:
        zipf.extractall(TARGET_DIR)
        for name in zipf.namelist():
            print(f"[+] Extraido para o File System: {TARGET_DIR / name}")

    print("=" * 80)
    print(" SUCESSO: Todas as pastas e folhas estao agora acessiveis no File System!")
    print(f" Pasta Raiz: {TARGET_DIR}")
    print("=" * 80)

if __name__ == "__main__":
    extrair_dossier()
