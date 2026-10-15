#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cruzamento_v9_polars_turbo.py
Implementação Polars Turbo para Cruzamento Multi-Sinal V9.
Executa join vetorial massivo entre Originais e Duplicados com hashing de stem e tamanho.
Totalmente em DRY-RUN.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Tentativa de importar polars
try:
    import polars as pl
except ImportError:
    print("[ERRO] A biblioteca 'polars' não está instalada no ambiente Python atual.")
    print("Para instalar: pip install polars")
    sys.exit(1)

BASE = Path(r"C:\ACERVO\logs\deduplicado")
OUT = Path(r"C:\ACERVO\logs\cruzamento_v9")
OUT.mkdir(parents=True, exist_ok=True)

TIPOS = [
    "database", "excel", "word", "csv", "yaml", "audio", "video",
    "pdf", "texto", "json", "imagem", "markdown"
]

RANK_CUSTODIA = [
    (r"(?i)acervo_consolidado", 0),
    (r"(?i)vault_central|vault", 1),
    (r"(?i)dossiers_master|dossier", 2),
    (r"(?i)01_work", 3),
    (r"(?i)dev", 4),
    (r"(?i)legacy_cookbook", 5),
    (r"(?i)legacy_arquivo_historico|legacy", 6),
]

def formatar_tempo(segundos):
    m, s = divmod(int(segundos), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def processar_turbo(min_score=70.0):
    t0 = time.time()
    print("=" * 80)
    print("  ACERVO V9 - CRUZAMENTO POLARS TURBO MULTI-SINAL")
    print(f"  Modo: DRY-RUN | Score Mínimo: {min_score}")
    print(f"  Diretório Origem: {BASE}")
    print(f"  Diretório Destino: {OUT}")
    print("=" * 80)

    lista_orig = []
    lista_dup = []

    print("[1/4] A carregar ficheiros com Polars...")
    for t in TIPOS:
        pasta_t = BASE / t
        f_orig = pasta_t / f"originais_{t}.csv"
        f_dup = pasta_t / f"duplicados_{t}.csv"

        if f_orig.exists():
            try:
                df_o = pl.read_csv(f_orig, infer_schema_length=1000, ignore_errors=True)
                # Normalizar nomes de colunas
                map_cols = {}
                for c in df_o.columns:
                    c_low = c.lower()
                    if c_low in ["nome", "name"]: map_cols[c] = "nome"
                    elif c_low in ["caminho", "path"]: map_cols[c] = "caminho"
                    elif c_low in ["tamanho", "size"]: map_cols[c] = "tamanho"
                    elif c_low in ["datamod", "date modified", "date_modified"]: map_cols[c] = "datamod"
                
                df_o = df_o.rename(map_cols)
                if all(k in df_o.columns for k in ["nome", "caminho", "tamanho"]):
                    df_o = df_o.select(["nome", "caminho", "tamanho", "datamod"]).with_columns([
                        pl.col("tamanho").cast(pl.Int64, strict=False).fill_null(0),
                        pl.lit(t).alias("tipo")
                    ])
                    lista_orig.append(df_o)
            except Exception as e:
                print(f"  [AVISO] Falha ao ler {f_orig.name}: {e}")

        if f_dup.exists():
            try:
                df_d = pl.read_csv(f_dup, infer_schema_length=1000, ignore_errors=True)
                map_cols = {}
                for c in df_d.columns:
                    c_low = c.lower()
                    if c_low in ["nome", "name"]: map_cols[c] = "nome"
                    elif c_low in ["caminho", "path"]: map_cols[c] = "caminho"
                    elif c_low in ["tamanho", "size"]: map_cols[c] = "tamanho"
                    elif c_low in ["datamod", "date modified", "date_modified"]: map_cols[c] = "datamod"
                
                df_d = df_d.rename(map_cols)
                if all(k in df_d.columns for k in ["nome", "caminho", "tamanho"]):
                    df_d = df_d.select(["nome", "caminho", "tamanho", "datamod"]).with_columns([
                        pl.col("tamanho").cast(pl.Int64, strict=False).fill_null(0),
                        pl.lit(t).alias("tipo")
                    ])
                    lista_dup.append(df_d)
            except Exception as e:
                print(f"  [AVISO] Falha ao ler {f_dup.name}: {e}")

    if not lista_orig or not lista_dup:
        print("[ERRO] Nenhum dado de originais ou duplicados pôde ser carregado.")
        sys.exit(1)

    df_orig = pl.concat(lista_orig)
    df_dup = pl.concat(lista_dup)
    print(f"      Originais: {df_orig.height:,} registos")
    print(f"      Duplicados: {df_dup.height:,} registos")

    print("[2/4] A normalizar stems e atribuir ranks de custódia...")
    # Função para extrair stem normalizado
    regex_limpeza = r"(?i)(_final|_v\d+|\(\d+\)|- copy|_backup|_alt|_copia|_rev\d+|\.[^.]+)$"

    df_orig = df_orig.with_columns([
        pl.col("nome").str.to_lowercase().str.replace_all(regex_limpeza, "").str.strip_chars().alias("stem"),
        pl.col("nome").str.extract(r"\.([^.]+)$", 1).str.to_lowercase().fill_null("").alias("ext"),
    ])

    df_dup = df_dup.with_columns([
        pl.col("nome").str.to_lowercase().str.replace_all(regex_limpeza, "").str.strip_chars().alias("stem"),
        pl.col("nome").str.extract(r"\.([^.]+)$", 1).str.to_lowercase().fill_null("").alias("ext"),
    ])

    # Ranks
    expr_rank_o = pl.lit(7)
    expr_rank_d = pl.lit(7)
    for rgx, rnk in RANK_CUSTODIA:
        expr_rank_o = pl.when(pl.col("caminho").str.contains(rgx)).then(rnk).otherwise(expr_rank_o)
        expr_rank_d = pl.when(pl.col("caminho").str.contains(rgx)).then(rnk).otherwise(expr_rank_d)

    df_orig = df_orig.with_columns(expr_rank_o.alias("rank_orig"))
    df_dup = df_dup.with_columns(expr_rank_d.alias("rank_dup"))

    print("[3/4] A executar Join Relacional e Cálculo de Score...")
    t_join = time.time()
    
    # Join em stem e tamanho
    merge = df_dup.join(
        df_orig.select(["stem", "tamanho", "nome", "caminho", "rank_orig", "tipo", "datamod", "ext"]),
        on=["stem", "tamanho"],
        how="inner",
        suffix="_orig"
    ).rename({
        "nome": "nome_dup",
        "caminho": "caminho_dup",
        "tipo": "tipo_dup",
        "datamod": "datamod_dup",
        "ext": "ext_dup"
    })

    # Scoring vetorial Polars
    merge = merge.with_columns([
        (
            pl.lit(70.0)
            + pl.when(pl.col("nome_dup").str.to_lowercase() == pl.col("nome").str.to_lowercase()).then(15.0).otherwise(7.5)
            + pl.when((pl.col("datamod_dup") == pl.col("datamod")) & (pl.col("datamod_dup") != "")).then(10.0).otherwise(0.0)
            + pl.when(pl.col("ext_dup") == pl.col("ext")).then(5.0).otherwise(2.5)
            + pl.when(pl.col("rank_dup") > pl.col("rank_orig")).then(20.0)
                .when(pl.col("rank_dup") == pl.col("rank_orig")).then(10.0)
                .otherwise(0.0)
        ).clip(0.0, 100.0).alias("score")
    ])

    merge = merge.with_columns(
        pl.when(pl.col("score") >= 100.0).then(pl.lit("IDENTIDADE_CRIPTO_PROVAVEL"))
          .when(pl.col("score") >= 95.0).then(pl.lit("COPIA_CONFIRMADA"))
          .when(pl.col("score") >= 85.0).then(pl.lit("VARIANTE_HOMOLOGA"))
          .when(pl.col("score") >= 70.0).then(pl.lit("SIMILARIDADE_FORTE"))
          .otherwise(pl.lit("SIMILARIDADE_MODERADA")).alias("grau_certeza")
    )

    out = merge.filter(pl.col("score") >= min_score)
    print(f"      Pares gerados: {out.height:,} ({time.time() - t_join:.2f}s)")

    print("[4/4] A gravar resultados...")
    t_w = time.time()
    csv_out = OUT / "cruzamento_multi_sinal_v9.csv"
    
    out = out.with_columns([
        pl.concat_str([pl.lit("PAR_"), pl.int_range(1, pl.len() + 1).cast(pl.Utf8).str.zfill(7)]).alias("id_par")
    ]).select([
        "id_par", "grau_certeza", "score",
        "tipo", "nome", "caminho", "rank_orig",
        "tipo_dup", "nome_dup", "caminho_dup", "rank_dup",
        "tamanho", "stem"
    ]).rename({
        "tipo": "orig_tipo",
        "nome": "orig_nome",
        "caminho": "orig_caminho",
        "tamanho": "tamanho_bytes",
        "stem": "stem_normalizado"
    })

    out.write_csv(csv_out)
    print(f"      CSV gravado: {csv_out} ({time.time() - t_w:.2f}s)")

    # Resumo Executivo
    dist = out.group_by("grau_certeza").len().sort("len", descending=True).to_dicts()
    espaco = out.group_by("grau_certeza").agg(pl.col("tamanho_bytes").sum().alias("bytes")).to_dicts()
    emap = {e["grau_certeza"]: round(e["bytes"] / (1024**3), 2) for e in espaco}

    rel = {
        "versao": "V9_POLARS_TURBO",
        "modo": "DRY-RUN",
        "timestamp": datetime.now().isoformat(),
        "duracao_segundos": round(time.time() - t0, 2),
        "duracao_formatada": formatar_tempo(time.time() - t0),
        "total_originais_analisados": int(df_orig.height),
        "total_duplicados_analisados": int(df_dup.height),
        "total_pares_identificados": int(out.height),
        "distribuicao_grau": {d["grau_certeza"]: int(d["len"]) for d in dist},
        "espaco_recuperavel_gb": emap,
        "ficheiros_alterados": 0,
        "ficheiros_movidos": 0,
        "ficheiros_apagados": 0
    }

    rel_out = OUT / "relatorio_executivo_v9.json"
    with open(rel_out, "w", encoding="utf-8") as f:
        json.dump(rel, f, indent=2, ensure_ascii=False)

    print("-" * 80)
    print("  RESULTADO EXECUTIVO CONSOLIDADO V9 (POLARS TURBO):")
    print("-" * 80)
    for d in dist:
        g = d["grau_certeza"]
        n = d["len"]
        gb = emap.get(g, 0)
        pct = (n / out.height) * 100 if out.height > 0 else 0
        print(f"  {g:<30} {n:>10,} pares ({pct:5.1f}%) | {gb:>8.2f} GB")
    print("-" * 80)
    print(f"  Tempo Total:      {rel['duracao_formatada']}")
    print(f"  Relatório JSON:   {rel_out}")
    print("=" * 80)

if __name__ == "__main__":
    score_param = 70.0
    if len(sys.argv) > 1:
        try: score_param = float(sys.argv[1])
        except ValueError: pass
    processar_turbo(score_param)
