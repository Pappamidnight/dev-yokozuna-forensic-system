#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
find_whatsapp_crypt_databases.py - Pesquisa exaustiva de bases de dados do WhatsApp (.db.crypt14, .crypt12, msgstore.db, backups) no sistema.
"""
import os
import sys
import sqlite3
from pathlib import Path

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
DB_PATH = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "02_DADOS_ESTRUTURADOS" / "memoria_forense_unificada.db"

def search_crypt_databases():
    print("=" * 80)
    print(" PESQUISA DE BASES DE DADOS WHATSAPP (.CRYPT / MSGSTORE / BACKUPS)")
    print("=" * 80)

    # 1. Pesquisa na Base SQLite
    if DB_PATH.exists():
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        cur.execute("""
        SELECT filename, filepath, size_bytes
        FROM evidencias
        WHERE filename LIKE '%msgstore%' OR filename LIKE '%.crypt%' OR filename LIKE '%wa.db%' OR filename LIKE '%whatsapp%backup%'
        ORDER BY size_bytes DESC
        LIMIT 30
        """)
        rows = cur.fetchall()
        print(f"[+] Registos identificados na base SQLite: {len(rows)}")
        for r in rows:
            print(f"  • {r[0]} ({r[2]} bytes) -> {r[1]}")
        conn.close()

    # 2. Pesquisa de caminhos comuns no OneDrive e Drives locais
    search_paths = [
        r"C:\Users\Yokozuna\OneDrive",
        r"I:\whatsappchatwithfilipedelgado",
        r"I:\Backup",
        r"I:\RECUPERADO",
        r"J:\audios",
        r"F:\defesa"
    ]

    print("\n[+] A verificar caminhos no sistema de ficheiros...")
    for sp in search_paths:
        if os.path.exists(sp):
            for root, dirs, files in os.walk(sp):
                for f in files:
                    f_lower = f.lower()
                    if 'msgstore' in f_lower or '.crypt' in f_lower or ('whatsapp' in f_lower and '.db' in f_lower):
                        full_p = os.path.join(root, f)
                        try:
                            sz = os.path.getsize(full_p)
                            print(f"  -> Encontrado: {f} ({sz} bytes) em {full_p}")
                        except Exception:
                            pass

    print("=" * 80)

if __name__ == "__main__":
    search_crypt_databases()
