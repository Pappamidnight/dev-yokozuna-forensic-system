# -*- coding: utf-8 -*-
r"""
analise.py - Analise total com progress bar
============================================
Uso:
    python analise.py
    python analise.py --top 50
    python analise.py --drives C:\ D:\ G:\
"""
import os
import sys
import time
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import (
    Everything, Progress, humano, agora, timestamp, garantir_dirs,
    gravar_csv, gravar_json, banner, DIR_CSV, DIR_JSON, DIR_YAML,
)
from _json_yaml import exportar

ANALISES = [
    ("maiores_1gb",  "size:>1gb",                             "Maiores que 1 GB"),
    ("maiores_500",  "size:>500mb size:<1gb",                 "500 MB - 1 GB"),
    ("video",        "video: size:>100mb",                    "Videos grandes"),
    ("audio",        "audio: size:>20mb",                     "Audio grande"),
    ("imagem",       "image: size:>10mb",                     "Imagens grandes"),
    ("doc",          "doc: size:>5mb",                        "Documentos"),
    ("exe",          "exe: size:>100mb",                      "Executaveis"),
    ("arquivo",      "ext:zip;rar;7z;iso size:>100mb",        "Arquivos"),
    ("sistema",      "attrib:S size:>500mb",                  "Sistema"),
    ("ocultos",      "attrib:H size:>500mb",                  "Ocultos"),
    ("recentes",     "dm:lastweek size:>100mb",               "Recentes"),
    ("antigos",      "dm:<2020 size:>500mb",                  "Antigos"),
    ("dup_video",    "video: dupe:size;duration",             "Videos duplicados"),
    ("dup_imagem",   "image: dupe:name;size",                 "Imagens duplicadas"),
    ("dup_audio",    "audio: dupe:size;duration",             "Audio duplicado"),
    ("dup_pdf",      "ext:pdf dupe:name;size",                "PDFs duplicados"),
    ("lixo_tmp",     "ext:tmp;temp;bak;old size:>10mb",       "Temporarios"),
]


def detetar_drives():
    drives = []
    for l in "CDEFGHIJKLMNOPQRSTUVWXYZ":
        if os.path.isdir(f"{l}:\\"):
            drives.append(f"{l}:\\")
    return drives


def correr(drives, top, quiet=False):
    garantir_dirs()
    ev = Everything()
    if ev.disponivel:
        fonte = "SDK"
    elif os.path.isfile(r"C:\ACERVO\bin\es.exe"):
        fonte = "es.exe (fallback)"
    else:
        print("[ERRO] Nem SDK nem es.exe disponiveis.")
        print("      Confirma que:")
        print("        1) Everything GUI esta a correr")
        print("        2) C:\\ACERVO\\bin\\SDK\\Everything64.dll existe")
        return None

    banner("ANALISE TOTAL", f"Fonte: {fonte}  |  Drives: {', '.join(drives)}")

    resultados = []
    t0 = time.time()
    prog = Progress(len(ANALISES), prefix="Analises", ativo=not quiet)

    for aid, query, desc in ANALISES:
        prog.update(0, sufixo=f"-> {aid}")
        t1 = time.time()
        todos = []
        for drive in drives:
            items = ev.search(f"{drive} {query}", limit=top)
            todos.extend(items)
        todos.sort(key=lambda x: -x["tamanho"])
        todos = todos[:top]
        tam = sum(i["tamanho"] for i in todos)
        resultados.append({
            "id": aid, "descricao": desc, "query": query,
            "total": len(todos), "tamanho": tam,
            "tempo": time.time() - t1, "items": todos,
        })
        prog.update(1, sufixo=f"{aid}: {len(todos)} ({humano(tam)})")

    prog.done()

    if not quiet:
        print()
        banner("RESUMO", f"Tempo total: {time.time()-t0:.2f}s")
        print(f"  {'ID':<15} {'TOTAL':>8} {'TAMANHO':>14} {'TEMPO':>8}  DESCRICAO")
        print("  " + "-" * 88)
        tot_b = 0
        for r in resultados:
            tot_b += r["tamanho"]
            print(f"  {r['id']:<15} {r['total']:>8} {humano(r['tamanho']):>14} "
                  f"{r['tempo']:>7.2f}s  {r['descricao']}")
        print("  " + "-" * 88)
        print(f"  {'TOTAL':<15} {sum(r['total'] for r in resultados):>8} "
              f"{humano(tot_b):>14}")
        print("=" * 92)

    ts = timestamp()
    for r in resultados:
        gravar_csv(os.path.join(DIR_CSV, f"{r['id']}_{ts}.csv"), r["items"])
    gravar_json(os.path.join(DIR_JSON, f"analise_{ts}.json"), {
        "data": agora(), "drives": drives, "fonte": fonte,
        "categorias": resultados,
    })
    exportar(resultados, os.path.join(DIR_YAML, "analise"), formato="yaml",
             meta={"drives": drives, "fonte": fonte})

    print(f"\n  [OK] CSV:  {DIR_CSV}")
    print(f"  [OK] JSON: {DIR_JSON}")
    print(f"  [OK] YAML: {DIR_YAML}")

    ev.cleanup()
    return resultados


def main():
    p = argparse.ArgumentParser(description="Analise total")
    p.add_argument("--drives", nargs="*", help="Drives (default: todos)")
    p.add_argument("--top", type=int, default=30)
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args()

    drives = args.drives if args.drives else detetar_drives()
    drives = [d if d.endswith("\\") else d + "\\" for d in drives]
    correr(drives, args.top, args.quiet)


if __name__ == "__main__":
    main()

