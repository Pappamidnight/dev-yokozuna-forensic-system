# -*- coding: utf-8 -*-
"""
Segregacao V4 - CORRIGIDA
- Originais: 1 por grupo (stem_raw, tamanho, extensao)
- Duplicados: mesmo grupo, mas perdedores do rank
- Cross-format: apenas stem RAW + tamanho
- NAO normaliza stems entre tipos diferentes
"""
import os
import time
import json
import re
import csv
from collections import defaultdict
from datetime import datetime

FONTE = r"C:\ACERVO\logs\google_drive\por_tipo"
DEST  = r"C:\ACERVO\logs\google_drive\segregado_v4"
os.makedirs(DEST, exist_ok=True)

TIPOS = ["database","video","excel","audio","word","pdf",
         "imagem","json","texto","yaml","csv","markdown"]

RE_SUF = re.compile(
    r"(?:[\s_\-]+(?:copy|copia|final|v\d+|backup|old|novo|new|\d+))+\s*$",
    re.IGNORECASE
)

def stem_raw(nome):
    """Stem RAW - sem normalizacao agressiva, so remove sufixos obvios."""
    stem = os.path.splitext(str(nome))[0]
    stem = RE_SUF.sub("", stem).strip()
    return stem.lower()

def rank_caminho(c):
    c = c.lower()
    if "o meu disco" in c:
        return 0
    if "outros computadores" in c:
        return 1
    return 2

def profundidade(c):
    return c.count("\\")

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
                "stem": stem_raw(nome),
                "rank": rank_caminho(caminho),
                "profundidade": profundidade(caminho),
            })
    return rows

