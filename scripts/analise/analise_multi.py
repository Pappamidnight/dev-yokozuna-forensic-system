# -*- coding: utf-8 -*-
"""
analise_multi.py - Analise multi-localizacao com progress bar
==============================================================
Locais: C:\Users\Yokozuna, Dev, OneDrive Copilot, G:\, D:\
Uso:
    python analise_multi.py
    python analise_multi.py --local "C:\Users\Yokozuna"
    python analise_multi.py --tipo pdf
"""
import os
import sys
import json
import time
import subprocess
import argparse
from datetime import datetime
from collections import defaultdict

# ============================================================
# CONFIG
# ============================================================
ES = r"C:\ACERVO\bin\es.exe"
INST = "1.5a"
OUT = r"C:\ACERVO\logs\analise_multi"
os.makedirs(OUT, exist_ok=True)

LOCAIS = [
    r"C:\Users\Yokozuna",
    r"C:\Users\Yokozuna\Dev",
    r"C:\Users\Yokozuna\OneDrive\Ficheiros do Microsoft Copilot Chat",
    r"C:\Users\Yokozuna\OneDrive\Microsoft Copilot Chat Files\Copilot Notebook Uploads",
    r"G:\",
    r"D:\",
]

TIPOS = [
    ("pdf",     "ext:pdf"),
    ("word",    "ext:doc;docx;odt;rtf"),
    ("excel",   "ext:xls;xlsx;ods"),
    ("imagem",  "image:"),
    ("video",   "video:"),
    ("audio",   "audio:"),
    ("codigo",  "ext:py;js;ts;cs;rs;go;ps1;sh;bat"),
    ("dados",   "ext:json;yaml;yml;csv;db;sqlite;duckdb"),
    ("zip",     "ext:zip;rar;7z;tar;gz;iso"),
    ("outros",  ""),
]


# ============================================================
# UTILITARIOS
# ============================================================
def humano(b):
    for u in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if b < 1024:
            return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} EB"


def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


class Progress:
    def __init__(self, total, prefix="", width=40):
        self.total = max(1, total)
        self.atual = 0
        self.prefix = prefix
        self.width = width
        self.t0 = time.time()

    def update(self, n=1, sufixo=""):
        self.atual = min(self.atual + n, self.total)
        pct = 100 * self.atual / self.total
        preenchido = int(self.width * self.atual / self.total)
        barra = "=" * preenchido + "-" * (self.width - preenchido)
        tempo = time.time() - self.t0
        eta = (tempo / self.atual) * (self.total - self.atual) if self.atual else 0
        linha = (f"\r  {self.prefix} [{barra}] {self.atual}/{self.total} "
                 f"({pct:5.1f}%) ETA {eta:5.1f}s {sufixo}")
        sys.stdout.write(linha[:200])
        sys.stdout.flush()

    def done(self, sufixo=""):
        tempo = time.time() - self.t0
        sys.stdout.write("\r" + " " * 200 + "\r")
        sys.stdout.flush()
        print(f"  {self.prefix} OK ({self.total} em {tempo:.2f}s) {sufixo}")


# ============================================================
# ES.EXE
# ============================================================
def es_count(query):
    try:
        r = subprocess.run(
            [ES, "-instance", INST, "-get-result-count", query],
            capture_output=True, text=True, timeout=60
        )
        return int(r.stdout.strip().split()[0] or 0)
    except Exception:
        return 0


def es_size(query):
    try:
        r = subprocess.run(
            [ES, "-instance", INST, "-get-total-size", query],
            capture_output=True, text=True, timeout=60
        )
        return int(r.stdout.strip().split()[0] or 0)
    except Exception:
        return 0


def es_top(query, n=10):
    try:
        r = subprocess.run(
            [ES, "-instance", INST, "-n", str(n), "-size", "-dm",
             "-sort", "size-descending", query],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=120
        )
        return [l for l in r.stdout.splitlines() if l.strip()]
    except Exception:
        return []


# ============================================================
# ANALISE POR LOCAL
# ============================================================
def analisar_local(local):
    """Analisa 1 local: contagem, tamanho, tipos, top."""
    if not os.path.exists(local):
        return {"local": local, "existe": False}

    query_base = f'path:"{local}"'
    n = es_count(query_base)
    b = es_size(query_base)

    # Por tipo
    por_tipo = {}
    for nome, q in TIPOS:
        if nome == "outros":
            continue
        full_q = f'{query_base} {q}'
        por_tipo[nome] = {
            "ficheiros": es_count(full_q),
            "bytes": es_size(full_q),
        }

    # Top 10
    top = es_top(f'{query_base} size:>10mb', n=10)

    return {
        "local": local,
        "existe": True,
        "ficheiros": n,
        "bytes": b,
        "humano": humano(b),
        "por_tipo": por_tipo,
        "top_10": top,
    }


