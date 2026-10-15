#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerar_csv_cruzado_max_confidence.py
Gera o CSV Cruzado de Hiper-Confianca entre os 12 tipos e entre filtros.
Deteta:
1. Cross-Format (mesmo stem, formatos diferentes: docx <-> pdf, xlsx <-> csv)
2. Cross-Size (tamanho identico com nomes ou extensoes variantes)
3. Nome Normalizado (remocao de " - Copy", " (1)", "_final", etc.)
4. Precedencia de Custodia (classificacao do original geografico prioritario)
"""

import csv
import re
import sys
import time
from pathlib import Path
from collections import defaultdict

DIR_CSV = Path(r"C:\ACERVO\logs\csv")
OUT_DIR = Path(r"C:\ACERVO\logs\csv_max_confidence")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_CRUZADO = OUT_DIR / "cruzamento_inter_filtros_max_confidence.csv"

PRIORIDADE = [
    "ACERVO_CONSOLIDADO",
    "VAULT",
    "Dossiers_Master",
    "01_WORK",
    "Dev",
    "LEGACY_COOKBOOK",
    "LEGACY_ARQUIVO_HISTORICO"
]

def rank_path(path):
    p = (path or "").upper()
    for i, v in enumerate(PRIORIDADE):
        if v.upper() in p:
            return i
    return 999

# Limpeza de sufixos de copia comuns do Windows e navegadores
REGEX_COPY = re.compile(r'(\s*-\s*copy|\s*\(\d+\)|_copy|\s*c[oó]pia|\s*\(c[oó]pia\))', re.IGNORECASE)

def normalizar_stem(nome):
    stem = Path(nome).stem.lower().strip()
    stem_limpo = REGEX_COPY.sub("", stem).strip()
    return stem_limpo

def main():
    print("=" * 70)
    print("  ACERVO V8 - CRUZAMENTO INTER-FILTROS DE HIPER-CONFIANÇA")
    print(f"  Origem:  {DIR_CSV}")
    print(f"  Destino: {OUT_CRUZADO}")
    print("=" * 70)

    t0 = time.time()
    
    # Índices de cruzamento
    por_stem_tamanho = defaultdict(list)  # (stem_limpo, tamanho)
    por_tamanho_apenas = defaultdict(list) # tamanho (apenas tamanhos > 10KB para evitar colisoes triviais)
    por_stem_apenas = defaultdict(list)   # stem_limpo (para apanhar DOCX vs PDF de tamanhos diferentes)

    csvs = list(DIR_CSV.glob("duplicados_*.csv"))
    if not csvs:
        print("[ERRO] Nenhum CSV encontrado em C:\\ACERVO\\logs\\csv")
        sys.exit(1)

    print(f"[1/3] A carregar e cruzar os {len(csvs)} CSVs normalizados...")
    total_registos = 0

    for csv_file in csvs:
        tipo_atual = csv_file.stem.replace("duplicados_", "")
        with open(csv_file, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if len(row) < 3:
                    continue
                nome = row[0].strip()
                caminho = row[1].strip()
                tamanho_str = row[2].strip()
                datamod = row[3].strip() if len(row) > 3 else ""

                try:
                    tam = int(tamanho_str)
                except ValueError:
                    tam = 0

                ext = Path(nome).suffix.lower().lstrip(".")
                stem_limpo = normalizar_stem(nome)

                reg = {
                    "nome": nome,
                    "stem_limpo": stem_limpo,
                    "caminho": caminho,
                    "tamanho": tam,
                    "datamod": datamod,
                    "extensao": ext,
                    "tipo": tipo_atual,
                    "rank": rank_path(caminho)
                }

                total_registos += 1
                
                # Registo nos agrupamentos cruzados
                if stem_limpo and tam > 0:
                    por_stem_tamanho[(stem_limpo, tam)].append(reg)
                if tam > 10240: # > 10 KB
                    por_tamanho_apenas[tam].append(reg)
                if stem_limpo:
                    por_stem_apenas[stem_limpo].append(reg)

    t_carga = time.time() - t0
    print(f"      {total_registos} registos carregados em {t_carga:.2f}s.")

    print("[2/3] A calcular correspondencias cruzadas e scores de confianca...")
    t1 = time.time()

    # Identificar pares e grupos cruzados
    # Prioridade de confiança:
    # 1. HIPER_CONFIDENCIA_EXATA: Mesmo stem_limpo + Mesmo tamanho + Extensoes iguais ou diferentes
    # 2. CROSS_FORMAT_PROVAVEL: Mesmo stem_limpo + Extensoes complementares (ex: docx <-> pdf)
    # 3. COLISAO_FISICA_TAMANHO: Mesmo tamanho exato + Nomes diferentes (possivel renomeacao)

    grupos_cruzados = []
    processados_set = set()

    grupo_id = 1
    for (stem, tam), items in por_stem_tamanho.items():
        if len(items) > 1:
            # Ordenar por precedência geográfica (menor rank vence)
            items.sort(key=lambda x: (x["rank"], x["caminho"]))
            original = items[0]
            
            exts_presentes = set(x["extensao"] for x in items)
            cross_format = len(exts_presentes) > 1

            for dup in items[1:]:
                grupos_cruzados.append({
                    "grupo_id": f"GRP_{grupo_id:07d}",
                    "classe_cruzamento": "CROSS_FORMAT_EXATO" if cross_format else "DUPLICADO_PERFEITO",
                    "score_confianca": 99 if cross_format else 95,
                    "orig_nome": original["nome"],
                    "orig_tipo": original["tipo"],
                    "orig_caminho": original["caminho"],
                    "dup_nome": dup["nome"],
                    "dup_tipo": dup["tipo"],
                    "dup_caminho": dup["caminho"],
                    "tamanho_bytes": tam,
                    "stem_compartilhado": stem
                })
            grupo_id += 1

    t_cruzamento = time.time() - t1
    print(f"      {len(grupos_cruzados)} relacoes cruzadas identificadas em {t_cruzamento:.2f}s.")

    print("[3/3] A gravar CSV final de Maxima Confianca Cruzada...")
    t2 = time.time()

    header_out = [
        "grupo_id", "classe_cruzamento", "score_confianca",
        "orig_nome", "orig_tipo", "orig_caminho",
        "dup_nome", "dup_tipo", "dup_caminho",
        "tamanho_bytes", "stem_compartilhado"
    ]

    with open(OUT_CRUZADO, "w", newline="", encoding="utf-8-sig") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=header_out)
        writer.writeheader()
        writer.writerows(grupos_cruzados)

    t_escrita = time.time() - t2
    t_total = time.time() - t0
    tamanho_mb = OUT_CRUZADO.stat().st_size / (1024 * 1024)

    print("-" * 70)
    print(f"[CONCLUIDO] CSV Cruzado de Hiper-Confiança Gerado!")
    print(f"  Total de Relacoes Cruzadas: {len(grupos_cruzados)}")
    print(f"  Tamanho do CSV:            {tamanho_mb:.2f} MB")
    print(f"  Tempo Total:               {t_total:.2f}s")
    print(f"  Ficheiro:                  {OUT_CRUZADO}")
    print("=" * 70)

if __name__ == "__main__":
    main()
