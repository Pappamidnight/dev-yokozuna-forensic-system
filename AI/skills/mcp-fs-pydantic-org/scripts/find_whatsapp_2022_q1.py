#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
find_whatsapp_2022_q1.py - Localizador e Analisador de Conversas de WhatsApp de 2021 e 1Q 2022.
"""
import os
import sys
import sqlite3
import re
from pathlib import Path

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
DB_PATH = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "02_DADOS_ESTRUTURADOS" / "memoria_forense_unificada.db"
OUTPUT_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "01_INDEX_E_RELATORIOS"

def search_whatsapp_archives():
    print("=" * 80)
    print(" PESQUISA DE CONVERSAS DE WHATSAPP ANTIGAS (1T 2022 / 2021 / 2022)")
    print("=" * 80)

    if not DB_PATH.exists():
        print("[-] Base SQLite nao encontrada.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    # 1. Pesquisa por conversas WhatsApp na base de dados
    cur.execute("""
    SELECT filename, filepath, size_bytes, categoria
    FROM evidencias
    WHERE (filename LIKE '%whatsapp%' OR filename LIKE '%chat%' OR filepath LIKE '%whatsapp%' OR filepath LIKE '%chat%')
      AND (filename LIKE '%2021%' OR filename LIKE '%2022%' OR filepath LIKE '%2021%' OR filepath LIKE '%2022%' OR filename LIKE '%.txt' OR filename LIKE '%.zip')
    ORDER BY filename
    LIMIT 50
    """)
    rows = cur.fetchall()
    print(f"\n[+] Total de ficheiros WhatsApp/Chat identificados: {len(rows)}")
    for r in rows:
        print(f"  - {r[0]} | Tamanho: {r[2]} B | Caminho: {r[1]}")

    conn.close()

if __name__ == "__main__":
    search_whatsapp_archives()
