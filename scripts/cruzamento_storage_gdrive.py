# -*- coding: utf-8 -*-
"""
Cruzamento entre:
- C:\ACERVO\storage\files (Content-Addressable Storage)
- Google Drive (por_tipo)
- Simulacao DRY-RUN de quarentena
"""
import os
import csv
import json
import time
import hashlib
import re
from collections import defaultdict
from datetime import datetime

STORAGE = r"C:\ACERVO\storage\files"
GDRIVE  = r"C:\ACERVO\logs\google_drive\por_tipo"
SEG_V4  = r"C:\ACERVO\logs\google_drive\segregado_v4"
DEST    = r"C:\ACERVO\logs\cruzamento_final"
os.makedirs(DEST, exist_ok=True)

TIPOS = ["database","video","excel","audio","word","pdf",
         "imagem","json","texto","yaml","csv","markdown"]

def humano(b):
    for u in ["B","KB","MB","GB","TB"]:
        if b < 1024:
            return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} PB"

def sha256_parcial(p, bloco=65536):
    """Hash SHA-256 dos primeiros 64KB + ultimos 64KB."""
    try:
        h = hashlib.sha256()
        with open(p, "rb") as f:
            h.update(f.read(bloco))
            try:
                f.seek(-bloco, 2)
                h.update(f.read(bloco))
            except OSError:
                pass
        return h.hexdigest()[:32]
    except Exception:
        return None

def carregar_storage():
    """Le todos os ficheiros do storage."""
    print("[1/5] A carregar C:\\ACERVO\\storage\\files...")
    t0 = time.time()
    regs = []
    if not os.path.isdir(STORAGE):
        print(f"  [ERRO] Storage nao existe: {STORAGE}")
        return regs

    for root, _, files in os.walk(STORAGE):
        for f in files:
            p = os.path.join(root, f)
            try:
                st = os.stat(p)
                regs.append({
                    "hash": f,
                    "caminho": p,
                    "tamanho": st.st_size,
                    "origem": "STORAGE",
                })
            except Exception:
                continue

    print(f"  Total: {len(regs):,} ficheiros em {time.time()-t0:.2f}s")
    return regs

