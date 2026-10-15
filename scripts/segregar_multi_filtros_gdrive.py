# -*- coding: utf-8 -*-
"""
Segrega originais e duplicados do Google Drive.
Aplica 6 filtros progressivos + cross-format.
"""
import os
import time
import json
import re
import csv
from collections import defaultdict
from datetime import datetime

FONTE = r"C:\ACERVO\logs\google_drive\por_tipo"
DEST  = r"C:\ACERVO\logs\google_drive\segregado_v2"
os.makedirs(DEST, exist_ok=True)

TIPOS = ["database","video","excel","audio","word","pdf",
         "imagem","json","texto","yaml","csv","markdown"]

RE_SUF = re.compile(
    r"(?:[\s_\-]+(?:copy|copia|final|v\d+|backup|old|novo|new|\d+))+\s*$",
    re.IGNORECASE
)

# Rank de custodia: G:\O meu disco vence G:\Outros computadores
def rank_caminho(c):
    c = c.lower()
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

def profundidade(caminho):
    return caminho.count("\\")

def carregar_tipo(tipo):
    p = os.path.join(FONTE, f"{tipo}.csv")
    if not os.path.isfile(p):
        return []
    rows = []
    with open(p, "r", encoding="utf-8", errors="replace", newline="") as f:
        r = csv.reader(f)
        header = next(r, None)
        idx = {h.lower(): i for i, h in enumerate(header)} if header else {}
        i_nome = idx.get("nome", 0)
        i_cam  = idx.get("caminho", 1)
        i_tam  = idx.get("tamanho", 2)
        i_dat  = idx.get("datamod", 3)
        i_att  = idx.get("atributos", 4)
        i_ext  = idx.get("extensao", 5)
        for row in r:
            if len(row) <= max(i_nome, i_cam, i_tam, i_ext):
                continue
            nome = row[i_nome].strip()
            caminho = row[i_cam].strip()
            try:
                tam = int(row[i_tam])
            except ValueError:
                continue
            if tam <= 0 or not nome or not caminho:
                continue
            rows.append({
                "tipo": tipo,
                "nome": nome,
                "caminho": caminho,
                "tamanho": tam,
                "data_mod": row[i_dat] if len(row) > i_dat else "",
                "atributos": row[i_att] if len(row) > i_att else "",
                "extensao": row[i_ext].lower() if len(row) > i_ext else "",
                "stem": normalizar_stem(nome),
                "rank": rank_caminho(caminho),
                "profundidade": profundidade(caminho),
            })
    return rows

def segregar(rows, chave_fn):
    """Segrega usando chave_fn. Retorna (originais, duplicados)."""
    grupos = defaultdict(list)
    for r in rows:
        grupos[chave_fn(r)].append(r)

    originais = []
    duplicados = []
    for chave, grupo in grupos.items():
        if len(grupo) == 1:
            originais.append(grupo[0])
            continue
        # Ordenar: rank menor vence, depois caminho mais curto, depois nome
        grupo.sort(key=lambda x: (x["rank"], x["profundidade"], x["caminho"], x["nome"]))
        originais.append(grupo[0])
        for d in grupo[1:]:
            duplicados.append(d)
    return originais, duplicados

