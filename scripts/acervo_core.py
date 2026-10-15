# -*- coding: utf-8 -*-
"""
acervo_core.py - Biblioteca central do ACERVO
==============================================
Funcoes reutilizaveis por todos os scripts.
- Definicao de tipos e regras
- Filtros combinados (rank, prof, tamanho, ext, regex)
- Utils (humano, hash, paths, logs)
- Regras de higienizacao (o que e lixo vs original)
"""
import os
import re
import csv
import json
import time
import hashlib
from datetime import datetime
from collections import defaultdict

# ============================================================
# PATHS PADRAO
# ============================================================
RAIZ        = r"C:\ACERVO"
ENTRADA_CSV = r"C:\ACERVO\logs\pipeline_v5\TODOS_NORMALIZADOS.csv"
DIR_LOGS    = r"C:\ACERVO\logs"
DIR_INV     = os.path.join(DIR_LOGS, "inventario")
DIR_FILTROS = os.path.join(DIR_LOGS, "filtros")
DIR_RELAT   = os.path.join(DIR_LOGS, "relatorios")
DIR_SNAP    = os.path.join(DIR_LOGS, "snapshots")
DIR_QUAR    = r"C:\ACERVO\quarentena"
DIR_MANIF   = r"C:\ACERVO\manifests"
DIR_BACKUP  = r"C:\ACERVO\backups"

# ============================================================
# TIPOS VALIDOS + REGRAS
# ============================================================
TIPOS = [
    "database", "video", "excel", "audio", "word", "pdf",
    "imagem", "json", "texto", "yaml", "csv", "markdown",
]

