# -*- coding: utf-8 -*-
"""
Extracao MAXIMA do Google Drive com TODOS os filtros do Everything.
Usa dupe: + multiplos atributos + exclusoes + colunas extra.
"""
import urllib.request
import urllib.parse
import json
import os
import time
import csv

DEST = r"C:\ACERVO\logs\google_drive\max"
os.makedirs(DEST, exist_ok=True)

# ============================================================
# FILTROS DO EVERYTHING (baseado no manual oficial)
# ============================================================

# Base: Google Drive
BASE = 'path:"G:\\O meu disco" | path:"G:\\Outros computadores"'

# Filtros de duplicados (testa varios)
DUPES = [
    ("dupe_name",       "dupe:name"),
    ("dupe_size",       "dupe:size"),
    ("dupe_name_size",  "dupe:name;size"),
    ("dupe_size_date",  "dupe:size;date-modified"),
    ("dupe_stem",       "dupe:stem"),
    ("dupe_ext",        "dupe:extension"),
    ("dupe_hash",       "dupe:hash"),
    ("dupe_sha256",     "dupe:sha256"),
    ("dupe_size_date_created", "dupe:size;date-created"),
    ("dupe_name_ext",   "dupe:name;extension"),
    ("dupe_name_size_date", "dupe:name;size;date-modified"),
]

# Exclusoes universais
EXCLUSOES = (
    '!attrib:H !attrib:S !empty: '
    '!path:"$Recycle.Bin" !path:"System Volume Information" '
    '!path:node_modules !path:.git !path:__pycache__ '
    '!path:venv !path:site-packages !path:AppData !path:ProgramData '
    '!path:cache !path:Cache !path:TEMP !path:Temp !path:tmp '
    '!path:.thumbnails !path:thumbnails'
)

def consultar_everything(query, count=10000000):
    params = {
        "search": query,
        "json": "1",
        "count": str(count),
        "path_column": "1",
        "size_column": "1",
        "date_modified_column": "1",
        "date_created_column": "1",
        "date_accessed_column": "1",
        "attributes_column": "1",
        "extension_column": "1",
    }
    url = "http://localhost:8080/?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=1800) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        data = json.loads(raw)
        return data.get("results", [])
    except Exception as e:
        print(f"  [ERRO] {e}")
        return []

def gravar_csv(results, path):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Nome", "Caminho", "Tamanho", "DataMod", "DataCriacao", "DataAcesso", "Atributos", "Extensao"])
        for x in results:
            name = x.get("name", "") or ""
            p = x.get("path", "") or ""
            size = x.get("size", 0) or 0
            dmod = x.get("date_modified", "") or ""
            dcre = x.get("date_created", "") or ""
            dacc = x.get("date_accessed", "") or ""
            attr = x.get("attributes", "") or ""
            ext = os.path.splitext(name)[1].lower()
            w.writerow([name, p, size, dmod, dcre, dacc, attr, ext])

def main():
    t0 = time.time()
    print("=" * 78)
    print("  EXTRACAO MAXIMA - GOOGLE DRIVE (TODOS OS FILTROS EVERYTHING)")
    print("=" * 78)
    print()

    # Testar se Everything responde
    print("[1/3] A testar Everything HTTP...")
    teste = consultar_everything("*.pdf", count=1)
    print(f"  [OK] Everything responde (teste: {len(teste)} resultados)")
    print()

    # ============================================================
    # FASE 1: EXTRAIR POR CADA FILTRO DE DUPLICADOS
    # ============================================================
    print("[2/3] A extrair por cada filtro de duplicados...")
    print()

    resultados_por_filtro = {}
    for nome, filtro in DUPES:
        query = f"{BASE} {filtro} {EXCLUSOES}"
        print(f"  [{nome}]")
        print(f"    Query: {query[:100]}...")
        t_f = time.time()
        results = consultar_everything(query)
        dt = time.time() - t_f
        resultados_por_filtro[nome] = results
        print(f"    Resultados: {len(results):,} em {dt:.2f}s")

        if results:
            out = os.path.join(DEST, f"dupe_{nome}.csv")
            gravar_csv(results, out)
            print(f"    [OK] {out}")
        print()

    # ============================================================
    # FASE 2: UNIAO DE TODOS OS RESULTADOS
    # ============================================================
    print("[3/3] A criar uniao de todos os resultados...")
    t_u = time.time()

    # Uniao por caminho unico
    uniao = {}
    for nome, results in resultados_por_filtro.items():
        for x in results:
            p = x.get("path", "") or ""
            n = x.get("name", "") or ""
            chave = f"{p}\\{n}" if p else n
            if chave not in uniao:
                uniao[chave] = x
                uniao[chave]["_filtros"] = set()
            uniao[chave]["_filtros"].add(nome)

    print(f"  Uniao total: {len(uniao):,} ficheiros unicos")
    print(f"  Tempo: {time.time()-t_u:.2f}s")

    # Gravar uniao
    out_u = os.path.join(DEST, "uniao_max.csv")
    with open(out_u, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Nome", "Caminho", "Tamanho", "DataMod", "DataCriacao", "DataAcesso", "Atributos", "Extensao", "Filtros_Match"])
        for chave, x in uniao.items():
            name = x.get("name", "") or ""
            p = x.get("path", "") or ""
            size = x.get("size", 0) or 0
            dmod = x.get("date_modified", "") or ""
            dcre = x.get("date_created", "") or ""
            dacc = x.get("date_accessed", "") or ""
            attr = x.get("attributes", "") or ""
            ext = os.path.splitext(name)[1].lower()
            filtros = "|".join(sorted(x.get("_filtros", set())))
            w.writerow([name, p, size, dmod, dcre, dacc, attr, ext, filtros])
    print(f"  [OK] {out_u}")

    # ============================================================
    # RESUMO
    # ============================================================
    print()
    print("=" * 78)
    print("  RESUMO FINAL")
    print("=" * 78)
    print(f"  {'Filtro':<30} {'Resultados':>15}")
    print("-" * 78)
    for nome, results in sorted(resultados_por_filtro.items(), key=lambda x: -len(x[1])):
        print(f"  {nome:<30} {len(results):>15,}")
    print("-" * 78)
    print(f"  {'UNIAO TOTAL':<30} {len(uniao):>15,}")
    print()
    print(f"  Tempo total: {time.time()-t0:.2f}s")
    print("=" * 78)

if __name__ == "__main__":
    main()
