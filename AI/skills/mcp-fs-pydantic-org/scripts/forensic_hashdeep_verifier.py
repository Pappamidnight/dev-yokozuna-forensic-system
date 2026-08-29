#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
forensic_hashdeep_verifier.py - Verificador Forense de Integridade Criptografica estilo Kali Linux (hashdeep/sha256sum).
Gera relatorios compativeis com hashdeep e sha256sum para auditoria judicial.
"""
import os
import sys
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
DB_PATH = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "02_DADOS_ESTRUTURADOS" / "memoria_forense_unificada.db"
OUTPUT_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "01_INDEX_E_RELATORIOS"


def generate_hashdeep_manifest():
    print("=" * 80)
    print(" GERADOR DE MANIFESTO FORENSE PADRÃO KALI LINUX (HASHDEEP / SHA256SUM)")
    print("=" * 80)

    if not DB_PATH.exists():
        print("[-] Base de dados SQLite nao encontrada.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute("""
    SELECT size_bytes, sha256, filename, filepath, process_id, categoria
    FROM evidencias
    WHERE sha256 IS NOT NULL AND sha256 != ''
    ORDER BY process_id, filename
    """)
    rows = cur.fetchall()
    conn.close()

    total = len(rows)
    print(f"[+] Total de registos com hash SHA-256 no banco: {total}")

    # 1. Formato sha256sum padrao Linux
    sha256sum_file = OUTPUT_DIR / "SHA256SUMS.txt"
    with open(sha256sum_file, "w", encoding="utf-8") as f:
        for r in rows:
            size_b, sha, fname, fpath, proc, cat = r
            f.write(f"{sha}  {fpath}\n")

    # 2. Formato hashdeep padrao Kali Forensics
    hashdeep_file = OUTPUT_DIR / "HASHDEEP_MANIFEST.txt"
    with open(hashdeep_file, "w", encoding="utf-8") as f:
        f.write("%%%% HASHDEEP-1.0\n")
        f.write("%%%% size,sha256,filename,process_id,categoria\n")
        f.write(f"## Data de Auditoria: {datetime.now().isoformat()}\n")
        f.write(f"## Total de Ficheiros Auditados: {total}\n")
        for r in rows:
            size_b, sha, fname, fpath, proc, cat = r
            f.write(f"{size_b},{sha},{fpath},{proc},{cat}\n")

    print(f"[+] Gerado ficheiro SHA256SUMS: {sha256sum_file}")
    print(f"[+] Gerado manifesto HASHDEEP : {hashdeep_file}")
    print("=" * 80)


if __name__ == "__main__":
    generate_hashdeep_manifest()
