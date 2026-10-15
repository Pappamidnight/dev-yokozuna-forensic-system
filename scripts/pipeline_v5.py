# -*- coding: utf-8 -*-
"""
Pipeline V5 - Classificacao + Normalizacao + Filtros Multi-Cruzados
- 21 combinacoes de filtros
- Classificacao MIME completa
- Normalizacao de nomes
- Cruzamento storage <-> gdrive
- Simulacao DRY-RUN
"""
import os
import csv
import json
import time
import re
import hashlib
from collections import defaultdict
from datetime import datetime

STORAGE = r"C:\ACERVO\storage\files"
GDRIVE  = r"C:\ACERVO\logs\google_drive\por_tipo"
SEG_V4  = r"C:\ACERVO\logs\google_drive\segregado_v4"
DEST    = r"C:\ACERVO\logs\pipeline_v5"
os.makedirs(DEST, exist_ok=True)

TIPOS = ["database","video","excel","audio","word","pdf",
         "imagem","json","texto","yaml","csv","markdown"]

# ============================================================
# MAPA MIME COMPLETO
# ============================================================
MIME_MAP = {
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".odt": "application/vnd.oasis.opendocument.text",
    ".rtf": "application/rtf",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".xlsm": "application/vnd.ms-excel.sheet.macroEnabled.12",
    ".csv": "text/csv",
    ".json": "application/json",
    ".yaml": "application/x-yaml",
    ".yml": "application/x-yaml",
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".webp": "image/webp",
    ".tiff": "image/tiff",
    ".svg": "image/svg+xml",
    ".heic": "image/heic",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".flac": "audio/flac",
    ".m4a": "audio/mp4",
    ".aac": "audio/aac",
    ".ogg": "audio/ogg",
    ".mp4": "video/mp4",
    ".mkv": "video/x-matroska",
    ".avi": "video/x-msvideo",
    ".mov": "video/quicktime",
    ".wmv": "video/x-ms-wmv",
    ".flv": "video/x-flv",
    ".webm": "video/webm",
    ".db": "application/x-sqlite3",
    ".sqlite": "application/x-sqlite3",
    ".mdb": "application/x-msaccess",
}

# Categorias MIME
CATEGORIAS = {
    "documento": ["application/pdf", "application/msword", "application/vnd.openxmlformats"],
    "planilha": [".xls", ".xlsx", ".csv"],
    "texto": ["text/plain", "text/markdown"],
    "dados": ["application/json", "application/x-yaml", "application/x-sqlite3"],
    "imagem": ["image/"],
    "audio": ["audio/"],
    "video": ["video/"],
}

def categorizar_mime(mime):
    for cat, mimes in CATEGORIAS.items():
        for m in mimes:
            if mime.startswith(m):
                return cat
    return "outros"

# ============================================================
# NORMALIZACAO
# ============================================================
RE_SUF = re.compile(
    r"(?:[\s_\-]+(?:copy|copia|cópia|final|finalizado|v\d+|versao\d*|backup|bkp|old|antigo|novo|new|bak|tmp|temp))+\s*$",
    re.IGNORECASE
)
RE_PAREN = re.compile(r"[\s_\-]*\(\d+\)\s*$")
RE_BRACK = re.compile(r"[\s_\-]*\[\d+\]\s*$")
RE_DATA = re.compile(r"(19|20)\d{2}[\-_]?\d{2}[\-_]?\d{2}")
RE_MULTI = re.compile(r"[\s_\-]+")

def normalizar_nome(nome):
    """Normalizacao completa de nome."""
    stem, ext = os.path.splitext(str(nome))
    ext = ext.lower()
    # Remover sufixos em loop
    for _ in range(3):
        novo = RE_SUF.sub("", stem).strip()
        if novo == stem:
            break
        stem = novo
    stem = RE_PAREN.sub("", stem)
    stem = RE_BRACK.sub("", stem)
    stem = RE_DATA.sub("", stem)
    # Normalizar separadores
    stem = RE_MULTI.sub(" ", stem).strip().lower()
    return stem, ext

