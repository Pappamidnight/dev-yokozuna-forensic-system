# -*- coding: utf-8 -*-
"""
V8 FAST - Processador de tipos reutilizavel
============================================
Uso:
    python processar_v8_fast.py <tipo>              # 1 tipo
    python processar_v8_fast.py <tipo1> <tipo2> ... # varios tipos
    python processar_v8_fast.py --all               # todos os 12 tipos
    python processar_v8_fast.py --list              # listar tipos
    python processar_v8_fast.py --help              # ajuda
"""
import os
import sys
import csv
import json
import time
import argparse
from collections import defaultdict
from datetime import datetime

TIPOS_VALIDOS = [
    "database", "video", "excel", "audio", "word", "pdf",
    "imagem", "json", "texto", "yaml", "csv", "markdown",
]

ENTRADA = r"C:\ACERVO\logs\pipeline_v5\TODOS_NORMALIZADOS.csv"
DEST    = r"C:\ACERVO\logs\v8_fast"
SANDBOX = r"C:\ACERVO\SANDBOX\v8"

CAMPOS = [
    "origem", "tipo", "nome", "caminho", "tamanho",
    "stem", "ext", "mime", "categoria", "rank", "grau", "score",
]


def humano(b):
    for u in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if b < 1024:
            return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} EB"


def garantir_dirs():
    os.makedirs(DEST, exist_ok=True)
    os.makedirs(SANDBOX, exist_ok=True)


