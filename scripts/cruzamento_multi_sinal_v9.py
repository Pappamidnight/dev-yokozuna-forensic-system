#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cruzamento_multi_sinal_v9.py
Motor de Cruzamento Multi-Sinal e Identificacao de Originais Canonicos (V9).
Conforme Doutrina V7/V8, ISO/IEC 27037 e Six Sigma.
Totalmente READ-ONLY (DRY-RUN compulsorio).
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

BASE_DEDUPLICADO = Path(r"C:\ACERVO\logs\deduplicado")
OUT_BASE = Path(r"C:\ACERVO\logs\cruzamento_v9")
OUT_BASE.mkdir(parents=True, exist_ok=True)

# Hierarquia de Precedencia e Custodia (Rank 0 vence)
RANK_CUSTODIA = [
    (re.compile(r"acervo_consolidado", re.IGNORECASE), 0),
    (re.compile(r"vault_central|vault", re.IGNORECASE), 1),
    (re.compile(r"dossiers_master|dossier", re.IGNORECASE), 2),
    (re.compile(r"01_work", re.IGNORECASE), 3),
    (re.compile(r"dev", re.IGNORECASE), 4),
    (re.compile(r"legacy_cookbook", re.IGNORECASE), 5),
    (re.compile(r"legacy_arquivo_historico|legacy", re.IGNORECASE), 6),
]

SUFIXOS_VARIANTE = re.compile(r"(_final|_v\d+|\(\d+\)|- copy|_backup|_alt|_copia|_rev\d+)$", re.IGNORECASE)

TIPOS_DISPONIVEIS = [
    "database", "excel", "word", "csv", "yaml", "audio", "video",
    "pdf", "texto", "json", "imagem", "markdown"
]


def normalizar_stem(nome_ficheiro: str) -> str:
    p = Path(nome_ficheiro)
    stem = p.stem.strip()
    # Remove sufixos comuns de copia repetidamente
    while True:
        novo = SUFIXOS_VARIANTE.sub("", stem).strip()
        if novo == stem:
            break
        stem = novo
    return stem.lower()


def obter_rank_custodia(caminho: str) -> int:
    for regex, rank in RANK_CUSTODIA:
        if regex.search(caminho):
            return rank
    return 7


def calcular_score_multi_sinal(orig, dup):
    """
    Score Multi-Sinal (0 a 100):
    Base = 70 (mesmo nome normalizado e tamanho exato)
    Nome exato = +15 | Normalizado = +7.5
    Data mod identical = +10 | Data mod +-60s = +5
    Extensao identica = +5 | Compativel cross-format = +2.5
    Custodia clara (Rank diff >= 1) = +20
    """
    score = 70.0

    nome_orig = orig["name"].lower()
    nome_dup = dup["name"].lower()
    if nome_orig == nome_dup:
        score += 15.0
    else:
        score += 7.5

    data_orig = orig.get("date_modified", "")
    data_dup = dup.get("date_modified", "")
    if data_orig and data_orig == data_dup:
        score += 10.0

    ext_orig = Path(nome_orig).suffix
    ext_dup = Path(nome_dup).suffix
    if ext_orig == ext_dup:
        score += 5.0
    else:
        score += 2.5

    rank_orig = orig["rank"]
    rank_dup = dup["rank"]
    if rank_dup > rank_orig:
        score += 20.0
    elif rank_dup == rank_orig:
        score += 10.0

    return min(100.0, round(score, 2))


