#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extrair_rapido_csv.py
Streaming direto de Everything HTTP para CSV em Python de alta performance.
Elimina o gargalo do PowerShell (ConvertFrom-Json / Export-Csv).
"""

import urllib.request
import urllib.parse
import json
import csv
import time
from pathlib import Path

OUT_DIR = Path(r"C:\ACERVO\logs\csv_max_confidence")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_CSV = OUT_DIR / "duplicados_max_confidence.csv"

QUERY = (
    'dupe:name;size !attrib:H !attrib:S !empty: '
    '!path:"$Recycle.Bin" !path:"System Volume Information" '
    '!path:node_modules !path:.git !path:__pycache__ !path:venv '
    '!path:site-packages !path:AppData !path:ProgramData'
)

def main():
    print("=" * 65)
    print("  EXTRACAO ULTRA-RAPIDA (PYTHON STREAMING)")
    print("=" * 65)

    params = urllib.parse.urlencode({
        'search': QUERY,
        'json': 1,
        'path_column': 1,
        'size_column': 1,
        'date_modified_column': 1,
        'attributes_column': 1,
        'extension_column': 1,
        'count': 9999999
    })
    url = f"http://localhost:8080/?{params}"

    print("[1/2] A descarregar dados de Everything HTTP...")
    t0 = time.time()
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    
    items = data.get('results', [])
    t_download = time.time() - t0
    print(f"      Descarregados {len(items)} registos em {t_download:.2f}s")

    print("[2/2] A gravar CSV...")
    t1 = time.time()
    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["Nome", "Caminho", "Tamanho", "DataMod", "Extensao", "Atributos"])
        for it in items:
            writer.writerow([
                it.get('name', ''),
                it.get('path', ''),
                it.get('size', 0),
                it.get('date_modified', ''),
                it.get('extension', ''),
                it.get('attributes', '')
            ])
    t_write = time.time() - t1
    t_total = time.time() - t0

    tamanho_mb = OUT_CSV.stat().st_size / (1024 * 1024)
    print(f"      CSV gravado em {t_write:.2f}s ({tamanho_mb:.2f} MB)")
    print("-" * 65)
    print(f"[CONCLUIDO] Total: {len(items)} registos em {t_total:.2f}s!")
    print(f"[FICHEIRO]  {OUT_CSV}")
    print("=" * 65)

if __name__ == "__main__":
    main()
