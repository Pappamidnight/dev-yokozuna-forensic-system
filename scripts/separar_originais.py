#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
separar_originais.py
Separa registos em originais e duplicados com base na hierarquia estrita de precedencia:
ACERVO_CONSOLIDADO > VAULT > Dossiers_Master > 01_WORK > Dev > LEGACY_COOKBOOK > LEGACY_ARQUIVO_HISTORICO
"""

import csv
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(r"C:\ACERVO\logs\csv")
OUT = Path(r"C:\ACERVO\logs\deduplicado")
OUT.mkdir(parents=True, exist_ok=True)

# Hierarquia estrita de precedencia do original
PRIORIDADE = [
    "ACERVO_CONSOLIDADO",
    "VAULT",
    "Dossiers_Master",
    "01_WORK",
    "Dev",
    "LEGACY_COOKBOOK",
    "LEGACY_ARQUIVO_HISTORICO"
]

def rank(path):
    p = (path or "").upper()
    for i, v in enumerate(PRIORIDADE):
        if v.upper() in p:
            return i
    return 999

def main():
    csv_files = sorted(ROOT.glob("duplicados_*.csv"))
    if not csv_files:
        print("[ERRO] Nenhum CSV encontrado em C:\\ACERVO\\logs\\csv")
        sys.exit(1)

    print("=" * 65)
    print("  SEPARACAO HIERARQUICA: ORIGINAIS VS DUPLICADOS")
    print("=" * 65)

    # Ordem de execucao prioritaria
    ORDEM = ["database", "video", "excel", "audio", "word", "pdf", "imagem", "json", "texto", "yaml", "csv", "markdown"]
    
    # Mapear ficheiros por tipo
    fichs_por_tipo = {}
    for f in csv_files:
        partes = f.stem.split("_")
        tipo = partes[1] if len(partes) >= 2 else "desconhecido"
        fichs_por_tipo[tipo] = f

    total_orig = 0
    total_dups = 0

    # Iterar segundo a ordem definida
    tipos_ordenados = [t for t in ORDEM if t in fichs_por_tipo] + [t for t in fichs_por_tipo if t not in ORDEM]

    for tipo in tipos_ordenados:
        csvfile = fichs_por_tipo[tipo]
        pasta = OUT / tipo
        pasta.mkdir(parents=True, exist_ok=True)

        originais = pasta / f"originais_{tipo}.csv"
        duplicados = pasta / f"duplicados_{tipo}.csv"

        grupos = defaultdict(list)

        with open(csvfile, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or ["Nome", "Caminho", "Tamanho", "DataMod"]
            for row in reader:
                chave = (row.get("Nome", "").strip(), row.get("Tamanho", "").strip())
                grupos[chave].append(row)

        sub_orig = 0
        sub_dup = 0

        with open(originais, "w", newline="", encoding="utf-8") as fo, \
             open(duplicados, "w", newline="", encoding="utf-8") as fd:

            w1 = csv.DictWriter(fo, fieldnames=fieldnames)
            w1.writeheader()

            w2 = csv.DictWriter(fd, fieldnames=fieldnames)
            w2.writeheader()

            for grupo in grupos.values():
                grupo.sort(key=lambda r: rank(r.get("Caminho", "")))

                original = grupo[0]
                w1.writerow(original)
                sub_orig += 1

                for dup in grupo[1:]:
                    w2.writerow(dup)
                    sub_dup += 1

        total_orig += sub_orig
        total_dups += sub_dup
        print(f"[{tipo:10}] Originais: {sub_orig:7} | Duplicados: {sub_dup:7}")

    print("=" * 65)
    print(f"[CONCLUIDO] Total Originais: {total_orig} | Total Duplicados: {total_dups}")
    print(f"[DESTINO]   {OUT}")
    print("=" * 65)

if __name__ == "__main__":
    main()
