# -*- coding: utf-8 -*-
"""
desktop_scan_total.py - Scan TOTAL do Desktop com Everything
=============================================================
Enumera TUDO no Desktop usando es.exe com filtros combinados.
Produz: CSV por categoria + JSON + HTML + resumo no terminal.

Uso:
    python desktop_scan_total.py
    python desktop_scan_total.py --top 50
    python desktop_scan_total.py --so-rapido
    python desktop_scan_total.py --desktop "C:\Users\Yokozuna\Desktop"
"""
import os
import sys
import csv
import json
import time
import shutil
import argparse
import subprocess
import concurrent.futures
from datetime import datetime


# ============================================================
# CONFIG
# ============================================================
DIR_LOGS  = r"C:\ACERVO\logs\desktop_scan"
DIR_RELAT = r"C:\ACERVO\logs\relatorios"
DIR_CSV   = os.path.join(DIR_LOGS, "csv")
DIR_JSON  = os.path.join(DIR_LOGS, "json")

CANDIDATOS_ES = [
    r"C:\ACERVO\bin\es.exe",
    r"C:\Program Files\Everything\es.exe",
    r"C:\Program Files (x86)\Everything\es.exe",
    r"C:\Tools\es.exe",
]

# ============================================================
# CATEGORIAS — filtros combinados (usam sintaxe Everything)
# ============================================================
CATEGORIAS = [
    # ---------- POR TAMANHO ----------
    ("tam_1gb",        "size:>1gb",                                            "Ficheiros > 1 GB"),
    ("tam_500mb_1gb",  "size:>500mb size:<1gb",                                "500 MB a 1 GB"),
    ("tam_100mb_500mb","size:>100mb size:<500mb",                              "100 MB a 500 MB"),
    ("tam_10mb_100mb", "size:>10mb size:<100mb",                               "10 MB a 100 MB"),

    # ---------- POR TIPO + TAMANHO ----------
    ("video_grande",   "video: size:>100mb",                                   "Videos > 100 MB"),
    ("video_4k",       "video: regex:2160p",                                   "Videos 4K"),
    ("video_1080p",    "video: regex:1080p",                                   "Videos 1080p"),
    ("audio_grande",   "audio: size:>20mb",                                    "Audio > 20 MB"),
    ("image_grande",   "image: size:>10mb",                                    "Imagens > 10 MB"),
    ("doc_grande",     "doc: size:>5mb",                                       "Documentos > 5 MB"),
    ("pdf_grande",     "ext:pdf size:>10mb",                                   "PDFs > 10 MB"),
    ("exe_grande",     "exe: size:>100mb",                                     "Executaveis > 100 MB"),
    ("zip_grande",     "ext:zip;rar;7z;tar;gz;iso size:>100mb",                "Arquivos > 100 MB"),
    ("codigo_grande",  "ext:py;rs;js;ts;cs;go;java;php;rb size:>100kb",        "Codigo > 100 KB"),

    # ---------- POR DATA ----------
    ("recentes_hoje",  "dm:today",                                             "Modificados hoje"),
    ("recentes_sem",   "dm:lastweek",                                          "Modificados esta semana"),
    ("recentes_mes",   "dm:thismonth",                                         "Modificados este mes"),
    ("antigos_2020",   "dm:<2020 size:>100mb",                                 "Antigos (>2020) > 100 MB"),
    ("criados_hoje",   "dc:today",                                             "Criados hoje"),

    # ---------- POR ATRIBUTO ----------
    ("ocultos",        "attrib:H",                                             "Ficheiros ocultos"),
    ("sistema",        "attrib:S",                                             "Ficheiros de sistema"),
    ("readonly",       "attrib:R",                                             "Somente leitura"),
    ("encriptados",    "attrib:E",                                             "Encriptados"),
    ("comprimidos",    "attrib:C",                                             "Comprimidos NTFS"),

    # ---------- DUPLICADOS ----------
    ("dup_nome",       "dupe:name",                                            "Duplicados por nome"),
    ("dup_tamanho",    "dupe:size",                                            "Duplicados por tamanho"),
    ("dup_nome_size",  "dupe:name;size",                                       "Duplicados nome+tamanho"),
    ("dup_pdf",        "ext:pdf dupe:name;size",                               "PDFs duplicados"),
    ("dup_video",      "video: dupe:size",                                     "Videos duplicados"),
    ("dup_image",      "image: dupe:name;size",                                "Imagens duplicadas"),
    ("dup_audio",      "audio: dupe:size",                                     "Audio duplicado"),

    # ---------- LIXO ----------
    ("lixo_tmp",       "ext:tmp;temp;bak;old",                                 "Temporarios/backup"),
    ("lixo_download",  "ext:crdownload;part",                                  "Downloads incompletos"),
    ("lixo_vazio",     "size:0",                                               "Ficheiros vazios"),
    ("lixo_thumbs",    "name:Thumbs.db;desktop.ini",                           "Thumbs/desktop.ini"),

    # ---------- ESPECIFICOS DO DESKTOP ----------
    ("pasta_scan",     "regex:^_SCAN|^_OUTPUT|^_MATRIZ|^_CONSOLIDADO",         "Pastas de scan"),
    ("pasta_copia",    "regex:C[oó]pia|\\s-\\sCopy|_bak|_old",                 "Pastas/ficheiros copia"),
    ("pasta_backup",   "regex:_backup|_BACKUP",                                "Pastas backup"),
    ("pasta_vazia",    "empty:",                                               "Pastas vazias"),
    ("json_grandes",   "ext:json size:>1mb",                                   "JSONs > 1 MB"),
    ("md_todos",       "ext:md",                                               "Todos os markdown"),
    ("log_todos",      "ext:log",                                              "Todos os logs"),
    ("notas",          "ext:txt;md;rtf",                                       "Notas/documentos"),
]