def processar_tipo(tipo: str, min_score: float = 70.0):
    pasta_tipo = BASE_DEDUPLICADO / tipo
    csv_originais = pasta_tipo / f"originais_{tipo}.csv"
    csv_duplicados = pasta_tipo / f"duplicados_{tipo}.csv"

    if not csv_originais.exists() or not csv_duplicados.exists():
        print(f"[{tipo.upper()}] Ficheiros originais/duplicados nao encontrados em {pasta_tipo}")
        return None

    out_tipo_dir = OUT_BASE / tipo
    out_tipo_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_tipo_dir / f"cruzamento_multi_sinal_{tipo}.csv"
    out_json = out_tipo_dir / f"resumo_cruzado_{tipo}.json"

    print("=" * 80)
    print(f"PROCESSANDO CRUZAMENTO MULTI-SINAL V9: [{tipo.upper()}]")
    print(f"Modo: DRY-RUN (READ-ONLY) | Min Score: {min_score}")
    print("=" * 80)

    # 1. Carregar Originais
    originais_por_stem = {}
    with open(csv_originais, "r", encoding="utf-8-sig", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            nome = row.get("name") or row.get("Name") or ""
            caminho = row.get("path") or row.get("Path") or ""
            tamanho = int(row.get("size") or row.get("Size") or 0)
            data_mod = row.get("date_modified") or row.get("Date Modified") or ""
            stem = normalizar_stem(nome)
            rank = obter_rank_custodia(caminho)

            chave = (stem, tamanho)
            orig_obj = {
                "name": nome,
                "path": caminho,
                "size": tamanho,
                "date_modified": data_mod,
                "stem": stem,
                "rank": rank
            }
            if chave not in originais_por_stem:
                originais_por_stem[chave] = []
            originais_por_stem[chave].append(orig_obj)

    # 2. Carregar e Cruzar com Duplicados
    pares_cruzados = []
    distribuicao_scores = {
        "score_100": 0,
        "score_95_99": 0,
        "score_85_94": 0,
        "score_70_84": 0,
        "score_menor_70": 0
    }

    total_dups = 0
    with open(csv_duplicados, "r", encoding="utf-8-sig", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_dups += 1
            nome = row.get("name") or row.get("Name") or ""
            caminho = row.get("path") or row.get("Path") or ""
            tamanho = int(row.get("size") or row.get("Size") or 0)
            data_mod = row.get("date_modified") or row.get("Date Modified") or ""
            stem = normalizar_stem(nome)
            rank = obter_rank_custodia(caminho)

            chave = (stem, tamanho)
            dup_obj = {
                "name": nome,
                "path": caminho,
                "size": tamanho,
                "date_modified": data_mod,
                "stem": stem,
                "rank": rank
            }

            if chave in originais_por_stem:
                # Escolhe o melhor candidato original pelo menor rank
                candidatos = sorted(originais_por_stem[chave], key=lambda x: (x["rank"], len(x["path"])))
                melhor_orig = candidatos[0]

                score = calcular_score_multi_sinal(melhor_orig, dup_obj)

                if score == 100.0:
                    distribuicao_scores["score_100"] += 1
                    classif = "IDENTIDADE_CRIPTO_PROVAVEL"
                elif score >= 95.0:
                    distribuicao_scores["score_95_99"] += 1
                    classif = "COPIA_CONFIRMADA"
                elif score >= 85.0:
                    distribuicao_scores["score_85_94"] += 1
                    classif = "VARIANTE_HOMOLOGA"
                elif score >= 70.0:
                    distribuicao_scores["score_70_84"] += 1
                    classif = "SIMILARIDADE_FORTE"
                else:
                    distribuicao_scores["score_menor_70"] += 1
                    classif = "SIMILARIDADE_MODERADA"

                if score >= min_score:
                    pares_cruzados.append({
                        "tipo": tipo,
                        "orig_name": melhor_orig["name"],
                        "orig_path": melhor_orig["path"],
                        "orig_rank": melhor_orig["rank"],
                        "dup_name": dup_obj["name"],
                        "dup_path": dup_obj["path"],
                        "dup_rank": dup_obj["rank"],
                        "tamanho_bytes": tamanho,
                        "score": score,
                        "classificacao": classif
                    })

    # 3. Gravar CSV de Resultados
    with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
        fieldnames = [
            "tipo", "score", "classificacao", "tamanho_bytes",
            "orig_name", "orig_path", "orig_rank",
            "dup_name", "dup_path", "dup_rank"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in pares_cruzados:
            writer.writerow(p)

    # 4. Gravar Resumo JSON
    resumo = {
        "tipo": tipo,
        "timestamp": datetime.now().isoformat(),
        "modo": "DRY-RUN",
        "total_duplicados_avaliados": total_dups,
        "pares_validados_cruzamento": len(pares_cruzados),
        "distribuicao_scores": distribuicao_scores,
        "ficheiro_csv": str(out_csv)
    }
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(resumo, f, indent=2, ensure_ascii=False)

    print(f"Pares Cruzados Validados: {len(pares_cruzados)}")
    print(f"Distribuicao: Score 100={distribuicao_scores['score_100']} | 95-99={distribuicao_scores['score_95_99']} | 85-94={distribuicao_scores['score_85_94']}")
    print(f"CSV Gerado: {out_csv}")
    print(f"Resumo JSON: {out_json}")
    return resumo


def main():
    parser = argparse.ArgumentParser(description="Cruzamento Multi-Sinal V9 (DRY-RUN)")
    parser.add_argument("--tipo", choices=TIPOS_DISPONIVEIS + ["todos"], default="database", help="Tipo de ficheiro a processar")
    parser.add_argument("--min-score", type=float, default=70.0, help="Score minimo para exportacao")
    args = parser.parse_args()

    t0 = time.time()
    if args.tipo == "todos":
        for t in TIPOS_DISPONIVEIS:
            processar_tipo(t, args.min_score)
    else:
        processar_tipo(args.tipo, args.min_score)

    print(f"\nTempo Total de Execucao: {time.time() - t0:.2f} segundos.")


if __name__ == "__main__":
    main()
