# -*- coding: utf-8 -*-
import os
import csv
import time
from collections import defaultdict

CSV = r"C:\ACERVO\logs\snapshot_atual.csv"

# Categorias
MAPA = {
    "database": [".db", ".sqlite", ".mdb", ".accdb"],
    "video":    [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
    "excel":    [".xls", ".xlsx", ".xlsm", ".xlsb"],
    "audio":    [".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".wma"],
    "word":     [".doc", ".docx", ".odt", ".rtf"],
    "pdf":      [".pdf"],
    "imagem":   [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp",
                 ".tiff", ".tif", ".svg", ".heic", ".raw"],
    "json":     [".json"],
    "texto":    [".txt"],
    "yaml":     [".yml", ".yaml"],
    "csv":      [".csv"],
    "markdown": [".md", ".markdown"],
    "codigo":   [".py", ".js", ".ts", ".cs", ".ps1", ".sh", ".bat", ".sql"],
    "outros":   [],
}
EXT2TIPO = {}
for tipo, exts in MAPA.items():
    for e in exts:
        EXT2TIPO[e] = tipo

def main():
    t0 = time.time()
    print("=" * 78)
    print("  ANALISE DO SNAPSHOT REAL (C:\\ACERVO)")
    print("=" * 78)
    print()

    por_tipo = defaultdict(int)
    por_tipo_bytes = defaultdict(int)
    total = 0
    total_bytes = 0

    with open(CSV, "r", encoding="utf-8", errors="replace", newline="") as f:
        r = csv.reader(f)
        next(r, None)
        for row in r:
            if len(row) < 5:
                continue
            nome = row[0]
            try:
                tam = int(row[2])
            except ValueError:
                tam = 0
            ext = row[4].lower() if row[4] else os.path.splitext(nome)[1].lower()
            tipo = EXT2TIPO.get(ext, "outros")
            por_tipo[tipo] += 1
            por_tipo_bytes[tipo] += tam
            total += 1
            total_bytes += tam

    print(f"  Total de ficheiros: {total:,}")
    print(f"  Total de bytes:     {total_bytes:,} ({total_bytes/1024/1024/1024:.2f} GB)")
    print()
    print("  DISTRIBUICAO POR TIPO:")
    print("-" * 78)
    print(f"  {'Tipo':<15} {'Ficheiros':>12} {'Bytes':>15} {'GB':>10}")
    print("-" * 78)
    for tipo in sorted(por_tipo.keys(), key=lambda x: -por_tipo[x]):
        n = por_tipo[tipo]
        b = por_tipo_bytes[tipo]
        print(f"  {tipo:<15} {n:>12,} {b:>15,} {b/1024/1024/1024:>10.2f}")
    print("-" * 78)

    # Top 20 maiores ficheiros
    print()
    print("  TOP 20 MAIORES FICHEIROS:")
    print("-" * 78)
    regs = []
    with open(CSV, "r", encoding="utf-8", errors="replace", newline="") as f:
        r = csv.reader(f)
        next(r, None)
        for row in r:
            if len(row) < 5:
                continue
            try:
                tam = int(row[2])
            except ValueError:
                continue
            regs.append((tam, row[0], row[1]))
    regs.sort(reverse=True)
    for tam, nome, cam in regs[:20]:
        print(f"  {tam/1024/1024:>8.2f} MB  {nome[:50]}")
        print(f"                        {cam[:100]}")

    print()
    print(f"  Tempo: {time.time()-t0:.2f}s")
    print("=" * 78)

if __name__ == "__main__":
    main()
