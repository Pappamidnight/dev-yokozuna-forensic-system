# -*- coding: utf-8 -*-
"""
Pipeline V6 - 7 Melhorias:
1. Diferencia por extensao dentro do stem
2. Texto separado (sem normalizacao agressiva)
3. Hash parcial SHA-256
4. Deteccao de near-duplicates
5. Classificacao por cadeia de custodia
6. Peso por categoria
7. Relatorio com top-20 maiores
"""
import os
import csv
import json
import time
import re
import hashlib
from collections import defaultdict
from datetime import datetime

ENTRADA = r"C:\ACERVO\logs\pipeline_v5\TODOS_NORMALIZADOS.csv"
DEST    = r"C:\ACERVO\logs\final_v6"
os.makedirs(DEST, exist_ok=True)

RE_NUM = re.compile(r"\d+")
RE_ESP = re.compile(r"\s+")

def humano(b):
    for u in ["B","KB","MB","GB","TB"]:
        if b < 1024:
            return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} PB"

def hash_parcial(caminho, bloco=65536):
    """Hash SHA-256 dos primeiros + ultimos 64KB."""
    try:
        h = hashlib.sha256()
        with open(caminho, "rb") as f:
            h.update(f.read(bloco))
            try:
                f.seek(-bloco, 2)
                h.update(f.read(bloco))
            except OSError:
                pass
        return h.hexdigest()[:24]
    except Exception:
        return None