# ============================================================
# DETECAO ES
# ============================================================
def detectar_es():
    es = shutil.which("es.exe") or shutil.which("es")
    if es:
        return es
    for c in CANDIDATOS_ES:
        if os.path.isfile(c):
            return c
    return None


def garantir_dirs():
    for d in [DIR_LOGS, DIR_RELAT, DIR_CSV, DIR_JSON]:
        os.makedirs(d, exist_ok=True)


# ============================================================
# ES.EXE
# ============================================================
def correr_es(es_path, args, timeout=300):
    try:
        r = subprocess.run(
            [es_path] + args,
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            timeout=timeout, check=False,
        )
        return r.stdout, r.returncode
    except subprocess.TimeoutExpired:
        return "", -1
    except Exception as e:
        return str(e), -2


def query_es(es_path, query, desktop, top=200):
    """Corre query dentro do Desktop."""
    full_query = f'"{desktop}" {query}'

    args = ["-no-header", "-json", "-n", str(top), full_query]
    out, rc = correr_es(es_path, args)

    if rc != 0 or not out.strip():
        return []

    try:
        dados = json.loads(out)
        if isinstance(dados, dict):
            dados = [dados]
        if not isinstance(dados, list):
            return []
    except json.JSONDecodeError:
        return []

    resultado = []
    for item in dados:
        if not isinstance(item, dict):
            continue
        nome = item.get("filename") or item.get("name") or ""
        if not nome:
            continue
        try:
            tam = int(item.get("size", 0))
        except (ValueError, TypeError):
            tam = 0
        dm = item.get("date_modified", "") or ""
        dc = item.get("date_created", "") or ""

        resultado.append({
            "caminho": nome,
            "nome": os.path.basename(nome),
            "tamanho": tam,
            "ext": os.path.splitext(nome)[1].lower(),
            "dm": dm,
            "dc": dc,
        })

    return resultado


# ============================================================
# ANALISE PARALELA
# ============================================================
def correr_categoria(es_path, cid, query, desc, desktop, top):
    t0 = time.time()
    try:
        items = query_es(es_path, query, desktop, top)
        return {
            "id": cid,
            "descricao": desc,
            "query": query,
            "total": len(items),
            "tempo": time.time() - t0,
            "items": items,
        }
    except Exception as e:
        return {
            "id": cid,
            "descricao": desc,
            "query": query,
            "total": 0,
            "tempo": time.time() - t0,
            "erro": str(e),
            "items": [],
        }


def humano(b):
    for u in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024:
            return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} PB"


