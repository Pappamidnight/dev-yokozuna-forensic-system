# -*- coding: utf-8 -*-
"""
fs_snapshot.py - Sistema de snapshots historicos
=================================================
Uso:
    python fs_snapshot.py C:\ACERVO              # tira snapshot
    python fs_snapshot.py C:\ACERVO --compare    # compara com o anterior
    python fs_snapshot.py --list                 # lista snapshots
    python fs_snapshot.py --history 10           # ultimos 10 snapshots
    python fs_snapshot.py --diff 1 5             # compara snapshot 1 com 5
"""
import os
import sys
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fs_scan import scan_pasta, humano, cor_delta, RESET, BOLD

SNAP_DIR = r"C:\ACERVO\logs\snapshots"
INDEX = os.path.join(SNAP_DIR, "_index.json")


# ============================================================
# SNAPSHOT
# ============================================================
def garantir_dir():
    os.makedirs(SNAP_DIR, exist_ok=True)


def carregar_index():
    if not os.path.isfile(INDEX):
        return []
    try:
        with open(INDEX, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def gravar_index(idx):
    with open(INDEX, "w", encoding="utf-8") as f:
        json.dump(idx, f, indent=2, ensure_ascii=False)


def tirar_snapshot(raiz):
    garantir_dir()

    print(f"A medir {raiz}...")
    s = scan_pasta(raiz, depth=1)
    if not s:
        print(f"[ERRO] Nao e pasta: {raiz}")
        sys.exit(1)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"snap_{ts}.json"
    path = os.path.join(SNAP_DIR, fname)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2, ensure_ascii=False)

    # Atualizar indice
    idx = carregar_index()
    idx.append({
        "arquivo": fname,
        "raiz": raiz,
        "data": s["data"],
        "ficheiros": s["total"]["ficheiros"],
        "bytes": s["total"]["bytes"],
    })
    gravar_index(idx)

    print(f"[OK] Snapshot #{len(idx)} gravado: {path}")
    print(f"     Ficheiros: {s['total']['ficheiros']:,}")
    print(f"     Tamanho:   {humano(s['total']['bytes'])}")

    # Se ha anterior, comparar automaticamente
    if len(idx) >= 2:
        anterior = idx[-2]
        print(f"\n  Comparacao com snapshot anterior ({anterior['data'][:19]}):")
        diff = s["total"]["ficheiros"] - anterior["ficheiros"]
        db = s["total"]["bytes"] - anterior["bytes"]
        c1 = cor_delta(diff)
        c2 = cor_delta(db)
        print(f"    Ficheiros: {c1}{diff:+,}{RESET}")
        print(f"    Tamanho:   {c2}{humano(db)}{RESET}")

    return s


# ============================================================
# LISTA
# ============================================================
def listar():
    idx = carregar_index()
    if not idx:
        print("[VAZIO] Sem snapshots ainda.")
        print(f"       Corre: python fs_snapshot.py <raiz>")
        return

    print()
    print("=" * 92)
    print(f"  {BOLD}SNAPSHOTS ({len(idx)}){RESET}")
    print("=" * 92)
    print(f"  {BOLD}{'#':>4} {'DATA':<20} {'RAIZ':<30} {'FICHEIROS':>12} {'TAMANHO':>12}{RESET}")
    print("  " + "-" * 88)
    for i, s in enumerate(idx, 1):
        print(f"  {i:>4} {s['data'][:19]:<20} {s['raiz']:<30} "
              f"{s['ficheiros']:>12,} {humano(s['bytes']):>12}")
    print("=" * 92)


