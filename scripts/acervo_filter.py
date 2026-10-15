# -*- coding: utf-8 -*-
"""
acervo_filter.py - Filtros combinados por tipo
===============================================
Uso:
    python acervo_filter.py --tipo pdf
    python acervo_filter.py --tipo video --tam-min 100MB
    python acervo_filter.py --tipo imagem --rank-max 1
    python acervo_filter.py --tipo pdf --regex "manual|guide"
    python acervo_filter.py --tipo video --ext .mp4 .mkv
    python acervo_filter.py --heuristica video    # agrupa variantes
"""
import os
import sys
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from acervo_core import (
    carregar_csv, gravar_csv, garantir_dirs, humano, timestamp,
    Filtro, agrupar_por_heuristica, TIPOS, DIR_FILTROS,
)


def parse_tamanho(s):
    """Converte '100MB' em bytes."""
    if not s:
        return None
    s = s.strip().upper()
    mult = 1
    for suf, m in [("GB", 1024**3), ("MB", 1024**2), ("KB", 1024), ("B", 1)]:
        if s.endswith(suf):
            s = s[:-len(suf)]
            mult = m
            break
    try:
        return int(float(s) * mult)
    except ValueError:
        return None


def main():
    parser = argparse.ArgumentParser(description="Filtros combinados")
    parser.add_argument("--tipo", choices=TIPOS, help="Tipo a filtrar")
    parser.add_argument("--rank-max", type=int, help="Rank maximo")
    parser.add_argument("--rank-min", type=int, help="Rank minimo")
    parser.add_argument("--prof-max", type=int, help="Profundidade maxima")
    parser.add_argument("--tam-min", help="Tamanho minimo (100MB)")
    parser.add_argument("--tam-max", help="Tamanho maximo")
    parser.add_argument("--ext", nargs="+", help="Extensoes (.pdf .jpg)")
    parser.add_argument("--regex", help="Regex no nome")
    parser.add_argument("--nome", help="Contem no nome")
    parser.add_argument("--heuristica", choices=TIPOS,
                        help="Agrupar por heuristica (variantes)")
    parser.add_argument("--output", help="Output CSV (default: auto)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    garantir_dirs()

    filtro = Filtro(
        tipo=args.tipo,
        rank_max=args.rank_max,
        rank_min=args.rank_min,
        prof_max=args.prof_max,
        tam_min=parse_tamanho(args.tam_min),
        tam_max=parse_tamanho(args.tam_max),
        ext=args.ext,
        regex=args.regex,
        nome_contem=args.nome,
    )

    print()
    print("=" * 88)
    print(f"  FILTRO: {filtro.descricao()}")
    print(f"  Data:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 88)

    regs = carregar_csv(filtro)

    if not regs:
        print("\n  [VAZIO] Nenhum registo corresponde ao filtro.")
        return

    total_bytes = sum(r["tamanho"] for r in regs)
    print(f"\n  Encontrados: {len(regs):,}  ({humano(total_bytes)})")

    # Heuristica
    if args.heuristica:
        print(f"\n  A agrupar por heuristica ({args.heuristica})...")
        grupos = agrupar_por_heuristica(regs, args.heuristica)
        print(f"  Grupos heuristicos: {len(grupos):,}")
        print()
        print(f"  {'PREFIXO':<40} {'REGISTOS':>10} {'TAMANHO':>12}")
        print("  " + "-" * 84)
        for prefixo, items in sorted(grupos.items(),
                                     key=lambda x: -len(x[1]))[:20]:
            tam = sum(i["tamanho"] for i in items)
            print(f"  {prefixo[:38]:<40} {len(items):>10,} {humano(tam):>12}")
        if len(grupos) > 20:
            print(f"  ... (+{len(grupos)-20} grupos)")

    # Output
    ts = timestamp()
    if not args.output:
        nome = args.tipo or "filtro"
        ext = "json" if args.json else "csv"
        args.output = os.path.join(DIR_FILTROS, f"{nome}_{ts}.{ext}")

    if args.json:
        from acervo_core import gravar_json
        gravar_json(args.output, {
            "filtro": filtro.descricao(),
            "total": len(regs),
            "bytes": total_bytes,
            "registos": regs,
        })
    else:
        gravar_csv(args.output, regs)

    print(f"\n  [OK] {args.output}")
    print("=" * 88)


if __name__ == "__main__":
    main()
