# -*- coding: utf-8 -*-
"""
V7 - Validacao + Sanitizacao + SANDBOX
SEM HASH - usa apenas filtros combinados ja validados.
"""
import os
import csv
import json
import time
import re
from collections import defaultdict
from datetime import datetime

ENTRADA = r"C:\ACERVO\logs\pipeline_v5\TODOS_NORMALIZADOS.csv"
DEST    = r"C:\ACERVO\logs\validacao_v7"
SANDBOX = r"C:\ACERVO\SANDBOX\validado_v7"
os.makedirs(DEST, exist_ok=True)
os.makedirs(SANDBOX, exist_ok=True)

# ============================================================
# FILTROS DE VALIDACAO
# ============================================================

# Exclusoes de lixo
LIXO = [
    "$recycle.bin", "system volume information",
    "\\temp\\", "\\tmp\\", "\\cache\\", "\\caches\\",
    "\\appdata\\local\\temp", "\\windows\\temp",
    "\\node_modules\\", "\\.git\\", "\\__pycache__\\",
    "\\venv\\", "\\site-packages\\", "\\programdata\\",
    "\\.cache\\", "\\.thumbnails\\", "\\internet cache",
    "\\windows.old\\",
]

def eh_lixo(caminho):
    c = caminho.lower()
    for p in LIXO:
        if p in c:
            return True
    return False

def humano(b):
    for u in ["B","KB","MB","GB","TB"]:
        if b < 1024:
            return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} PB"

