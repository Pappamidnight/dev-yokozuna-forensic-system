# -*- coding: utf-8 -*-
import os
import csv
import json
import time
import sys
from datetime import datetime
from collections import defaultdict

FONTE = r"C:\ACERVO\logs\google_drive\cruzamento_google_drive.csv"
DEST  = r"C:\ACERVO\logs\google_drive\quarentena_dryrun"

def main():
    tipo = sys.argv[1] if len(sys.argv) > 1 else "pdf"
    os.makedirs(DEST, exist_ok=True)
    t0 = time.time()

    print("=" * 70)
    print(f"  SIMULACAO DRY-RUN: [{tipo.upper()}]")
    print("=" * 70)
    print(f"  Modo:   DRY-RUN (READ-ONLY)")
    print(f"  Filtro: Score de Confianca == 100")
    print()

    if not os.path.isfile(FONTE):
        print(f"  [ERRO] Fonte nao encontrada: {FONTE}")
        return

    originais = set()
    candidatos = []
    total_bytes = 0

    with open(FONTE, "r", encoding="utf-8", errors="replace", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            if row.get("score_confianca") != "100":
                continue
            if row.get("dup_tipo") != tipo:
                continue
            originais.add(row.get("orig_caminho"))
            candidatos.append(row)
            try:
                total_bytes += int(row.get("tamanho_bytes", 0))
            except ValueError:
                pass

    gb = total_bytes / 1024 / 1024 / 1024

    print("-" * 70)
    print("  RESULTADO DA SIMULACAO (DRY-RUN):")
    print(f"  Originais protegidos no Hub:        {len(originais):>10,}")
    print(f"  Copias mapeadas para Quarentena:    {len(candidatos):>10,}")
    print(f"  Espaco Recuperavel Projetado:       {gb:>10.2f} GB")
    print(f"  Tempo de Analise:                   {time.time()-t0:>10.2f}s")
    print(f"  Ficheiros Fisicamente Alterados:    0 (INTEGRIDADE TOTAL)")
    print("-" * 70)

    # Manifesto JSON
    manifesto = {
        "tipo": tipo,
        "data": datetime.now().isoformat(),
        "modo": "DRYRUN",
        "originais_protegidos": len(originais),
        "duplicados_mapeados": len(candidatos),
        "bytes_recuperaveis": total_bytes,
        "gb_recuperaveis": round(gb, 2),
        "ficheiros_alterados": 0,
        "ficheiros_movidos": 0,
        "ficheiros_apagados": 0,
    }
    man_path = os.path.join(DEST, f"manifesto_quarentena_dryrun_{tipo}.json")
    with open(man_path, "w", encoding="utf-8") as f:
        json.dump(manifesto, f, indent=2, ensure_ascii=False)

    # Lista CSV de candidatos
    csv_path = os.path.join(DEST, f"candidatos_quarentena_{tipo}.csv")
    if candidatos:
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(candidatos[0].keys()))
            w.writeheader()
            w.writerows(candidatos)

    print(f"  Manifesto JSON: {man_path}")
    print(f"  Lista CSV:      {csv_path}")
    print("=" * 70)

if __name__ == "__main__":
    main()
