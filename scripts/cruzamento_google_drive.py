# -*- coding: utf-8 -*-
import os
import csv
import time
import json
import re
from collections import defaultdict
from datetime import datetime

FONTE = r"C:\ACERVO\logs\google_drive\por_tipo"
DEST  = r"C:\ACERVO\logs\google_drive"
TIPOS = ["database","video","excel","audio","word","pdf",
         "imagem","json","texto","yaml","csv","markdown"]

RE_SUF = re.compile(
    r"(?:[\s_\-]+(?:copy|copia|final|v\d+|backup|old|novo|new|\d+))+\s*$",
    re.IGNORECASE
)

def main():
    t0 = time.time()
    print("=" * 70)
    print("  CRUZAMENTO ULTRA-FORENSE - GOOGLE DRIVE")
    print("=" * 70)
    print(f"  Fonte:   {FONTE}")
    print(f"  Destino: {DEST}\\cruzamento_google_drive.csv")
    print()

    print("[1/3] A carregar registos...")
    grupos = defaultdict(list)
    total = 0

    for tipo in TIPOS:
        p = os.path.join(FONTE, f"{tipo}.csv")
        if not os.path.isfile(p):
            continue
        with open(p, "r", encoding="utf-8", errors="replace", newline="") as f:
            r = csv.reader(f)
            next(r, None)
            for row in r:
                if len(row) < 6:
                    continue
                nome = row[0].strip()
                caminho = row[1].strip()
                try:
                    tam = int(row[2])
                except (ValueError, IndexError):
                    continue
                if tam <= 0 or not nome:
                    continue
                stem = RE_SUF.sub("", os.path.splitext(nome)[0]).strip().lower()
                stem = re.sub(r"\s+", " ", stem)
                chave = (stem, tam)
                grupos[chave].append({
                    "tipo": tipo,
                    "nome": nome,
                    "caminho": caminho,
                    "tam": tam,
                    "data": row[3] if len(row) > 3 else "",
                })
                total += 1

    print(f"  Registos: {total:,}")
    print(f"  Grupos:   {len(grupos):,}")
    print()

    print("[2/3] A calcular scores forenses...")
    pares = []
    for chave, rows in grupos.items():
        if len(rows) < 2:
            continue
        rows.sort(key=lambda x: (x["caminho"], x["nome"]))
        orig = rows[0]
        for dup in rows[1:]:
            if orig["tam"] == dup["tam"]:
                score = 100
                grau = "IDENTIDADE_CRIPTO_PROVAVEL"
            else:
                score = 85
                grau = "VARIANTE_HOMOLOGA"
            pares.append({
                "id_par": f"PAR_{len(pares)+1:07d}",
                "score_confianca": score,
                "grau_certeza": grau,
                "orig_tipo": orig["tipo"],
                "orig_nome": orig["nome"],
                "orig_caminho": orig["caminho"],
                "dup_tipo": dup["tipo"],
                "dup_nome": dup["nome"],
                "dup_caminho": dup["caminho"],
                "tamanho_bytes": dup["tam"],
                "stem": chave[0],
            })

    print(f"  Pares: {len(pares):,}")
    print()

    print("[3/3] A gravar CSV...")
    out = os.path.join(DEST, "cruzamento_google_drive.csv")
    campos = ["id_par","score_confianca","grau_certeza",
              "orig_tipo","orig_nome","orig_caminho",
              "dup_tipo","dup_nome","dup_caminho",
              "tamanho_bytes","stem"]
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(pares)

    sz = os.path.getsize(out) / 1024 / 1024
    print(f"  [OK] {out}")
    print(f"  Tamanho: {sz:.2f} MB")
    print(f"  Tempo: {time.time()-t0:.2f}s")
    print("=" * 70)

if __name__ == "__main__":
    main()
