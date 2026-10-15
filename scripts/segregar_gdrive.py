# -*- coding: utf-8 -*-
import os
import csv
import time
from collections import defaultdict

FONTE = r"C:\ACERVO\logs\google_drive\google_drive_full.csv"
DEST  = r"C:\ACERVO\logs\google_drive\por_tipo"

os.makedirs(DEST, exist_ok=True)

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
}

EXT2TIPO = {}
for tipo, exts in MAPA.items():
    for e in exts:
        EXT2TIPO[e] = tipo

def main():
    t0 = time.time()
    print("=" * 78)
    print("  SEGREGAR GOOGLE DRIVE POR TIPO")
    print("=" * 78)
    print(f"  Fonte:   {FONTE}")
    print(f"  Destino: {DEST}")
    print()

    if not os.path.isfile(FONTE):
        print(f"  [ERRO] Ficheiro nao encontrado: {FONTE}")
        return

    buckets = defaultdict(list)
    header = None
    total = 0

    with open(FONTE, "r", encoding="utf-8", errors="replace", newline="") as f:
        r = csv.reader(f)
        header = next(r)
        for row in r:
            if len(row) < 6:
                continue
            total += 1
            ext = row[5].strip().lower()
            tipo = EXT2TIPO.get(ext, "outros")
            buckets[tipo].append(row)

    print(f"  Total lidos: {total:,}")
    print()
    print("  RESULTADO DA SEGREGACAO:")
    print("-" * 78)
    print(f"  {'Tipo':<12} {'Ficheiros':>12} {'KB':>12}")
    print("-" * 78)

    for tipo in sorted(buckets.keys()):
        rows = buckets[tipo]
        out = os.path.join(DEST, f"{tipo}.csv")
        with open(out, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)
        sz = os.path.getsize(out) / 1024
        print(f"  {tipo:<12} {len(rows):>12,} {sz:>12.2f}")

    print("-" * 78)
    print(f"  Tempo total: {time.time()-t0:.2f}s")
    print("=" * 78)

if __name__ == "__main__":
    main()