def main():
    t0 = time.time()
    print("=" * 78)
    print("  SEGREGAR ORIGINAIS vs DUPLICADOS - MULTI-FILTROS")
    print("=" * 78)
    print()

    # ============================================================
    # CARREGAR
    # ============================================================
    print("[1/6] A carregar todos os tipos...")
    todos = []
    for tipo in TIPOS:
        rows = carregar_tipo(tipo)
        if rows:
            todos.extend(rows)
            print(f"  [{tipo:>10}] {len(rows):>10,} registos")
    print(f"\n  TOTAL: {len(todos):,} registos")
    print()

    if not todos:
        print("  [ERRO] Nenhum registo!")
        return

    # ============================================================
    # ITERACAO 1: Stem + Tamanho
    # ============================================================
    print("=" * 78)
    print("  ITERACAO 1: Stem + Tamanho")
    print("=" * 78)
    t1 = time.time()
    o1, d1 = segregar(todos, lambda r: (r["stem"], r["tamanho"]))
    print(f"  Originais:  {len(o1):>10,}")
    print(f"  Duplicados: {len(d1):>10,}")
    print(f"  Tempo: {time.time()-t1:.2f}s")
    print()

    # ============================================================
    # ITERACAO 2: Stem + Tamanho + Extensao
    # ============================================================
    print("=" * 78)
    print("  ITERACAO 2: Stem + Tamanho + Extensao")
    print("=" * 78)
    t2 = time.time()
    o2, d2 = segregar(todos, lambda r: (r["stem"], r["tamanho"], r["extensao"]))
    print(f"  Originais:  {len(o2):>10,}")
    print(f"  Duplicados: {len(d2):>10,}")
    print(f"  Tempo: {time.time()-t2:.2f}s")
    print()

    # ============================================================
    # ITERACAO 3: Stem + Tamanho + Extensao + Data
    # ============================================================
    print("=" * 78)
    print("  ITERACAO 3: Stem + Tamanho + Extensao + Data")
    print("=" * 78)
    t3 = time.time()
    o3, d3 = segregar(todos, lambda r: (r["stem"], r["tamanho"], r["extensao"], r["data_mod"]))
    print(f"  Originais:  {len(o3):>10,}")
    print(f"  Duplicados: {len(d3):>10,}")
    print(f"  Tempo: {time.time()-t3:.2f}s")
    print()

    # ============================================================
    # ITERACAO 4: Stem + Tamanho + Extensao + Data + Atributos
    # ============================================================
    print("=" * 78)
    print("  ITERACAO 4: Stem + Tamanho + Extensao + Data + Atributos")
    print("=" * 78)
    t4 = time.time()
    o4, d4 = segregar(todos, lambda r: (r["stem"], r["tamanho"], r["extensao"], r["data_mod"], r["atributos"]))
    print(f"  Originais:  {len(o4):>10,}")
    print(f"  Duplicados: {len(d4):>10,}")
    print(f"  Tempo: {time.time()-t4:.2f}s")
    print()

    # ============================================================
    # ITERACAO 5: Stem + Tamanho + Rank (so)
    # ============================================================
    print("=" * 78)
    print("  ITERACAO 5: Stem + Tamanho (sem extensao)")
    print("=" * 78)
    t5 = time.time()
    o5, d5 = segregar(todos, lambda r: (r["stem"], r["tamanho"]))
    print(f"  Originais:  {len(o5):>10,}")
    print(f"  Duplicados: {len(d5):>10,}")
    print(f"  Tempo: {time.time()-t5:.2f}s")
    print()

    # ============================================================
    # CROSS-FORMAT
    # ============================================================
    print("=" * 78)
    print("  CROSS-FORMAT: DOCX<->PDF, XLSX<->CSV, YAML<->JSON, etc")
    print("=" * 78)
    t6 = time.time()
    EQUIV = [
        ("word", "pdf"), ("pdf", "word"),
        ("excel", "csv"), ("csv", "excel"),
        ("markdown", "texto"), ("texto", "markdown"),
        ("yaml", "json"), ("json", "yaml"),
    ]
    # Agrupar por stem + tamanho
    grupos_cross = defaultdict(list)
    for r in todos:
        grupos_cross[(r["stem"], r["tamanho"])].append(r)

    cross_pares = []
    for chave, grupo in grupos_cross.items():
        if len(grupo) < 2:
            continue
        # Verificar se ha tipos equivalentes
        tipos_presentes = set(r["tipo"] for r in grupo)
        for t1_, t2_ in EQUIV:
            if t1_ in tipos_presentes and t2_ in tipos_presentes:
                cross_pares.append({
                    "stem": chave[0],
                    "tamanho": chave[1],
                    "tipos": list(tipos_presentes),
                    "n": len(grupo),
                })
                break
    print(f"  Grupos cross-format: {len(cross_pares):,}")
    print(f"  Tempo: {time.time()-t6:.2f}s")
    print()

    # ============================================================
    # GRAVAR RESULTADOS FINAIS (iteracao 3 = equilibrada)
    # ============================================================
    print("=" * 78)
    print("  A GRAVAR RESULTADOS (ITERACAO 3)")
    print("=" * 78)

    # Gravar CSV originais
    orig_path = os.path.join(DEST, "ORIGINAIS.csv")
    with open(orig_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["tipo","nome","caminho","tamanho","data_mod","atributos","extensao","stem","rank"])
        w.writeheader()
        for r in o3:
            w.writerow({k: r[k] for k in w.fieldnames})
    print(f"  [OK] {orig_path} ({len(o3):,})")

    # Gravar CSV duplicados
    dup_path = os.path.join(DEST, "DUPLICADOS.csv")
    with open(dup_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["tipo","nome","caminho","tamanho","data_mod","atributos","extensao","stem","rank"])
        w.writeheader()
        for r in d3:
            w.writerow({k: r[k] for k in w.fieldnames})
    print(f"  [OK] {dup_path} ({len(d3):,})")

    # Gravar cross-format
    cross_path = os.path.join(DEST, "CROSS_FORMAT.csv")
    if cross_pares:
        with open(cross_path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["stem","tamanho","tipos","n"])
            w.writeheader()
            for r in cross_pares:
                w.writerow(r)
        print(f"  [OK] {cross_path} ({len(cross_pares):,})")

    # Estatisticas por tipo
    print()
    print("  DISTRIBUICAO POR TIPO (iteracao 3):")
    print("-" * 78)
    for tipo in TIPOS:
        o_t = sum(1 for r in o3 if r["tipo"] == tipo)
        d_t = sum(1 for r in d3 if r["tipo"] == tipo)
        if o_t or d_t:
            print(f"  {tipo:<12} orig: {o_t:>8,}   dup: {d_t:>8,}")

    # Espaco recuperavel
    espaco = sum(r["tamanho"] for r in d3)
    gb = espaco / 1024 / 1024 / 1024

    print()
    print("=" * 78)
    print("  RESUMO FINAL")
    print("=" * 78)
    print(f"  Total registos:      {len(todos):,}")
    print(f"  Originais:           {len(o3):,}")
    print(f"  Duplicados:          {len(d3):,}")
    print(f"  Cross-format:        {len(cross_pares):,}")
    print(f"  Espaco recuperavel:  {gb:.2f} GB")
    print(f"  Tempo total:         {time.time()-t0:.2f}s")
    print("=" * 78)

    # Manifesto
    rel = {
        "data": datetime.now().isoformat(),
        "total_registos": len(todos),
        "iteracoes": {
            "1_stem_tam": {"orig": len(o1), "dup": len(d1)},
            "2_stem_tam_ext": {"orig": len(o2), "dup": len(d2)},
            "3_stem_tam_ext_data": {"orig": len(o3), "dup": len(d3)},
            "4_stem_tam_ext_data_attr": {"orig": len(o4), "dup": len(d4)},
        },
        "cross_format": len(cross_pares),
        "espaco_recuperavel_gb": round(gb, 2),
        "ficheiros_alterados": 0,
    }
    rel_path = os.path.join(DEST, "manifesto.json")
    with open(rel_path, "w", encoding="utf-8") as f:
        json.dump(rel, f, indent=2, ensure_ascii=False)
    print(f"  Manifesto: {rel_path}")

if __name__ == "__main__":
    main()
