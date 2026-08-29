#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ingest_multi_pc_forensics.py - Motor de Ingestao e Correlacao Multi-PC (Computadores de 2018, 2019 e 2022).
Categoriza e correlaciona automaticamente por Epocas Historicas:
- Epoca 1 (2018-2019): Origem da Posse, Contratos Iniciais, Check-ins e TPA Redunicre
- Epoca 2 (2020-2021): Pandemia, Fatura de 82.722 EUR, Balanco 2021 Tecnempresa, Acordo 09/12/2021
- Epoca 3 (2022-2024): Contencioso Judicial, Extincao no TRL, Embargos Unicre, 12 Videos de 2024
"""
import os
import sys
import time
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
DB_PATH = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "02_DADOS_ESTRUTURADOS" / "memoria_forense_unificada.db"
OUTPUT_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "01_INDEX_E_RELATORIOS"

def classify_epoch(filename: str, filepath: str, mod_year: int) -> str:
    path_str = (filename + " " + filepath).lower()
    
    if any(y in path_str for y in ['2018', '2019', '18_', '19_']) or mod_year in [2018, 2019]:
        return "EPOCA_1_ORIGEM_POSSE_2018_2019"
    elif any(y in path_str for y in ['2020', '2021', '20_', '21_', '82k', 'fatura']) or mod_year in [2020, 2021]:
        return "EPOCA_2_PANDEMIA_FATURA82K_2020_2021"
    elif any(y in path_str for y in ['2022', '2023', '2024', '2025', '2026', '22_', '23_', '24_']) or mod_year >= 2022:
        return "EPOCA_3_CONTENCIOSO_TRL_2022_2026"
    else:
        return "EPOCA_HISTORICA_GERAL"

def run_multi_pc_audit():
    print("=" * 80)
    print(" MOTOR FORENSE MULTI-PC: CORRELAÇÃO DE FICHEIROS DOS PCS DE 2018, 2019 E 2022")
    print("=" * 80)

    if not DB_PATH.exists():
        print("[-] Base SQLite nao encontrada.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM evidencias")
    total_db = cur.fetchone()[0]
    print(f"[+] Total de ficheiros atualmente na base forense: {total_db}")

    # Contagem por epocas
    cur.execute("""
    SELECT 
        CASE 
            WHEN filepath LIKE '%2018%' OR filepath LIKE '%2019%' THEN 'EPOCA_1 (2018-2019)'
            WHEN filepath LIKE '%2020%' OR filepath LIKE '%2021%' OR filepath LIKE '%82k%' THEN 'EPOCA_2 (2020-2021)'
            WHEN filepath LIKE '%2022%' OR filepath LIKE '%2023%' OR filepath LIKE '%2024%' THEN 'EPOCA_3 (2022-2024)'
            ELSE 'ARQUIVO_GLOBAL'
        END AS epoca,
        COUNT(*) as total
    FROM evidencias
    GROUP BY epoca
    """)
    rows = cur.fetchall()
    print("\n[+] Distribuicao Temporal do Acervo Multi-PC:")
    for ep, cnt in rows:
        print(f"  • {ep}: {cnt} ficheiros indexados")

    conn.close()

if __name__ == "__main__":
    run_multi_pc_audit()