# ============================================================
# ANALISE G:\ E D:\ (TOP-LEVEL)
# ============================================================
def analisar_raiz(letra):
    """Analisa raiz de um drive (pastas top-level)."""
    raiz = f"{letra}:\\"
    if not os.path.exists(raiz):
        return None

    pastas = []
    try:
        for d in sorted(os.listdir(raiz)):
            full = os.path.join(raiz, d)
            if not os.path.isdir(full):
                continue
            q = f'path:"{full}"'
            pastas.append({
                "nome": d,
                "caminho": full,
                "ficheiros": es_count(q),
                "bytes": es_size(q),
            })
    except PermissionError:
        pass

    pastas.sort(key=lambda x: -x["bytes"])
    return {"raiz": raiz, "pastas": pastas}


# ============================================================
# MAIN
# ============================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", help="Só 1 local")
    parser.add_argument("--tipo", help="Só 1 tipo")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    ts = timestamp()

    print()
    print("=" * 78)
    print(f"  ANALISE MULTI-LOCALIZACAO  |  {datetime.now():%Y-%m-%d %H:%M:%S}")
    print("=" * 78)
    print()

    locais = [args.local] if args.local else LOCAIS

    resultados = []
    prog = Progress(len(locais), prefix="Locais")

    for local in locais:
        prog.update(0, sufixo=f"-> {local[:40]}")
        t0 = time.time()
        r = analisar_local(local)
        r["tempo"] = round(time.time() - t0, 2)
        resultados.append(r)

        # Mostrar resumo
        prog.update(1, sufixo=f"{local[:30]}: {r.get('ficheiros',0):,}")

    prog.done()

    # Mostrar
    print()
    print(f"  {'LOCAL':<50} {'FICHEIROS':>12} {'TAMANHO':>12} {'TEMPO':>8}")
    print("  " + "-" * 84)

    total_f = 0
    total_b = 0
    for r in resultados:
        if not r.get("existe"):
            print(f"  {r['local'][:48]:<50} {'[nao existe]':>12}")
            continue
        print(f"  {r['local'][:48]:<50} {r['ficheiros']:>12,} "
              f"{r['humano']:>12} {r['tempo']:>7.2f}s")
        total_f += r["ficheiros"]
        total_b += r["bytes"]

    print("  " + "-" * 84)
    print(f"  {'TOTAL':<50} {total_f:>12,} {humano(total_b):>12}")
    print()

    # Por tipo (tabela cruzada)
    print("=" * 78)
    print("  POR TIPO")
    print("=" * 78)
    print()

    tipos_nomes = [t[0] for t in TIPOS if t[0] != "outros"]
    header = f"  {'LOCAL':<30} " + " ".join(f"{t[:7]:>9}" for t in tipos_nomes)
    print(header)
    print("  " + "-" * len(header))

    for r in resultados:
        if not r.get("existe"):
            continue
        linha = f"  {r['local'][:28]:<30} "
        for t in tipos_nomes:
            n = r["por_tipo"].get(t, {}).get("ficheiros", 0)
            linha += f"{n:>9,} "
        print(linha)
    print()

    # Drive raizes (G e D)
    for letra in ["G", "D"]:
        if args.local and not args.local.startswith(letra):
            continue
        raiz = analisar_raiz(letra)
        if not raiz:
            continue
        print("=" * 78)
        print(f"  DRIVE {letra}:\\  (TOP-LEVEL)")
        print("=" * 78)
        print()
        print(f"  {'PASTA':<50} {'FICHEIROS':>12} {'TAMANHO':>12}")
        print("  " + "-" * 78)
        total_rf = 0
        total_rb = 0
        for p in raiz["pastas"]:
            print(f"  {p['nome'][:48]:<50} {p['ficheiros']:>12,} "
                  f"{humano(p['bytes']):>12}")
            total_rf += p["ficheiros"]
            total_rb += p["bytes"]
        print("  " + "-" * 78)
        print(f"  {'TOTAL':<50} {total_rf:>12,} {humano(total_rb):>12}")
        print()

    # Gravar JSON
    path = os.path.join(OUT, f"analise_{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "data": datetime.now().isoformat(),
            "resultados": resultados,
        }, f, indent=2, ensure_ascii=False, default=str)
    print(f"  [OK] {path}")
    print()


if __name__ == "__main__":
    main()
