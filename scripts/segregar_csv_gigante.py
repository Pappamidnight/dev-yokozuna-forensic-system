#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
segregar_csv_gigante.py
Segrega o CSV de maxima confianca (3.996.445 registos) nos 12 CSVs canonicos por tipo.
Performance: leitura em streaming com buffers de escrita individuais (execucao em ~3-5 segundos).
"""

import csv
import sys
import time
from pathlib import Path

INPUT_CSV = Path(r"C:\ACERVO\logs\csv_max_confidence\duplicados_max_confidence.csv")
OUT_DIR = Path(r"C:\ACERVO\logs\csv")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Mapeamento de extensoes para as 12 tipologias
EXT_TO_TIPO = {}

TIPOLOGIAS = {
    "database": {"db", "sqlite", "mdb", "accdb"},
    "video":    {"mp4", "mkv", "avi", "mov", "wmv"},
    "excel":    {"xls", "xlsx", "xlsm"},
    "audio":    {"mp3", "wav", "flac", "m4a", "aac"},
    "word":     {"doc", "docx"},
    "pdf":      {"pdf"},
    "imagem":   {"jpg", "jpeg", "png", "gif", "bmp", "webp", "tiff"},
    "json":     {"json"},
    "texto":    {"txt"},
    "yaml":     {"yml", "yaml"},
    "csv":      {"csv"},
    "markdown": {"md"}
}

for tipo, exts in TIPOLOGIAS.items():
    for ext in exts:
        EXT_TO_TIPO[ext.lower()] = tipo

def main():
    if not INPUT_CSV.exists():
        print(f"[ERRO] Ficheiro de entrada nao encontrado: {INPUT_CSV}")
        sys.exit(1)

    print("=" * 70)
    print("  ACERVO V8 - SEGREGAÇÃO ULTRA-RÁPIDA EM 12 TIPOS")
    print(f"  Origem:  {INPUT_CSV}")
    print(f"  Destino: {OUT_DIR}")
    print("=" * 70)

    t0 = time.time()

    # Abrir os 12 ficheiros de saida
    handles = {}
    writers = {}
    contadores = {tipo: 0 for tipo in TIPOLOGIAS}
    outros = 0
    total_lido = 0

    header = ["Nome", "Caminho", "Tamanho", "DataMod"]

    for tipo in TIPOLOGIAS:
        p = OUT_DIR / f"duplicados_{tipo}.csv"
        f = open(p, "w", newline="", encoding="utf-8-sig")
        w = csv.writer(f)
        w.writerow(header)
        handles[tipo] = f
        writers[tipo] = w

    print("[INFO] A processar streaming de registos...")

    with open(INPUT_CSV, "r", encoding="utf-8-sig", newline="") as f_in:
        reader = csv.reader(f_in)
        header_in = next(reader, None)

        for row in reader:
            total_lido += 1
            if len(row) < 3:
                continue

            nome = row[0]
            caminho = row[1]
            tamanho = row[2]
            datamod = row[3] if len(row) > 3 else ""
            extensao = row[4].lower() if len(row) > 4 and row[4] else ""

            # Extrair extensao se vazia na coluna
            if not extensao and "." in nome:
                extensao = nome.rsplit(".", 1)[1].lower()

            tipo = EXT_TO_TIPO.get(extensao)
            if tipo:
                writers[tipo].writerow([nome, caminho, tamanho, datamod])
                contadores[tipo] += 1
            else:
                outros += 1

    # Fechar handles
    for f in handles.values():
        f.close()

    duracao = time.time() - t0

    print("-" * 70)
    print("  RESULTADO DA SEGREGAÇÃO:")
    print("-" * 70)
    
    ORDEM = ["database", "video", "excel", "audio", "word", "pdf", "imagem", "json", "texto", "yaml", "csv", "markdown"]
    total_classificado = 0

    for tipo in ORDEM:
        n = contadores[tipo]
        total_classificado += n
        p = OUT_DIR / f"duplicados_{tipo}.csv"
        size_mb = p.stat().st_size / (1024 * 1024)
        print(f"  [{tipo:10}] {n:8} registos | {size_mb:6.2f} MB -> duplicados_{tipo}.csv")

    print("-" * 70)
    print(f"  Total Lido:         {total_lido:8} registos")
    print(f"  Classificados:      {total_classificado:8} registos (12 tipos)")
    print(f"  Outras Extensoes:   {outros:8} registos (descartadas do acervo)")
    print(f"  Tempo Total:        {duracao:.2f}s")
    print("=" * 70)

if __name__ == "__main__":
    main()
