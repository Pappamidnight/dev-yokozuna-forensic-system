# -*- coding: utf-8 -*-
"""
incremental.py - Analise 1 local, 1 tipo de cada vez
=====================================================
Nao congela. Cada query e rapida. Guarda resultados incrementalmente.

Uso:
    python incremental.py --local 1
    python incremental.py --local 1 --tipo pdf
    python incremental.py --listar-locais
"""
import os
import sys
import json
import time
import subprocess
import argparse
from datetime import datetime

ES = r"C:\ACERVO\bin\es.exe"
INST = "1.5a"
OUT = r"C:\ACERVO\logs\incremental"
os.makedirs(OUT, exist_ok=True)

LOCAIS = {
    1: {"nome": "Perfil",             "path": r"C:\Users\Yokozuna"},
    2: {"nome": "Dev",                "path": r"C:\Users\Yokozuna\Dev"},
    3: {"nome": "Copilot Chat",       "path": r"C:\Users\Yokozuna\OneDrive\Ficheiros do Microsoft Copilot Chat"},
    4: {"nome": "Copilot Notebooks",  "path": r"C:\Users\Yokozuna\OneDrive\Microsoft Copilot Chat Files\Copilot Notebook Uploads"},
    5: {"nome": "Drive G:",           "path": "G:\\"},
}

TIPOS = {
    "total":  "",
    "pdf":    "ext:pdf",
    "word":   "ext:doc;docx;odt;rtf",
    "excel":  "ext:xls;xlsx;ods",
    "imagem": "image:",
    "video":  "video:",
    "audio":  "audio:",
    "codigo": "ext:py;js;ts;cs;rs;go;ps1;sh;bat",
    "dados":  "ext:json;yaml;yml;csv;db;sqlite;duckdb",
    "zip":    "ext:zip;rar;7z;tar;gz;iso",
}


def humano(b):
    # Detetar valores invalidos (sentinela do es.exe)
    if b <= 0:
        return "0 B"
    if b > 2**53:  # > 8 PB — impossivel
        return f"(invalido: {b} bytes)"
    for u in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024:
            return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} PB"


def bytes_valido(b):
    """Retorna True se b for um valor plausivel."""
    return 0 < b < 2**53


def es_query(query, timeout=30):
    """Corre 1 query com timeout curto."""
    try:
        r = subprocess.run(
            [ES, "-instance", INST, "-get-result-count", query],
            capture_output=True, text=True, timeout=timeout
        )
        n = r.stdout.strip().split()[0] if r.stdout.strip() else "0"
        return int(n) if n.isdigit() else 0
    except Exception:
        return 0


def es_size(query, timeout=30):
    try:
        r = subprocess.run(
            [ES, "-instance", INST, "-get-total-size", query],
            capture_output=True, text=True, timeout=timeout
        )
        n = r.stdout.strip().split()[0] if r.stdout.strip() else "0"
        val = int(n) if n.isdigit() else 0
        # Detetar valor sentinela (2^54 = 16384 PB)
        if val >= 2**53:
            return 0
        return val
    except Exception:
        return 0


def analisar_local_tipo(local_id, tipo):
    """Analisa 1 local + 1 tipo."""
    local = LOCAIS[local_id]
    path = local["path"]

    if not os.path.exists(path):
        return None

    q = f'path:"{path}"'
    if TIPOS[tipo]:
        q += f' {TIPOS[tipo]}'

    t0 = time.time()
    n = es_query(q, timeout=30)
    b = es_size(q, timeout=30)
    tempo = round(time.time() - t0, 2)

    return {
        "local_id": local_id,
        "local_nome": local["nome"],
        "local_path": path,
        "tipo": tipo,
        "query": q,
        "ficheiros": n,
        "bytes": b,
        "humano": humano(b),
        "tempo": tempo,
        "timestamp": datetime.now().isoformat(),
    }


def listar_locais():
    print()
    print("=" * 70)
    print("  LOCAIS DISPONIVEIS")
    print("=" * 70)
    for lid, info in LOCAIS.items():
        existe = "OK" if os.path.exists(info["path"]) else "FALTA"
        print(f"  [{lid}] {info['nome']:<22} {info['path']:<50} [{existe}]")
    print()
    print("  TIPOS DISPONIVEIS")
    print("=" * 70)
    for tipo in TIPOS.keys():
        print(f"  - {tipo}")
    print()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--local", type=int, help="ID do local (1-5)")
    p.add_argument("--tipo", help="Tipo (default: total)")
    p.add_argument("--todos-tipos", action="store_true",
                   help="Todos os tipos do local")
    p.add_argument("--listar-locais", action="store_true")
    a = p.parse_args()

    if a.listar_locais:
        listar_locais()
        return

    if not a.local:
        print("[ERRO] Usa --local 1 a 5")
        print("       Ou --listar-locais")
        return

    if a.local not in LOCAIS:
        print(f"[ERRO] Local {a.local} nao existe (1-5)")
        return

    local_info = LOCAIS[a.local]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    print()
    print("=" * 70)
    print(f"  ANALISE: {local_info['nome']}  ({local_info['path']})")
    print("=" * 70)
    print()

    # 1 tipo
    if a.tipo:
        if a.tipo not in TIPOS:
            print(f"[ERRO] Tipo '{a.tipo}' nao existe")
            print(f"       Validos: {', '.join(TIPOS.keys())}")
            return
        r = analisar_local_tipo(a.local, a.tipo)
        if not r:
            print(f"[ERRO] Local nao existe: {local_info['path']}")
            return
        print(f"  Tipo:      {r['tipo']}")
        print(f"  Query:     {r['query']}")
        print(f"  Ficheiros: {r['ficheiros']:,}")
        print(f"  Tamanho:   {r['humano']}")
        print(f"  Tempo:     {r['tempo']}s")
        print()

        path = os.path.join(OUT, f"{local_info['nome']}_{r['tipo']}_{ts}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(r, f, indent=2, ensure_ascii=False)
        print(f"  [OK] {path}")
        return

    # Todos os tipos
    if a.todos_tipos:
        print(f"  A analisar {len(TIPOS)} tipos...")
        print()
        print(f"  {'TIPO':<12} {'FICHEIROS':>12} {'TAMANHO':>12} {'TEMPO':>8}")
        print("  " + "-" * 48)

        resultados = []
        for tipo in TIPOS.keys():
            r = analisar_local_tipo(a.local, tipo)
            if not r:
                continue
            resultados.append(r)
            print(f"  {r['tipo']:<12} {r['ficheiros']:>12,} {r['humano']:>12} {r['tempo']:>7.2f}s")

        path = os.path.join(OUT, f"{local_info['nome']}_todos_{ts}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "local": local_info,
                "resultados": resultados,
                "timestamp": datetime.now().isoformat(),
            }, f, indent=2, ensure_ascii=False)
        print()
        print(f"  [OK] {path}")
        return

    # So total
    r = analisar_local_tipo(a.local, "total")
    if not r:
        print(f"[ERRO] Local nao existe: {local_info['path']}")
        return

    print(f"  Local:     {r['local_nome']}")
    print(f"  Path:      {r['local_path']}")
    print(f"  Ficheiros: {r['ficheiros']:,}")
    print(f"  Tamanho:   {r['humano']}")
    print(f"  Tempo:     {r['tempo']}s")
    print()

    path = os.path.join(OUT, f"{local_info['nome']}_total_{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(r, f, indent=2, ensure_ascii=False)
    print(f"  [OK] {path}")


if __name__ == "__main__":
    main()




