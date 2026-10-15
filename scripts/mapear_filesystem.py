# -*- coding: utf-8 -*-
"""
mapear_filesystem.py - Mapeia pastas e conta ficheiros
=======================================================
Uso:
    python mapear_filesystem.py <raiz>
    python mapear_filesystem.py <raiz> --depth 2
    python mapear_filesystem.py <raiz> --json
    python mapear_filesystem.py <raiz> --ext .pdf .jpg .docx
"""
import os
import sys
import json
import argparse
from collections import defaultdict
from datetime import datetime


def humano(b):
    for u in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if b < 1024:
            return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} EB"


def mapear(raiz, profundidade=1, filtro_ext=None):
    """Percorre a raiz e devolve estatisticas por pasta."""
    raiz = os.path.abspath(raiz)
    if not os.path.isdir(raiz):
        print(f"[ERRO] Nao e pasta: {raiz}")
        sys.exit(1)

    resultados = []
    total_geral = {"ficheiros": 0, "bytes": 0, "pastas": 0}

    # 1) Sub-pastas de 1º nivel
    try:
        subpastas = sorted([
            os.path.join(raiz, d)
            for d in os.listdir(raiz)
            if os.path.isdir(os.path.join(raiz, d))
        ])
    except PermissionError:
        subpastas = []

    # 2) Ficheiros diretamente na raiz
    ficheiros_raiz = [
        f for f in os.listdir(raiz)
        if os.path.isfile(os.path.join(raiz, f))
    ]

    if ficheiros_raiz:
        n = len(ficheiros_raiz)
        b = sum(os.path.getsize(os.path.join(raiz, f)) for f in ficheiros_raiz)
        resultados.append({
            "pasta": "(raiz)",
            "ficheiros": n,
            "bytes": b,
            "subpastas": 0,
        })
        total_geral["ficheiros"] += n
        total_geral["bytes"] += b

    # 3) Por cada subpasta
    for sub in subpastas:
        n_ficheiros = 0
        b_total = 0
        n_subpastas = 0

        for dirpath, dirnames, filenames in os.walk(sub):
            # Limitar profundidade
            nivel = dirpath[len(sub):].count(os.sep)
            if nivel >= profundidade:
                dirnames[:] = []  # nao descer mais
                continue

            n_subpastas += len(dirnames)

            for f in filenames:
                # Filtro por extensao
                if filtro_ext:
                    ext = os.path.splitext(f)[1].lower()
                    if ext not in filtro_ext:
                        continue

                fp = os.path.join(dirpath, f)
                try:
                    b_total += os.path.getsize(fp)
                    n_ficheiros += 1
                except (OSError, PermissionError):
                    continue

        resultados.append({
            "pasta": os.path.basename(sub),
            "caminho": sub,
            "ficheiros": n_ficheiros,
            "bytes": b_total,
            "subpastas": n_subpastas,
        })

        total_geral["ficheiros"] += n_ficheiros
        total_geral["bytes"] += b_total
        total_geral["pastas"] += 1 + n_subpastas

    return resultados, total_geral


def imprimir(resultados, total, raiz):
    print()
    print("=" * 92)
    print(f"  ANALISE: {raiz}")
    print(f"  Data:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 92)
    print()
    print(f"  {'PASTA':<30} {'FICHEIROS':>12} {'SUBPASTAS':>10} {'TAMANHO':>14}")
    print("  " + "-" * 88)

    for r in resultados:
        print(f"  {r['pasta']:<30} {r['ficheiros']:>12,} {r.get('subpastas', 0):>10,} "
              f"{humano(r['bytes']):>14}")

    print("  " + "-" * 88)
    print(f"  {'TOTAL':<30} {total['ficheiros']:>12,} {total['pastas']:>10,} "
          f"{humano(total['bytes']):>14}")
    print("=" * 92)
    print()


def main():
    parser = argparse.ArgumentParser(description="Mapear filesystem")
    parser.add_argument("raiz", help="Pasta a analisar")
    parser.add_argument("--depth", type=int, default=99, help="Profundidade maxima (default: tudo)")
    parser.add_argument("--json", action="store_true", help="Saida em JSON")
    parser.add_argument("--ext", nargs="*", default=None,
                        help="Filtrar por extensoes (ex: .pdf .jpg)")
    args = parser.parse_args()

    # Normalizar extensoes
    ext = None
    if args.ext:
        ext = [e.lower() if e.startswith(".") else f".{e.lower()}" for e in args.ext]

    resultados, total = mapear(args.raiz, args.depth, ext)

    if args.json:
        print(json.dumps({
            "raiz": os.path.abspath(args.raiz),
            "data": datetime.now().isoformat(),
            "pastas": resultados,
            "total": total,
        }, indent=2, ensure_ascii=False))
    else:
        imprimir(resultados, total, os.path.abspath(args.raiz))


if __name__ == "__main__":
    main()