def mostrar_history(n=10):
    idx = carregar_index()
    if not idx:
        print("[VAZIO] Sem snapshots.")
        return
    ultimos = idx[-n:]
    print()
    print("=" * 92)
    print(f"  {BOLD}HISTORICO (ultimos {len(ultimos)}){RESET}")
    print("=" * 92)
    print(f"  {BOLD}{'#':>4} {'DATA':<20} {'FICHEIROS':>12} {'TAMANHO':>12} {'DELTA':>12}{RESET}")
    print("  " + "-" * 88)

    anterior = None
    base_i = len(idx) - len(ultimos) + 1
    for i, s in enumerate(ultimos, base_i):
        delta_f = delta_b = None
        if anterior:
            delta_f = s["ficheiros"] - anterior["ficheiros"]
            delta_b = s["bytes"] - anterior["bytes"]
        linha_d = ""
        if delta_f is not None:
            c1 = cor_delta(delta_f)
            c2 = cor_delta(delta_b)
            linha_d = f"{c1}{delta_f:+,}{RESET} / {c2}{humano(delta_b)}{RESET}"
        print(f"  {i:>4} {s['data'][:19]:<20} {s['ficheiros']:>12,} "
              f"{humano(s['bytes']):>12} {linha_d:>12}")
        anterior = s
    print("=" * 92)


# ============================================================
# DIFF ENTRE 2 SNAPSHOTS
# ============================================================
def diff_snapshots(i, j):
    idx = carregar_index()
    if not idx:
        print("[VAZIO] Sem snapshots.")
        return
    if i < 1 or j < 1 or i > len(idx) or j > len(idx):
        print(f"[ERRO] Indices fora de intervalo (1..{len(idx)})")
        return

    with open(os.path.join(SNAP_DIR, idx[i-1]["arquivo"]), encoding="utf-8") as f:
        a = json.load(f)
    with open(os.path.join(SNAP_DIR, idx[j-1]["arquivo"]), encoding="utf-8") as f:
        b = json.load(f)

    print()
    print("=" * 92)
    print(f"  {BOLD}DIFF #{i} -> #{j}{RESET}")
    print("=" * 92)
    print(f"  A: {a['data'][:19]}  ({a['raiz']})")
    print(f"  B: {b['data'][:19]}  ({b['raiz']})")
    print()

    da = b["total"]["ficheiros"] - a["total"]["ficheiros"]
    db = b["total"]["bytes"] - a["total"]["bytes"]
    print(f"  Ficheiros: {a['total']['ficheiros']:>12,} -> {b['total']['ficheiros']:>12,}  "
          f"{cor_delta(da)}{da:+,}{RESET}")
    print(f"  Tamanho:   {humano(a['total']['bytes']):>12} -> {humano(b['total']['bytes']):>12}  "
          f"{cor_delta(db)}{humano(db)}{RESET}")
    print()

    ma = {p["nome"]: p for p in a["pastas"]}
    mb = {p["nome"]: p for p in b["pastas"]}
    todas = sorted(set(ma) | set(mb))

    print(f"  {BOLD}{'PASTA':<32} {'A':>15} {'B':>15} {'DELTA':>15}{RESET}")
    print("  " + "-" * 88)
    for nome in todas:
        pa = ma.get(nome, {"bytes": 0, "ficheiros": 0})
        pb = mb.get(nome, {"bytes": 0, "ficheiros": 0})
        db = pb["bytes"] - pa["bytes"]
        print(f"  {nome:<32} {humano(pa['bytes']):>15} {humano(pb['bytes']):>15} "
              f"{cor_delta(db)}{humano(db):>15}{RESET}")
    print("=" * 92)


# ============================================================
# MAIN
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="Snapshots de filesystem")
    parser.add_argument("raiz", nargs="?", help="Pasta para snapshot")
    parser.add_argument("--compare", action="store_true",
                        help="Comparar com anterior (usado com raiz)")
    parser.add_argument("--list", action="store_true", help="Listar snapshots")
    parser.add_argument("--history", type=int, metavar="N", help="Mostrar N ultimos")
    parser.add_argument("--diff", nargs=2, type=int, metavar=("I", "J"),
                        help="Diff entre snapshots I e J")
    args = parser.parse_args()

    if args.list:
        listar()
        return
    if args.history:
        mostrar_history(args.history)
        return
    if args.diff:
        diff_snapshots(args.diff[0], args.diff[1])
        return
    if args.raiz:
        tirar_snapshot(args.raiz)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
