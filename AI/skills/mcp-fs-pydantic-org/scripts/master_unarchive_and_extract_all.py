#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
master_unarchive_and_extract_all.py - Extrator e Descompactador Exaustivo de Todos os Arquivos Forenses.
Varre todas as pastas e drives (OneDrive, Dev, I:, F:, J:) e extrai todos os ZIPs e ficheiros compactados.
"""
import os
import sys
import zipfile
import tarfile
import shutil
import hashlib
import sqlite3
from pathlib import Path

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
DB_PATH = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "02_DADOS_ESTRUTURADOS" / "memoria_forense_unificada.db"
EXTRACT_ROOT = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "02_DADOS_ESTRUTURADOS" / "ARQUIVO_GLOBAL_EXTRAIDO"

SEARCH_ROOTS = [
    r"C:\Users\Yokozuna\OneDrive\GESTAO",
    r"C:\Users\Yokozuna\Dev",
    r"I:\whatsappchatwithfilipedelgado",
    r"I:\RECUPERADO",
    r"I:\Backup",
    r"J:\audios",
    r"J:\SPARK LEGAL",
    r"F:\defesa"
]

def calculate_sha256(filepath):
    try:
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""

def extract_all_archives():
    print("=" * 80)
    print(" EXTRATOR E DESCOMPACTADOR FORENSE GLOBAL")
    print(f" Destino: {EXTRACT_ROOT}")
    print("=" * 80)

    EXTRACT_ROOT.mkdir(parents=True, exist_ok=True)

    extracted_count = 0
    total_files_extracted = 0

    conn = None
    if DB_PATH.exists():
        conn = sqlite3.connect(str(DB_PATH))

    for sroot in SEARCH_ROOTS:
        if not os.path.exists(sroot):
            continue
        print(f"\n[+] A procurar arquivos em: {sroot}")
        for root, dirs, files in os.walk(sroot):
            # Evitar recursao infinita no proprio destino de extracao
            if "ARQUIVO_GLOBAL_EXTRAIDO" in root or ".git" in root or ".gemini" in root:
                continue

            for f in files:
                f_lower = f.lower()
                fp = os.path.join(root, f)

                if f_lower.endswith(".zip"):
                    sub_name = Path(f).stem
                    dest_dir = EXTRACT_ROOT / sub_name
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    try:
                        print(f"  -> A extrair ZIP: {f} ...")
                        with zipfile.ZipFile(fp, "r") as z:
                            z.extractall(dest_dir)
                            extracted_count += 1
                            extracted_files = list(dest_dir.rglob("*"))
                            total_files_extracted += len([ef for ef in extracted_files if ef.is_file()])
                            print(f"     [OK] {len(extracted_files)} itens extraidos para {dest_dir.name}")
                    except Exception as e:
                        print(f"     [-] Erro ao extrair ZIP {f}: {e}")

                elif f_lower.endswith((".tar.gz", ".tgz", ".tar")):
                    sub_name = Path(f).stem
                    dest_dir = EXTRACT_ROOT / sub_name
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    try:
                        print(f"  -> A extrair TAR: {f} ...")
                        with tarfile.open(fp, "r:*") as t:
                            t.extractall(dest_dir)
                            extracted_count += 1
                            print(f"     [OK] Extraido com sucesso.")
                    except Exception as e:
                        print(f"     [-] Erro ao extrair TAR {f}: {e}")

    if conn:
        conn.close()

    print("\n" + "=" * 80)
    print(f" EXTRAÇÃO CONCLUÍDA:")
    print(f" - Arquivos compactados processados: {extracted_count}")
    print(f" - Total de novos ficheiros extraídos: {total_files_extracted}")
    print(f" - Pasta de Destino: {EXTRACT_ROOT}")
    print("=" * 80)

if __name__ == "__main__":
    extract_all_archives()