def correr_tudo(es_path, desktop, top=200, so_rapido=False):
    print()
    print("=" * 100)
    print(f"  DESKTOP SCAN TOTAL  |  {desktop}")
    print(f"  Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)

    cats = CATEGORIAS
    if so_rapido:
        rapidas = {
            "tam_1gb", "tam_100mb_500mb",
            "video_grande", "image_grande", "doc_grande",
            "recentes_sem", "dup_nome_size", "lixo_tmp",
            "pasta_scan", "pasta_copia",
        }
        cats = [c for c in CATEGORIAS if c[0] in rapidas]

    print(f"  A correr {len(cats)} categorias (paralelo: 4 workers)...")
    print()

    resultados = []
    t0 = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futures = {
            ex.submit(correr_categoria, es_path, cid, q, d, desktop, top): cid
            for cid, q, d in cats
        }
        for fut in concurrent.futures.as_completed(futures):
            r = fut.result()
            resultados.append(r)
            status = "OK" if not r.get("erro") else "ERRO"
            print(f"  [{status:4}] {r['id']:<20} {r['total']:>6}  ({r['tempo']:.2f}s)")

    tempo_total = time.time() - t0

    # Ordenar pela ordem original
    ordem = {c[0]: i for i, c in enumerate(cats)}
    resultados.sort(key=lambda x: ordem.get(x["id"], 999))

    # RESUMO
    print()
    print("=" * 100)
    print(f"  RESUMO  |  Tempo total: {tempo_total:.2f}s")
    print("=" * 100)
    print(f"  {'ID':<22} {'TOTAL':>8} {'TAMANHO':>14}  DESCRICAO")
    print("  " + "-" * 94)

    total_bytes = 0
    total_itens = 0
    for r in resultados:
        tam = sum(i["tamanho"] for i in r["items"])
        total_bytes += tam
        total_itens += r["total"]
        print(f"  {r['id']:<22} {r['total']:>8} {humano(tam):>14}  {r['descricao']}")
    print("  " + "-" * 94)
    print(f"  {'TOTAL':<22} {total_itens:>8} {humano(total_bytes):>14}")
    print("=" * 100)

    return resultados, tempo_total


# ============================================================
# OUTPUTS
# ============================================================
def gravar_csvs(resultados):
    print()
    print("[CSV] A gravar...")
    for r in resultados:
        if not r["items"]:
            continue
        path = os.path.join(DIR_CSV, f"{r['id']}.csv")
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["caminho", "nome", "tamanho", "tamanho_humano",
                        "ext", "dm", "dc"])
            for item in sorted(r["items"], key=lambda x: -x["tamanho"]):
                w.writerow([
                    item["caminho"], item["nome"], item["tamanho"],
                    humano(item["tamanho"]), item["ext"],
                    item.get("dm", ""), item.get("dc", ""),
                ])
    print(f"  [OK] {len(resultados)} CSVs em {DIR_CSV}")


def gravar_json(resultados, desktop, tempo_total):
    path = os.path.join(DIR_JSON, f"desktop_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    dados = {
        "data": datetime.now().isoformat(),
        "desktop": desktop,
        "tempo_total_s": round(tempo_total, 2),
        "categorias": [],
    }
    for r in resultados:
        tam = sum(i["tamanho"] for i in r["items"])
        dados["categorias"].append({
            "id": r["id"],
            "descricao": r["descricao"],
            "query": r["query"],
            "total": r["total"],
            "tamanho_bytes": tam,
            "tamanho_humano": humano(tam),
            "tempo_s": round(r["tempo"], 2),
            "items": sorted(r["items"], key=lambda x: -x["tamanho"])[:100],
        })
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    print(f"  [OK] {path}")


