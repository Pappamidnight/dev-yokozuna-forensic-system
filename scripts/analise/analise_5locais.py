# -*- coding: utf-8 -*-
"""
analise_5locais.py - Analise de 5 locais com progress bar
==========================================================
Locais:
  1. C:\Users\Yokozuna
  2. C:\Users\Yokozuna\Dev
  3. OneDrive\Ficheiros do Microsoft Copilot Chat
  4. OneDrive\Microsoft Copilot Chat Files\Copilot Notebook Uploads
  5. G:\

Uso:
    python analise_5locais.py
    python analise_5locais.py --local 1        # so o local 1
    python analise_5locais.py --json
"""
import os
import sys
import json
import time
import subprocess
import argparse
from datetime import datetime

# ============================================================
# CONFIG
# ============================================================
ES = r"C:\ACERVO\bin\es.exe"
INST = "1.5a"
OUT = r"C:\ACERVO\logs\analise_5locais"
os.makedirs(OUT, exist_ok=True)

LOCAIS = [
    {"id": 1, "nome": "Perfil",              "path": r"C:\Users\Yokozuna"},
    {"id": 2, "nome": "Dev",                 "path": r"C:\Users\Yokozuna\Dev"},
    {"id": 3, "nome": "Copilot Chat",        "path": r"C:\Users\Yokozuna\OneDrive\Ficheiros do Microsoft Copilot Chat"},
    {"id": 4, "nome": "Copilot Notebooks",   "path": r"C:\Users\Yokozuna\OneDrive\Microsoft Copilot Chat Files\Copilot Notebook Uploads"},
    {"id": 5, "nome": "Drive G:",            "path": r"G:\"},
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
]

DRIVES = ["G"]


# ============================================================
# UTILS
# ============================================================
def humano(b):
    for u in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if b < 1024:
            return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} EB"


def ts():
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
        linha = f"\r  {self.prefix} [{barra}] {self.atual}/{self.total} ({pct:5.1f}%) ETA {eta:5.1f}s {sufixo}"
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
def es_count(query, timeout=60):
    try:
        r = subprocess.run(
            [ES, "-instance", INST, "-get-result-count", query],
            capture_output=True, text=True, timeout=timeout
        )
        return int(r.stdout.strip().split()[0] or 0)
    except Exception:
        return 0


def es_size(query, timeout=60):
    try:
        r = subprocess.run(
            [ES, "-instance", INST, "-get-total-size", query],
            capture_output=True, text=True, timeout=timeout
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
            errors="replace", timeout=180
        )
        return [l for l in r.stdout.splitlines() if l.strip()]
    except Exception:
        return []


# ============================================================
# ANALISAR LOCAL
# ============================================================
def analisar_local(local, prog=None):
    path = local["path"]

    if not os.path.exists(path):
        return {"id": local["id"], "nome": local["nome"], "path": path, "existe": False}

    q = f'path:"{path}"'
    n = es_count(q)
    b = es_size(q)

    por_tipo = {}
    for nome, tq in TIPOS:
        full_q = f'{q} {tq}'
        por_tipo[nome] = {
            "ficheiros": es_count(full_q),
            "bytes": es_size(full_q),
        }
        if prog:
            prog.update(0, sufixo=f"{local['nome']}: {nome}")

    top = es_top(f'{q} size:>10mb', n=10)

    return {
        "id": local["id"],
        "nome": local["nome"],
        "path": path,
        "existe": True,
        "ficheiros": n,
        "bytes": b,
        "humano": humano(b),
        "por_tipo": por_tipo,
        "top_10": top,
    }


# ============================================================
# ANALISAR DRIVE G:\
# ============================================================
def analisar_drive(letra):
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
    parser.add_argument("--local", type=int, help="Só 1 local (1-5)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    ts_str = ts()

    print()
    print("=" * 90)
    print(f"  ANALISE 5 LOCAIS  |  {datetime.now():%Y-%m-%d %H:%M:%S}")
    print("=" * 90)

    locais = LOCAIS
    if args.local:
        locais = [l for l in LOCAIS if l["id"] == args.local]
        if not locais:
            print(f"[ERRO] Local {args.local} nao existe (1-5)")
            return

    resultados = []
    prog = Progress(len(locais), prefix="Locais")

    for local in locais:
        prog.update(0, sufixo=f"-> {local['nome']}")
        t0 = time.time()
        r = analisar_local(local, prog)
        r["tempo"] = round(time.time() - t0, 2)
        resultados.append(r)
        prog.update(1, sufixo=f"{local['nome']}: {r.get('ficheiros',0):,}")

    prog.done()

    # Tabela principal
    print()
    print("=" * 90)
    print("  LOCAIS")
    print("=" * 90)
    print()
    print(f"  {'#':>2} {'NOME':<22} {'FICHEIROS':>12} {'TAMANHO':>12} {'TEMPO':>8}")
    print("  " + "-" * 88)

    total_f = 0
    total_b = 0
    for r in resultados:
        if not r.get("existe"):
            print(f"  {r['id']:>2} {r['nome']:<22} {'[nao existe]':>12}")
            continue
        print(f"  {r['id']:>2} {r['nome']:<22} {r['ficheiros']:>12,} "
              f"{r['humano']:>12} {r['tempo']:>7.2f}s")
        total_f += r["ficheiros"]
        total_b += r["bytes"]

    print("  " + "-" * 88)
    print(f"  {'':>2} {'TOTAL':<22} {total_f:>12,} {humano(total_b):>12}")
    print()

    # Tabela por tipo
    print("=" * 90)
    print("  POR TIPO")
    print("=" * 90)
    print()

    tipos_nomes = [t[0] for t in TIPOS]
    header = f"  {'LOCAL':<22} " + " ".join(f"{t[:7]:>8}" for t in tipos_nomes)
    print(header)
    print("  " + "-" * len(header))

    for r in resultados:
        if not r.get("existe"):
            continue
        linha = f"  {r['nome']:<22} "
        for t in tipos_nomes:
            n = r["por_tipo"].get(t, {}).get("ficheiros", 0)
            linha += f"{n:>8,} "
        print(linha)
    print()

    # Drive G:\
    for letra in DRIVES:
        if args.local and args.local != 5:
            continue
        raiz = analisar_drive(letra)
        if not raiz:
            continue
        print("=" * 90)
        print(f"  DRIVE {letra}:\\  (TOP-LEVEL)")
        print("=" * 90)
        print()
        print(f"  {'PASTA':<50} {'FICHEIROS':>12} {'TAMANHO':>12}")
        print("  " + "-" * 80)
        trf = 0
        trb = 0
        for p in raiz["pastas"]:
            print(f"  {p['nome'][:48]:<50} {p['ficheiros']:>12,} {humano(p['bytes']):>12}")
            trf += p["ficheiros"]
            trb += p["bytes"]
        print("  " + "-" * 80)
        print(f"  {'TOTAL':<50} {trf:>12,} {humano(trb):>12}")
        print()

    # Top 10 por local
    for r in resultados:
        if not r.get("existe") or not r.get("top_10"):
            continue
        print("=" * 90)
        print(f"  TOP 10 > 10MB  |  {r['nome']}  ({r['path']})")
        print("=" * 90)
        for linha in r["top_10"]:
            print(f"  {linha}")
        print()

    # JSON
    path = os.path.join(OUT, f"analise_{ts_str}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "data": datetime.now().isoformat(),
            "resultados": resultados,
        }, f, indent=2, ensure_ascii=False, default=str)
    print(f"  [OK] {path}")
    print()


if __name__ == "__main__":
    main()
