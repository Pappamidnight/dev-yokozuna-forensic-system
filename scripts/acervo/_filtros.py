# -*- coding: utf-8 -*-
r"""
_filtros.py - Filtros combinados, regex, heuristica, dicionarios
================================================================
"""
import re
import os

# ============================================================
# TIPOS E EXTENSOES
# ============================================================
EXTS = {
    "database": [".db", ".sqlite", ".sqlite3", ".mdb"],
    "video":    [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm", ".m4v"],
    "excel":    [".xls", ".xlsx", ".xlsm", ".ods"],
    "audio":    [".mp3", ".flac", ".wav", ".aac", ".m4a", ".ogg"],
    "word":     [".doc", ".docx", ".odt", ".rtf"],
    "pdf":      [".pdf"],
    "imagem":   [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".heic"],
    "json":     [".json", ".jsonl", ".ndjson"],
    "texto":    [".txt", ".log", ".nfo", ".ini", ".cfg"],
    "yaml":     [".yaml", ".yml"],
    "csv":      [".csv", ".tsv"],
    "markdown": [".md", ".markdown"],
}

# ============================================================
# HEURISTICAS (regex para agrupar variantes)
# ============================================================
HEURISTICAS = {
    "video": [
        r"^(.*?)[. _\-](?:s\d{2}e\d{2})",       # series
        r"^(.*?)[. _\-](?:1080p|720p|4k|2160p)", # resolucao
        r"^(.*?)[. _\-](?:x264|x265|hevc)",       # codec
    ],
    "imagem": [
        r"^(.*?)[. _\-](?:img|dsc|pxl)[_\-]?\d+", # fotos
        r"^(.*?)[. _\-](\d{4})[. _\-](\d{2})[. _\-](\d{2})", # data
    ],
    "audio": [
        r"^(.*?)[. _\-]\d{2}[. _\-]",             # 01 - Track
        r"^(.*?)[. _\-](?:feat|ft)\.",            # feat.
    ],
    "pdf": [
        r"^(.*?)[. _\-](?:v\d+|final|draft)",     # versao
    ],
    "markdown": [
        r"^(.*?)[. _\-](?:readme|changelog|license|todo)",
    ],
}

# ============================================================
# DICIONARIOS DE SINONIMOS
# ============================================================
SINONIMOS = {
    "color":   ["colour", "cor", "cores", "colors"],
    "brasil":  ["brazil", "br"],
    "config":  ["configuration", "cfg", "settings"],
    "imagem":  ["image", "img", "picture", "photo"],
    "video":   ["movie", "film", "clip"],
    "documento": ["document", "doc", "file"],
    "manual":  ["guide", "handbook", "manual"],
    "temp":    ["temporario", "tmp", "temp"],
    "backup":  ["bk", "backup", "bkp"],
    "relatorio": ["report", "reports"],
}


# ============================================================
# REGEX PRE-CONSTRUIDAS
# ============================================================
REGEX = {
    "ano":          r"(?:19|20)\d{2}",
    "data_iso":     r"\d{4}-\d{2}-\d{2}",
    "data_br":      r"\d{2}[/-]\d{2}[/-]\d{4}",
    "hora":         r"\d{2}[:h]\d{2}",
    "serie":        r"[sS]\d{1,2}[eE]\d{1,2}",
    "versao":       r"v\d+(?:\.\d+)*",
    "email":        r"[\w.+-]+@[\w-]+\.[\w.-]+",
    "url":          r"https?://[^\s]+",
    "hash_md5":     r"[a-fA-F0-9]{32}",
    "hash_sha1":    r"[a-fA-F0-9]{40}",
    "hash_sha256":  r"[a-fA-F0-9]{64}",
    "uuid":         r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
    "copia":        r"(?:copia|copy|-\s*copy|\bcopy\b|\bc[oó]pia\b)",
    "final":        r"(?:final|vfinal|_final)",
    "backup":       r"(?:backup|bak|bkp)",
    "temp":         r"(?:temp|tmp|~)",
}


# ============================================================
# FILTRO COMBINADO
# ============================================================
class Filtro:
    def __init__(self, tipo=None, rank_max=None, rank_min=None,
                 prof_max=None, tam_min=None, tam_max=None,
                 ext=None, regex=None, nome_contem=None,
                 sinonimos=None, case_insensitive=True):
        self.tipo = tipo
        self.rank_max = rank_max
        self.rank_min = rank_min
        self.prof_max = prof_max
        self.tam_min = tam_min
        self.tam_max = tam_max
        self.ext = [e.lower() for e in ext] if ext else None
        flags = re.IGNORECASE if case_insensitive else 0
        self.regex = re.compile(regex, flags) if regex else None
        self.nome_contem = nome_contem.lower() if nome_contem else None
        self.sinonimos = sinonimos

    def _expandir_sinonimos(self, texto):
        """Expande texto com sinonimos."""
        if not self.sinonimos:
            return [texto]
        chave = texto.lower()
        if chave in SINONIMOS:
            return [texto] + SINONIMOS[chave]
        for base, alts in SINONIMOS.items():
            if chave in alts:
                return [texto, base] + alts
        return [texto]

    def aceita(self, reg):
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
        if self.nome_contem:
            nome = reg.get("nome", "").lower()
            variantes = self._expandir_sinonimos(self.nome_contem)
            if not any(v in nome for v in variantes):
                return False
        if self.regex and not self.regex.search(reg.get("nome", "")):
            return False
        return True

    def descricao(self):
        p = []
        if self.tipo: p.append(f"tipo={self.tipo}")
        if self.rank_max is not None: p.append(f"rank<={self.rank_max}")
        if self.tam_min: p.append(f"tam>={self.tam_min}")
        if self.tam_max: p.append(f"tam<={self.tam_max}")
        if self.ext: p.append(f"ext={','.join(self.ext)}")
        if self.regex: p.append(f"regex={self.regex.pattern}")
        if self.nome_contem: p.append(f"nome~{self.nome_contem}")
        return " | ".join(p) if p else "(sem filtro)"


# ============================================================
# HEURISTICA
# ============================================================
def extrair_prefixo(nome, tipo):
    padroes = HEURISTICAS.get(tipo, [])
    base = os.path.splitext(nome)[0]
    for p in padroes:
        m = re.search(p, base, re.IGNORECASE)
        if m:
            return m.group(1).strip().lower()
    return None


def agrupar_por_heuristica(items, tipo):
    from collections import defaultdict
    grupos = defaultdict(list)
    for r in items:
        prefixo = extrair_prefixo(r.get("nome", ""), tipo)
        if prefixo:
            grupos[prefixo].append(r)
    return grupos


# ============================================================
# HELPERS
# ============================================================
def testar_regex(texto, padrao):
    return bool(re.search(padrao, texto, re.IGNORECASE))


def listar_regex():
    for k, v in REGEX.items():
        print(f"  {k:<14} {v}")
