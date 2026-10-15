# -*- coding: utf-8 -*-
"""analise_5locais.py - Analise de 5 locais + G:\ com progress bar"""
import os, sys, json, time, subprocess, argparse
from datetime import datetime

ES = r"C:\ACERVO\bin\es.exe"
INST = "1.5a"
OUT = r"C:\ACERVO\logs\analise_5locais"
os.makedirs(OUT, exist_ok=True)

LOCAIS = [
    {"id": 1, "nome": "Perfil",            "path": r"C:\Users\Yokozuna"},
    {"id": 2, "nome": "Dev",               "path": r"C:\Users\Yokozuna\Dev"},
    {"id": 3, "nome": "Copilot Chat",      "path": r"C:\Users\Yokozuna\OneDrive\Ficheiros do Microsoft Copilot Chat"},
    {"id": 4, "nome": "Copilot Notebooks", "path": r"C:\Users\Yokozuna\OneDrive\Microsoft Copilot Chat Files\Copilot Notebook Uploads"},
    {"id": 5, "nome": "Drive G:",          "path": "G:\\"},
]

TIPOS = [
    ("pdf",    "ext:pdf"),
    ("word",   "ext:doc;docx;odt;rtf"),
    ("excel",  "ext:xls;xlsx;ods"),
    ("imagem", "image:"),
    ("video",  "video:"),
    ("audio",  "audio:"),
    ("codigo", "ext:py;js;ts;cs;rs;go;ps1;sh;bat"),
    ("dados",  "ext:json;yaml;yml;csv;db;sqlite;duckdb"),
    ("zip",    "ext:zip;rar;7z;tar;gz;iso"),
]


def humano(b):
    for u in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if b < 1024:
            return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} EB"


class Progress:
    def __init__(self, total, prefix="", width=40):
        self.total, self.atual = max(1, total), 0
        self.prefix, self.width = prefix, width
        self.t0 = time.time()

    def update(self, n=1, sufixo=""):
        self.atual = min(self.atual + n, self.total)
        pct = 100 * self.atual / self.total
        preench = int(self.width * self.atual / self.total)
        barra = "=" * preench + "-" * (self.width - preench)
        tempo = time.time() - self.t0
        eta = (tempo / self.atual) * (self.total - self.atual) if self.atual else 0
        sys.stdout.write(f"\r  {self.prefix} [{barra}] {self.atual}/{self.total} ({pct:5.1f}%) ETA {eta:5.1f}s {sufixo}"[:200])
        sys.stdout.flush()

    def done(self, sufixo=""):
        tempo = time.time() - self.t0
        sys.stdout.write("\r" + " " * 200 + "\r")
        sys.stdout.flush()
        print(f"  {self.prefix} OK ({self.total} em {tempo:.2f}s) {sufixo}")


def es_count(q):
    try:
        r = subprocess.run([ES, "-instance", INST, "-get-result-count", q],
                           capture_output=True, text=True, timeout=60)
        return int(r.stdout.strip().split()[0] or 0)
    except Exception:
        return 0


def es_size(q):
    try:
        r = subprocess.run([ES, "-instance", INST, "-get-total-size", q],
                           capture_output=True, text=True, timeout=60)
        return int(r.stdout.strip().split()[0] or 0)
    except Exception:
        return 0


def es_top(q, n=10):
    try:
        r = subprocess.run([ES, "-instance", INST, "-n", str(n), "-size", "-dm",
                            "-sort", "size-descending", q],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=180)
        return [l for l in r.stdout.splitlines() if l.strip()]
    except Exception:
        return []