def carregar_gdrive():
    """Le os originais do Google Drive."""
    print("[2/5] A carregar originais do Google Drive...")
    t0 = time.time()
    regs = []
    orig_path = os.path.join(SEG_V4, "ORIGINAIS.csv")
    if not os.path.isfile(orig_path):
        print(f"  [ERRO] Nao existe: {orig_path}")
        return regs

    with open(orig_path, "r", encoding="utf-8", errors="replace", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                tam = int(row.get("tamanho", 0))
            except ValueError:
                continue
            if tam <= 0:
                continue
            regs.append({
                "tipo": row.get("tipo", ""),
                "nome": row.get("nome", ""),
                "caminho": row.get("caminho", ""),
                "tamanho": tam,
                "origem": "GDRIVE",
            })

    print(f"  Total: {len(regs):,} ficheiros em {time.time()-t0:.2f}s")
    return regs

def cruzar(storage, gdrive):
    """Cruza por (nome, tamanho)."""
    print("[3/5] A cruzar por (nome, tamanho)...")
    t0 = time.time()

    # Indexar storage por (nome, tamanho)
    idx_storage = defaultdict(list)
    for r in storage:
        chave = (r["hash"].lower(), r["tamanho"])
        idx_storage[chave].append(r)

    # Indexar gdrive por (nome, tamanho)
    idx_gdrive = defaultdict(list)
    for r in gdrive:
        chave = (r["nome"].lower(), r["tamanho"])
        idx_gdrive[chave].append(r)

    # Encontrar chaves em comum
    comuns = set(idx_storage.keys()) & set(idx_gdrive.keys())

    print(f"  Chaves storage: {len(idx_storage):,}")
    print(f"  Chaves gdrive:  {len(idx_gdrive):,}")
    print(f"  Chaves comuns:  {len(comuns):,}")
    print(f"  Tempo: {time.time()-t0:.2f}s")
    print()

    return idx_storage, idx_gdrive, comuns

def simular_quarentena(gdrive):
    """Simula quarentena DRY-RUN."""
    print("[4/5] A simular quarentena DRY-RUN...")
    t0 = time.time()

    por_tipo = defaultdict(lambda: {"orig": 0, "dup": 0, "bytes": 0})

    # Ler duplicados
    dup_path = os.path.join(SEG_V4, "DUPLICADOS.csv")
    if os.path.isfile(dup_path):
        with open(dup_path, "r", encoding="utf-8", errors="replace", newline="") as f:
            r = csv.DictReader(f)
            for row in r:
                tipo = row.get("tipo", "outro")
                try:
                    tam = int(row.get("tamanho", 0))
                except ValueError:
                    tam = 0
                por_tipo[tipo]["dup"] += 1
                por_tipo[tipo]["bytes"] += tam

    # Ler originais
    orig_path = os.path.join(SEG_V4, "ORIGINAIS.csv")
    if os.path.isfile(orig_path):
        with open(orig_path, "r", encoding="utf-8", errors="replace", newline="") as f:
            r = csv.DictReader(f)
            for row in r:
                tipo = row.get("tipo", "outro")
                por_tipo[tipo]["orig"] += 1

    print(f"  Tempo: {time.time()-t0:.2f}s")
    return por_tipo

def main():
    t0 = time.time()
    print("=" * 78)
    print("  CRUZAMENTO FINAL - STORAGE vs GDRIVE")
    print("=" * 78)
    print()

    storage = carregar_storage()
    gdrive = carregar_gdrive()
    print()

    if not storage and not gdrive:
        print("  [ERRO] Nenhum registo!")
        return

    idx_s, idx_g, comuns = cruzar(storage, gdrive)
    print()

    por_tipo = simular_quarentena(gdrive)
    print()

    # ============================================================
    # GRAVAR RESULTADOS
    # ============================================================
    print("[5/5] A gravar resultados...")

    # 1. Ficheiros comuns (no storage E no gdrive)
    if comuns:
        out_comuns = os.path.join(DEST, "comuns_storage_gdrive.csv")
        with open(out_comuns, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["nome", "tamanho", "storage_caminho", "gdrive_caminho", "gdrive_tipo"])
            for chave in comuns:
                for s in idx_s[chave]:
                    for g in idx_g[chave]:
                        w.writerow([chave[0], chave[1], s["caminho"], g["caminho"], g["tipo"]])
        print(f"  [OK] {out_comuns}")
    else:
        print(f"  [--] Nenhum ficheiro comum")

    # 2. Relatorio de quarentena simulada
    rel = {
        "data": datetime.now().isoformat(),
        "modo": "DRYRUN",
        "storage": {
            "total": len(storage),
            "bytes": sum(r["tamanho"] for r in storage),
        },
        "gdrive": {
            "total": len(gdrive),
            "bytes": sum(r["tamanho"] for r in gdrive),
        },
        "comuns": {
            "total": len(comuns),
        },
        "por_tipo": dict(por_tipo),
        "ficheiros_alterados": 0,
    }
    out_rel = os.path.join(DEST, "relatorio_cruzamento.json")
    with open(out_rel, "w", encoding="utf-8") as f:
        json.dump(rel, f, indent=2, ensure_ascii=False)
    print(f"  [OK] {out_rel}")

    # ============================================================
    # RESUMO
    # ============================================================
    total_storage = sum(r["tamanho"] for r in storage)
    total_gdrive = sum(r["tamanho"] for r in gdrive)
    total_dup = sum(v["bytes"] for v in por_tipo.values())

    print()
    print("=" * 78)
    print("  RESUMO FINAL")
    print("=" * 78)
    print(f"  Storage (C:\\ACERVO):")
    print(f"    Ficheiros:  {len(storage):>12,}")
    print(f"    Bytes:      {total_storage:>15,}")
    print(f"    Humano:     {humano(total_storage):>15}")
    print()
    print(f"  Google Drive (originais):")
    print(f"    Ficheiros:  {len(gdrive):>12,}")
    print(f"    Bytes:      {total_gdrive:>15,}")
    print(f"    Humano:     {humano(total_gdrive):>15}")
    print()
    print(f"  Ficheiros em comum (mesmo nome + tamanho):")
    print(f"    Chaves:     {len(comuns):>12,}")
    print()
    print(f"  Quarentena simulada (DRY-RUN):")
    print(f"    Duplicados: {sum(v['dup'] for v in por_tipo.values()):>12,}")
    print(f"    Espaco:     {humano(total_dup):>15}")
    print()
    print(f"  Ficheiros alterados: 0 (INTEGRIDADE TOTAL)")
    print(f"  Tempo total: {time.time()-t0:.2f}s")
    print("=" * 78)

    # Top 20 tipos com mais duplicados
    print()
    print("  POR TIPO (ordenado por espaço):")
    print("-" * 78)
    print(f"  {'Tipo':<12} {'Orig':>10} {'Dup':>10} {'%dup':>8} {'Bytes':>15}")
    print("-" * 78)
    for tipo, dados in sorted(por_tipo.items(), key=lambda x: -x[1]["bytes"]):
        orig = dados["orig"]
        dup = dados["dup"]
        pct = (dup / (orig + dup) * 100) if (orig + dup) else 0
        print(f"  {tipo:<12} {orig:>10,} {dup:>10,} {pct:>7.1f}% {humano(dados['bytes']):>15}")
    print("-" * 78)

if __name__ == "__main__":
    main()
