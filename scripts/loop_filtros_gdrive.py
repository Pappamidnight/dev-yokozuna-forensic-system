# -*- coding: utf-8 -*-
"""
LOOP ITERATIVO DE FILTROS - GOOGLE DRIVE
Aplica filtros progressivamente ate 100% de certeza (Score 100).
"""
import os
import csv
import time
import json
import re
from collections import defaultdict
from datetime import datetime

FONTE = r"C:\ACERVO\logs\google_drive\google_drive_full.csv"
DEST  = r"C:\ACERVO\logs\google_drive\iteracoes"
os.makedirs(DEST, exist_ok=True)

RE_SUF = re.compile(r"(?:[\s_\-]+(?:copy|copia|final|v\d+|backup|old|novo|new|\d+))+\s*$", re.IGNORECASE)

def normalizar_stem(nome):
    stem = os.path.splitext(str(nome))[0]
    stem = RE_SUF.sub("", stem).strip()
    stem = re.sub(r"\s+", " ", stem).lower()
    return stem

def carregar_registos():
    regs = []
    with open(FONTE, "r", encoding="utf-8", errors="replace", newline="") as f:
        r = csv.reader(f)
        next(r, None)
        for row in r:
            if len(row) < 6:
                continue
            nome, caminho, tam_s, dm, attr, ext = row[:6]
            try:
                tam = int(tam_s)
            except ValueError:
                continue
            if tam <= 0 or not nome:
                continue
            regs.append({
                "nome": nome,
                "caminho": caminho,
                "tam": tam,
                "data": dm,
                "attr": attr,
                "ext": ext.lower(),
                "stem": normalizar_stem(nome),
            })
    return regs

def agrupar(regs, chave_fn):
    grupos = defaultdict(list)
    for r in regs:
        grupos[chave_fn(r)].append(r)
    return grupos

def calcular_pares(grupos):
    pares = []
    for chave, rows in grupos.items():
        if len(rows) < 2:
            continue
        rows.sort(key=lambda x: (x["caminho"], x["nome"]))
        orig = rows[0]
        for dup in rows[1:]:
            score = 0
            if orig["stem"] == dup["stem"]:
                score += 40
            if orig["tam"] == dup["tam"]:
                score += 30
            if orig["ext"] == dup["ext"]:
                score += 10
            if orig["data"] == dup["data"]:
                score += 15
            if orig["attr"] == dup["attr"]:
                score += 5
            score = min(score, 100)
            if score >= 100:
                grau = "IDENTIDADE_CRIPTO_PROVAVEL"
            elif score >= 95:
                grau = "COPIA_CONFIRMADA"
            elif score >= 85:
                grau = "VARIANTE_HOMOLOGA"
            elif score >= 70:
                grau = "SIMILARIDADE_FORTE"
            else:
                grau = "SIMILARIDADE_MODERADA"
            pares.append({
                "id_par": f"PAR_{len(pares)+1:07d}",
                "score": score,
                "grau": grau,
                "orig_nome": orig["nome"],
                "orig_caminho": orig["caminho"],
                "orig_tam": orig["tam"],
                "orig_data": orig["data"],
                "orig_attr": orig["attr"],
                "dup_nome": dup["nome"],
                "dup_caminho": dup["caminho"],
                "dup_tam": dup["tam"],
                "dup_data": dup["data"],
                "dup_attr": dup["attr"],
                "stem": orig["stem"],
                "ext": orig["ext"],
            })
    return pares