def analisar_local(local):
    path = local["path"]
    if not os.path.exists(path):
        return {"id": local["id"], "nome": local["nome"], "path": path, "existe": False}
    q = f'path:"{path}"'
    n, b = es_count(q), es_size(q)
    por_tipo = {}
    for nome, tq in TIPOS:
        full = f'{q} {tq}'
        por_tipo[nome] = {"ficheiros": es_count(full), "bytes": es_size(full)}
    return {"id": local["id"], "nome": local["nome"], "path": path, "existe": True,
            "ficheiros": n, "bytes": b, "humano": humano(b),
            "por_tipo": por_tipo, "top_10": es_top(f'{q} size:>10mb', 10)}


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
            pastas.append({"nome": d, "caminho": full, "ficheiros": es_count(q), "bytes": es_size(q)})
    except PermissionError:
        pass
    pastas.sort(key=lambda x: -x["bytes"])
    return {"raiz": raiz, "pastas": pastas}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--local", type=int)
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    print()
    print("=" * 90)
    print(f"  ANALISE 5 LOCAIS  |  {datetime.now():%Y-%m-%d %H:%M:%S}")
    print("=" * 90)

    locais = [l for l in LOCAIS if l["id"] == a.local] if a.local else LOCAIS
    if not locais:
        print(f"[ERRO] Local {a.local} nao existe (1-5)")
        return

    res, prog = [], Progress(len(locais), "Locais")
    for local in locais:
        prog.update(0, f"-> {local['nome']}")
        t0 = time.time()
        r = analisar_local(local)
        r["tempo"] = round(time.time() - t0, 2)
        res.append(r)
        prog.update(1, f"{local['nome']}: {r.get('ficheiros',0):,}")
    prog.done()

    # Tabela
    print()
    print(f"  {'#':>2} {'NOME':<22} {'FICHEIROS':>12} {'TAMANHO':>12} {'TEMPO':>8}")
    print("  " + "-" * 88)
    tf = tb = 0
    for r in res:
        if not r.get("existe"):
            print(f"  {r['id']:>2} {r['nome']:<22} {'[nao existe]':>12}")
            continue
        print(f"  {r['id']:>2} {r['nome']:<22} {r['ficheiros']:>12,} {r['humano']:>12} {r['tempo']:>7.2f}s")
        tf += r["ficheiros"]; tb += r["bytes"]
    print("  " + "-" * 88)
    print(f"  {'':>2} {'TOTAL':<22} {tf:>12,} {humano(tb):>12}")
    print()

    # Por tipo
    print("  POR TIPO")
    print("  " + "-" * 88)
    tipos_nomes = [t[0] for t in TIPOS]
    header = f"  {'LOCAL':<22} " + " ".join(f"{t[:7]:>8}" for t in tipos_nomes)
    print(header)
    for r in res:
        if not r.get("existe"):
            continue
        linha = f"  {r['nome']:<22} "
        for t in tipos_nomes:
            linha += f"{r['por_tipo'].get(t, {}).get('ficheiros', 0):>8,} "
        print(linha)
    print()

    # Drive G:
    if not a.local or a.local == 5:
        raiz = analisar_drive("G")
        if raiz:
            print("  DRIVE G:\\ (TOP-LEVEL)")
            print("  " + "-" * 88)
            print(f"  {'PASTA':<50} {'FICHEIROS':>12} {'TAMANHO':>12}")
            trf = trb = 0
            for pp in raiz["pastas"]:
                print(f"  {pp['nome'][:48]:<50} {pp['ficheiros']:>12,} {humano(pp['bytes']):>12}")
                trf += pp["ficheiros"]; trb += pp["bytes"]
            print("  " + "-" * 88)
            print(f"  {'TOTAL':<50} {trf:>12,} {humano(trb):>12}")
            print()

    # Top 10
    for r in res:
        if not r.get("existe") or not r.get("top_10"):
            continue
        print(f"  TOP 10 >10MB  |  {r['nome']}")
        for linha in r["top_10"]:
            print(f"    {linha}")
        print()

    # JSON
    path = os.path.join(OUT, f"analise_{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"data": datetime.now().isoformat(), "resultados": res},
                  f, indent=2, ensure_ascii=False, default=str)
    print(f"  [OK] {path}")
    print()


if __name__ == "__main__":
    main()