def gravar_html(resultados, desktop, tempo_total):
    path = os.path.join(DIR_RELAT, f"desktop_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

    total_bytes = sum(sum(i["tamanho"] for i in r["items"]) for r in resultados)
    total_itens = sum(r["total"] for r in resultados)

    html = f"""<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<title>Desktop Scan — ACERVO</title>
<style>
:root {{ --bg:#0f172a; --fg:#e2e8f0; --card:#1e293b; --accent:#38bdf8; --border:#334155; }}
body {{ font-family: -apple-system, 'Segoe UI', system-ui, sans-serif;
        background: var(--bg); color: var(--fg); margin: 0; padding: 20px; }}
.container {{ max-width: 1600px; margin: 0 auto; }}
h1 {{ color: var(--accent); border-bottom: 3px solid var(--accent); padding-bottom: 10px; margin: 0 0 20px; }}
h2 {{ color: var(--accent); margin: 30px 0 15px; border-left: 4px solid var(--accent); padding-left: 12px; }}
.header {{ background: var(--card); border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 1px solid var(--border); }}
.header p {{ margin: 6px 0; color: #94a3b8; }}
.header strong {{ color: var(--fg); }}
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
.stat {{ background: var(--card); border-radius: 12px; padding: 20px; text-align: center; border: 1px solid var(--border); }}
.stat .valor {{ font-size: 32px; font-weight: bold; color: var(--accent); }}
.stat .label {{ color: #94a3b8; font-size: 13px; margin-top: 5px; }}
table {{ width: 100%; background: var(--card); border-radius: 12px; border-collapse: collapse; overflow: hidden; margin-bottom: 20px; border: 1px solid var(--border); }}
th {{ background: #0b1220; color: var(--accent); padding: 12px; text-align: left; font-weight: 600; font-size: 13px; }}
td {{ padding: 10px 12px; border-bottom: 1px solid var(--border); font-size: 13px; }}
tr:hover {{ background: #273549; }}
.mono {{ font-family: 'Consolas', monospace; font-size: 12px; color: #94a3b8; }}
.tag {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }}
.tag-ok {{ background: #064e3b; color: #6ee7b7; }}
.tag-warn {{ background: #78350f; color: #fcd34d; }}
.tag-dup {{ background: #7c2d12; color: #fdba74; }}
.tag-lixo {{ background: #7f1d1d; color: #fca5a5; }}
.footer {{ text-align: center; color: #64748b; margin-top: 40px; font-size: 12px; padding: 20px; }}
.search-hint {{ background: #1e293b; border-left: 3px solid var(--accent); padding: 10px 15px; border-radius: 6px; margin: 15px 0; font-family: monospace; font-size: 12px; color: #94a3b8; }}
</style>
</head>
<body>
<div class="container">

<h1>Desktop Scan — ACERVO</h1>

<div class="header">
<p><strong>Desktop:</strong> <span class="mono">{desktop}</span></p>
<p><strong>Data:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<p><strong>Tempo total:</strong> {tempo_total:.2f}s</p>
<p><strong>Categorias:</strong> {len(resultados)}</p>
</div>

<div class="stats">
<div class="stat"><div class="valor">{len(resultados)}</div><div class="label">Categorias</div></div>
<div class="stat"><div class="valor">{total_itens:,}</div><div class="label">Total resultados</div></div>
<div class="stat"><div class="valor">{humano(total_bytes)}</div><div class="label">Espaco total</div></div>
</div>

<h2>Resumo por categoria</h2>
<table>
<tr><th>Categoria</th><th>Descricao</th><th>Query</th><th>Total</th><th>Tamanho</th><th>Tempo</th></tr>
"""

    for r in resultados:
        tam = sum(i["tamanho"] for i in r["items"])
        tag_cls = "tag-ok"
        if "lixo" in r["id"]:
            tag_cls = "tag-lixo"
        elif "dup" in r["id"]:
            tag_cls = "tag-dup"
        elif "pasta" in r["id"]:
            tag_cls = "tag-warn"

        html += f"""<tr>
<td><span class="tag {tag_cls}">{r['id']}</span></td>
<td>{r['descricao']}</td>
<td class="mono">{r['query']}</td>
<td><strong>{r['total']:,}</strong></td>
<td>{humano(tam)}</td>
<td>{r['tempo']:.2f}s</td>
</tr>
"""
    html += "</table>"

    # Detalhe por categoria (só com resultados)
    for r in resultados:
        if not r["items"]:
            continue
        html += f"<h2>{r['id']} — {r['descricao']}</h2>"
        html += f"<div class='search-hint'>Query: {r['query']}</div>"
        html += """<table>
<tr><th>#</th><th>Tamanho</th><th>Nome</th><th>Caminho</th><th>Modificado</th></tr>
"""
        items = sorted(r["items"], key=lambda x: -x["tamanho"])[:30]
        for i, item in enumerate(items, 1):
            html += f"""<tr>
<td>{i}</td>
<td><strong>{humano(item['tamanho'])}</strong></td>
<td>{item['nome']}</td>
<td class="mono">{item['caminho']}</td>
<td class="mono">{item.get('dm','')}</td>
</tr>
"""
        html += "</table>"

    html += f"""<div class="footer">ACERVO Desktop Scan — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
</div>
</body>
</html>"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  [OK] {path}")


# ============================================================
# MAIN
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="Desktop Scan Total com Everything")
    parser.add_argument("--desktop", default=os.path.join(os.path.expanduser("~"), "Desktop"),
                        help="Pasta a analisar")
    parser.add_argument("--top", type=int, default=200, help="Top N por categoria")
    parser.add_argument("--so-rapido", action="store_true", help="Só categorias principais")
    args = parser.parse_args()

    garantir_dirs()

    es_path = detectar_es()
    if not es_path:
        print("[ERRO] es.exe nao encontrado.")
        print("      Descarrega: https://www.voidtools.com/downloads/#cli")
        print("      Coloca em C:\\ACERVO\\bin\\es.exe")
        sys.exit(1)
    print(f"[OK] es.exe: {es_path}")

    if not os.path.isdir(args.desktop):
        print(f"[ERRO] Desktop nao existe: {args.desktop}")
        sys.exit(1)
    print(f"[OK] Desktop: {args.desktop}")

    # Correr
    resultados, tempo = correr_tudo(es_path, args.desktop, args.top, args.so_rapido)

    # Gravar
    gravar_csvs(resultados)
    gravar_json(resultados, args.desktop, tempo)
    gravar_html(resultados, args.desktop, tempo)

    print()
    print("=" * 100)
    print("  CONCLUIDO")
    print("=" * 100)
    print(f"  CSV:  {DIR_CSV}")
    print(f"  JSON: {DIR_JSON}")
    print(f"  HTML: {DIR_RELAT}")
    print()


if __name__ == "__main__":
    main()