def profundidade(c):
    return c.count("\\")

def rank_caminho(c):
    c = c.lower()
    if "o meu disco" in c:
        return 0
    if "outros computadores" in c:
        return 1
    if "storage" in c:
        return 2
    return 3

def mime_de(nome, ext):
    ext = ext.lower()
    if ext in MIME_MAP:
        return MIME_MAP[ext]
    return "application/octet-stream"

# ============================================================
# CARREGAR
# ============================================================
def carregar_storage():
    print("[1/6] A carregar C:\\ACERVO\\storage\\files...")
    t0 = time.time()
    regs = []
    if not os.path.isdir(STORAGE):
        print(f"  [ERRO] {STORAGE} nao existe")
        return regs
    for root, _, files in os.walk(STORAGE):
        for f in files:
            p = os.path.join(root, f)
            try:
                st = os.stat(p)
                stem, ext = normalizar_nome(f)
                regs.append({
                    "origem": "STORAGE",
                    "nome": f,
                    "caminho": p,
                    "tamanho": st.st_size,
                    "stem": stem,
                    "ext": ext,
                    "tipo": "outros",
                    "mime": mime_de(f, ext),
                    "rank": rank_caminho(p),
                    "prof": profundidade(p),
                })
            except Exception:
                continue
    print(f"  Total: {len(regs):,} em {time.time()-t0:.2f}s")
    return regs

def carregar_gdrive():
    print("[2/6] A carregar Google Drive...")
    t0 = time.time()
    regs = []
    for tipo in TIPOS:
        p = os.path.join(GDRIVE, f"{tipo}.csv")
        if not os.path.isfile(p):
            continue
        with open(p, "r", encoding="utf-8", errors="replace", newline="") as f:
            r = csv.reader(f)
            header = next(r, None)
            idx = {h.lower(): i for i, h in enumerate(header)} if header else {}
            i_nome = idx.get("nome", 0)
            i_cam  = idx.get("caminho", 1)
            i_tam  = idx.get("tamanho", 2)
            i_dat  = idx.get("datamod", 3)
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
                stem, ext = normalizar_nome(nome)
                regs.append({
                    "origem": "GDRIVE",
                    "tipo": tipo,
                    "nome": nome,
                    "caminho": caminho,
                    "tamanho": tam,
                    "data_mod": row[i_dat] if len(row) > i_dat else "",
                    "stem": stem,
                    "ext": ext,
                    "mime": mime_de(nome, ext),
                    "rank": rank_caminho(caminho),
                    "prof": profundidade(caminho),
                })
    print(f"  Total: {len(regs):,} em {time.time()-t0:.2f}s")
    return regs

# ============================================================
# 21 FILTROS/COMBINACOES
# ============================================================
FILTROS = [
    # (nome, funcao_chave)
    ("F01_nome_tam",           lambda r: (r["nome"].lower(), r["tamanho"])),
    ("F02_stem_tam",           lambda r: (r["stem"], r["tamanho"])),
    ("F03_stem_tam_ext",       lambda r: (r["stem"], r["tamanho"], r["ext"])),
    ("F04_stem_tam_tipo",      lambda r: (r["stem"], r["tamanho"], r.get("tipo", ""))),
    ("F05_stem_tam_mime",      lambda r: (r["stem"], r["tamanho"], r["mime"])),
    ("F06_stem_tam_rank",      lambda r: (r["stem"], r["tamanho"], r["rank"])),
    ("F07_nome_tam_ext",       lambda r: (r["nome"].lower(), r["tamanho"], r["ext"])),
    ("F08_stem_ext",           lambda r: (r["stem"], r["ext"])),
    ("F09_stem",               lambda r: (r["stem"],)),
    ("F10_tam",                lambda r: (r["tamanho"],)),
    ("F11_ext_tam",            lambda r: (r["ext"], r["tamanho"])),
    ("F12_mime_tam",           lambda r: (r["mime"], r["tamanho"])),
    ("F13_stem_tam_data",      lambda r: (r["stem"], r["tamanho"], r.get("data_mod", ""))),
    ("F14_stem_tam_rank_prof", lambda r: (r["stem"], r["tamanho"], r["rank"], r["prof"])),
    ("F15_caminho_exato",      lambda r: (r["caminho"].lower(),)),
    ("F16_caminho_nome",       lambda r: (r["caminho"].lower(), r["nome"].lower())),
    ("F17_stem_num",           lambda r: (r["stem"], re.sub(r"\d+", "#", r["nome"]))),
    ("F18_palavras",           lambda r: (tuple(sorted(set(r["stem"].split()))), r["tamanho"])),
    ("F19_letras",             lambda r: (re.sub(r"[^a-z]", "", r["stem"]), r["tamanho"])),
    ("F20_hash_tam",           lambda r: (r.get("hash", ""), r["tamanho"])),
    ("F21_nome_sem_num",       lambda r: (re.sub(r"\d+", "", r["nome"].lower()), r["tamanho"])),
]

