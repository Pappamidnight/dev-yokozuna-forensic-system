# -*- coding: utf-8 -*-
"""
acervo_scan.py - Inventario do ACERVO
=====================================
Uso:
    python acervo_scan.py                  # inventario geral
    python acervo_scan.py --tipo pdf       # 1 tipo
    python acervo_scan.py --snapshot       # guarda snapshot datado
    python acervo_scan.py --fs C:\ACERVO   # scan do filesystem tambem
"""
import os
import sys
import json
import argparse
import time
from datetime import datetime
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from acervo_core import (
    carregar_csv, gravar_json, garantir_dirs, humano, agora_str, timestamp,
    TIPOS, DIR_INV, DIR_SNAP, Filtro,
)


def inventario_por_tipo():
    """Conta registos por tipo."""
    regs = carregar_csv(verbose=False)
    cont = Counter(r["tipo"] for r in regs)
    tam = {}
    for r in regs:
        tam[r["tipo"]] = tam.get(r["tipo"], 0) + r["tamanho"]
    return regs, cont, tam


def inventario_fs(raiz):
    """Conta ficheiros/bytes por pasta de 1o nivel."""
    if not os.path.isdir(raiz):
        return None
    resultado = {"raiz": raiz, "data": agora_str(), "pastas": {}, "total": [0, 0]}
    alvos = [("(raiz)", raiz)]
    for d in sorted(os.listdir(raiz)):
        full = os.path.join(raiz, d)
        if os.path.isdir(full):
            alvos.append((d, full))
    for nome, caminho in alvos:
        n = 0
        b = 0
        for dirpath, dirnames, filenames in os.walk(caminho, onerror=lambda e: None):
            for f in filenames:
                try:
                    b += os.path.getsize(os.path.join(dirpath, f))
                    n += 1
                except (OSError, PermissionError):
                    continue
        resultado["pastas"][nome] = {"ficheiros": n, "bytes": b}
        resultado["total"][0] += n
        resultado["total"][1] += b
    return resultado


def main():
    parser = argparse.ArgumentParser(description="Inventario ACERVO")
    parser.add_argument("--tipo", help="Filtrar 1 tipo")
    parser.add_argument("--snapshot", action="store_true",
                        help="Guardar snapshot datado")
    parser.add_argument("--fs", help="Scan tambem esta pasta do filesystem")
    parser.add_argument("--json", help="Output JSON")
    args = parser.parse_args()

    garantir_dirs()

    if args.tipo:
        filtro = Filtro(tipo=args.tipo)
        regs = carregar_csv(filtro)
        print(f"\n=== INVENTARIO: {args.tipo.upper()} ===")
        print(f"  Registos: {len(regs):,}")
        print(f"  Total:    {humano(sum(r['tamanho'] for r in regs))}")
        if args.json:
            gravar_json(args.json, {"tipo": args.tipo, "total": len(regs),
                                     "bytes": sum(r['tamanho'] for r in regs)})
        return

    # Inventario geral
    print()
    print("=" * 88)
    print(f"  INVENTARIO ACERVO  |  {agora_str()}")
    print("=" * 88)

    t0 = time.time()
    regs, cont, tam = inventario_por_tipo()
    total_regs = sum(cont.values())
    total_bytes = sum(tam.values())

    print(f"\n  {'TIPO':<14} {'REGISTOS':>12} {'TAMANHO':>14} {'%':>6}")
    print("  " + "-" * 84)
    for t in sorted(cont, key=lambda x: -cont[x]):
        pct = 100 * cont[t] / total_regs if total_regs else 0
        print(f"  {t:<14} {cont[t]:>12,} {humano(tam[t]):>14} {pct:>5.1f}%")
    print("  " + "-" * 84)
    print(f"  {'TOTAL':<14} {total_regs:>12,} {humano(total_bytes):>14}")

    # FS scan opcional
    if args.fs:
        print(f"\n=== FILESYSTEM: {args.fs} ===")
        fs = inventario_fs(args.fs)
        if fs:
            print(f"  {'PASTA':<30} {'FICHEIROS':>12} {'TAMANHO':>14}")
            print("  " + "-" * 84)
            for nome, info in sorted(fs["pastas"].items(),
                                     key=lambda x: -x[1]["bytes"]):
                print(f"  {nome:<30} {info['ficheiros']:>12,} "
                      f"{humano(info['bytes']):>14}")
            print("  " + "-" * 84)
            print(f"  {'TOTAL':<30} {fs['total'][0]:>12,} "
                  f"{humano(fs['total'][1]):>14}")

    # Snapshot
    if args.snapshot:
        ts = timestamp()
        snap = {
            "data": agora_str(),
            "tipos": {t: {"regs": cont[t], "bytes": tam[t]} for t in cont},
            "total_regs": total_regs,
            "total_bytes": total_bytes,
        }
        path = os.path.join(DIR_SNAP, f"scan_{ts}.json")
        gravar_json(path, snap)
        print(f"\n  [OK] Snapshot: {path}")

    if args.json:
        gravar_json(args.json, {
            "data": agora_str(),
            "tipos": {t: {"regs": cont[t], "bytes": tam[t]} for t in cont},
            "total_regs": total_regs,
            "total_bytes": total_bytes,
        })
        print(f"  [OK] JSON: {args.json}")

    print(f"\n  Tempo: {time.time()-t0:.2f}s")
    print("=" * 88)


if __name__ == "__main__":
    main()