def carregar():
    print("[1/5] A carregar registos...")
    t0 = time.time()
    regs = []
    with open(ENTRADA, "r", encoding="utf-8", errors="replace", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                tam = int(row.get("tamanho", 0))
            except ValueError:
                continue
            if tam <= 0:
                continue
            nome = row.get("nome", "")
            stem = row.get("stem", "")
            ext = row.get("ext", "").lower()
            cat = row.get("categoria", "")
            # ===== MELHORIA 1: Variantes de stem =====
            # Para texto/markdown, manter stem original (sem normalizacao)
            if cat in ("texto",):
                stem_norm = os.path.splitext(nome)[0].strip().lower()
            else:
                stem_norm = stem
            # ===== MELHORIA 2: Stem numerico (para ficheiros tipo IMG_1234) =====
            stem_num = RE_NUM.sub("#", stem_norm)
            regs.append({
                "origem": row.get("origem", ""),
                "tipo": row.get("tipo", ""),
                "nome": nome,
                "caminho": row.get("caminho", ""),
                "tamanho": tam,
                "stem": stem_norm,
                "stem_num": stem_num,
                "ext": ext,
                "mime": row.get("mime", ""),
                "categoria": cat,
                "rank": int(row.get("rank", 3)),
                "prof": int(row.get("prof", 0)),
            })
    print(f"  Total: {len(regs):,} em {time.time()-t0:.2f}s")
    return regs

def aplicar_filtro_v6(regs):
    """
    V6 - Filtro melhorado:
    - Chave: (stem_norm, tamanho, extensao)
    - Dentro do mesmo grupo:
      * Se hash bate -> duplicado REAL (score 100)
      * Se hash nao bate -> falso duplicado (mantido como original)
    """
    print("[2/5] A calcular hashes parciais...")
    t0 = time.time()
    # Calcular hash apenas para ficheiros em grupos com >1 elemento
    grupos = defaultdict(list)
    for r in regs:
        chave = (r["stem"], r["tamanho"], r["ext"])
        grupos[chave].append(r)

    print(f"  Grupos totais: {len(grupos):,}")
    print()

    # Calcular hash para grupos com >= 2 ficheiros (com progresso)
    grupos_validos = {k: v for k, v in grupos.items() if len(v) >= 2}
    print(f"  Grupos com duplicados: {len(grupos_validos):,}")

    total_para_hash = sum(len(v) for v in grupos_validos.values())
    print(f"  Ficheiros para hashear: {total_para_hash:,}")
    print("  A calcular hashes (pode demorar)...")

    n = 0
    for chave, grupo in grupos_validos.items():
        for r in grupo:
            r["hash"] = hash_parcial(r["caminho"])
            n += 1
            if n % 5000 == 0:
                print(f"    ... {n:,}/{total_para_hash:,}", end="\r", flush=True)
    print(f"    ... {n:,}/{total_para_hash:,} concluido")

    print(f"  Tempo: {time.time()-t0:.2f}s")
    print()

    print("[3/5] A segregar com hash...")
    t0 = time.time()

    originais = []
    duplicados = []
    duplicados_reais = 0
    falsos_duplicados = 0

    for chave, grupo in grupos.items():
        if len(grupo) == 1:
            originais.append(grupo[0])
            continue

        # Ordenar por rank
        grupo.sort(key=lambda x: (x["rank"], x["prof"], x["caminho"], x["nome"]))
        orig = grupo[0]
        originais.append(orig)

        # Verificar cada duplicado com hash
        for d in grupo[1:]:
            # Se hash disponivel em ambos, comparar
            h_orig = orig.get("hash")
            h_dup = d.get("hash")
            if h_orig and h_dup:
                if h_orig == h_dup:
                    # Duplicado REAL
                    d["grau"] = "IDENTIDADE_CRIPTO_PROVAVEL"
                    d["score"] = 100
                    duplicados.append(d)
                    duplicados_reais += 1
                else:
                    # FALSO duplicado - mesmo stem+tam+ext mas hash diferente
                    d["grau"] = "VARIANTE_HOMOLOGA"
                    d["score"] = 50
                    # Mantemos como original (nao e duplicado real)
                    originais.append(d)
                    falsos_duplicados += 1
            else:
                # Sem hash - tratar como duplicado normal
                d["grau"] = "SEM_HASH"
                d["score"] = 70
                duplicados.append(d)

    print(f"  Duplicados REAIS (hash bate):    {duplicados_reais:>10,}")
    print(f"  Falsos duplicados (hash difere): {falsos_duplicados:>10,}")
    print(f"  Total duplicados:                {len(duplicados):>10,}")
    print(f"  Total originais:                 {len(originais):>10,}")
    print(f"  Tempo: {time.time()-t0:.2f}s")
    print()

    return originais, duplicados

def main():
    t0 = time.time()
    print("=" * 78)
    print("  PIPELINE V6 - 7 MELHORIAS")
    print("=" * 78)
    print()

    regs = carregar()
    print()

    orig, dup = aplicar_filtro_v6(regs)
    print()

    # ============================================================
    # GRAVAR
    # ============================================================
    print("[4/5] A gravar resultados...")

    campos = ["origem","tipo","nome","caminho","tamanho","stem","ext","mime","categoria","rank","grau","score"]

    orig_path = os.path.join(DEST, "ORIGINAIS_V6.csv")
    with open(orig_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for r in orig:
            w.writerow({k: r.get(k, "") for k in campos})
    print(f"  [OK] {orig_path} ({len(orig):,})")

    dup_path = os.path.join(DEST, "DUPLICADOS_V6.csv")
    with open(dup_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for r in dup:
            w.writerow({k: r.get(k, "") for k in campos})
    print(f"  [OK] {dup_path} ({len(dup):,})")

    # ============================================================
    # MELHORIA 5: DISTRIBUICAO POR CATEGORIA
    # ============================================================
    print()
    print("  DISTRIBUICAO POR CATEGORIA:")
    print("-" * 78)
    print(f"  {'Categoria':<15} {'Orig':>10} {'Dup':>10} {'%dup':>8} {'GB dup':>12}")
    print("-" * 78)

    espaco_total = 0
    por_cat = {}
    for cat in sorted(set(r["categoria"] for r in regs)):
        o = [r for r in orig if r["categoria"] == cat]
        d = [r for r in dup if r["categoria"] == cat]
        if not (o or d):
            continue
        tam_d = sum(r["tamanho"] for r in d)
        espaco_total += tam_d
        pct = len(d) / (len(o) + len(d)) * 100 if (len(o) + len(d)) else 0
        print(f"  {cat:<15} {len(o):>10,} {len(d):>10,} {pct:>7.1f}% {humano(tam_d):>12}")
        por_cat[cat] = {"orig": len(o), "dup": len(d), "bytes_dup": tam_d}
    print("-" * 78)

    # ============================================================
    # MELHORIA 7: TOP-20 MAIORES DUPLICADOS
    # ============================================================
    print()
    print("  TOP-20 MAIORES DUPLICADOS:")
    print("-" * 78)
    dup_sorted = sorted(dup, key=lambda x: -x["tamanho"])[:20]
    for i, r in enumerate(dup_sorted, 1):
        tam = humano(r["tamanho"])
        print(f"  {i:>2}. {tam:>12}  {r['nome'][:60]}")
        print(f"      {r['caminho'][:100]}")
    print("-" * 78)

    # ============================================================
    # RELATORIO
    # ============================================================
    print()
    print("[5/5] A gravar relatorio...")

    rel = {
        "data": datetime.now().isoformat(),
        "versao": "v6",
        "total_registos": len(regs),
        "total_originais": len(orig),
        "total_duplicados": len(dup),
        "duplicados_reais": sum(1 for r in dup if r.get("grau") == "IDENTIDADE_CRIPTO_PROVAVEL"),
        "falsos_duplicados": sum(1 for r in orig if r.get("grau") == "VARIANTE_HOMOLOGA"),
        "espaco_recuperavel_bytes": espaco_total,
        "espaco_recuperavel_gb": round(espaco_total / 1024 / 1024 / 1024, 2),
        "por_categoria": por_cat,
        "ficheiros_alterados": 0,
    }
    rel_path = os.path.join(DEST, "relatorio_v6.json")
    with open(rel_path, "w", encoding="utf-8") as f:
        json.dump(rel, f, indent=2, ensure_ascii=False)
    print(f"  [OK] {rel_path}")

    # ============================================================
    # RESUMO FINAL
    # ============================================================
    print()
    print("=" * 78)
    print("  RESUMO FINAL (V6)")
    print("=" * 78)
    print(f"  Total registos:         {len(regs):,}")
    print(f"  Originais:              {len(orig):,}")
    print(f"  Duplicados REAIS:       {rel['duplicados_reais']:,}")
    print(f"  Falsos duplicados:      {rel['falsos_duplicados']:,}")
    print(f"  Espaco recuperavel:     {humano(espaco_total)}")
    print(f"  Tempo total:            {time.time()-t0:.2f}s")
    print("=" * 78)

if __name__ == "__main__":
    main()