def carregar_tipo(tipo_alvo):
    regs = []
    with open(ENTRADA, "r", encoding="utf-8", errors="replace", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            if row.get("tipo", "") != tipo_alvo:
                continue
            try:
                tam = int(row.get("tamanho", 0))
            except (ValueError, TypeError):
                continue
            if tam <= 0:
                continue
            regs.append({
                "origem":    row.get("origem", ""),
                "tipo":      row.get("tipo", ""),
                "nome":      row.get("nome", ""),
                "caminho":   row.get("caminho", ""),
                "tamanho":   tam,
                "stem":      row.get("stem", ""),
                "ext":       row.get("ext", ""),
                "mime":      row.get("mime", ""),
                "categoria": row.get("categoria", ""),
                "rank":      int(row.get("rank", 3) or 3),
                "prof":      int(row.get("prof", 0) or 0),
            })
    return regs


def segregar(regs):
    grupos = defaultdict(list)
    for r in regs:
        chave = (r["stem"], r["tamanho"], r["ext"])
        grupos[chave].append(r)

    originais = []
    duplicados = []
    for chave, grupo in grupos.items():
        if len(grupo) == 1:
            originais.append(grupo[0])
            continue
        grupo.sort(key=lambda x: (x["rank"], x["prof"], x["caminho"], x["nome"]))
        originais.append(grupo[0])
        for d in grupo[1:]:
            d["grau"] = "DUPLICADO"
            d["score"] = 85
            duplicados.append(d)
    return originais, duplicados, len(grupos)


def gravar_csv(caminho, registos, campos=CAMPOS):
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for r in registos:
            w.writerow({k: r.get(k, "") for k in campos})


def processar_tipo(tipo_alvo, verbose=True):
    if tipo_alvo not in TIPOS_VALIDOS:
        print(f"[ERRO] Tipo invalido: {tipo_alvo}")
        print(f"       Validos: {', '.join(TIPOS_VALIDOS)}")
        return None

    t0 = time.time()

    if verbose:
        print("=" * 78)
        print(f"  V8 FAST - {tipo_alvo.upper()}")
        print("=" * 78)

    t1 = time.time()
    regs = carregar_tipo(tipo_alvo)
    if verbose:
        print(f"[1/3] Carregados: {len(regs):>10,} registos  ({time.time()-t1:.2f}s)")
    if not regs:
        if verbose:
            print(f"      [AVISO] Nenhum registo para '{tipo_alvo}'")
        return {
            "tipo": tipo_alvo, "originais": 0, "duplicados": 0,
            "espaco": 0, "tempo": time.time() - t0, "vazio": True,
        }

    t2 = time.time()
    originais, duplicados, n_grupos = segregar(regs)
    if verbose:
        print(f"[2/3] Grupos:    {n_grupos:>10,}")
        print(f"      Originais: {len(originais):>10,}")
        print(f"      Duplicados:{len(duplicados):>10,}  ({time.time()-t2:.2f}s)")

    t3 = time.time()
    orig_path = os.path.join(DEST, f"originais_{tipo_alvo}.csv")
    dup_path  = os.path.join(DEST, f"duplicados_{tipo_alvo}.csv")
    sbx_dir   = os.path.join(SANDBOX, tipo_alvo)
    sbx_path  = os.path.join(sbx_dir, f"duplicados_{tipo_alvo}.csv")
    man_path  = os.path.join(DEST, f"manifesto_{tipo_alvo}.json")

    gravar_csv(orig_path, originais)
    gravar_csv(dup_path, duplicados)
    os.makedirs(sbx_dir, exist_ok=True)
    gravar_csv(sbx_path, duplicados)

    espaco = sum(r["tamanho"] for r in duplicados)
    manifesto = {
        "tipo": tipo_alvo,
        "data": datetime.now().isoformat(),
        "originais": len(originais),
        "duplicados": len(duplicados),
        "espaco_recuperavel_bytes": espaco,
        "espaco_recuperavel_gb": round(espaco / 1024 / 1024 / 1024, 2),
    }
    with open(man_path, "w", encoding="utf-8") as f:
        json.dump(manifesto, f, indent=2, ensure_ascii=False)

    if verbose:
        print(f"[3/3] Gravado em {time.time()-t3:.2f}s")
        print()
        print("-" * 78)
        print(f"  Originais:          {len(originais):>10,}")
        print(f"  Duplicados:         {len(duplicados):>10,}")
        print(f"  Espaco recuperavel: {humano(espaco)}")
        print(f"  Tempo total:        {time.time()-t0:.2f}s")
        print("-" * 78)

    return {
        "tipo": tipo_alvo,
        "originais": len(originais),
        "duplicados": len(duplicados),
        "espaco": espaco,
        "tempo": time.time() - t0,
    }


def main():
    parser = argparse.ArgumentParser(
        description="V8 FAST - Processador de tipos reutilizavel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("tipos", nargs="*", help="Tipo(s) a processar")
    parser.add_argument("--all", action="store_true", help="Processar todos os 12 tipos")
    parser.add_argument("--list", action="store_true", help="Listar tipos validos")
    parser.add_argument("--quiet", action="store_true", help="Modo silencioso")
    args = parser.parse_args()

    if args.list:
        print("Tipos validos:")
        for t in TIPOS_VALIDOS:
            print(f"  - {t}")
        return

    garantir_dirs()

    if args.all:
        alvos = TIPOS_VALIDOS
    elif args.tipos:
        alvos = args.tipos
    else:
        parser.print_help()
        return

    verbose = not args.quiet
    resultados = []
    t_inicio = time.time()

    for tipo in alvos:
        res = processar_tipo(tipo, verbose=verbose)
        if res:
            resultados.append(res)
        if verbose and len(alvos) > 1:
            print()

    if len(resultados) > 1:
        print()
        print("=" * 78)
        print("  RESUMO FINAL")
        print("=" * 78)
        print(f"  {'TIPO':<12} {'ORIGINAIS':>12} {'DUPLICADOS':>12} {'ESPACO':>14} {'TEMPO':>8}")
        print("-" * 78)
        tot_orig = tot_dup = tot_esp = 0
        for r in resultados:
            print(f"  {r['tipo']:<12} {r['originais']:>12,} {r['duplicados']:>12,} "
                  f"{humano(r['espaco']):>14} {r['tempo']:>7.2f}s")
            tot_orig += r["originais"]
            tot_dup  += r["duplicados"]
            tot_esp  += r["espaco"]
        print("-" * 78)
        print(f"  {'TOTAL':<12} {tot_orig:>12,} {tot_dup:>12,} "
              f"{humano(tot_esp):>14} {time.time()-t_inicio:>7.2f}s")
        print("=" * 78)

        global_path = os.path.join(DEST, "_manifesto_global.json")
        with open(global_path, "w", encoding="utf-8") as f:
            json.dump({
                "data": datetime.now().isoformat(),
                "tipos_processados": len(resultados),
                "total_originais": tot_orig,
                "total_duplicados": tot_dup,
                "espaco_total_bytes": tot_esp,
                "espaco_total_gb": round(tot_esp / 1024 / 1024 / 1024, 2),
                "tempo_total_s": round(time.time() - t_inicio, 2),
                "detalhes": resultados,
            }, f, indent=2, ensure_ascii=False)
        print(f"\n  [OK] Manifesto global: {global_path}")


if __name__ == "__main__":
    main()
