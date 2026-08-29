#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analise_mapas_2021_2022.py - Mapeamento e Analise Forense dos Mapas Contabilisticos e Fiscais de 2021 e 2022.
"""
import os
import sys
import sqlite3
from pathlib import Path

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
DB_PATH = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "02_DADOS_ESTRUTURADOS" / "memoria_forense_unificada.db"
OUTPUT_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "01_INDEX_E_RELATORIOS"

def extract_2021_2022_maps():
    print("=" * 80)
    print(" AUDITORIA DE MAPAS CONTABILÍSTICOS, FINANCEIROS E FISCAIS DE 2021 E 2022")
    print("=" * 80)

    if not DB_PATH.exists():
        print("[-] Base SQLite nao encontrada.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    queries = [
        ("Mapas e Listas de Recibos 2021/2022", "SELECT filename, filepath, size_bytes FROM evidencias WHERE (filename LIKE '%21%' OR filename LIKE '%22%') AND (filename LIKE '%recibo%' OR filename LIKE '%mapa%' OR filename LIKE '%contab%' OR filename LIKE '%cash%')"),
        ("Guias de IVA e Pagamentos AT 2021/2022", "SELECT filename, filepath, size_bytes FROM evidencias WHERE (filename LIKE '%2021%' OR filename LIKE '%2022%') AND (filename LIKE '%iva%' OR filename LIKE '%finan%' OR filename LIKE '%declar%')"),
        ("Contratos e Acertos 2021/2022", "SELECT filename, filepath, size_bytes FROM evidencias WHERE (filename LIKE '%2021%' OR filename LIKE '%2022%') AND (filename LIKE '%contrato%' OR filename LIKE '%acerto%' OR filename LIKE '%transmiss%')"),
        ("Extratos e Invoices 2021/2022", "SELECT filename, filepath, size_bytes FROM evidencias WHERE (filename LIKE '%2021%' OR filename LIKE '%2022%') AND (filename LIKE '%extrato%' OR filename LIKE '%invoice%' OR filename LIKE '%fatura%')")
    ]

    all_found = {}
    for title, q in queries:
        cur.execute(q)
        rows = cur.fetchall()
        all_found[title] = rows
        print(f"\n[+] {title}: {len(rows)} ficheiros identificados")
        for r in rows[:6]:
            print(f"  - {r[0]} ({r[2]} bytes)")

    conn.close()
    return all_found

if __name__ == "__main__":
    extract_2021_2022_maps()
