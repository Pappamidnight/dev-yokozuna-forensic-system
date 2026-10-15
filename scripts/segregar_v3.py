# -*- coding: utf-8 -*-
"""
Segregacao V3 - Melhorada
- Filtro 1: Stem + Tamanho (base)
- Filtro 2: + Extensao
- Filtro 3: + Data (mas com tolerancia de 1h)
- Filtro 4: Hash parcial se disponivel
- Cross-format melhorado (stems mais agressivos)
- Deduplicacao entre grupos
"""
import os
import time
import json
import re
import csv
import hashlib
from collections import defaultdict
from datetime import datetime, timedelta

FONTE = r"C:\ACERVO\logs\google_drive\por_tipo"
DEST  = r"C:\ACERVO\logs\google_drive\segregado_v3"
os.makedirs(DEST, exist_ok=True)

TIPOS = ["database","video","excel","audio","word","pdf",
         "imagem","json","texto","yaml","csv","markdown"]

# ============================================================
# NORMALIZACAO AGRESSIVA DE STEM
# ============================================================
RE_SUFIXOS = [
    r"[\s_\-]*(?:copy|copia|cópia|final|finalizado|v\d+|versao\d*|backup|bkp|old|antigo|novo|new|bak|tmp|temp)\s*$",
    r"[\s_\-]*\(\d+\)\s*$",
    r"[\s_\-]*\[\d+\]\s*$",
    r"[\s_\-]*_\d{6,}\s*$",
    r"[\s_\-]*\d{8,}\s*$",
    r"[\s_\-]+$",
]
RE_SUF = re.compile("|".join(RE_SUFIXOS), re.IGNORECASE)

RE_DATA = re.compile(r"(19|20)\d{2}[\-_]?\d{2}[\-_]?\d{2}")

def normalizar_stem(nome):
    """Normalizacao agressiva."""
    stem = os.path.splitext(str(nome))[0]
    # Remover sufixos de copia
    for _ in range(3):
        novo = RE_SUF.sub("", stem).strip()
        if novo == stem:
            break
        stem = novo
    # Remover datas
    stem = RE_DATA.sub("", stem)
    # Normalizar espacos
    stem = re.sub(r"[\s_\-]+", " ", stem).strip().lower()
    return stem

def stem_sem_ext(nome):
    """Stem puro sem extensao, sem normalizacao agressiva."""
    return os.path.splitext(str(nome))[0].strip().lower()

# ============================================================
# RANK DE CUSTODIA
# ============================================================
def rank_caminho(c):
    c = c.lower()
    if "o meu disco" in c:
        return 0
    if "outros computadores" in c:
        return 1
    return 2

def profundidade(c):
    return c.count("\\")

# ============================================================
# DATA COM TOLERANCIA
# ============================================================
def data_para_minutos(d):
    """Converte data para minutos desde epoch (tolera formatos)."""
    if not d:
        return None
    formatos = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y",
        "%Y/%m/%d %H:%M:%S",
    ]
    for fmt in formatos:
        try:
            dt = datetime.strptime(d.strip(), fmt)
            return int(dt.timestamp() / 60)
        except ValueError:
            continue
    return None

def data_igual(d1, d2, tolerancia_min=60):
    """Compara datas com tolerancia."""
    m1 = data_para_minutos(d1)
    m2 = data_para_minutos(d2)
    if m1 is None or m2 is None:
        return d1 == d2  # fallback texto
    return abs(m1 - m2) <= tolerancia_min

# ============================================================
# CARREGAR
# ============================================================
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
                "stem_raw": stem_sem_ext(nome),
                "rank": rank_caminho(caminho),
                "profundidade": profundidade(caminho),
            })
    return rows

# ============================================================
# SEGREGAR GENÉRICO
# ============================================================
def segregar(rows, chave_fn):
    grupos = defaultdict(list)
    for r in rows:
        grupos[chave_fn(r)].append(r)

    originais = []
    duplicados = []
    for chave, grupo in grupos.items():
        if len(grupo) == 1:
            originais.append(grupo[0])
            continue
        grupo.sort(key=lambda x: (x["rank"], x["profundidade"], x["caminho"], x["nome"]))
        originais.append(grupo[0])
        for d in grupo[1:]:
            duplicados.append(d)
    return originais, duplicados