# Extensoes por tipo (para filtros)
EXTS = {
    "database": [".db", ".sqlite", ".sqlite3", ".mdb", ".accdb"],
    "video":    [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
    "excel":    [".xls", ".xlsx", ".xlsm", ".ods"],
    "audio":    [".mp3", ".flac", ".wav", ".aac", ".m4a", ".ogg", ".wma"],
    "word":     [".doc", ".docx", ".odt", ".rtf"],
    "pdf":      [".pdf"],
    "imagem":   [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg", ".heic"],
    "json":     [".json", ".jsonl", ".ndjson"],
    "texto":    [".txt", ".log", ".nfo", ".ini", ".cfg", ".conf"],
    "yaml":     [".yaml", ".yml"],
    "csv":      [".csv", ".tsv"],
    "markdown": [".md", ".markdown", ".mdx"],
}

# Regex heuristicas por tipo (para agrupar variantes)
HEURISTICAS = {
    "video":    [r"^(.*?)[. _\-](?:S\d{2}E\d{2})",           # series S01E01
                 r"^(.*?)[. _\-](?:1080p|720p|4K|2160p)",     # resolucao
                 r"^(.*?)[. _\-](?:x264|x265|HEVC|AVC)"],     # codec
    "imagem":   [r"^(.*?)[. _\-](?:IMG|DSC|PXL)[_\-]?\d+",    # fotos camera
                 r"^(.*?)[. _\-](\d{4})[. _\-](\d{2})[. _\-](\d{2})"],  # datas
    "audio":    [r"^(.*?)[. _\-]\d{2}[. _\-]",                # 01 - Track
                 r"^(.*?)[. _\-](?:feat|ft)\."],              # feat.
    "markdown": [r"^(.*?)[. _\-](?:README|CHANGELOG|LICENSE|TODO)"],
    "pdf":      [r"^(.*?)[. _\-](?:v\d+|final|draft|copy)"],
}

# Ficheiros de sistema/lixo (NUNCA higienizar)
PROTEGIDOS = {
    "thumbs.db", "desktop.ini", ".ds_store", "icon\r",
    ".gitignore", ".gitkeep", "readme.md",
}

# Padroes de lixo (candidatos a quarentena)
LIXO_PADROES = [
    r"^~\$",              # temporarios Office
    r"\.tmp$",            # temporarios
    r"\.crdownload$",     # Chrome downloads
    r"\.part$",           # downloads parciais
    r"^\._",              # macOS metadata
    r"\.bak$",            # backups automaticos
    r"\.old$",            # ficheiros antigos
    r"^\$",               # ficheiros especiais
]


# ============================================================
# UTILS
# ============================================================
def humano(b):
    """Converte bytes para formato legivel."""
    if b is None:
        return "—"
    neg = b < 0
    b = abs(b)
    for u in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if b < 1024:
            s = f"{b:.2f} {u}"
            return f"-{s}" if neg else s
        b /= 1024
    return f"{b:.2f} EB"


def agora_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def garantir_dirs():
    """Cria todas as pastas necessarias."""
    for d in [DIR_INV, DIR_FILTROS, DIR_RELAT, DIR_SNAP,
              DIR_QUAR, DIR_MANIF, DIR_BACKUP]:
        os.makedirs(d, exist_ok=True)


def hash_ficheiro(caminho, bloco=65536):
    """SHA-256 duma parte do ficheiro (rapido)."""
    h = hashlib.sha256()
    try:
        with open(caminho, "rb") as f:
            h.update(f.read(bloco))
            try:
                f.seek(-bloco, 2)
                h.update(f.read(bloco))
            except OSError:
                pass
        return h.hexdigest()[:16]
    except (OSError, PermissionError):
        return None


def e_lixo(nome):
    """Verifica se um nome corresponde a padrao de lixo."""
    nome_lower = nome.lower()
    if nome_lower in PROTEGIDOS:
        return False
    for padrao in LIXO_PADROES:
        if re.search(padrao, nome, re.IGNORECASE):
            return True
    return False


def e_protegido(nome):
    return nome.lower() in PROTEGIDOS


# ============================================================
# FILTROS COMBINADOS
# ============================================================
class Filtro:
    """Filtro combinado por tipo, rank, prof, tamanho, ext, regex."""
    def __init__(self, tipo=None, rank_max=None, rank_min=None,
                 prof_max=None, tam_min=None, tam_max=None,
                 ext=None, regex=None, nome_contem=None):
        self.tipo = tipo
        self.rank_max = rank_max
        self.rank_min = rank_min
        self.prof_max = prof_max
        self.tam_min = tam_min
        self.tam_max = tam_max
        self.ext = [e.lower() for e in ext] if ext else None
        self.regex = re.compile(regex, re.IGNORECASE) if regex else None
        self.nome_contem = nome_contem.lower() if nome_contem else None

    def aceita(self, reg):
        """Retorna True se o registo passa o filtro."""
        if self.tipo and reg.get("tipo") != self.tipo:
            return False
        if self.rank_max is not None and reg.get("rank", 3) > self.rank_max:
            return False
        if self.rank_min is not None and reg.get("rank", 3) < self.rank_min:
            return False
        if self.prof_max is not None and reg.get("prof", 0) > self.prof_max:
            return False
        tam = reg.get("tamanho", 0)
        if self.tam_min is not None and tam < self.tam_min:
            return False
        if self.tam_max is not None and tam > self.tam_max:
            return False
        if self.ext:
            e = (reg.get("ext") or "").lower()
            if not e.startswith("."):
                e = "." + e
            if e not in self.ext:
                return False
        if self.nome_contem and self.nome_contem not in reg.get("nome", "").lower():
            return False
        if self.regex and not self.regex.search(reg.get("nome", "")):
            return False
        return True

    def descricao(self):
        partes = []
        if self.tipo: partes.append(f"tipo={self.tipo}")
        if self.rank_max is not None: partes.append(f"rank<={self.rank_max}")
        if self.rank_min is not None: partes.append(f"rank>={self.rank_min}")
        if self.prof_max is not None: partes.append(f"prof<={self.prof_max}")
        if self.tam_min: partes.append(f"tam>={humano(self.tam_min)}")
        if self.tam_max: partes.append(f"tam<={humano(self.tam_max)}")
        if self.ext: partes.append(f"ext={','.join(self.ext)}")
        if self.nome_contem: partes.append(f"nome~{self.nome_contem}")
        if self.regex: partes.append(f"regex={self.regex.pattern}")
        return " | ".join(partes) if partes else "(sem filtro)"


# ============================================================
# I/O
# ============================================================
def carregar_csv(filtro=None, limite=None, verbose=True):
    """Carrega registos do CSV, aplicando filtro opcional."""
    if not os.path.isfile(ENTRADA_CSV):
        print(f"[ERRO] CSV nao existe: {ENTRADA_CSV}")
        return []

    regs = []
    t0 = time.time()
    with open(ENTRADA_CSV, "r", encoding="utf-8", errors="replace", newline="") as f:
        r = csv.DictReader(f)
        for i, row in enumerate(r):
            try:
                tam = int(row.get("tamanho", 0))
            except (ValueError, TypeError):
                continue
            if tam <= 0:
                continue
            reg = {
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
            }
            if filtro and not filtro.aceita(reg):
                continue
            regs.append(reg)
            if limite and len(regs) >= limite:
                break

    if verbose:
        print(f"  Carregados: {len(regs):,}  ({time.time()-t0:.2f}s)")
    return regs


def gravar_csv(caminho, registos, campos=None):
    """Grava lista de dicts em CSV."""
    if not registos:
        with open(caminho, "w", encoding="utf-8", newline="") as f:
            f.write("")
        return

    if not campos:
        campos = ["origem", "tipo", "nome", "caminho", "tamanho",
                  "stem", "ext", "mime", "categoria", "rank", "prof",
                  "grau", "score"]

    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for r in registos:
            w.writerow({k: r.get(k, "") for k in campos})


def gravar_json(caminho, obj):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


# ============================================================
# SEGREGACAO
# ============================================================
def segregar(regs, chave_fn=None):
    """
    Separa originais de duplicados.
    chave_fn: funcao que extrai a chave de agrupamento.
             default = (stem, tamanho, ext)
    """
    if chave_fn is None:
        def chave_fn(r):
            return (r["stem"].lower(), r["tamanho"], (r["ext"] or "").lower())

    grupos = defaultdict(list)
    for r in regs:
        grupos[chave_fn(r)].append(r)

    originais = []
    duplicados = []
    for chave, grupo in grupos.items():
        if len(grupo) == 1:
            originais.append(grupo[0])
            continue
        grupo.sort(key=lambda x: (x["rank"], x["prof"], x["caminho"], x["nome"]))
        orig = grupo[0]
        orig["grau"] = "ORIGINAL"
        orig["score"] = 100
        originais.append(orig)
        for d in grupo[1:]:
            d["grau"] = "DUPLICADO"
            d["score"] = 85
            duplicados.append(d)

    return originais, duplicados, len(grupos)


# ============================================================
# HEURISTICAS
# ============================================================
def extrair_grupo_heuristica(nome, tipo):
    """Extrai prefixo heuristico para agrupar variantes."""
    padroes = HEURISTICAS.get(tipo, [])
    nome_base = os.path.splitext(nome)[0]
    for padrao in padroes:
        m = re.search(padrao, nome_base, re.IGNORECASE)
        if m:
            return m.group(1).strip().lower()
    return None


def agrupar_por_heuristica(regs, tipo):
    """Agrupa registos por prefixo heuristico."""
    grupos = defaultdict(list)
    for r in regs:
        prefixo = extrair_grupo_heuristica(r["nome"], tipo)
        if prefixo:
            grupos[prefixo].append(r)
    return grupos
