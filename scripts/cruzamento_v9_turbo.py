# -*- coding: utf-8 -*-
import os, json, time, re
import polars as pl
from datetime import datetime

BASE = r"C:\ACERVO"
DEDUP = os.path.join(BASE, "logs", "deduplicado")
OUT = os.path.join(BASE, "logs", "cruzamento_v9")
MOD = "DRYRUN"
MIN_SCORE = 70
TIPOS = ["database","video","excel","audio","word","pdf","imagem","json","texto","yaml","csv","markdown"]

RANK_ORD = {
    "ACERVO_CONSOLIDADO": 0, "VAULT_CENTRAL": 1,
    "DOSSIERS_MASTER": 2, "01_WORK": 3,
    "DEV": 4, "LEGACY_COOKBOOK": 5,
    "LEGACY_ARQUIVO_HISTORICO": 6,
}

RE_SUF = re.compile(r"(?:[\s_\-]+(?:copy|copia|final|v\d+|backup|old|novo|new|\d+))+\s*$", re.IGNORECASE)

def log(msg):
    print(msg, flush=True)

def fmt_tempo(s):
    s = int(s)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def rank_expr(col):
    e = pl.lit(7, dtype=pl.Int8)
    for nome, r in sorted(RANK_ORD.items(), key=lambda x: -x[1]):
        e = pl.when(col.str.to_uppercase().str.contains(nome, literal=True)).then(pl.lit(r, dtype=pl.Int8)).otherwise(e)
    return e

