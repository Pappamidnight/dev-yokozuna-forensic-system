"""Classificador de arvores de projeto (ficheiros + pastas)."""
from __future__ import annotations
import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path


# ============================================================
# REGRAS
# ============================================================

EXTENSOES_CODIGO = {
    "py", "pyi", "rs", "js", "ts", "tsx", "jsx",
    "ps1", "psm1", "bat", "cmd", "sh", "bash",
    "c", "cpp", "h", "hpp", "cs", "java", "go", "rb", "php",
    "sql", "html", "css", "scss", "vue", "svelte",
}
EXTENSOES_DADOS = {
    "json", "csv", "tsv", "parquet", "db", "sqlite", "sqlite3",
    "xlsx", "xls", "ods", "xml", "yaml", "yml", "toml", "ini",
}
EXTENSOES_DOCS = {"md", "txt", "rst", "adoc", "pdf", "docx", "doc", "odt", "rtf"}
EXTENSOES_CONFIG = {"gitignore", "env", "editorconfig", "dockerignore"}
EXTENSOES_INTEGRIDADE = {"sha256", "sha1", "sha512", "md5", "sfv", "asc", "sig"}
EXTENSOES_MIDIA = {
    "png", "jpg", "jpeg", "gif", "svg", "webp", "ico", "bmp", "tiff",
    "mp3", "wav", "flac", "m4a", "ogg", "opus",
    "mp4", "mkv", "mov", "avi", "webm",
}
EXTENSOES_COMPRIMIDOS = {"zip", "tar", "gz", "7z", "rar", "bz2", "xz"}

FUNCAO_PATTERNS = {
    "analise":       [r"^analyze_", r"^detect_", r"^inspect_", r"^diagnose_"],
    "geracao":       [r"^generate_", r"^create_", r"^build_", r"^init_", r"^make_"],
    "validacao":     [r"^validate_", r"^test_", r"^check_", r"^verify_"],
    "sincronizacao": [r"^sync_", r"^merge_", r"^dedup", r"^consolidat"],
    "simulacao":     [r"^dry_run", r"^dryrun", r"^simulat"],
    "povoamento":    [r"^populate_", r"^deep_", r"^exhaustively_"],
    "reset":         [r"^reset_", r"^clean_", r"^wipe_"],
    "orquestracao":  [r"^orquestr", r"^run_", r"^start_", r"^pipeline"],
    "exportacao":    [r"^export_", r"^dump_", r"^extract_"],
    "importacao":    [r"^import_", r"^load_", r"^ingest_"],
}

DOMINIO_PATTERNS = {
    "LEA": ["lea", "lisbon experience", "filipe delgado", "teresa", "vanda",
            "white nest", "parreiras", "heaven", "sky family"],
    "SPARK": ["spark", "sparkgest", "finpartner", "celtis",
              "six sigma", "scrum", "psm", "cfa"],
    "CASO_15547": ["15547", "refutacao", "provas_15547", "forense"],
    "LEGAL_AI": ["legalai", "legal_ai", "legal_core", "legal_hub"],
}

DOC_SUBCATEGORIA = {
    "governanca":     [r"^CIRCUITO_", r"^MANIFESTO_", r"^POLITICA_"],
    "relatorio":      [r"^DOSSIER_", r"^RELATORIO_", r"^REPORT_"],
    "contexto":       [r"^CONTEXT", r"^README", r"^CLAUDE", r"^AGENTS"],
    "acompanhamento": [r"^CHANGELOG", r"^TODO", r"^ROADMAP", r"^NOTES"],
}

DADOS_SUBCATEGORIA = {
    "custodia":    [r"^MANIFESTO_", r"^CUSTODIA", r"^custodia"],
    "golden":      [r"^FROZEN_", r"^GOLDEN_", r"^golden_"],
    "integridade": [r"HASHES", r"CHECKSUMS", r"checksums", r"hashes"],
    "inventario":  [r"inventory", r"inventario", r"catalog"],
}

PASTA_TIPO = {
    "codigo":     {"src", "backend", "bin", "tools", "lib", "app"},
    "testes":     {"tests", "test", "evals", "spec", "specs"},
    "dados":      {"data", "exports", "backups", "backup", "fixtures"},
    "docs":       {"docs", "documentation", "manuals"},
    "infra":      {"docker", "docker_legal_master_vault", "k8s", "terraform"},
    "config":     {"config", "configs", "settings", ".github"},
    "artefactos": {"dist", "build", "target", "out", "__pycache__", ".venv"},
}