def aplicar_filtro(regs, chave_fn):
    grupos = defaultdict(list)
    for r in regs:
        try:
            grupos[chave_fn(r)].append(r)
        except Exception:
            continue
    orig = 0
    dup = 0
    bytes_dup = 0
    for chave, grupo in grupos.items():
        if len(grupo) == 1:
            orig += 1
            continue
        grupo.sort(key=lambda x: (x["rank"], x["prof"], x["caminho"], x["nome"]))
        orig += 1
        for d in grupo[1:]:
            dup += 1
            bytes_dup += d["tamanho"]
    return len(grupos), orig, dup, bytes_dup

# ============================================================
# CLASSIFICACAO
# ============================================================
def classificar(regs):
    print("[4/6] A classificar...")
    t0 = time.time()
    por_tipo = defaultdict(lambda: {"n": 0, "bytes": 0, "orig": 0, "dup": 0})
    por_mime = defaultdict(lambda: {"n": 0, "bytes": 0})
    por_cat = defaultdict(lambda: {"n": 0, "bytes": 0})
    por_origem = defaultdict(lambda: {"n": 0, "bytes": 0})

    # Classificar por categoria MIME
    for r in regs:
        mime = r["mime"]
        cat = categorizar_mime(mime)
        por_mime[mime]["n"] += 1
        por_mime[mime]["bytes"] += r["tamanho"]
        por_cat[cat]["n"] += 1
        por_cat[cat]["bytes"] += r["tamanho"]
        por_tipo[r.get("tipo", "outros")]["n"] += 1
        por_tipo[r.get("tipo", "outros")]["bytes"] += r["tamanho"]
        por_origem[r["origem"]]["n"] += 1
        por_origem[r["origem"]]["bytes"] += r["tamanho"]

    print(f"  Tempo: {time.time()-t0:.2f}s")
    return por_tipo, por_mime, por_cat, por_origem

# ============================================================
# MAIN
# ============================================================
def humano(b):
    for u in ["B","KB","MB","GB","TB"]:
        if b < 1024:
            return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} PB"