# ============================================================
# CARREGAR
# ============================================================
def carregar():
    print("[1/6] A carregar TODOS_NORMALIZADOS.csv...")
    t0 = time.time()
    regs = []
    with open(ENTRADA, "r", encoding="utf-8", errors="replace", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                tam = int(row.get("tamanho", 0))
            except ValueError:
                continue
            if tam <= 0:
                continue
            regs.append({
                "origem": row.get("origem", ""),
                "tipo": row.get("tipo", ""),
                "nome": row.get("nome", ""),
                "caminho": row.get("caminho", ""),
                "tamanho": tam,
                "stem": row.get("stem", ""),
                "ext": row.get("ext", ""),
                "mime": row.get("mime", ""),
                "categoria": row.get("categoria", ""),
                "rank": int(row.get("rank", 3)),
                "prof": int(row.get("prof", 0)),
            })
    print(f"  Total: {len(regs):,} em {time.time()-t0:.2f}s")
    return regs

# ============================================================
# VALIDACAO 1: EXISTENCIA NO DISCO
# ============================================================
def validar_existencia(regs):
    print("[2/6] A validar existencia no disco...")
    t0 = time.time()
    existe = 0
    nao_existe = 0
    lixo = 0
    validos = []
    invalidos = []
    for r in regs:
        if eh_lixo(r["caminho"]):
            lixo += 1
            invalidos.append(r)
            continue
        if os.path.isfile(r["caminho"]):
            existe += 1
            validos.append(r)
        else:
            nao_existe += 1
            invalidos.append(r)
    print(f"  Existem no disco:  {existe:>10,}")
    print(f"  Nao existem:       {nao_existe:>10,}")
    print(f"  Lixo (temp/cache): {lixo:>10,}")
    print(f"  Tempo: {time.time()-t0:.2f}s")
    return validos, invalidos

# ============================================================
# VALIDACAO 2: STEM HIGIENIZADO
# ============================================================
def validar_stem(regs):
    print("[3/6] A validar stems...")
    t0 = time.time()
    vazios = 0
    curtos = 0
    ok = 0
    validos = []
    for r in regs:
        stem = r["stem"].strip()
        if not stem:
            vazios += 1
            continue
        if len(stem) < 2:
            curtos += 1
            continue
        ok += 1
        validos.append(r)
    print(f"  Stems OK:    {ok:>10,}")
    print(f"  Stems vazios: {vazios:>10,}")
    print(f"  Stems curtos: {curtos:>10,}")
    print(f"  Tempo: {time.time()-t0:.2f}s")
    return validos

# ============================================================
# VALIDACAO 3: DUPLICADOS DE CAMINHO
# ============================================================
def validar_caminhos(regs):
    print("[4/6] A validar caminhos unicos...")
    t0 = time.time()
    vistos = set()
    unicos = []
    dup_caminhos = 0
    for r in regs:
        cam = r["caminho"].lower()
        if cam in vistos:
            dup_caminhos += 1
            continue
        vistos.add(cam)
        unicos.append(r)
    print(f"  Caminhos unicos:     {len(unicos):>10,}")
    print(f"  Caminhos duplicados: {dup_caminhos:>10,}")
    print(f"  Tempo: {time.time()-t0:.2f}s")
    return unicos

# ============================================================
# SEGREGACAO COM FILTROS COMBINADOS
# ============================================================
def segregar(regs):
    print("[5/6] A segregar com filtros combinados...")
    t0 = time.time()

    # FILTRO: (stem, tamanho, extensao, tipo)
    # Nao usa hash - apenas metadados
    grupos = defaultdict(list)
    for r in regs:
        chave = (r["stem"], r["tamanho"], r["ext"], r["tipo"])
        grupos[chave].append(r)

    originais = []
    duplicados = []
    for chave, grupo in grupos.items():
        if len(grupo) == 1:
            originais.append(grupo[0])
            continue
        # Ordenar por rank de custodia
        grupo.sort(key=lambda x: (x["rank"], x["prof"], x["caminho"], x["nome"]))
        originais.append(grupo[0])
        for d in grupo[1:]:
            d["grau"] = "DUPLICADO_METADADOS"
            d["score"] = 85
            duplicados.append(d)

    print(f"  Grupos:     {len(grupos):>10,}")
    print(f"  Originais:  {len(originais):>10,}")
    print(f"  Duplicados: {len(duplicados):>10,}")
    print(f"  Tempo: {time.time()-t0:.2f}s")
    return originais, duplicados

# ============================================================
# SANDBOX
# ============================================================
def mover_para_sandbox(duplicados):
    print("[6/6] A mover duplicados para SANDBOX...")
    t0 = time.time()

    sbx_dup = os.path.join(SANDBOX, "duplicados")
    os.makedirs(sbx_dup, exist_ok=True)

    # Por categoria
    for cat in set(r["categoria"] for r in duplicados):
        os.makedirs(os.path.join(sbx_dup, cat), exist_ok=True)

    # Gravar CSV em vez de mover ficheiros (DRY-RUN)
    for cat in set(r["categoria"] for r in duplicados):
        regs_cat = [r for r in duplicados if r["categoria"] == cat]
        p = os.path.join(sbx_dup, cat, f"duplicados_{cat}.csv")
        with open(p, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["nome","caminho","tamanho","stem","ext","mime","rank","grau","score"])
            w.writeheader()
            for r in regs_cat:
                w.writerow({k: r.get(k, "") for k in w.fieldnames})

    # Manifesto
    manifesto = {
        "data": datetime.now().isoformat(),
        "modo": "DRYRUN",
        "sandbox": SANDBOX,
        "total_duplicados": len(duplicados),
        "por_categoria": {cat: sum(1 for r in duplicados if r["categoria"] == cat)
                          for cat in set(r["categoria"] for r in duplicados)},
        "ficheiros_alterados": 0,
    }
    with open(os.path.join(SANDBOX, "manifesto_v7.json"), "w", encoding="utf-8") as f:
        json.dump(manifesto, f, indent=2, ensure_ascii=False)

    print(f"  [OK] SANDBOX: {SANDBOX}")
    print(f"  Tempo: {time.time()-t0:.2f}s")

# ============================================================
# MAIN
# ============================================================
def main():
    t0 = time.time()
    print("=" * 78)
    print("  V7 - VALIDACAO + SANITIZACAO + SANDBOX (SEM HASH)")
    print("=" * 78)
    print()

    regs = carregar()
    print()

    validos, invalidos = validar_existencia(regs)
    print()

    validos = validar_stem(validos)
    print()

    validos = validar_caminhos(validos)
    print()

    orig, dup = segregar(validos)
    print()

    mover_para_sandbox(dup)
    print()

    # ============================================================
    # GRAVAR RESULTADOS
    # ============================================================
    print("A gravar resultados finais...")

    campos = ["origem","tipo","nome","caminho","tamanho","stem","ext","mime","categoria","rank","grau","score"]

    orig_path = os.path.join(DEST, "ORIGINAIS_VALIDADOS.csv")
    with open(orig_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for r in orig:
            w.writerow({k: r.get(k, "") for k in campos})
    print(f"  [OK] {orig_path} ({len(orig):,})")

    dup_path = os.path.join(DEST, "DUPLICADOS_VALIDADOS.csv")
    with open(dup_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for r in dup:
            w.writerow({k: r.get(k, "") for k in campos})
    print(f"  [OK] {dup_path} ({len(dup):,})")

    # ============================================================
    # DISTRIBUICAO POR CATEGORIA
    # ============================================================
    print()
    print("  DISTRIBUICAO POR CATEGORIA:")
    print("-" * 78)
    print(f"  {'Categoria':<15} {'Orig':>10} {'Dup':>10} {'%dup':>8} {'GB dup':>12}")
    print("-" * 78)

    espaco_total = 0
    for cat in sorted(set(r["categoria"] for r in regs)):
        o = [r for r in orig if r["categoria"] == cat]
        d = [r for r in dup if r["categoria"] == cat]
        if not (o or d):
            continue
        tam_d = sum(r["tamanho"] for r in d)
        espaco_total += tam_d
        pct = len(d) / (len(o) + len(d)) * 100 if (len(o) + len(d)) else 0
        print(f"  {cat:<15} {len(o):>10,} {len(d):>10,} {pct:>7.1f}% {humano(tam_d):>12}")
    print("-" * 78)

    # ============================================================
    # RESUMO FINAL
    # ============================================================
    print()
    print("=" * 78)
    print("  RESUMO FINAL (V7)")
    print("=" * 78)
    print(f"  Total entrada:      {len(regs):>10,}")
    print(f"  Validos no disco:   {len(validos):>10,}")
    print(f"  Invalidos/Lixo:     {len(invalidos):>10,}")
    print(f"  Originais:          {len(orig):>10,}")
    print(f"  Duplicados:         {len(dup):>10,}")
    print(f"  Espaco recuperavel: {humano(espaco_total)}")
    print(f"  Tempo total:        {time.time()-t0:.2f}s")
    print("=" * 78)

    # Relatorio
    rel = {
        "data": datetime.now().isoformat(),
        "versao": "v7",
        "modo": "DRYRUN_SEM_HASH",
        "total_entrada": len(regs),
        "validos": len(validos),
        "invalidos": len(invalidos),
        "originais": len(orig),
        "duplicados": len(dup),
        "espaco_recuperavel_bytes": espaco_total,
        "espaco_recuperavel_gb": round(espaco_total / 1024 / 1024 / 1024, 2),
        "sandbox": SANDBOX,
        "ficheiros_alterados": 0,
    }
    rel_path = os.path.join(DEST, "relatorio_v7.json")
    with open(rel_path, "w", encoding="utf-8") as f:
        json.dump(rel, f, indent=2, ensure_ascii=False)
    print(f"  Relatorio: {rel_path}")

if __name__ == "__main__":
    main()
