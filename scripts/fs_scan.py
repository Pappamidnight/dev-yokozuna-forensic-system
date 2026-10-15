# -*- coding: utf-8 -*-
"""
fs_scan.py - Scanner profissional de filesystem (rapido)
==========================================================
Uso:
    python fs_scan.py <raiz>
    python fs_scan.py <raiz> --depth 2
    python fs_scan.py <raiz> --top 20
    python fs_scan.py <raiz> --json out.json
    python fs_scan.py <raiz> --min-mb 100
    python fs_scan.py --compare A.json B.json
    python fs_scan.py --multi C:\ D:\ G:\
"""
import os
import sys
import json
import time
import argparse
from datetime import datetime
from collections import defaultdict

# ============================================================
# CONFIG
# ============================================================
IGNORAR_PADRAO = {
    "$RECYCLE.BIN", "System Volume Information", "$WinREAgent",
    "Windows.old", "Recovery", "Config.Msi",
}


# ============================================================
# UTILITARIOS
# ============================================================
def humano(b):
    if b is None:
        return "—"
    neg = b < 0
    b = abs(b)
    for u in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if b < 1024:
            s = f"{b:.2f} {u}"
            return f"-{s}" if neg else s
        b /= 1024
    return f"{b:.2f} EB"


def cor_delta(d):
    """Retorna codigo ANSI verde/vermelho/neutro."""
    if d > 0:
        return "\033[92m"
    if d < 0:
        return "\033[91m"
    return "\033[90m"


RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
YELLOW = "\033[93m"


# ============================================================
# MEDICAO (rapida, com cache)
# ============================================================
def medir_pasta(caminho, cache=None, ignorar=None):
    """Retorna (n_ficheiros, bytes). Cache evita re-medir."""
    if cache is not None and caminho in cache:
        return cache[caminho]

    n = 0
    b = 0
    ign = ignorar or set()

    for dirpath, dirnames, filenames in os.walk(caminho, onerror=lambda e: None):
        # Filtrar pastas ignoradas in-place
        dirnames[:] = [d for d in dirnames if d not in ign]

        for f in filenames:
            try:
                b += os.path.getsize(os.path.join(dirpath, f))
                n += 1
            except (OSError, PermissionError):
                continue

    if cache is not None:
        cache[caminho] = (n, b)
    return n, b


# ============================================================
# SCAN
# ============================================================
def scan_pasta(raiz, depth=1, top=30, min_bytes=0, ignorar=None):
    raiz = os.path.abspath(raiz)
    if not os.path.isdir(raiz):
        return None

    t0 = time.time()
    cache = {}
    ign = ignorar or IGNORAR_PADRAO

    # Subpastas de 1º nivel
    try:
        subpastas = sorted([
            os.path.join(raiz, d)
            for d in os.listdir(raiz)
            if os.path.isdir(os.path.join(raiz, d)) and d not in ign
        ])
    except PermissionError:
        subpastas = []

    resultado = {
        "raiz": raiz,
        "data": datetime.now().isoformat(),
        "tempo_s": 0,
        "pastas": [],
        "total": {"ficheiros": 0, "bytes": 0},
    }

    # 1) Subpastas (1º nivel)
    for sub in subpastas:
        n, b = medir_pasta(sub, cache, ign)
        if b < min_bytes:
            continue
        resultado["pastas"].append({
            "nome": os.path.basename(sub),
            "caminho": sub,
            "nivel": 1,
            "ficheiros": n,
            "bytes": b,
        })
        resultado["total"]["ficheiros"] += n
        resultado["total"]["bytes"] += b

    # 2) Detalhe 2º nivel (top N maiores)
    if depth >= 2:
        resultado["pastas"].sort(key=lambda x: x["bytes"], reverse=True)
        for p in resultado["pastas"][:5]:  # só expandir as 5 maiores
            try:
                subsub = sorted([
                    os.path.join(p["caminho"], d)
                    for d in os.listdir(p["caminho"])
                    if os.path.isdir(os.path.join(p["caminho"], d)) and d not in ign
                ])
            except PermissionError:
                continue

            p["filhos"] = []
            for s in subsub:
                n, b = medir_pasta(s, cache, ign)
                if b < min_bytes:
                    continue
                p["filhos"].append({
                    "nome": os.path.basename(s),
                    "caminho": s,
                    "nivel": 2,
                    "ficheiros": n,
                    "bytes": b,
                })
            p["filhos"].sort(key=lambda x: x["bytes"], reverse=True)

    resultado["pastas"].sort(key=lambda x: x["bytes"], reverse=True)
    resultado["tempo_s"] = round(time.time() - t0, 2)
    return resultado


# ============================================================
# IMPRESSAO
# ============================================================
def imprimir(scan, top=30):
    print()
    print("=" * 96)
    print(f"  {BOLD}SCAN:{RESET} {scan['raiz']}")
    print(f"  Data:  {scan['data'][:19]}")
    print(f"  Tempo: {scan['tempo_s']}s")
    print("=" * 96)
    print(f"  {BOLD}{'PASTA':<45} {'FICHEIROS':>12} {'TAMANHO':>15}{RESET}")
    print("  " + "-" * 92)

    for p in scan["pastas"][:top]:
        print(f"  {p['nome']:<45} {p['ficheiros']:>12,} {humano(p['bytes']):>15}")

    if len(scan["pastas"]) > top:
        resto_n = sum(p["ficheiros"] for p in scan["pastas"][top:])
        resto_b = sum(p["bytes"] for p in scan["pastas"][top:])
        print(f"  {'... (+' + str(len(scan['pastas'])-top) + ' pastas)':<45} "
              f"{resto_n:>12,} {humano(resto_b):>15}")

    print("  " + "-" * 92)
    print(f"  {BOLD}{'TOTAL':<45} {scan['total']['ficheiros']:>12,} "
          f"{humano(scan['total']['bytes']):>15}{RESET}")
    print("=" * 96)

    # Detalhe 2º nivel
    for p in scan["pastas"][:5]:
        if "filhos" not in p or not p["filhos"]:
            continue
        print()
        print(f"  {CYAN}{BOLD}>>> {p['nome']}{RESET}  ({humano(p['bytes'])})")
        print("  " + "-" * 92)
        for f in p["filhos"][:10]:
            print(f"    {f['nome']:<43} {f['ficheiros']:>12,} {humano(f['bytes']):>15}")


