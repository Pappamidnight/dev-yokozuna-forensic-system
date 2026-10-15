# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import json
import os
import time
import csv

os.makedirs(r"C:\ACERVO\logs\google_drive", exist_ok=True)

QUERY = (
    'path:"G:\\O meu disco" | path:"G:\\Outros computadores" '
    '!attrib:H !attrib:S !empty: '
    '!path:"$Recycle.Bin" !path:"System Volume Information" '
    '!path:node_modules !path:.git !path:__pycache__ '
    '!path:venv !path:site-packages !path:AppData !path:ProgramData'
)

BASE_URL = "http://localhost:8080/"

def main():
    t0 = time.time()
    print("=" * 70)
    print("  EXTRACAO GOOGLE DRIVE - MAXIMA CONFIANCA")
    print("=" * 70)
    print(f"  Query:    {QUERY}")
    print(f"  Destino:  C:\\ACERVO\\logs\\google_drive\\google_drive_full.csv")
    print()

    params = {
        "search": QUERY,
        "json": "1",
        "count": "10000000",
        "path_column": "1",
        "size_column": "1",
        "date_modified_column": "1",
        "attributes_column": "1",
    }
    url = BASE_URL + "?" + urllib.parse.urlencode(params)

    print("[1/2] A consultar Everything HTTP...")
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=1800) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  [ERRO] Falha na consulta HTTP: {e}")
        print("  Verifique se o Everything esta a correr na porta 8080")
        return

    print(f"  Download: {len(raw)/1024/1024:.2f} MB em {time.time()-t0:.2f}s")

    data = json.loads(raw)
    results = data.get("results", [])
    print(f"  Registos: {len(results):,}")
    print()

    print("[2/2] A gravar CSV...")
    out = r"C:\ACERVO\logs\google_drive\google_drive_full.csv"
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Nome", "Caminho", "Tamanho", "DataMod", "Atributos", "Extensao"])
        for x in results:
            name = x.get("name", "") or ""
            path = x.get("path", "") or ""
            size = x.get("size", 0) or 0
            dmod = x.get("date_modified", "") or ""
            attr = x.get("attributes", "") or ""
            ext = os.path.splitext(name)[1].lower()
            w.writerow([name, path, size, dmod, attr, ext])

    sz = os.path.getsize(out) / 1024 / 1024
    print(f"  [OK] {out}")
    print(f"  Tamanho: {sz:.2f} MB")
    print(f"  Tempo total: {time.time()-t0:.2f}s")
    print("=" * 70)

if __name__ == "__main__":
    main()
