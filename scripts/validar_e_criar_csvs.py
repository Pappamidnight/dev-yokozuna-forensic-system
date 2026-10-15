# -*- coding: utf-8 -*-
import os, json, time
import polars as pl
from datetime import datetime

BASE = r"C:\ACERVO"
DEDUP = os.path.join(BASE, "logs", "deduplicado")
OUT = os.path.join(BASE, "logs", "cruzamento_v9")
MOD = "DRYRUN"
TIPOS = ["database","video","excel","audio","word","pdf","imagem","json","texto","yaml","csv","markdown"]

def log(msg):
    print(msg, flush=True)

def contar_linhas(p):
    if not os.path.isfile(p):
        return 0
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            return max(0, sum(1 for _ in f) - 1)
    except Exception:
        return 0

def main():
    t0 = time.time()
    log("=" * 78)
    log("  VALIDACAO DE ORIGINAIS + CRIACAO DE DUPLICADOS")
    log(f"  MODO: {MOD}")
    log("=" * 78)

    log("")
    log("[1/3] Validando CSVs de originais...")
    totais_orig = 0
    validos = []
    falhas = []
    for t in TIPOS:
        p = os.path.join(DEDUP, t, "originais_" + t + ".csv")
        n = contar_linhas(p)
        if n > 0:
            validos.append((t, n, p))
            totais_orig += n
            log(f"  [OK] originais_{t}.csv -> {n:,} linhas")
        else:
            falhas.append(t)
            log(f"  [FALHA] originais_{t}.csv -> <empty or missing>")

    log("")
    log(f"  Total de originais: {totais_orig:,} em {len(validos)}/12 tipos")
    if falhas:
        log(f"  Tipos com falha: {falhas}")
    else:
        log("  TODOS os 12 tipos tem originais consolidados!")

    log("")
    log("[2/3] Criando CSV consolidado de originais...")
    frames_orig = []
    for t, n, p in validos:
        try:
            df = pl.read_csv(p, infer_schema_length=0, ignore_errors=True, truncate_ragged_lines=True)
        except Exception as e:
            log(f"  ! erro a ler {p}: {e}")
            continue
        df = df.with_columns(pl.lit(t).alias("tipo"))
        frames_orig.append(df)
    if frames_orig:
        cons_orig = pl.concat(frames_orig, how="diagonal_relaxed")
        cns_orig_path = os.path.join(OUT, "ORIGINAIS_CONSOLIDADOS.csv")
        cons_orig.write_csv(cns_orig_path)
        log(f"  [OK] {cns_orig_path}  ({cons_orig.height:,} linhas)")
    else:
        log("  [!!!] Nenhum original encontrado!")

    log("")
    log("[3/3] Criando CSV consolidado de duplicados...")
    frames_dup = []
    totais_dup = 0
    for t in TIPOS:
        p = os.path.join(DEDUP, t, "duplicados_" + t + ".csv")
        n = contar_linhas(p)
        if n == 0:
            log(f"  [FALHA] duplicados_{t}.csv -> <empty or missing>")
            continue
        try:
            df = pl.read_csv(p, infer_schema_length=0, ignore_errors=True, truncate_ragged_lines=True)
        except Exception as e:
            log(f"  ! erro a ler {p}: {e}")
            continue
        df = df.with_columns(pl.lit(t).alias("tipo"))
        frames_dup.append(df)
        totais_dup += n
        log(f"  [OK] duplicados_{t}.csv -> {n:,} linhas")

    if frames_dup:
        cons_dup = pl.concat(frames_dup, how="diagonal_relaxed")
        cns_dup_path = os.path.join(OUT, "DUPLICADOS_CONSOLIDADOS.csv")
        cons_dup.write_csv(cns_dup_path)
        log(f"  [OK] {cns_dup_path}  ({cons_dup.height:,} linhas)")
    else:
        log("  [!!!] Nenhum duplicado encontrado!")

    log("")
    log("=" * 78)
    log("  RESUMO FINAL")
    log("=" * 78)
    log(f"  Total de originais: {totais_orig:,}")
    log(f"  Total de duplicados: {totais_dup:,}")
    log(f"  Total geral: {totais_orig + totais_dup:,}")
    log(f"  Tempo total: {time.time() - t0:.2f}s")
    log("  ALTERADOS: 0  |  MOVIDOS: 0  |  APAGADOS: 0")
    log("=" * 78)
    log("  [OK] VALIDACAO E CRIACAO CONCLUIDOS EM DRYRUN")
    log("=" * 78)

    manifesto = {
        "data": datetime.now().isoformat(),
        "modo": MOD,
        "total_originais": totais_orig,
        "total_duplicados": totais_dup,
        "total_geral": totais_orig + totais_dup,
        "tipos_com_originais": len(validos),
        "tipos_com_falha": falhas,
    }
    man_path = os.path.join(OUT, "manifesto_csvs_v9.json")
    with open(man_path, "w", encoding="utf-8") as f:
        json.dump(manifesto, f, indent=2, ensure_ascii=False)
    log(f"  Manifesto: {man_path}")

if __name__ == "__main__":
    main()