# ============================================================
# COMPARACAO
# ============================================================
def comparar(path_a, path_b):
    with open(path_a, encoding="utf-8") as f:
        a = json.load(f)
    with open(path_b, encoding="utf-8") as f:
        b = json.load(f)

    print()
    print("=" * 96)
    print(f"  {BOLD}COMPARACAO{RESET}")
    print("=" * 96)
    print(f"  A: {a['raiz']}  @  {a['data'][:19]}")
    print(f"  B: {b['raiz']}  @  {b['data'][:19]}")
    print()

    a_f = a["total"]["ficheiros"]
    b_f = b["total"]["ficheiros"]
    a_b = a["total"]["bytes"]
    b_b = b["total"]["bytes"]

    da = b_f - a_f
    db = b_b - a_b

    c1 = cor_delta(da)
    c2 = cor_delta(db)
    print(f"  Ficheiros: {a_f:>12,}  ->  {b_f:>12,}   "
          f"{c1}({da:+,}){RESET}")
    print(f"  Tamanho:   {humano(a_b):>12}  ->  {humano(b_b):>12}   "
          f"{c2}({humano(db)}){RESET}")
    print()

    # Por pasta
    mapa_a = {p["nome"]: p for p in a["pastas"]}
    mapa_b = {p["nome"]: p for p in b["pastas"]}
    todas = sorted(set(mapa_a) | set(mapa_b))

    print(f"  {BOLD}{'PASTA':<32} {'ANTES':>15} {'AGORA':>15} {'DELTA':>14}{RESET}")
    print("  " + "-" * 92)

    for nome in todas:
        pa = mapa_a.get(nome, {"ficheiros": 0, "bytes": 0})
        pb = mapa_b.get(nome, {"ficheiros": 0, "bytes": 0})
        db = pb["bytes"] - pa["bytes"]
        c = cor_delta(db)
        print(f"  {nome:<32} {humano(pa['bytes']):>15} {humano(pb['bytes']):>15} "
              f"{c}{humano(db):>14}{RESET}")

    print("=" * 96)


# ============================================================
# MAIN
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="Scanner profissional de filesystem",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("raiz", nargs="?", help="Pasta a analisar")
    parser.add_argument("--depth", type=int, default=1, choices=[1, 2])
    parser.add_argument("--top", type=int, default=30)
    parser.add_argument("--json", help="Guardar resultado em JSON")
    parser.add_argument("--min-mb", type=float, default=0, help="Ignorar pastas < N MB")
    parser.add_argument("--compare", nargs=2, metavar=("A.json", "B.json"),
                        help="Comparar 2 scans")
    parser.add_argument("--multi", nargs="+", metavar="RAIZ",
                        help="Scan a multiplas raizes")

    args = parser.parse_args()

    # Modo comparacao
    if args.compare:
        comparar(args.compare[0], args.compare[1])
        return

    # Modo multi-raiz
    if args.multi:
        todos = []
        t0 = time.time()
        for r in args.multi:
            print(f"\n{YELLOW}A medir {r}...{RESET}")
            s = scan_pasta(r, args.depth, args.top, args.min_mb * 1024 * 1024)
            if s:
                todos.append(s)
                imprimir(s, args.top)
        print()
        print("=" * 96)
        print(f"  {BOLD}RESUMO MULTI-RAIZ{RESET}")
        print("=" * 96)
        print(f"  {BOLD}{'LOCAL':<45} {'FICHEIROS':>12} {'TAMANHO':>15}{RESET}")
        print("  " + "-" * 92)
        tn = tb = 0
        for s in todos:
            print(f"  {s['raiz']:<45} {s['total']['ficheiros']:>12,} "
                  f"{humano(s['total']['bytes']):>15}")
            tn += s["total"]["ficheiros"]
            tb += s["total"]["bytes"]
        print("  " + "-" * 92)
        print(f"  {BOLD}{'TOTAL':<45} {tn:>12,} {humano(tb):>15}{RESET}")
        print(f"\n  Tempo total: {time.time()-t0:.2f}s")
        print("=" * 96)

        if args.json:
            with open(args.json, "w", encoding="utf-8") as f:
                json.dump({"multi": todos}, f, indent=2, ensure_ascii=False)
            print(f"\n  [OK] {args.json}")
        return

    # Modo normal
    if not args.raiz:
        parser.print_help()
        return

    s = scan_pasta(args.raiz, args.depth, args.top, args.min_mb * 1024 * 1024)
    if not s:
        print(f"[ERRO] Nao e pasta valida: {args.raiz}")
        sys.exit(1)

    imprimir(s, args.top)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(s, f, indent=2, ensure_ascii=False)
        print(f"\n  [OK] {args.json}")


if __name__ == "__main__":
    main()