def main():
    t0 = time.time()
    print("=" * 78)
    print("  SEGREGAR V4 - CORRIGIDA")
    print("=" * 78)
    print()

    print("[1/5] A carregar...")
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
    # ITERACAO 1: Stem + Tamanho + Extensao + TIPO
    # ============================================================
    print("=" * 78)
    print("  ITERACAO 1: Stem + Tamanho + Extensao + Tipo")
    print("=" * 78)
    t1 = time.time()

    grupos = defaultdict(list)
    for r in todos:
        chave = (r["tipo"], r["stem"], r["tamanho"], r["extensao"])
        grupos[chave].append(r)

    originais = []
    duplicados = []
    for chave, grupo in grupos.items():
        grupo.sort(key=lambda x: (x["rank"], x["profundidade"], x["caminho"], x["nome"]))
        originais.append(grupo[0])
        for d in grupo[1:]:
            duplicados.append(d)

    print(f"  Grupos:      {len(grupos):>10,}")
    print(f"  Originais:   {len(originais):>10,}")
    print(f"  Duplicados:  {len(duplicados):>10,}")
    print(f"  Tempo: {time.time()-t1:.2f}s")
    print()

    # ============================================================
    # ITERACAO 2: Stem RAW + Tamanho (sem tipo, sem extensao)
    # ============================================================
    print("=" * 78)
    print("  ITERACAO 2: Stem RAW + Tamanho (cross-tipo, cross-ext)")
    print("=" * 78)
    t2 = time.time()

    grupos2 = defaultdict(list)
    for r in todos:
        chave = (r["stem"], r["tamanho"])
        grupos2[chave].append(r)

    orig2 = []
    dup2 = []
    for chave, grupo in grupos2.items():
        grupo.sort(key=lambda x: (x["rank"], x["profundidade"], x["caminho"], x["nome"]))
        orig2.append(grupo[0])
        for d in grupo[1:]:
            dup2.append(d)

    print(f"  Grupos:      {len(grupos2):>10,}")
    print(f"  Originais:   {len(orig2):>10,}")
    print(f"  Duplicados:  {len(dup2):>10,}")
    print(f"  Tempo: {time.time()-t2:.2f}s")
    print()

    # ============================================================
    # ITERACAO 3: Cross-Format (word<->pdf, etc)
    # ============================================================
    print("=" * 78)
    print("  ITERACAO 3: Cross-Format (stem + tamanho)")
    print("=" * 78)
    t3 = time.time()

    EQUIV = {
        frozenset(["word", "pdf"]):      "WORD_PDF",
        frozenset(["excel", "csv"]):     "EXCEL_CSV",
        frozenset(["markdown", "texto"]): "MD_TXT",
        frozenset(["yaml", "json"]):     "YAML_JSON",
    }

    cross = []
    for chave, grupo in grupos2.items():
        if len(grupo) < 2:
            continue
        tipos = set(r["tipo"] for r in grupo)
        for eq, label in EQUIV.items():
            if eq.issubset(tipos):
                cross.append({
                    "stem": chave[0],
                    "tamanho": chave[1],
                    "tipos": "|".join(sorted(tipos)),
                    "label": label,
                    "n": len(grupo),
                })
                break

    print(f"  Cross-format: {len(cross):>10,}")
    print(f"  Tempo: {time.time()-t3:.2f}s")
    print()

    # ============================================================
    # GRAVAR
    # ============================================================
    print("=" * 78)
    print("  A GRAVAR RESULTADOS")
    print("=" * 78)

    campos = ["tipo","nome","caminho","tamanho","data_mod","atributos","extensao","stem","rank"]

    # ORIGINAIS (iteracao 1 - dentro do tipo)
    orig_path = os.path.join(DEST, "ORIGINAIS.csv")
    with open(orig_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for r in originais:
            w.writerow({k: r.get(k, "") for k in campos})
    print(f"  [OK] {orig_path} ({len(originais):,})")

    # DUPLICADOS (iteracao 1)
    dup_path = os.path.join(DEST, "DUPLICADOS.csv")
    with open(dup_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for r in duplicados:
            w.writerow({k: r.get(k, "") for k in campos})
    print(f"  [OK] {dup_path} ({len(duplicados):,})")

    # ORIGINAIS CROSS-FORMAT (iteracao 2)
    orig2_path = os.path.join(DEST, "ORIGINAIS_CROSS.csv")
    with open(orig2_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for r in orig2:
            w.writerow({k: r.get(k, "") for k in campos})
    print(f"  [OK] {orig2_path} ({len(orig2):,})")

    # CROSS-FORMAT (iteracao 3)
    cross_path = os.path.join(DEST, "CROSS_FORMAT.csv")
    if cross:
        with open(cross_path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["stem","tamanho","tipos","label","n"])
            w.writeheader()
            for r in cross:
                w.writerow(r)
        print(f"  [OK] {cross_path} ({len(cross):,})")

    # ============================================================
    # ESTATISTICAS
    # ============================================================
    print()
    print("  DISTRIBUICAO POR TIPO (iteracao 1):")
    print("-" * 78)
    print(f"  {'Tipo':<12} {'Originais':>12} {'Duplicados':>12} {'%dup':>8} {'GB dup':>10}")
    print("-" * 78)

    espaco_total = 0
    for tipo in TIPOS:
        o_t = [r for r in originais if r["tipo"] == tipo]
        d_t = [r for r in duplicados if r["tipo"] == tipo]
        if o_t or d_t:
            tam_d = sum(r["tamanho"] for r in d_t)
            espaco_total += tam_d
            gb = tam_d / 1024 / 1024 / 1024
            pct = (len(d_t) / (len(o_t) + len(d_t)) * 100) if (len(o_t) + len(d_t)) else 0
            print(f"  {tipo:<12} {len(o_t):>12,} {len(d_t):>12,} {pct:>7.1f}% {gb:>9.2f} GB")
    print("-" * 78)

    gb_total = espaco_total / 1024 / 1024 / 1024

    print()
    print("=" * 78)
    print("  RESUMO FINAL (V4)")
    print("=" * 78)
    print(f"  Total registos:      {len(todos):,}")
    print(f"  Originais:           {len(originais):,}")
    print(f"  Duplicados:          {len(duplicados):,}")
    print(f"  Cross-format:        {len(cross):,}")
    print(f"  Espaco recuperavel:  {gb_total:.2f} GB")
    print(f"  Tempo total:         {time.time()-t0:.2f}s")
    print("=" * 78)

    # Manifesto
    rel = {
        "data": datetime.now().isoformat(),
        "versao": "v4",
        "total_registos": len(todos),
        "iteracao_1_tipo_stem_tam_ext": {
            "orig": len(originais),
            "dup": len(duplicados),
        },
        "iteracao_2_stem_tam_cross": {
            "orig": len(orig2),
            "dup": len(dup2),
        },
        "iteracao_3_cross_format": len(cross),
        "espaco_recuperavel_gb": round(gb_total, 2),
        "ficheiros_alterados": 0,
    }
    rel_path = os.path.join(DEST, "manifesto_v4.json")
    with open(rel_path, "w", encoding="utf-8") as f:
        json.dump(rel, f, indent=2, ensure_ascii=False)
    print(f"  Manifesto: {rel_path}")

if __name__ == "__main__":
    main()
