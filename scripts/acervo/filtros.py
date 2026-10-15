# -*- coding: utf-8 -*-
r"""
filtros.py - Aplicar filtros combinados, regex, heuristica, sinonimos
=====================================================================
Uso:
    python filtros.py --tipo video --tam-min 100MB
    python filtros.py --tipo imagem --regex "IMG_\d+"
    python filtros.py --heuristica video
    python filtros.py --sinonimo color
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import (
    Everything, Progress, humano, agora, timestamp, garantir_dirs,
    gravar_csv, gravar_json, banner, DIR_CSV, DIR_JSON, DIR_YAML,
)
from _filtros import Filtro, agrupar_por_heuristica, listar_regex
from _json_yaml import exportar


def parse_tam(s):
    if not s:
        return None
    s = s.strip().upper()
    for suf, m in [("GB", 1024**3), ("MB", 1024**2), ("KB", 1024), ("B", 1)]:
        if s.endswith(suf):
            try:
                return int(float(s[:-len(suf)]) * m)
            except ValueError:
                return None
    return None


def main():
    p = argparse.ArgumentParser(description="Filtros combinados")
    p.add_argument("--tipo")
    p.add_argument("--tam-min")
    p.add_argument("--tam-max")
    p.add_argument("--ext", nargs="+")
    p.add_argument("--regex")
    p.add_argument("--nome")
    p.add_argument("--sinonimo", action="store_true", help="Ativar sinonimos no --nome")
    p.add_argument("--heuristica", help="Agrupar por heuristica (tipo)")
    p.add_argument("--listar-regex", action="store_true")
    p.add_argument("--top", type=int, default=500)
    args = p.parse_args()

    if args.listar_regex:
        listar_regex()
        return

    garantir_dirs()
    ev = Everything()
    if not ev.disponivel and not os.path.isfile(r"C:\ACERVO\bin\es.exe"):
        print("[ERRO] Sem SDK nem es.exe.")
        return

    filtro = Filtro(
        tipo=args.tipo,
        tam_min=parse_tam(args.tam_min),
        tam_max=parse_tam(args.tam_max),
        ext=args.ext,
        regex=args.regex,
        nome_contem=args.nome,
        sinonimos=args.sinonimo,
    )
    banner("FILTROS", filtro.descricao())

    # Pesquisa base via SDK
    base_q = ""
    if args.tipo:
        base_q = f"{args.tipo}:"
    items = ev.search(base_q, limit=args.top)

    # Aplicar filtro em Python
    filtrados = [r for r in items if filtro.aceita(r)]

    print(f"  Base:      {len(items):,} ficheiros")
    print(f"  Filtrados: {len(filtrados):,}")
    print(f"  Espaco:    {humano(sum(r['tamanho'] for r in filtrados))}")

    if args.heuristica:
        grupos = agrupar_por_heuristica(filtrados, args.heuristica)
        print(f"  Grupos heuristicos: {len(grupos):,}")
        for prefixo, grupo in sorted(grupos.items(), key=lambda x: -len(x[1]))[:20]:
            tam = sum(g["tamanho"] for g in grupo)
            print(f"    {prefixo[:60]:<60} {len(grupo):>5}  {humano(tam)}")

    ts = timestamp()
    gravar_csv(os.path.join(DIR_CSV, f"filtro_{ts}.csv"), filtrados)
    gravar_json(os.path.join(DIR_JSON, f"filtro_{ts}.json"), {
        "data": agora(), "filtro": filtro.descricao(), "items": filtrados,
    })
    exportar(filtrados, os.path.join(DIR_YAML, "filtro"), formato="yaml",
             meta={"filtro": filtro.descricao()})

    print(f"\n  [OK] CSV:  {DIR_CSV}")
    print(f"  [OK] JSON: {DIR_JSON}")
    print(f"  [OK] YAML: {DIR_YAML}")

    ev.cleanup()


if __name__ == "__main__":
    main()