# ============================================================
# MAIN
# ============================================================
def main():
    t0 = time.time()
    print("=" * 78)
    print("  SEGREGAR V3 - MELHORADO")
    print("=" * 78)
    print()

    # Carregar
    print("[1/7] A carregar...")
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
    # ITERACAO 1: Stem + Tamanho (BASE)
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
    # ITERACAO 2: + Extensao
    # ============================================================
    print("=" * 78)
    print("  ITERACAO 2: + Extensao")
    print("=" * 78)
    t2 = time.time()
    o2, d2 = segregar(todos, lambda r: (r["stem"], r["tamanho"], r["extensao"]))
    print(f"  Originais:  {len(o2):>10,}")
    print(f"  Duplicados: {len(d2):>10,}")
    print(f"  Tempo: {time.time()-t2:.2f}s")
    print()

    # ============================================================
    # ITERACAO 3: Stem + Tamanho + DATA COM TOLERANCIA 1h
    # ============================================================
    print("=" * 78)
    print("  ITERACAO 3: Stem + Tamanho + Data (tolerancia 1h)")
    print("=" * 78)
    t3 = time.time()

    grupos3 = defaultdict(list)
    for r in todos:
        grupos3[(r["stem"], r["tamanho"])].append(r)

    o3, d3 = [], []
    for chave, grupo in grupos3.items():
        if len(grupo) == 1:
            o3.append(grupo[0])
            continue
        # Ordenar por rank
        grupo.sort(key=lambda x: (x["rank"], x["profundidade"], x["caminho"], x["nome"]))
        # Agrupar por data (com tolerancia)
        subgrupos = []
        for item in grupo:
            colocado = False
            for sg in subgrupos:
                if data_igual(sg[0]["data_mod"], item["data_mod"], 60):
                    sg.append(item)
                    colocado = True
                    break
            if not colocado:
                subgrupos.append([item])
        # Cada subgrupo gera 1 original
        for sg in subgrupos:
            o3.append(sg[0])
            for d in sg[1:]:
                d3.append(d)

    print(f"  Originais:  {len(o3):>10,}")
    print(f"  Duplicados: {len(d3):>10,}")
    print(f"  Tempo: {time.time()-t3:.2f}s")
    print()

    # ============================================================
    # ITERACAO 4: Cross-Format (stem raw sem extensao)
    # ============================================================
    print("=" * 78)
    print("  ITERACAO 4: Cross-Format (stem normalizado)")
    print("=" * 78)
    t4 = time.time()

    EQUIV = [
        frozenset(["word", "pdf"]),
        frozenset(["excel", "csv"]),
        frozenset(["markdown", "texto"]),
        frozenset(["yaml", "json"]),
        frozenset(["imagem", "imagem"]),
        frozenset(["video", "video"]),
        frozenset(["audio", "audio"]),
        frozenset(["database", "database"]),
    ]

    grupos4 = defaultdict(list)
    for r in todos:
        grupos4[(r["stem"], r["tamanho"])].append(r)

    cross_pares = []
    for chave, grupo in grupos4.items():
        if len(grupo) < 2:
            continue
        tipos = set(r["tipo"] for r in grupo)
        # Procurar pares equivalentes
        for eq in EQUIV:
            inter = tipos & eq
            if len(inter) >= 2:
                cross_pares.append({
                    "stem": chave[0],
                    "tamanho": chave[1],
                    "tipos": sorted(tipos),
                    "n": len(grupo),
                })
                break

    print(f"  Grupos cross-format: {len(cross_pares):,}")
    print(f"  Tempo: {time.time()-t4:.2f}s")
    print()

    # ============================================================
    # ITERACAO 5: Duplicados reais (presentes em >1 grupo)
    # ============================================================
    print("=" * 78)
    print("  ITERACAO 5: Duplicados reais (presentes em multiplos grupos)")
    print("=" * 78)
    t5 = time.time()

    # Um ficheiro e duplicado se aparece em mais de um grupo
    # Aqui usamos (caminho) como identificador
    contagem = defaultdict(int)
    for r in todos:
        contagem[r["caminho"]] += 1

    # Ficheiros duplicados = com o mesmo caminho
    dups_reais = [r for r in todos if contagem[r["caminho"]] > 1]
    print(f"  Ficheiros com caminho duplicado: {len(dups_reais):,}")
    print(f"  Tempo: {time.time()-t5:.2f}s")
    print()

    # ============================================================
    # GRAVAR RESULTADOS
    # ============================================================
    print("=" * 78)
    print("  A GRAVAR RESULTADOS (ITERACAO 2 = base solida)")
    print("=" * 78)

    # Escolhemos iteracao 2 (stem + tam + ext) como base
    campos = ["tipo","nome","caminho","tamanho","data_mod","atributos","extensao","stem","rank"]

    orig_path = os.path.join(DEST, "ORIGINAIS.csv")
    with open(orig_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for r in o2:
            w.writerow({k: r.get(k, "") for k in campos})
    print(f"  [OK] {orig_path} ({len(o2):,})")

    dup_path = os.path.join(DEST, "DUPLICADOS.csv")
    with open(dup_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for r in d2:
            w.writerow({k: r.get(k, "") for k in campos})
    print(f"  [OK] {dup_path} ({len(d2):,})")

    cross_path = os.path.join(DEST, "CROSS_FORMAT.csv")
    if cross_pares:
        with open(cross_path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["stem","tamanho","tipos","n"])
            w.writeheader()
            for r in cross_pares:
                r2 = dict(r)
                r2["tipos"] = "|".join(r2["tipos"])
                w.writerow(r2)
        print(f"  [OK] {cross_path} ({len(cross_pares):,})")

    # ============================================================
    # ESTATISTICAS POR TIPO (iteracao 2)
    # ============================================================
    print()
    print("  DISTRIBUICAO POR TIPO (iteracao 2):")
    print("-" * 78)
    print(f"  {'Tipo':<12} {'Originais':>12} {'Duplicados':>12} {'%dup':>8}")
    print("-" * 78)
    for tipo in TIPOS:
        o_t = sum(1 for r in o2 if r["tipo"] == tipo)
        d_t = sum(1 for r in d2 if r["tipo"] == tipo)
        if o_t or d_t:
            pct = (d_t / (o_t + d_t) * 100) if (o_t + d_t) else 0
            print(f"  {tipo:<12} {o_t:>12,} {d_t:>12,} {pct:>7.1f}%")
    print("-" * 78)

    # Espaco recuperavel
    espaco = sum(r["tamanho"] for r in d2)
    gb = espaco / 1024 / 1024 / 1024

    print()
    print("=" * 78)
    print("  RESUMO FINAL (V3)")
    print("=" * 78)
    print(f"  Total registos:      {len(todos):,}")
    print(f"  Originais:           {len(o2):,}")
    print(f"  Duplicados:          {len(d2):,}")
    print(f"  Cross-format:        {len(cross_pares):,}")
    print(f"  Espaco recuperavel:  {gb:.2f} GB")
    print(f"  Tempo total:         {time.time()-t0:.2f}s")
    print("=" * 78)

    # Manifesto
    rel = {
        "data": datetime.now().isoformat(),
        "versao": "v3",
        "total_registos": len(todos),
        "iteracoes": {
            "1_stem_tam": {"orig": len(o1), "dup": len(d1)},
            "2_stem_tam_ext": {"orig": len(o2), "dup": len(d2)},
            "3_stem_tam_data_tol": {"orig": len(o3), "dup": len(d3)},
        },
        "cross_format": len(cross_pares),
        "espaco_recuperavel_gb": round(gb, 2),
        "ficheiros_alterados": 0,
    }
    rel_path = os.path.join(DEST, "manifesto_v3.json")
    with open(rel_path, "w", encoding="utf-8") as f:
        json.dump(rel, f, indent=2, ensure_ascii=False)
    print(f"  Manifesto: {rel_path}")

if __name__ == "__main__":
    main()
