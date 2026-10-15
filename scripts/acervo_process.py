# -*- coding: utf-8 -*-
"""
acervo_process.py - Processa 1 tipo de cada vez
================================================
Uso:
    python acervo_process.py pdf
    python acervo_process.py video --heuristica
    python acervo_process.py pdf --rank-max 1
    python acervo_process.py --all        # todos os 12 (sequencial)
    python acervo_process.py --all --quiet
"""
import os
import sys
import argparse
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from acervo_core import (
    carregar_csv, gravar_csv, gravar_json, garantir_dirs, humano,
    segregar, agrupar_por_heuristica, timestamp, agora_str,
    TIPOS, DIR_FILTROS, DIR_MANIF, Filtro,
)


def processar(tipo, rank_max=None, usar_heuristica=False, verbose=True):
    t0 = time.time()
    if verbose:
        print()
        print("=" * 88)
        print(f"  PROCESSAR: {tipo.upper()}  |  {agora_str()}")
        print("=" * 88)

    # 1) Carregar
    filtro = Filtro(tipo=tipo, rank_max=rank_max)
    t1 = time.time()
    regs = carregar_csv(filtro, verbose=False)
    if verbose:
        print(f"[1/4] Carregados: {len(regs):>10,}  ({time.time()-t1:.2f}s)")

    if not regs:
        if verbose:
            print(f"      [AVISO] Nenhum registo para '{tipo}'")
        return None

    # 2) Segregar
    t2 = time.time()
    originais, duplicados, n_grupos = segregar(regs)
    if verbose:
        print(f"[2/4] Grupos: {n_grupos:>10,}  "
              f"orig={len(originais):>8,}  dup={len(duplicados):>8,}  "
              f"({time.time()-t2:.2f}s)")

    # 3) Heuristica (opcional)
    heur = None
    if usar_heuristica:
        t3 = time.time()
        heur = agrupar_por_heuristica(regs, tipo)
        if verbose:
            print(f"[3/4] Heuristica: {len(heur):>8,} grupos  "
                  f"({time.time()-t3:.2f}s)")
    else:
        if verbose:
            print("[3/4] Heuristica: (desativada)")

    # 4) Gravar
    ts = timestamp()
    t4 = time.time()
    orig_path = os.path.join(DIR_FILTROS, f"originais_{tipo}_{ts}.csv")
    dup_path = os.path.join(DIR_FILTROS, f"duplicados_{tipo}_{ts}.csv")
    man_path = os.path.join(DIR_MANIF, f"manifesto_{tipo}_{ts}.json")

    gravar_csv(orig_path, originais)
    gravar_csv(dup_path, duplicados)

    espaco = sum(r["tamanho"] for r in duplicados)
    manifesto = {
        "tipo": tipo,
        "data": agora_str(),
        "filtro": filtro.descricao(),
        "regs_total": len(regs),
        "grupos": n_grupos,
        "originais": len(originais),
        "duplicados": len(duplicados),
        "espaco_recuperavel_bytes": espaco,
        "espaco_recuperavel_humano": humano(espaco),
        "heuristica_ativa": usar_heuristica,
        "heuristica_grupos": len(heur) if heur else 0,
        "outputs": {
            "originais": orig_path,
            "duplicados": dup_path,
        },
    }
    gravar_json(man_path, manifesto)

    if verbose:
        print(f"[4/4] Gravado em {time.time()-t4:.2f}s")
        print()
        print("-" * 88)
        print(f"  Originais:           {len(originais):>10,}")
        print(f"  Duplicados:          {len(duplicados):>10,}")
        print(f"  Espaco recuperavel:  {humano(espaco):>10}")
        print(f"  Tempo:               {time.time()-t0:>10.2f}s")
        print("-" * 88)

    return {
        "tipo": tipo,
        "originais": len(originais),
        "duplicados": len(duplicados),
        "espaco": espaco,
        "tempo": time.time() - t0,
        "manifesto": man_path,
    }


def main():
    parser = argparse.ArgumentParser(description="Processa tipo(s) do ACERVO")
    parser.add_argument("tipo", nargs="?", choices=TIPOS, help="Tipo a processar")
    parser.add_argument("--all", action="store_true", help="Todos os 12 tipos")
    parser.add_argument("--rank-max", type=int, help="Rank maximo")
    parser.add_argument("--heuristica", action="store_true", help="Ativar heuristica")
    parser.add_argument("--quiet", action="store_true", help="Modo silencioso")
    parser.add_argument("--list", action="store_true", help="Listar tipos")
    args = parser.parse_args()

    if args.list:
        print("Tipos validos:")
        for t in TIPOS:
            print(f"  - {t}")
        return

    garantir_dirs()
    verbose = not args.quiet

    if args.all:
        alvos = TIPOS
    elif args.tipo:
        alvos = [args.tipo]
    else:
        parser.print_help()
        return

    resultados = []
    t0 = time.time()
    for t in alvos:
        res = processar(t, args.rank_max, args.heuristica, verbose)
        if res:
            resultados.append(res)
        if verbose and len(alvos) > 1:
            print()

    # Resumo final
    if len(resultados) > 1:
        print()
        print("=" * 88)
        print("  RESUMO FINAL")
        print("=" * 88)
        print(f"  {'TIPO':<12} {'ORIG':>10} {'DUP':>10} {'ESPACO':>14} {'TEMPO':>8}")
        print("  " + "-" * 84)
        to = td = te = 0
        for r in resultados:
            print(f"  {r['tipo']:<12} {r['originais']:>10,} {r['duplicados']:>10,} "
                  f"{humano(r['espaco']):>14} {r['tempo']:>7.2f}s")
            to += r["originais"]; td += r["duplicados"]; te += r["espaco"]
        print("  " + "-" * 84)
        print(f"  {'TOTAL':<12} {to:>10,} {td:>10,} {humano(te):>14} "
              f"{time.time()-t0:>7.2f}s")
        print("=" * 88)


if __name__ == "__main__":
    main()
