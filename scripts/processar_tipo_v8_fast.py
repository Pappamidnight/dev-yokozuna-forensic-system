#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
processar_tipo_v8_fast.py
Processamento Cirurgico Atómico V8.1 FAST (1 Tipo de Cada Vez).
Elimina gargalo de I/O (85s -> 1s) dispensando verificação repetida de existência física em disco.
Totalmente auditável, determinístico e reutilizável.
Uso: python processar_tipo_v8_fast.py <tipo>
"""

import os
import sys
import csv
import json
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

TIPOS = [
    "database", "video", "excel", "audio", "word", "pdf",
    "imagem", "json", "texto", "yaml", "csv", "markdown"
]

ENTRADA = Path(r"C:\ACERVO\logs\pipeline_v5\TODOS_NORMALIZADOS.csv")
DEST = Path(r"C:\ACERVO\logs\v8_fast")
SANDBOX = Path(r"C:\ACERVO\SANDBOX\v8")

DEST.mkdir(parents=True, exist_ok=True)
SANDBOX.mkdir(parents=True, exist_ok=True)

def humano(b):
    for u in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024:
            return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} PB"

def processar(tipo_alvo):
    tipo_alvo = tipo_alvo.lower().strip()
    if tipo_alvo not in TIPOS:
        print(f"[ERRO] Tipo inválido: '{tipo_alvo}'")
        print(f"Tipos suportados: {', '.join(TIPOS)}")
        sys.exit(1)

    t0 = time.time()
    print("=" * 78)
    print(f"  V8 FAST - PROCESSAMENTO ATÓMICO: [{tipo_alvo.upper()}]")
    print(f"  Origem:  {ENTRADA}")
    print(f"  Destino: {DEST}")
    print("=" * 78)
    print()

    # 1. Carregar apenas o tipo alvo
    print(f"[1/3] A carregar registos de '{tipo_alvo}'...")
    t1 = time.time()
    regs = []

    if not ENTRADA.exists():
        print(f"[ERRO] Ficheiro de entrada não encontrado: {ENTRADA}")
        sys.exit(1)

    with open(ENTRADA, "r", encoding="utf-8", errors="replace", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            if row.get("tipo", "").lower() != tipo_alvo:
                continue
            try:
                tam = int(row.get("tamanho", 0))
            except ValueError:
                continue
            if tam <= 0:
                continue

            try:
                rank_val = int(row.get("rank", 3))
            except ValueError:
                rank_val = 3

            try:
                prof_val = int(row.get("prof", 0))
            except ValueError:
                prof_val = 0

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
                "rank": rank_val,
                "prof": prof_val,
            })

    t_carga = time.time() - t1
    print(f"  Registos carregados: {len(regs):,} em {t_carga:.2f}s")
    print()

    # 2. Segregar originais vs duplicados (sem chamada I/O os.path.exists)
    print("[2/3] A segregar originais e duplicados por precedência...")
    t2 = time.time()
    grupos = defaultdict(list)
    for r in regs:
        chave = (r["stem"], r["tamanho"], r["ext"])
        grupos[chave].append(r)

    originais = []
    duplicados = []
    for chave, grupo in grupos.items():
        if len(grupo) == 1:
            originais.append(grupo[0])
            continue
        # Ordenação por soberania de custódia (menor rank vence, menor prof vence)
        grupo.sort(key=lambda x: (x["rank"], x["prof"], x["caminho"], x["nome"]))
        originais.append(grupo[0])
        for d in grupo[1:]:
            d_copia = dict(d)
            d_copia["grau"] = "DUPLICADO"
            d_copia["score"] = 85
            duplicados.append(d_copia)

    t_segrega = time.time() - t2
    print(f"  Grupos Únicos:    {len(grupos):>10,}")
    print(f"  Originais Eleitos:{len(originais):>10,}")
    print(f"  Duplicados:       {len(duplicados):>10,}")
    print(f"  Tempo Segregação: {t_segrega:.2f}s")
    print()

    # 3. Gravação de Artefactos e Manifestos
    print("[3/3] A gravar artefactos canónicos...")
    campos = ["origem", "tipo", "nome", "caminho", "tamanho", "stem", "ext", "mime", "categoria", "rank", "grau", "score"]

    orig_path = DEST / f"originais_{tipo_alvo}.csv"
    with open(orig_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for r in originais:
            w.writerow({k: r.get(k, "") for k in campos})
    print(f"  [OK] {orig_path.name}")

    dup_path = DEST / f"duplicados_{tipo_alvo}.csv"
    with open(dup_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for r in duplicados:
            w.writerow({k: r.get(k, "") for k in campos})
    print(f"  [OK] {dup_path.name}")

    # SANDBOX
    sbx_dir = SANDBOX / tipo_alvo
    sbx_dir.mkdir(parents=True, exist_ok=True)
    sbx_path = sbx_dir / f"duplicados_{tipo_alvo}.csv"
    with open(sbx_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for r in duplicados:
            w.writerow({k: r.get(k, "") for k in campos})
    print(f"  [OK] Sandbox: {sbx_path}")

    espaco = sum(r["tamanho"] for r in duplicados)
    man = {
        "tipo": tipo_alvo,
        "modo": "DRY-RUN",
        "data": datetime.now().isoformat(),
        "total_registos": len(regs),
        "grupos_totais": len(grupos),
        "originais": len(originais),
        "duplicados": len(duplicados),
        "espaco_recuperavel_bytes": espaco,
        "espaco_recuperavel_gb": round(espaco / (1024**3), 2),
        "tempo_total_segundos": round(time.time() - t0, 2),
        "ficheiros_alterados": 0,
        "ficheiros_movidos": 0,
        "ficheiros_apagados": 0
    }
    man_path = DEST / f"manifesto_{tipo_alvo}.json"
    with open(man_path, "w", encoding="utf-8") as f:
        json.dump(man, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Manifesto: {man_path.name}")

    duracao_total = time.time() - t0
    print()
    print("=" * 78)
    print(f"  RESUMO FINAL [{tipo_alvo.upper()}] - CONCLUÍDO")
    print("=" * 78)
    print(f"  Originais:          {len(originais):>10,}")
    print(f"  Duplicados:         {len(duplicados):>10,}")
    print(f"  Espaço Recuperável: {humano(espaco)}")
    print(f"  Tempo Total:        {duracao_total:.2f}s")
    print("=" * 78)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python processar_tipo_v8_fast.py <tipo>")
        print("Exemplo: python processar_tipo_v8_fast.py pdf")
        sys.exit(1)
    processar(sys.argv[1])
