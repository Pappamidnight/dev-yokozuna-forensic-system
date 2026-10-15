# -*- coding: utf-8 -*-
"""
snapshot_filesystem.py - Guarda contagem de ficheiros/bytes por pasta
======================================================================
Cada execucao cria um snapshot em C:\ACERVO\logs\snapshots\
Uso:
    python snapshot_filesystem.py C:\ACERVO
    python snapshot_filesystem.py C:\ACERVO --compare
"""
import os
import sys
import json
import argparse
from datetime import datetime


SNAP_DIR = r"C:\ACERVO\logs\snapshots"


def humano(b):
    for u in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024:
            return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} PB"


def snapshot(raiz):
    raiz = os.path.abspath(raiz)
    resultado = {
        "raiz": raiz,
        "data": datetime.now().isoformat(),
        "pastas": {},
        "total": {"ficheiros": 0, "bytes": 0},
    }

    # Sub-pastas de 1º nivel + raiz
    alvos = [("(raiz)", raiz)]
    try:
        for d in sorted(os.listdir(raiz)):
            full = os.path.join(raiz, d)
            if os.path.isdir(full):
                alvos.append((d, full))
    except PermissionError:
        pass

    for nome, caminho in alvos:
        n = 0
        b = 0
        for dirpath, dirnames, filenames in os.walk(caminho):
            for f in filenames:
                try:
                    b += os.path.getsize(os.path.join(dirpath, f))
                    n += 1
                except (OSError, PermissionError):
                    continue
        resultado["pastas"][nome] = {"ficheiros": n, "bytes": b}
        resultado["total"]["ficheiros"] += n
        resultado["total"]["bytes"] += b

    return resultado


def gravar_snapshot(snap):
    os.makedirs(SNAP_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(SNAP_DIR, f"snapshot_{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snap, f, indent=2, ensure_ascii=False)
    return path


def listar_snapshots():
    if not os.path.isdir(SNAP_DIR):
        return []
    return sorted([
        os.path.join(SNAP_DIR, f)
        for f in os.listdir(SNAP_DIR)
        if f.startswith("snapshot_") and f.endswith(".json")
    ])


def comparar(antigo_path, novo):
    with open(antigo_path, "r", encoding="utf-8") as f:
        antigo = json.load(f)

    print()
    print("=" * 92)
    print("  COMPARACAO DE SNAPSHOTS")
    print("=" * 92)
    print(f"  ANTES: {antigo['data']}  ({antigo_path})")
    print(f"  AGORA: {novo['data']}")
    print()

    # Totais
    a_f = antigo["total"]["ficheiros"]
    n_f = novo["total"]["ficheiros"]
    a_b = antigo["total"]["bytes"]
    n_b = novo["total"]["bytes"]

    print(f"  TOTAL FICHEIROS: {a_f:>12,} -> {n_f:>12,}  ({n_f - a_f:+,})")
    print(f"  TOTAL TAMANHO:   {humano(a_b):>12} -> {humano(n_b):>12}  ({humano(n_b - a_b)})")
    print()
    print(f"  {'PASTA':<30} {'ANTES':>12} {'AGORA':>12} {'DELTA':>10}")
    print("  " + "-" * 88)

    todas = set(antigo["pastas"].keys()) | set(novo["pastas"].keys())
    for p in sorted(todas):
        a = antigo["pastas"].get(p, {}).get("ficheiros", 0)
        n = novo["pastas"].get(p, {}).get("ficheiros", 0)
        delta = n - a
        sinal = "+" if delta > 0 else ""
        cor = "\033[92m" if delta > 0 else ("\033[91m" if delta < 0 else "")
        reset = "\033[0m"
        print(f"  {p:<30} {a:>12,} {n:>12,} {cor}{sinal}{delta:>9,}{reset}")
    print("=" * 92)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("raiz", help="Pasta a analisar")
    parser.add_argument("--compare", action="store_true",
                        help="Comparar com o snapshot anterior")
    parser.add_argument("--json", action="store_true", help="Saida JSON")
    args = parser.parse_args()

    snap = snapshot(args.raiz)

    if args.json:
        print(json.dumps(snap, indent=2, ensure_ascii=False))
        return

    # Comparacao automatica com o ultimo snapshot
    anteriores = listar_snapshots()
    if args.compare and anteriores:
        comparar(anteriores[-1], snap)

    # Gravar novo snapshot
    path = gravar_snapshot(snap)
    print(f"[OK] Snapshot gravado: {path}")
    print(f"     Total ficheiros: {snap['total']['ficheiros']:,}")
    print(f"     Total tamanho:   {humano(snap['total']['bytes'])}")


if __name__ == "__main__":
    main()