MODULO_POR_EXT = {
    "py": "python", "pyi": "python", "rs": "rust",
    "ps1": "powershell", "psm1": "powershell",
    "bat": "batch", "cmd": "batch",
    "sh": "shell", "bash": "shell",
    "js": "javascript", "ts": "typescript", "tsx": "typescript",
    "jsx": "javascript", "go": "go", "rb": "ruby", "php": "php",
    "java": "java", "cs": "csharp", "c": "c", "cpp": "cpp",
    "h": "c", "hpp": "cpp", "sql": "sql", "html": "html", "css": "css",
}


# ============================================================
# MODELO
# ============================================================

@dataclass
class Classificacao:
    path: str
    nome: str
    extensao: str
    e_pasta: bool
    tipo: str = "outros"
    funcao: str = ""
    dominio: str = ""
    subcategoria: str = ""
    modulo: str = ""
    tamanho: int = 0
    data_modificacao: str = ""
    projeto: str = ""
    pasta_pai: str = ""
    profundidade: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================
# CLASSIFICADOR
# ============================================================

class ClassificadorArvore:
    def __init__(self, projeto: str = ""):
        self.projeto = projeto

    @staticmethod
    def _ext(nome: str) -> str:
        return nome.rsplit(".", 1)[-1].lower() if "." in nome else ""

    @staticmethod
    def _match(patterns: list[str], texto: str) -> str:
        t = texto.lower()
        for p in patterns:
            if re.search(p, t, re.IGNORECASE):
                return p
        return ""

    def _tipo(self, path: Path, e_pasta: bool) -> str:
        if e_pasta:
            n = path.name.lower()
            for tipo, nomes in PASTA_TIPO.items():
                if n in nomes:
                    return f"pasta_{tipo}"
            if n.startswith("docker"):
                return "pasta_infra"
            if n.endswith("_rust"):
                return "pasta_modulo_rust"
            if re.search(r"_v\d+$", n):
                return "pasta_modulo_versionado"
            if n.startswith("obsidian"):
                return "pasta_integracao"
            return "pasta_outros"

        ext = self._ext(path.name)
        nome = path.name.lower()
        if ext in EXTENSOES_CODIGO: return "codigo"
        if ext in EXTENSOES_DADOS: return "dados"
        if ext in EXTENSOES_DOCS: return "docs"
        if ext in EXTENSOES_INTEGRIDADE: return "integridade"
        if ext in EXTENSOES_MIDIA: return "midia"
        if ext in EXTENSOES_COMPRIMIDOS: return "comprimido"
        if nome in EXTENSOES_CONFIG: return "config"
        if nome in {"requirements.txt", "pyproject.toml", "package.json",
                    "cargo.toml", "go.mod", "composer.json"}: return "config"
        return "outros"

    def _funcao(self, path: Path) -> str:
        if path.is_dir(): return ""
        for f, pats in FUNCAO_PATTERNS.items():
            if self._match(pats, path.stem): return f
        return ""

    def _dominio(self, path: Path) -> str:
        texto = str(path).lower()
        for d, keys in DOMINIO_PATTERNS.items():
            for k in keys:
                if k in texto: return d
        return ""

    def _subcategoria(self, path: Path, tipo: str) -> str:
        if path.is_dir(): return ""
        if tipo == "docs":
            for s, pats in DOC_SUBCATEGORIA.items():
                if self._match(pats, path.stem): return s
        if tipo == "dados":
            for s, pats in DADOS_SUBCATEGORIA.items():
                if self._match(pats, path.stem): return s
        return ""

    def _modulo(self, path: Path) -> str:
        if path.is_dir(): return ""
        return MODULO_POR_EXT.get(self._ext(path.name), "")

    def classificar(self, path: Path) -> Classificacao:
        e_pasta = path.is_dir()
        c = Classificacao(
            path=str(path), nome=path.name,
            extensao="" if e_pasta else self._ext(path.name),
            e_pasta=e_pasta, projeto=self.projeto,
            pasta_pai=str(path.parent), profundidade=len(path.parts),
        )
        c.tipo = self._tipo(path, e_pasta)
        c.funcao = self._funcao(path)
        c.dominio = self._dominio(path)
        c.subcategoria = self._subcategoria(path, c.tipo)
        c.modulo = self._modulo(path)
        if not e_pasta:
            try:
                st = path.stat()
                c.tamanho = st.st_size
                c.data_modificacao = datetime.fromtimestamp(
                    st.st_mtime).isoformat(timespec="seconds")
            except OSError:
                pass
        return c

    def classificar_arvore(self, raiz: Path, recursivo: bool = True) -> list[Classificacao]:
        raiz = Path(raiz)
        itens: list[Classificacao] = []
        for p in (raiz.rglob("*") if recursivo else raiz.iterdir()):
            itens.append(self.classificar(p))
        return itens

    @staticmethod
    def resumo(classificacoes: list[Classificacao]) -> dict:
        r = {
            "total": len(classificacoes),
            "por_tipo": {}, "por_funcao": {}, "por_dominio": {},
            "por_subcategoria": {}, "por_modulo": {}, "por_extensao": {},
            "espaco_total": 0,
        }
        for c in classificacoes:
            r["por_tipo"][c.tipo] = r["por_tipo"].get(c.tipo, 0) + 1
            if c.funcao: r["por_funcao"][c.funcao] = r["por_funcao"].get(c.funcao, 0) + 1
            if c.dominio: r["por_dominio"][c.dominio] = r["por_dominio"].get(c.dominio, 0) + 1
            if c.subcategoria: r["por_subcategoria"][c.subcategoria] = r["por_subcategoria"].get(c.subcategoria, 0) + 1
            if c.modulo: r["por_modulo"][c.modulo] = r["por_modulo"].get(c.modulo, 0) + 1
            if c.extensao: r["por_extensao"][c.extensao] = r["por_extensao"].get(c.extensao, 0) + 1
            r["espaco_total"] += c.tamanho
        return r

    @staticmethod
    def guardar_json(classificacoes: list[Classificacao], destino: Path) -> Path:
        destino.parent.mkdir(parents=True, exist_ok=True)
        dados = {
            "data": datetime.now().isoformat(timespec="seconds"),
            "total": len(classificacoes),
            "resumo": ClassificadorArvore.resumo(classificacoes),
            "itens": [c.to_dict() for c in classificacoes],
        }
        destino.write_text(
            json.dumps(dados, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return destino

    @staticmethod
    def guardar_html(classificacoes: list[Classificacao], destino: Path) -> Path:
        resumo = ClassificadorArvore.resumo(classificacoes)
        destino.parent.mkdir(parents=True, exist_ok=True)

        def _tabela(nome: str, dic: dict, limite: int = 20) -> str:
            itens = sorted(dic.items(), key=lambda x: -x[1])[:limite]
            rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in itens)
            return f'<h2>{nome}</h2><table><thead><tr><th>Chave</th><th>Total</th></tr></thead><tbody>{rows}</tbody></table>'

        cards = "".join(
            f'<div class="card"><div class="v">{v}</div><div class="l">{k}</div></div>'
            for k, v in sorted(resumo["por_tipo"].items(), key=lambda x: -x[1])
        )

        html = f"""<!DOCTYPE html>
<html lang="pt"><head><meta charset="utf-8">
<title>ACERVO — Classificacao</title>
<style>
:root{{--bg:#0f172a;--fg:#e2e8f0;--card:#1e293b;--accent:#38bdf8}}
body{{font-family:system-ui;background:var(--bg);color:var(--fg);margin:0;padding:2em}}
h1{{color:var(--accent)}} h2{{color:var(--accent);border-bottom:1px solid #334155;padding-bottom:.4em}}
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:1em;margin-bottom:2em}}
.card{{background:var(--card);border-radius:10px;padding:1.5em;text-align:center;border:1px solid #334155}}
.card .v{{font-size:2.2em;font-weight:bold;color:var(--accent)}}
.card .l{{color:#94a3b8;font-size:.9em;margin-top:.4em}}
table{{border-collapse:collapse;width:100%;margin-bottom:1.5em;background:var(--card);border-radius:8px;overflow:hidden}}
th,td{{padding:.6em 1em;text-align:left;border-bottom:1px solid #334155}}
th{{background:#0b1220;color:var(--accent)}}
footer{{color:#64748b;text-align:center;padding:2em;font-size:.85em}}
</style></head><body>
<h1>ACERVO — Classificacao de Arvore</h1>
<p>Gerado: {datetime.now():%Y-%m-%d %H:%M:%S}</p>
<div class="cards">{cards}</div>
{_tabela("Por Tipo", resumo["por_tipo"])}
{_tabela("Por Funcao", resumo["por_funcao"])}
{_tabela("Por Dominio", resumo["por_dominio"])}
{_tabela("Por Subcategoria", resumo["por_subcategoria"])}
{_tabela("Por Modulo", resumo["por_modulo"])}
{_tabela("Por Extensao", resumo["por_extensao"])}
<footer>ACERVO v6.0 — Classificador de Arvore</footer>
</body></html>"""
        destino.write_text(html, encoding="utf-8")
        return destino
