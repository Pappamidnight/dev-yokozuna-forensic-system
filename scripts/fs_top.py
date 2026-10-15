# -*- coding: utf-8 -*-
"""
fs_top.py - Lista os N ficheiros maiores (recursivo)
=====================================================
Uso:
    python fs_top.py <raiz> --top 30
    python fs_top.py <raiz> --top 50 --ext .mp4 .mkv
    python fs_top.py <raiz> --older-than 365
"""
import os
import sys
import argparse
import heapq
import time
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fs_scan import humano, BOLD, RESET, YELLOW


def top_ficheiros(raiz, n=30, filtro_ext=None, older_than_days=None):
    raiz = os.path.abspath(raiz)
    if not os.path.isdir(raiz):
        print(f"[ERRO] Nao e pasta: {raiz}")
        sys.exit(1)

    limite = None
    if older_than_days:
        limite = datetime.now() - timedelta(days=older_than_days)

    ext_norm = None
    if filtro_ext:
        ext_norm = {e.lower() if e.startswith(".") else f".{e.lower()}" for e in filtro_ext}

    # Heap de tamanho n (mantem apenas os n maiores)
    heap = []
    total_ficheiros = 0
    total_bytes = 0

    t0 = time.time()
    for dirpath, dirnames, filenames in os.walk(raiz, onerror=lambda e: None):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                st = os.stat(fp)
            except (OSError, PermissionError):
                continue

            if ext_norm:
                ext = os.path.splitext(f)[1].lower()
                if ext not in ext_norm:
                    continue

            if limite and datetime.fromtimestamp(st.st_mtime) < limite:
                continue

            total_ficheiros += 1
            total_bytes += st.st_size

            item = (st.st_size, fp, st.st_mtime)
            if len(heap) < n:
                heapq.heappush(heap, item)
            elif st.st_size > heap[0][0]:
                heapq.heapreplace(heap, item)

    tempo = time.time() - t0
    top = sorted(heap, reverse=True)

    print()
    print("=" * 96)
    print(f"  {BOLD}TOP {n} FICHEIROS MAIORES{RESET}")
    print(f"  Raiz: {raiz}")
    print(f"  Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Tempo: {tempo:.2f}s  |  Analisados: {total_ficheiros:,} ficheiros "
          f"({humano(total_bytes)})")
    print("=" * 96)
    print(f"  {BOLD}{'#':>4} {'TAMANHO':>12} {'DATA':<12} {'FICHEIRO':<65}{RESET}")
    print("  " + "-" * 92)

    for i, (tam, fp, mtime) in enumerate(top, 1):
        data_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        nome = os.path.basename(fp)
        if len(nome) > 63:
            nome = nome[:60] + "..."
        print(f"  {i:>4} {humano(tam):>12} {data_str:<12} {nome:<65}")
        # Caminho completo em linha separada se muito longo
        if len(fp) > 60:
            print(f"       {YELLOW}-> {fp}{RESET}")
    print("=" * 96)


def main():
    parser = argparse.ArgumentParser(description="Top N ficheiros maiores")
    parser.add_argument("raiz", help="Pasta a analisar")
    parser.add_argument("--top", type=int, default=30, help="Numero de ficheiros (default: 30)")
    parser.add_argument("--ext", nargs="*", help="Filtrar por extensoes (.mp4 .pdf)")
    parser.add_argument("--older-than", type=int, metavar="DIAS",
                        help="So ficheiros mais antigos que N dias")
    args = parser.parse_args()
    top_ficheiros(args.raiz, args.top, args.ext, args.older_than)


if __name__ == "__main__":
    main()