def main():
    t0 = time.time()
    print("=" * 78)
    print("  LOOP ITERATIVO DE FILTROS - GOOGLE DRIVE")
    print("=" * 78)
    print(f"  Fonte:   {FONTE}")
    print(f"  Destino: {DEST}")
    print()

    if not os.path.isfile(FONTE):
        print(f"  [ERRO] Fonte nao encontrada")
        return

    print("[0] A carregar registos...")
    regs = carregar_registos()
    print(f"  Total: {len(regs):,} registos")
    print()

    iteracoes = [
        {"nome": "1 - Stem + Tamanho",
         "chave": lambda r: (r["stem"], r["tam"])},
        {"nome": "2 - Stem + Tamanho + Extensao",
         "chave": lambda r: (r["stem"], r["tam"], r["ext"])},
        {"nome": "3 - Stem + Tamanho + Extensao + Data",
         "chave": lambda r: (r["stem"], r["tam"], r["ext"], r["data"])},
        {"nome": "4 - Stem + Tamanho + Extensao + Data + Atributos",
         "chave": lambda r: (r["stem"], r["tam"], r["ext"], r["data"], r["attr"])},
    ]

    hist = []

    for it in iteracoes:
        print("=" * 78)
        print(f"  ITERACAO: {it['nome']}")
        print("=" * 78)
        t_it = time.time()

        grupos = agrupar(regs, it["chave"])
        pares = calcular_pares(grupos)

        total_pares = len(pares)
        score_100 = sum(1 for p in pares if p["score"] == 100)
        score_95 = sum(1 for p in pares if 95 <= p["score"] < 100)
        score_85 = sum(1 for p in pares if 85 <= p["score"] < 95)
        score_70 = sum(1 for p in pares if 70 <= p["score"] < 85)
        score_baixo = sum(1 for p in pares if p["score"] < 70)
        pct_100 = (score_100 / total_pares * 100) if total_pares > 0 else 0

        print(f"  Grupos: {len(grupos):,}")
        print(f"  Pares:  {total_pares:,}")
        print()
        print(f"  Score 100 (CERTEZA):     {score_100:>10,}  ({pct_100:>6.2f}%)")
        print(f"  Score  95-99 (COPIA):    {score_95:>10,}")
        print(f"  Score  85-94 (VARIANTE): {score_85:>10,}")
        print(f"  Score  70-84 (SIMILAR):  {score_70:>10,}")
        print(f"  Score  <70   (BAIXO):    {score_baixo:>10,}")
        print()
        print(f"  Tempo: {time.time()-t_it:.2f}s")

        hist.append({
            "iteracao": it["nome"],
            "grupos": len(grupos),
            "pares": total_pares,
            "score_100": score_100,
            "score_95": score_95,
            "score_85": score_85,
            "score_70": score_70,
            "score_baixo": score_baixo,
            "pct_100": round(pct_100, 2),
            "tempo": round(time.time()-t_it, 2),
        })

        if total_pares > 0:
            out = os.path.join(DEST, f"iter_{it['nome'][:1]}_pares.csv")
            with open(out, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(pares[0].keys()))
                w.writeheader()
                w.writerows(pares)
            print(f"  [OK] {out}")

        if total_pares > 0 and score_100 == total_pares:
            print()
            print("  *** 100% DE CERTEZA ATINGIDO! PARANDO ***")
            break

        print()

    print()
    print("=" * 78)
    print("  HISTORICO")
    print("=" * 78)
    print(f"  {'Iteracao':<50} {'Pares':>10} {'100%':>10} {'%':>8}")
    print("-" * 78)
    for h in hist:
        print(f"  {h['iteracao'][:50]:<50} {h['pares']:>10,} {h['score_100']:>10,} {h['pct_100']:>7.2f}%")
    print("-" * 78)

    rel = {
        "data": datetime.now().isoformat(),
        "fonte": FONTE,
        "total_registos": len(regs),
        "historico": hist,
    }
    rel_path = os.path.join(DEST, "relatorio_iteracoes.json")
    with open(rel_path, "w", encoding="utf-8") as f:
        json.dump(rel, f, indent=2, ensure_ascii=False)
    print(f"\n  Relatorio: {rel_path}")
    print(f"  Tempo total: {time.time()-t0:.2f}s")
    print("=" * 78)

if __name__ == "__main__":
    main()
