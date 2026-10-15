# -*- coding: utf-8 -*-
"""
Segrega originais e duplicados do Google Drive.
Aplica hierarquia de custodia + filtros multi-sinal.
"""
import os
import time
import json
import re
import polars as pl
from datetime import datetime

FONTE = r"C:\ACERVO\logs\google_drive\por_tipo"
DEST  = r"C:\ACERVO\logs\google_drive\segregado"
os.makedirs(DEST, exist_ok=True)

TIPOS = ["database","video","excel","audio","word","pdf",
         "imagem","json","texto","yaml","csv","markdown"]

RE_SUF = re.compile(
    r"(?:[\s_\-]+(?:copy|copia|final|v\d+|backup|old|novo|new|\d+))+\s*$",
    re.IGNORECASE
)

# Hierarquia de custodia (Rank 0 vence)
RANK_HIERARQUIA = {
    "meu_disco": 0,        # G:\O meu disco (principal)
    "outros_computadores": 1,  # G:\Outros computadores (backup)
}

def calcular_rank(caminho):
    """Determina o rank do caminho."""
    c = caminho.lower()
    if "o meu disco" in c:
        return 0
    if "outros computadores" in c:
        return 1
    return 2

def normalizar_stem(nome):
    stem = os.path.splitext(str(nome))[0]
    stem = RE_SUF.sub("", stem).strip()
    stem = re.sub(r"\s+", " ", stem).lower()
    return stem

def carregar_tipo(tipo):
    p = os.path.join(FONTE, f"{tipo}.csv")
    if not os.path.isfile(p):
        return None
    try:
        df = pl.read_csv(p, infer_schema_length=0, ignore_errors=True,
                         truncate_ragged_lines=True, low_memory=False)
    except Exception as e:
        print(f"  [ERRO] {tipo}: {e}")
        return None

    # Colunas: Nome, Caminho, Tamanho, DataMod, Atributos, Extensao
    cols = {c.lower(): c for c in df.columns}
    cn = cols.get("nome")
    cc = cols.get("caminho")
    ct = cols.get("tamanho")
    cd = cols.get("datamod") or cols.get("data_mod")
    ca = cols.get("atributos")
    ce = cols.get("extensao")

    if not (cn and cc):
        return None

    df = df.select([
        pl.col(cn).cast(pl.Utf8).alias("nome"),
        pl.col(cc).cast(pl.Utf8).alias("caminho"),
        pl.col(ct).cast(pl.Utf8, strict=False).str.replace_all(r"[^0-9]", "")
          .cast(pl.Int64, strict=False).fill_null(0).alias("tamanho"),
        (pl.col(cd).cast(pl.Utf8) if cd else pl.lit("")).alias("data_mod"),
        (pl.col(ca).cast(pl.Utf8) if ca else pl.lit("")).alias("atributos"),
        (pl.col(ce).cast(pl.Utf8) if ce else pl.lit("")).alias("extensao"),
    ])

    df = df.filter(pl.col("tamanho") > 0)
    df = df.filter(pl.col("nome").is_not_null() & (pl.col("nome") != ""))

    df = df.with_columns([
        pl.lit(tipo).alias("tipo"),
        pl.col("caminho").map_elements(calcular_rank, return_dtype=pl.Int8).alias("rank"),
    ])

    # Normalizar stem
    def norm_nome(n):
        return normalizar_stem(n)
    df = df.with_columns([
        pl.col("nome").map_elements(norm_nome, return_dtype=pl.Utf8).alias("stem"),
    ])

    return df