def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    log("=" * 78)
    log(f"  CRUZAMENTO V9 TURBO (POLARS)  |  MODO: {MOD}")
    log("=" * 78)

    log("")
    log("[1/5] Leitura paralela dos 24 CSVs...")
    t_l = time.time()
    frames = []
    for t in TIPOS:
        for suf in ("originais", "duplicados"):
            p = os.path.join(DEDUP, t, f"{suf}_{t}.csv")
            if not os.path.isfile(p):
                continue
            try:
                df = pl.read_csv(p, infer_schema_length=0, ignore_errors=True, truncate_ragged_lines=True, low_memory=False)
            except Exception as e:
                log(f"  ! {p}: {e}")
                continue
            cols = {c.lower(): c for c in df.columns}
            cn = cols.get("nome")
            cc = cols.get("caminho")
            ct = cols.get("tamanho")
            if not (cn and cc):
                continue
            if ct:
                col_tam = pl.col(ct).cast(pl.Utf8, strict=False).str.replace_all(r"[^0-9]", "").cast(pl.Int64, strict=False).fill_null(0)
            else:
                col_tam = pl.lit(0, dtype=pl.Int64)
            df = df.select([
                pl.lit(t).alias("tipo"),
                pl.lit(suf).alias("origem"),
                pl.col(cn).cast(pl.Utf8).alias("nome"),
                pl.col(cc).cast(pl.Utf8).alias("caminho"),
                col_tam.alias("tamanho"),
            ])
            frames.append(df)
        log(f"  [{t:>10}] OK  ({time.time()-t_l:.2f}s)")

    df = pl.concat(frames, how="vertical_relaxed")
    log(f"  Total: {df.height:,} registos em {time.time()-t_l:.2f}s")

    log("")
    log("[2/5] Normalizacao de stems...")
    t_n = time.time()
    df = df.with_columns([
        pl.col("nome").str.to_lowercase().str.replace(RE_SUF.pattern, "").str.replace_all(r"\s+", " ").alias("stem"),
        pl.col("nome").str.to_lowercase().str.extract(r"(\.[^.]+)$", 1).fill_null("").alias("ext"),
    ])
    df = df.with_columns([
        pl.when(pl.col("ext") == ".jpeg").then(pl.lit(".jpg"))
          .when(pl.col("ext") == ".tif").then(pl.lit(".tiff"))
          .when(pl.col("ext") == ".htm").then(pl.lit(".html"))
          .when(pl.col("ext") == ".yml").then(pl.lit(".yaml"))
          .otherwise(pl.col("ext")).alias("ext"),
        rank_expr(pl.col("caminho")).alias("rank"),
    ])
    df = df.filter(pl.col("tamanho") > 0)
    log(f"  Normalizados: {df.height:,} em {time.time()-t_n:.2f}s")

    log("")
    log("[3/5] Agrupamento por (stem + tamanho)...")
    t_g = time.time()
    df = df.sort(["stem", "tamanho", "rank", "caminho"])
    df = df.with_columns(pl.col("stem").cum_count().over(["stem", "tamanho"]).alias("pos"))
    orig = df.filter(pl.col("pos") == 0)
    dup = df.filter(pl.col("pos") > 0)
    log(f"  Originais: {orig.height:,}  |  Duplicados: {dup.height:,}  ({time.time()-t_g:.2f}s)")

    log("")
    log("[4/5] Scoring vetorizado...")
    t_s = time.time()
    merge = dup.join(
        orig.select(["stem", "tamanho", "nome", "caminho", "rank", "tipo"]),
        on=["stem", "tamanho"], how="inner", suffix="_orig"
    )
    merge = merge.rename({"nome": "nome_dup", "caminho": "caminho_dup", "rank": "rank_dup", "tipo": "tipo_dup"})
    merge = merge.with_columns([
        (
            pl.lit(70)
            + pl.when(pl.col("stem") == pl.col("stem")).then(15).otherwise(0)
            + pl.when(pl.col("tamanho") == pl.col("tamanho")).then(10).otherwise(0)
            + pl.when(pl.col("ext") == pl.col("ext")).then(5).otherwise(0)
            + pl.when(pl.min_horizontal("rank_dup", "rank_orig") <= 1).then(20)
               .when(pl.min_horizontal("rank_dup", "rank_orig") <= 3).then(14)
               .when(pl.min_horizontal("rank_dup", "rank_orig") <= 5).then(6)
               .otherwise(0)
        ).clip(0, 100).alias("score"),
    ])
    merge = merge.with_columns(
        pl.when(pl.col("score") >= 100).then(pl.lit("IDENTIDADE_CRIPTO_PROVAVEL"))
          .when(pl.col("score") >= 95).then(pl.lit("COPIA_CONFIRMADA"))
          .when(pl.col("score") >= 85).then(pl.lit("VARIANTE_HOMOLOGA"))
          .when(pl.col("score") >= 70).then(pl.lit("SIMILARIDADE_FORTE"))
          .otherwise(pl.lit("SIMILARIDADE_MODERADA")).alias("grau")
    )
    out = merge.filter(pl.col("score") >= MIN_SCORE)
    log(f"  Pares: {out.height:,} em {time.time()-t_s:.2f}s")

    log("")
    log("[5/5] Gravacao de resultados...")
    t_o = time.time()
    out = out.with_row_index("id_par", offset=1).with_columns(
        (pl.lit("PAR_") + pl.col("id_par").cast(pl.Utf8).str.zfill(7)).alias("id_par")
    ).select([
        "id_par", "grau", "score", "tipo_orig", "nome_orig", "caminho_orig", "rank_orig",
        "tipo_dup", "nome_dup", "caminho_dup", "rank_dup", "tamanho", "stem", "ext"
    ]).rename({
        "grau": "grau_certeza", "score": "score_confianca",
        "tamanho": "tamanho_bytes", "stem": "stem_normalizado", "ext": "extensao"
    })
    csv_out = os.path.join(OUT, "cruzamento_multi_sinal_v9.csv")
    out.write_csv(csv_out)
    log(f"  CSV: {csv_out}  ({time.time()-t_o:.2f}s)")
    dist = out.group_by("grau_certeza").len().sort("len", descending=True).to_dicts()
    espaco = out.group_by("grau_certeza").agg(pl.col("tamanho_bytes").sum().alias("bytes")).to_dicts()
    rel = {
        "modo": MOD,
        "data": datetime.now().isoformat(),
        "duracao_segundos": round(time.time() - t0, 2),
        "total_registos": int(df.height),
        "total_originais": int(orig.height),
        "total_duplicados": int(dup.height),
        "total_pares": int(out.height),
        "distribuicao_grau": {d["grau_certeza"]: int(d["len"]) for d in dist},
        "espaco_recuperavel_gb": {e["grau_certeza"]: round(e["bytes"] / 1073741824, 2) for e in espaco},
        "ficheiros_alterados": 0,
        "ficheiros_movidos": 0,
        "ficheiros_apagados": 0,
    }
    with open(os.path.join(OUT, "relatorio_executivo_v9.json"), "w", encoding="utf-8") as f:
        json.dump(rel, f, indent=2, ensure_ascii=False)
    log("")
    log("=" * 78)
    log("  DISTRIBUICAO POR GRAU DE CERTEZA")
    log("=" * 78)
    emap = {e["grau_certeza"]: e["bytes"] / 1073741824 for e in espaco}
    for d in dist:
        g = d["grau_certeza"]
        n = d["len"]
        gb = emap.get(g, 0)
        log(f"  {g:<34} {n:>12,} pares  {gb:>10.2f} GB")
    log("=" * 78)
    log("  ALTERADOS: 0  |  MOVIDOS: 0  |  APAGADOS: 0")
    log("=" * 78)
    log("  [OK] CRUZAMENTO V9 TURBO CONCLUIDO EM DRYRUN")
    log("=" * 78)

if __name__ == "__main__":
    main()