def main():
    t0 = time.time()
    print("=" * 78)
    print("  PIPELINE V5 - CLASSIFICACAO + NORMALIZACAO + 21 FILTROS")
    print("=" * 78)
    print()

    # Carregar
    storage = carregar_storage()
    gdrive = carregar_gdrive()
    print()

    todos = storage + gdrive
    print(f"[3/6] Total consolidado: {len(todos):,} registos")
    print()

    if not todos:
        print("  [ERRO] Nenhum registo!")
        return

    # ============================================================
    # APLICAR 21 FILTROS
    # ============================================================
    print("[3/6] A aplicar 21 filtros/combinações...")
    print()
    print("=" * 78)
    print(f"  {'Filtro':<28} {'Grupos':>10} {'Orig':>10} {'Dup':>10} {'%dup':>8} {'Bytes':>12}")
    print("=" * 78)

    resultados = {}
    for nome, chave_fn in FILTROS:
        t_f = time.time()
        grupos, orig, dup, bytes_dup = aplicar_filtro(todos, chave_fn)
        pct = (dup / (orig + dup) * 100) if (orig + dup) else 0
        dt = time.time() - t_f
        resultados[nome] = {
            "grupos": grupos,
            "orig": orig,
            "dup": dup,
            "pct_dup": round(pct, 2),
            "bytes_dup": bytes_dup,
            "tempo": round(dt, 2),
        }
        print(f"  {nome:<28} {grupos:>10,} {orig:>10,} {dup:>10,} {pct:>7.1f}% {humano(bytes_dup):>12}")
    print("=" * 78)
    print()

    # ============================================================
    # CLASSIFICACAO
    # ============================================================
    por_tipo, por_mime, por_cat, por_origem = classificar(todos)
    print()

    # ============================================================
    # GRAVAR RESULTADOS
    # ============================================================
    print("[5/6] A gravar resultados...")

    # 1. Todos os registos normalizados
    out_all = os.path.join(DEST, "TODOS_NORMALIZADOS.csv")
    with open(out_all, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["origem", "tipo", "nome", "caminho", "tamanho", "stem", "ext", "mime", "categoria", "rank", "prof"])
        for r in todos:
            cat = categorizar_mime(r["mime"])
            w.writerow([
                r["origem"], r.get("tipo", ""), r["nome"], r["caminho"],
                r["tamanho"], r["stem"], r["ext"], r["mime"], cat,
                r["rank"], r["prof"],
            ])
    print(f"  [OK] {out_all}")

    # 2. Por categoria MIME
    for cat in sorted(por_cat.keys()):
        cat_regs = [r for r in todos if categorizar_mime(r["mime"]) == cat]
        if not cat_regs:
            continue
        out_cat = os.path.join(DEST, f"categoria_{cat}.csv")
        with open(out_cat, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["origem", "tipo", "nome", "caminho", "tamanho", "mime"])
            for r in cat_regs:
                w.writerow([r["origem"], r.get("tipo", ""), r["nome"], r["caminho"], r["tamanho"], r["mime"]])
        print(f"  [OK] {out_cat} ({len(cat_regs):,})")

    # 3. Relatorio JSON
    rel = {
        "data": datetime.now().isoformat(),
        "versao": "v5",
        "total_registos": len(todos),
        "storage": {"n": len(storage), "bytes": sum(r["tamanho"] for r in storage)},
        "gdrive": {"n": len(gdrive), "bytes": sum(r["tamanho"] for r in gdrive)},
        "filtros": resultados,
        "por_tipo": dict(por_tipo),
        "por_mime": {k: dict(v) for k, v in por_mime.items()},
        "por_categoria": {k: dict(v) for k, v in por_cat.items()},
        "por_origem": {k: dict(v) for k, v in por_origem.items()},
        "ficheiros_alterados": 0,
    }
    out_rel = os.path.join(DEST, "relatorio_v5.json")
    with open(out_rel, "w", encoding="utf-8") as f:
        json.dump(rel, f, indent=2, ensure_ascii=False)
    print(f"  [OK] {out_rel}")

    # ============================================================
    # RESUMO FINAL
    # ============================================================
    print()
    print("=" * 78)
    print("  RESUMO FINAL (V5)")
    print("=" * 78)
    print(f"  Total registos: {len(todos):,}")
    print(f"  Storage: {len(storage):,}  ({humano(sum(r['tamanho'] for r in storage))})")
    print(f"  GDrive:  {len(gdrive):,}  ({humano(sum(r['tamanho'] for r in gdrive))})")
    print()
    print("  POR CATEGORIA MIME:")
    print("-" * 78)
    for cat in sorted(por_cat.keys(), key=lambda x: -por_cat[x]["n"]):
        d = por_cat[cat]
        print(f"  {cat:<15} {d['n']:>12,}  {humano(d['bytes']):>15}")
    print("-" * 78)
    print()
    print(f"  Tempo total: {time.time()-t0:.2f}s")
    print("=" * 78)

if __name__ == "__main__":
    main()
