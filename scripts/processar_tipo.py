# -*- coding: utf-8 -*-
"""
Processar 1 tipo de cada vez
Ordem: pdf, imagem, audio, video, excel, word, csv, md, json, texto, yaml, database, markdown
SEM hash. SEM conflitos de renomeacao.
Output: HTML originais + HTML duplicados
"""
import os
import sys
import csv
import json
import time
import re
from collections import defaultdict
from datetime import datetime

# ============================================================
# MAPA DE TIPOS
# ============================================================
TIPOS = {
    "pdf":      [".pdf"],
    "imagem":   [".jpg",".jpeg",".png",".gif",".bmp",".webp",".tiff",".tif",".svg",".heic"],
    "audio":    [".mp3",".wav",".flac",".m4a",".aac",".ogg"],
    "video":    [".mp4",".mkv",".avi",".mov",".wmv",".flv",".webm"],
    "excel":    [".xls",".xlsx",".xlsm",".xlsb"],
    "word":     [".doc",".docx",".odt",".rtf"],
    "csv":      [".csv"],
    "md":       [".md",".markdown"],
    "json":     [".json"],
    "texto":    [".txt"],
    "yaml":     [".yml",".yaml"],
    "database": [".db",".sqlite",".mdb",".accdb"],
}

ENTRADA = r"C:\ACERVO\logs\pipeline_v5\TODOS_NORMALIZADOS.csv"
REPORTS = r"C:\ACERVO\reports"

def humano(b):
    for u in ["B","KB","MB","GB","TB"]:
        if b < 1024:
            return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} PB"

def limpar_nome(nome):
    """Limpa nome para uso seguro em ficheiros."""
    stem = os.path.splitext(nome)[0]
    ext = os.path.splitext(nome)[1].lower()
    # Substituir caracteres problematicos
    stem = re.sub(r'[<>:"/\\|?*]', "_", stem)
    stem = re.sub(r"\s+", "_", stem.strip())
    stem = stem[:80]  # limite
    return stem, ext

def gerar_nome_unico(base, usados):
    """Gera nome unico, adicionando sufixo se necessario."""
    if base not in usados:
        usados.add(base)
        return base
    i = 2
    while f"{base}_{i}" in usados:
        i += 1
    novo = f"{base}_{i}"
    usados.add(novo)
    return novo