def main():
    t0 = time.time()
    print("=" * 78)
    print("  SEGREGAR ORIGINAIS vs DUPLICADOS - GOOGLE DRIVE")
    print("=" * 78)
    print()

    # Carregar todos os tipos
    print("[1/3] A carregar tipos...")
    frames = []
    for tipo in TIPOS:
        df = carregar_tipo(tipo)
        if df is not None and df.height > 0:
            frames.append(df)
            print(f"  [{tipo:>10}] {df.height:>10,} registos")
        else:
            print(f"  [{tipo:>10}] vazio ou erro")

    if not frames:
        print("\n  [ERRO] Nenhum registo carregado!")
        return

    df = pl.concat(frames, how="diagonal_relaxed")
    print(f"\n  Total: {df.height:,} registos")
    print()

    # ============================================================
    # ITERACAO 1: Stem + Tamanho
    # ============================================================
    print("=" * 78)
    print("  ITERACAO 1: Stem + Tamanho")
    print("=" * 78)
    t1 = time.time()

    df_sorted = df.sort(["stem", "tamanho", "rank", "caminho", "nome"])
    df_pos = df_sorted.with_columns(
        pl.col("stem").cum_count().over(["stem", "tamanho"]).alias("pos")
    )

    orig1 = df_pos.filter(pl.col("pos") == 0)
    dup1 = df_pos.filter(pl.col("pos") > 0)

    print(f"  Grupos:        {df_pos.select(pl.col('stem').n_unique()).item():,}")
    print(f"  Originais:     {orig1.height:,}")
    print(f"  Duplicados:    {dup1.height:,}")
    print(f"  Tempo:         {time.time()-t1:.2f}s")
    print()

    # ============================================================
    # ITERACAO 2: Stem + Tamanho + Extensao
    # ============================================================
    print("=" * 78)
    print("  ITERACAO 2: Stem + Tamanho + Extensao")
    print("=" * 78)
    t2 = time.time()

    df_sorted = df.sort(["stem", "tamanho", "extensao", "rank", "caminho", "nome"])
    df_pos = df_sorted.with_columns(
        pl.col("stem").cum_count().over(["stem", "tamanho", "extensao"]).alias("pos")
    )

    orig2 = df_pos.filter(pl.col("pos") == 0)
    dup2 = df_pos.filter(pl.col("pos") > 0)

    print(f"  Originais:     {orig2.height:,}")
    print(f"  Duplicados:    {dup2.height:,}")
    print(f"  Tempo:         {time.time()-t2:.2f}s")
    print()

    # ============================================================
    # ITERACAO 3: Stem + Tamanho + Extensao + Data
    # ============================================================
    print("=" * 78)
    print("  ITERACAO 3: Stem + Tamanho + Extensao + Data")
    print("=" * 78)
    t3 = time.time()

    df_sorted = df.sort(["stem", "tamanho", "extensao", "data_mod", "rank", "caminho", "nome"])
    df_pos = df_sorted.with_columns(
        pl.col("stem").cum_count().over(["stem", "tamanho", "extensao", "data_mod"]).alias("pos")
    )

    orig3 = df_pos.filter(pl.col("pos") == 0)
    dup3 = df_pos.filter(pl.col("pos") > 0)

    print(f"  Originais:     {orig3.height:,}")
    print(f"  Duplicados:    {dup3.height:,}")
    print(f"  Tempo:         {time.time()-t3:.2f}s")
    print()

    # ============================================================
    # GRAVAR RESULTADOS
    # ============================================================
    print("[2/3] A gravar CSVs segregados...")

    # Originais finais (iteracao 3 = mais especifica)
    orig_path = os.path.join(DEST, "ORIGINAIS_GDRIVE.csv")
    orig3.write_csv(orig_path)
    print(f"  [OK] {orig_path} ({orig3.height:,})")

    # Duplicados finais
    dup_path = os.path.join(DEST, "DUPLICADOS_GDRIVE.csv")
    dup3.write_csv(dup_path)
    print(f"  [OK] {dup_path} ({dup3.height:,})")

    # Por tipo
    print()
    print("[3/3] A segregar por tipo...")
    for tipo in TIPOS:
        orig_t = orig3.filter(pl.col("tipo") == tipo)
        dup_t = dup3.filter(pl.col("tipo") == tipo)
        if orig_t.height > 0:
            p_orig = os.path.join(DEST, f"originais_{tipo}.csv")
            orig_t.write_csv(p_orig)
        if dup_t.height > 0:
            p_dup = os.path.join(DEST, f"duplicados_{tipo}.csv")
            dup_t.write_csv(p_dup)
        if orig_t.height > 0 or dup_t.height > 0:
            print(f"  [{tipo:>10}] orig: {orig_t.height:>8,}  dup: {dup_t.height:>8,}")

    # ============================================================
    # RELATORIO
    # ============================================================
    print()
    print("=" * 78)
    print("  RELATORIO FINAL")
    print("=" * 78)

    espaco_recuperavel = dup3.select(pl.col("tamanho").sum()).item()
    gb = espaco_recuperavel / 1024 / 1024 / 1024

    print(f"  Total registos:      {df.height:,}")
    print(f"  Originais finais:    {orig3.height:,}")
    print(f"  Duplicados finais:   {dup3.height:,}")
    print(f"  Espaco recuperavel:  {gb:.2f} GB")
    print()
    print("  Distribuicao por tipo (originais / duplicados):")
    print("-" * 78)
    for tipo in TIPOS:
        o = orig3.filter(pl.col("tipo") == tipo).height
        d = dup3.filter(pl.col("tipo") == tipo).height
        if o > 0 or d > 0:
            print(f"  {tipo:<12} orig: {o:>8,}   dup: {d:>8,}")

    print()
    print(f"  Tempo total: {time.time()-t0:.2f}s")
    print("=" * 78)

    # Manifesto
    rel = {
        "data": datetime.now().isoformat(),
        "fonte": FONTE,
        "total_registos": df.height,
        "iteracoes": {
            "1_stem_tam": {"orig": orig1.height, "dup": dup1.height},
            "2_stem_tam_ext": {"orig": orig2.height, "dup": dup2.height},
            "3_stem_tam_ext_data": {"orig": orig3.height, "dup": dup3.height},
        },
        "espaco_recuperavel_bytes": int(espaco_recuperavel),
        "espaco_recuperavel_gb": round(gb, 2),
        "ficheiros_alterados": 0,
    }
    rel_path = os.path.join(DEST, "manifesto_segregacao.json")
    with open(rel_path, "w", encoding="utf-8") as f:
        json.dump(rel, f, indent=2, ensure_ascii=False)
    print(f"  Manifesto: {rel_path}")

if __name__ == "__main__":
    main()
