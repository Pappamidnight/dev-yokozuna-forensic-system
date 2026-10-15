# -*- coding: utf-8 -*-
"""
Aplica o filtro F06 (stem + tamanho + rank) e gera:
- ORIGINAIS_FINAIS.csv
- DUPLICADOS_FINAIS.csv
- Relatorio por categoria
"""
import os
import csv
import json
import time
from collections import defaultdict
from datetime import datetime

ENTRADA = r"C:\ACERVO\logs\pipeline_v5\TODOS_NORMALIZADOS.csv"
DEST = r"C:\ACERVO\logs\final_f06"
os.makedirs(DEST, exist_ok=True)

def humano(b):
    for u in ["B","KB","MB","GB","TB"]:
        if b < 1024:
            return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} PB"

def main():
    t0 = time.time()
    print("=" * 78)
    print("  APLICAR FILTRO F06 (stem + tamanho + rank)")
    print("=" * 78)
    print()

    # Ler todos os registos normalizados
    print("[1/3] A carregar registos normalizados...")
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
    print(f"  Total: {len(regs):,}")
    print()

    # Aplicar F06: (stem, tamanho, rank)
    print("[2/3] A aplicar F06...")
    grupos = defaultdict(list)
    for r in regs:
        chave = (r["stem"], r["tamanho"])
        grupos[chave].append(r)

    originais = []
    duplicados = []
    for chave, grupo in grupos.items():
        grupo.sort(key=lambda x: (x["rank"], x["prof"], x["caminho"], x["nome"]))
        originais.append(grupo[0])
        for d in grupo[1:]:
            duplicados.append(d)

    print(f"  Grupos:     {len(grupos):,}")
    print(f"  Originais:  {len(originais):,}")
    print(f"  Duplicados: {len(duplicados):,}")
    print()

    # Gravar
    print("[3/3] A gravar...")
    campos = ["origem","tipo","nome","caminho","tamanho","stem","ext","mime","categoria","rank"]

    orig_path = os.path.join(DEST, "ORIGINAIS_FINAIS.csv")
    with open(orig_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for r in originais:
            w.writerow({k: r.get(k, "") for k in campos})
    print(f"  [OK] {orig_path} ({len(originais):,})")

    dup_path = os.path.join(DEST, "DUPLICADOS_FINAIS.csv")
    with open(dup_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for r in duplicados:
            w.writerow({k: r.get(k, "") for k in campos})
    print(f"  [OK] {dup_path} ({len(duplicados):,})")

    # Por categoria
    print()
    print("  DISTRIBUICAO POR CATEGORIA (originais vs duplicados):")
    print("-" * 78)
    print(f"  {'Categoria':<15} {'Orig':>10} {'Dup':>10} {'%dup':>8} {'GB dup':>12}")
    print("-" * 78)

    espaco_total = 0
    for cat in sorted(set(r["categoria"] for r in regs)):
        o = [r for r in originais if r["categoria"] == cat]
        d = [r for r in duplicados if r["categoria"] == cat]
        if not (o or d):
            continue
        tam_d = sum(r["tamanho"] for r in d)
        espaco_total += tam_d
        pct = len(d) / (len(o) + len(d)) * 100 if (len(o) + len(d)) else 0
        print(f"  {cat:<15} {len(o):>10,} {len(d):>10,} {pct:>7.1f}% {humano(tam_d):>12}")
    print("-" * 78)

    # Relatorio
    rel = {
        "data": datetime.now().isoformat(),
        "filtro": "F06_stem_tam_rank",
        "total": len(regs),
        "originais": len(originais),
        "duplicados": len(duplicados),
        "espaco_recuperavel_bytes": espaco_total,
        "espaco_recuperavel_gb": round(espaco_total / 1024 / 1024 / 1024, 2),
        "ficheiros_alterados": 0,
    }
    rel_path = os.path.join(DEST, "relatorio_f06.json")
    with open(rel_path, "w", encoding="utf-8") as f:
        json.dump(rel, f, indent=2, ensure_ascii=False)
    print()
    print(f"  Espaco recuperavel: {humano(espaco_total)}")
    print(f"  Relatorio: {rel_path}")
    print(f"  Tempo: {time.time()-t0:.2f}s")
    print("=" * 78)

if __name__ == "__main__":
    main()