def main():
    if len(sys.argv) < 2:
        print("Uso: python processar_tipo.py <tipo>")
        print(f"Tipos: {', '.join(TIPOS.keys())}")
        sys.exit(1)

    tipo = sys.argv[1].lower()
    if tipo not in TIPOS:
        print(f"[ERRO] Tipo invalido: {tipo}")
        sys.exit(1)

    exts = TIPOS[tipo]
    t0 = time.time()

    print("=" * 78)
    print(f"  PROCESSAR TIPO: {tipo.upper()}")
    print("=" * 78)
    print()

    # ============================================================
    # 1. CARREGAR
    # ============================================================
    print(f"[1/4] A carregar {tipo}...")
    regs = []
    with open(ENTRADA, "r", encoding="utf-8", errors="replace", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            if row.get("ext", "").lower() not in exts:
                continue
            try:
                tam = int(row.get("tamanho", 0))
            except ValueError:
                continue
            if tam <= 0:
                continue
            regs.append({
                "nome": row.get("nome", ""),
                "caminho": row.get("caminho", ""),
                "tamanho": tam,
                "stem": row.get("stem", ""),
                "ext": row.get("ext", "").lower(),
                "data_mod": row.get("data_mod", ""),
                "rank": int(row.get("rank", 3)),
            })
    print(f"  Registos: {len(regs):,}")
    print()

    if not regs:
        print("[ERRO] Sem registos")
        return

    # ============================================================
    # 2. SEGREGAR (FILTRO DEDUP)
    # ============================================================
    print("[2/4] A segregar originais/duplicados...")
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
        # Ordenar por rank de custodia
        grupo.sort(key=lambda x: (x["rank"], x["caminho"]))
        originais.append(grupo[0])
        for d in grupo[1:]:
            d["duplicado_de"] = grupo[0]["nome"]
            duplicados.append(d)

    print(f"  Grupos:     {len(grupos):,}")
    print(f"  Originais:  {len(originais):,}")
    print(f"  Duplicados: {len(duplicados):,}")
    print()

    # ============================================================
    # 3. RENOMEAR (SEM CONFLITOS)
    # ============================================================
    print("[3/4] A renomear (sem conflitos)...")
    usados = set()
    for i, r in enumerate(originais, 1):
        base, ext = limpar_nome(r["nome"])
        # Formato: TIPO_ORDEM_base.ext
        nome_base = f"{tipo.upper()}_{i:05d}_{base}"
        nome_unico = gerar_nome_unico(nome_base, usados)
        r["nome_novo"] = f"{nome_unico}{ext}"
    for i, r in enumerate(duplicados, 1):
        base, ext = limpar_nome(r["nome"])
        nome_base = f"{tipo.upper()}_DUP_{i:05d}_{base}"
        nome_unico = gerar_nome_unico(nome_base, usados)
        r["nome_novo"] = f"{nome_unico}{ext}"
    print(f"  Nomes unicos: {len(usados):,}")
    print()

    # ============================================================
    # 4. GERAR HTML
    # ============================================================
    print("[4/4] A gerar HTML...")
    os.makedirs(REPORTS, exist_ok=True)

    # HTML ORIGINAIS
    html_orig = []
    html_orig.append('<!DOCTYPE html><html><head><meta charset="utf-8">')
    html_orig.append(f'<title>ORIGINAIS - {tipo.upper()}</title>')
    html_orig.append('<style>')
    html_orig.append('body{font-family:Consolas,monospace;background:#1e1e1e;color:#d4d4d4;padding:20px}')
    html_orig.append('h1{color:#4ec9b0;border-bottom:2px solid #4ec9b0}')
    html_orig.append('table{border-collapse:collapse;width:100%;margin:10px 0}')
    html_orig.append('th{background:#2d2d30;color:#4ec9b0;padding:8px;text-align:left;border:1px solid #3e3e42}')
    html_orig.append('td{padding:6px;border:1px solid #3e3e42}')
    html_orig.append('tr:nth-child(even){background:#252526}')
    html_orig.append('.orig{color:#4ec9b0;font-weight:bold}')
    html_orig.append('.info{background:#252526;padding:15px;border-left:4px solid #4ec9b0;margin:20px 0}')
    html_orig.append('</style></head><body>')
    html_orig.append(f'<h1>ORIGINAIS - {tipo.upper()} ({len(originais)})</h1>')
    html_orig.append('<div class="info">')
    html_orig.append(f'<div><strong>Data:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>')
    html_orig.append(f'<div><strong>Tipo:</strong> {tipo.upper()}</div>')
    html_orig.append(f'<div><strong>Total:</strong> {len(originais)}</div>')
    html_orig.append(f'<div><strong>Espaco:</strong> {humano(sum(r["tamanho"] for r in originais))}</div>')
    html_orig.append('</div>')
    html_orig.append('<table>')
    html_orig.append('<tr><th>#</th><th>Nome Original</th><th>Nome Novo</th><th>Caminho</th><th>Tamanho</th></tr>')
    for i, r in enumerate(sorted(originais, key=lambda x: x["nome_novo"]), 1):
        html_orig.append(f'<tr><td>{i}</td><td>{r["nome"]}</td><td class="orig">{r["nome_novo"]}</td><td>{r["caminho"][:80]}</td><td>{humano(r["tamanho"])}</td></tr>')
    html_orig.append('</table></body></html>')

    orig_path = os.path.join(REPORTS, f"originais_{tipo}.html")
    with open(orig_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_orig))
    print(f"  [OK] {orig_path}")

    # HTML DUPLICADOS
    html_dup = []
    html_dup.append('<!DOCTYPE html><html><head><meta charset="utf-8">')
    html_dup.append(f'<title>DUPLICADOS - {tipo.upper()}</title>')
    html_dup.append('<style>')
    html_dup.append('body{font-family:Consolas,monospace;background:#1e1e1e;color:#d4d4d4;padding:20px}')
    html_dup.append('h1{color:#f48771;border-bottom:2px solid #f48771}')
    html_dup.append('table{border-collapse:collapse;width:100%;margin:10px 0}')
    html_dup.append('th{background:#2d2d30;color:#f48771;padding:8px;text-align:left;border:1px solid #3e3e42}')
    html_dup.append('td{padding:6px;border:1px solid #3e3e42}')
    html_dup.append('tr:nth-child(even){background:#252526}')
    html_dup.append('.dup{color:#f48771;font-weight:bold}')
    html_dup.append('.info{background:#252526;padding:15px;border-left:4px solid #f48771;margin:20px 0}')
    html_dup.append('</style></head><body>')
    html_dup.append(f'<h1>DUPLICADOS - {tipo.upper()} ({len(duplicados)})</h1>')
    html_dup.append('<div class="info">')
    html_dup.append(f'<div><strong>Data:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>')
    html_dup.append(f'<div><strong>Tipo:</strong> {tipo.upper()}</div>')
    html_dup.append(f'<div><strong>Total:</strong> {len(duplicados)}</div>')
    html_dup.append(f'<div><strong>Espaco recuperavel:</strong> {humano(sum(r["tamanho"] for r in duplicados))}</div>')
    html_dup.append('</div>')
    html_dup.append('<table>')
    html_dup.append('<tr><th>#</th><th>Nome</th><th>Duplicado de</th><th>Caminho</th><th>Tamanho</th></tr>')
    for i, r in enumerate(sorted(duplicados, key=lambda x: x["nome"]), 1):
        html_dup.append(f'<tr><td>{i}</td><td class="dup">{r["nome"]}</td><td>{r.get("duplicado_de", "")}</td><td>{r["caminho"][:80]}</td><td>{humano(r["tamanho"])}</td></tr>')
    html_dup.append('</table></body></html>')

    dup_path = os.path.join(REPORTS, f"duplicados_{tipo}.html")
    with open(dup_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_dup))
    print(f"  [OK] {dup_path}")

    # ============================================================
    # RESUMO
    # ============================================================
    print()
    print("=" * 78)
    print(f"  FIM ACO-z - {tipo.upper()}")
    print("=" * 78)
    print(f"  Originais:   {len(originais):,}")
    print(f"  Duplicados:  {len(duplicados):,}")
    print(f"  Espaco:      {humano(sum(r['tamanho'] for r in duplicados))}")
    print(f"  Tempo:       {time.time()-t0:.2f}s")
    print("=" * 78)
    print()
    print(f"  HTML Originais:   {orig_path}")
    print(f"  HTML Duplicados:  {dup_path}")

if __name__ == "__main__":
    main()
