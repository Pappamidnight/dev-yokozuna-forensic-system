# -*- coding: utf-8 -*-
r"""
duplicados.py - Duplicados por tipo com progress bar
=====================================================
Uso:
    python duplicados.py
    python duplicados.py --tipo video
    python duplicados.py --santuario "C:\ACERVO\storage"
"""
import os
import sys
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import (
    Everything, Progress, humano, agora, timestamp, garantir_dirs,
    gravar_csv, gravar_json, banner, DIR_CSV, DIR_JSON, DIR_YAML,
    everything_a_correr,
)
from _json_yaml import exportar

TIPOS = {
    "video":    "video: dupe:size;duration",
    "audio":    "audio: dupe:size;duration",
    "imagem":   "image: dupe:name;size",
    "pdf":      "ext:pdf dupe:name;size",
    "word":     "ext:doc;docx dupe:name;size",
    "excel":    "ext:xls;xlsx dupe:name;size",
    "markdown": "ext:md dupe:name;size",
    "geral":    "dupe:name;size size:>10mb",
}


def correr(tipos, santuario, top, quiet=False):
    garantir_dirs()

    # (check removido — es.exe e a fonte)

    ev = Everything()
    if ev.disponivel:
        fonte = "SDK"
    elif os.path.isfile(r"C:\ACERVO\bin\es.exe"):
        fonte = "es.exe (fallback)"
    else:
        print("[ERRO] Sem SDK nem es.exe.")
        return None

    banner("DUPLICADOS", f"Fonte: {fonte}  |  Tipos: {len(tipos)}")
    if santuario:
        print(f"  Santuario: {santuario}")

    resultados = []
    prog = Progress(len(tipos), prefix="Tipos", ativo=not quiet)

    for t in tipos:
        query = TIPOS.get(t, t)
        if santuario:
            query = f'{query} dupe-from:"{santuario}"'
        prog.update(0, sufixo=f"-> {t}")
        items = ev.search(query, limit=top)
        items.sort(key=lambda x: -x["tamanho"])
        tam = sum(i["tamanho"] for i in items)
        resultados.append({
            "tipo": t, "query": query,
            "total": len(items), "tamanho": tam, "items": items,
        })
        prog.update(1, sufixo=f"{t}: {len(items)} ({humano(tam)})")

    prog.done()

    if not quiet:
        print()
        banner("RESUMO")
        print(f"  {'TIPO':<12} {'TOTAL':>8} {'TAMANHO':>14}")
        print("  " + "-" * 88)
        tot_b = 0
        for r in resultados:
            tot_b += r["tamanho"]
            print(f"  {r['tipo']:<12} {r['total']:>8} {humano(r['tamanho']):>14}")
        print("  " + "-" * 88)
        print(f"  {'TOTAL':<12} {sum(r['total'] for r in resultados):>8} {humano(tot_b):>14}")
        print("=" * 92)

    ts = timestamp()
    for r in resultados:
        gravar_csv(os.path.join(DIR_CSV, f"dup_{r['tipo']}_{ts}.csv"), r["items"])
    gravar_json(os.path.join(DIR_JSON, f"duplicados_{ts}.json"), {
        "data": agora(), "fonte": fonte, "santuario": santuario,
        "tipos": resultados,
    })
    exportar(resultados, os.path.join(DIR_YAML, "duplicados"), formato="yaml",
             meta={"santuario": santuario})

    print(f"\n  [OK] CSV:  {DIR_CSV}")
    print(f"  [OK] JSON: {DIR_JSON}")
    print(f"  [OK] YAML: {DIR_YAML}")

    ev.cleanup()
    return resultados


def main():
    p = argparse.ArgumentParser(description="Duplicados")
    p.add_argument("--tipos", nargs="*")
    p.add_argument("--tipo")
    p.add_argument("--santuario")
    p.add_argument("--top", type=int, default=200)
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args()

    if args.tipo:
        tipos = [args.tipo]
    elif args.tipos:
        tipos = args.tipos
    else:
        tipos = list(TIPOS.keys())

    correr(tipos, args.santuario, args.top, args.quiet)


if __name__ == "__main__":
    main()


