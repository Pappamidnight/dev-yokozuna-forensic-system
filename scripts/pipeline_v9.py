# -*- coding: utf-8 -*-
"""
Pipeline V9 — Polars + SANDBOX
1. Le os 24 CSVs (12 originais + 12 duplicados)
2. Consolida em 2 CSVs unificados
3. Move os duplicados para SANDBOX com isolamento de 5 dias
"""
import os
import json
import shutil
import time
from datetime import datetime, timedelta
import polars as pl

# ---------- CONFIGURACAO ----------
DEDUP     = r"C:\ACERVO\logs\deduplicado"
SANDBOX   = r"C:\ACERVO\SANDBOX\duplicados_isolados"
MANIFESTO = r"C:\ACERVO\SANDBOX\manifesto_isolamento.json"
OUTPUT    = r"C:\ACERVO\logs\cruzamento_v9"
DIAS      = 5
TIPOS     = ["database","video","excel","audio","word","pdf",
             "imagem","json","texto","yaml","csv","markdown"]

def log(msg):
    print(msg, flush=True)

def humano(b):
    for u in ["B","KB","MB","GB","TB"]:
        if b < 1024:
            return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} PB"

def main():
    t0 = time.time()
    dt_ini = datetime.now()
    dt_lib = dt_ini + timedelta(days=DIAS)

    os.makedirs(SANDBOX, exist_ok=True)
    os.makedirs(OUTPUT, exist_ok=True)

    log("=" * 78)
    log("  PIPELINE V9 - POLARS + SANDBOX")
    log("=" * 78)
    log(f"  Origem:   {DEDUP}")
    log(f"  Sandbox:  {SANDBOX}")
    log(f"  Output:   {OUTPUT}")
    log(f"  Liberta:  {dt_lib.isoformat()}")
    log("")

    # ---------- ETAPA 1: LER CSVs ----------
    log("[1/4] A ler CSVs com Polars...")
    frames_orig = []
    frames_dup  = []
    for t in TIPOS:
        po = os.path.join(DEDUP, t, f"originais_{t}.csv")
        pd = os.path.join(DEDUP, t, f"duplicados_{t}.csv")
        ok_o = False
        ok_d = False
        if os.path.isfile(po):
            try:
                df = pl.read_csv(po, infer_schema_length=0,
                                 ignore_errors=True,
                                 truncate_ragged_lines=True)
                df = df.with_columns(pl.lit(t).alias("tipo"))
                frames_orig.append(df)
                ok_o = True
            except Exception as e:
                log(f"  ! erro a ler {po}: {e}")
        if os.path.isfile(pd):
            try:
                df = pl.read_csv(pd, infer_schema_length=0,
                                 ignore_errors=True,
                                 truncate_ragged_lines=True)
                df = df.with_columns(pl.lit(t).alias("tipo"))
                frames_dup.append(df)
                ok_d = True
            except Exception as e:
                log(f"  ! erro a ler {pd}: {e}")
        if not ok_o and not ok_d:
            log(f"  [--] {t} sem ficheiros")
        else:
            log(f"  [OK] {t} -> orig={ok_o} dup={ok_d}")

    # ---------- ETAPA 2: CONSOLIDAR ----------
    log("")
    log("[2/4] A consolidar originais e duplicados...")
    co = pl.concat(frames_orig, how="diagonal_relaxed") if frames_orig else pl.DataFrame()
    cd = pl.concat(frames_dup,  how="diagonal_relaxed") if frames_dup  else pl.DataFrame()
    n_orig = co.height if co.height else 0
    n_dup  = cd.height if cd.height else 0
    log(f"  Originais consolidados: {n_orig:,} linhas")
    log(f"  Duplicados consolidados: {n_dup:,} linhas")

    # ---------- ETAPA 3: GRAVAR CSVs ----------
    log("")
    log("[3/4] A gravar CSVs consolidados...")
    po_out = os.path.join(OUTPUT, "ORIGINAIS_CONSOLIDADOS.csv")
    pd_out = os.path.join(OUTPUT, "DUPLICADOS_CONSOLIDADOS.csv")
    if n_orig:
        co.write_csv(po_out)
        log(f"  [OK] {po_out}")
    if n_dup:
        cd.write_csv(pd_out)
        log(f"  [OK] {pd_out}")

    # ---------- ETAPA 4: MOVER PARA SANDBOX ----------
    log("")
    log("[4/4] A mover duplicados para SANDBOX...")
    movidos = []
    falhas  = []
    total_bytes = 0
    for t in TIPOS:
        src = os.path.join(DEDUP, t, f"duplicados_{t}.csv")
        dst = os.path.join(SANDBOX, t, f"duplicados_{t}.csv")
        if not os.path.isfile(src):
            log(f"  [SKIP] duplicados_{t}.csv nao existe")
            falhas.append({"tipo": t, "erro": "nao existe"})
            continue
        try:
            sz = os.path.getsize(src)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
            movidos.append({"tipo": t, "origem": src, "destino": dst, "bytes": sz})
            total_bytes += sz
            log(f"  [OK] duplicados_{t}.csv -> {humano(sz)}")
        except Exception as e:
            log(f"  [ERRO] {t}: {e}")
            falhas.append({"tipo": t, "erro": str(e)})

    # ---------- MANIFESTO ----------
    json.dump({
        "versao": "v9",
        "data_criacao": dt_ini.isoformat(),
        "data_libertacao": dt_lib.isoformat(),
        "dias_isolamento": DIAS,
        "origem": DEDUP,
        "sandbox": SANDBOX,
        "total_movidos": len(movidos),
        "total_bytes": total_bytes,
        "total_humano": humano(total_bytes),
        "originais_consolidados": n_orig,
        "duplicados_consolidados": n_dup,
        "ficheiros": movidos,
        "falhas": falhas,
    }, open(MANIFESTO, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    log(f"  [OK] {MANIFESTO}")

    # ---------- RESUMO ----------
    log("")
    log("=" * 78)
    log("  RESUMO FINAL")
    log("=" * 78)
    log(f"  Originais consolidados:   {n_orig:,}")
    log(f"  Duplicados consolidados:  {n_dup:,}")
    log(f"  Movidos para SANDBOX:     {len(movidos)}/{len(TIPOS)}")
    log(f"  Total movido:             {humano(total_bytes)}")
    log(f"  Falhas:                   {len(falhas)}")
    log(f"  Tempo total:              {time.time()-t0:.2f}s")
    log(f"  Liberta em:               {dt_lib.isoformat()}")
    log("=" * 78)
    log("  [OK] PIPELINE COMPLETO")
    log("=" * 78)

if __name__ == "__main__":
    main()
