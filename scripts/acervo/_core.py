# -*- coding: utf-8 -*-
r"""
_core.py - Biblioteca central do ACERVO (es.exe prioritario)
=============================================================
Fonte de dados: es.exe (funciona sempre com instancia correta).
SDK e opcional; nao bloqueia se falhar.
"""
import os
import sys
import time
import json
import csv
import subprocess
import ctypes
from ctypes import c_uint32, c_uint64, c_bool, c_wchar_p, POINTER
from datetime import datetime, timedelta

# ============================================================
# CONFIGURACAO
# ============================================================
ES_EXE = r"C:\ACERVO\bin\es.exe"
DLL_SDK = r"C:\ACERVO\bin\SDK\Everything64.dll"
INSTANCIA = "1.5a"  # substituido no setup

DIR_LOGS = r"C:\ACERVO\logs\acervo"
DIR_CSV = os.path.join(DIR_LOGS, "csv")
DIR_JSON = os.path.join(DIR_LOGS, "json")
DIR_YAML = os.path.join(DIR_LOGS, "yaml")
DIR_RELAT = os.path.join(DIR_LOGS, "relatorios")


# ============================================================
# UTILS
# ============================================================
def humano(b):
    for u in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if b < 1024:
            return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} EB"


def agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def garantir_dirs():
    for d in [DIR_LOGS, DIR_CSV, DIR_JSON, DIR_YAML, DIR_RELAT]:
        os.makedirs(d, exist_ok=True)


def filetime_to_dt(ft):
    if not ft:
        return None
    try:
        return datetime(1601, 1, 1) + timedelta(microseconds=ft // 10)
    except (OverflowError, OSError):
        return None


def banner(titulo, subtitulo=""):
    print()
    print("=" * 92)
    print(f"  {titulo}")
    if subtitulo:
        print(f"  {subtitulo}")
    print("=" * 92)


# ============================================================
# PROGRESS BAR
# ============================================================
class Progress:
    def __init__(self, total, prefix="", width=40, ativo=True):
        self.total = max(1, total)
        self.atual = 0
        self.prefix = prefix
        self.width = width
        self.t0 = time.time()
        self.ativo = ativo

    def update(self, n=1, sufixo=""):
        if not self.ativo:
            self.atual += n
            return
        self.atual = min(self.atual + n, self.total)
        pct = 100 * self.atual / self.total
        preenchido = int(self.width * self.atual / self.total)
        barra = "=" * preenchido + "-" * (self.width - preenchido)
        tempo = time.time() - self.t0
        eta = (tempo / self.atual) * (self.total - self.atual) if self.atual else 0
        linha = (f"\r  {self.prefix} [{barra}] {self.atual}/{self.total} "
                 f"({pct:5.1f}%) ETA {eta:5.1f}s {sufixo}")
        sys.stdout.write(linha[:200])
        sys.stdout.flush()

    def done(self, sufixo=""):
        if self.ativo:
            sys.stdout.write("\r" + " " * 200 + "\r")
            sys.stdout.flush()
            print(f"  {self.prefix} OK  ({self.total} em {time.time()-self.t0:.2f}s) {sufixo}")


# ============================================================
# ES.EXE WRAPPER (motor principal)
# ============================================================
class Everything:
    def __init__(self, instancia=None):
        self.instancia = instancia if instancia is not None else INSTANCIA
        self.instancia = self.instancia.strip()
        self.disponivel = os.path.isfile(ES_EXE)

    def search(self, query, limit=0, sort=None, match_case=False, regex=False):
        if not self.disponivel:
            return []
        args = [ES_EXE, "-no-header", "-json"]
        if self.instancia:
            args += ["-instance", self.instancia]
        if limit > 0:
            args += ["-n", str(limit)]
        if match_case:
            args.append("-i")
        if regex:
            args.append("-r")
        if sort:
            args += ["-sort", sort]
        args.extend(query.split())
        try:
            r = subprocess.run(args, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=300)
            if r.returncode != 0 or not r.stdout.strip():
                return []
            dados = json.loads(r.stdout)
            if isinstance(dados, dict):
                dados = [dados]
            res = []
            for item in dados:
                if not isinstance(item, dict):
                    continue
                nome = item.get("filename", item.get("name", ""))
                try:
                    tam = int(item.get("size", 0))
                except (ValueError, TypeError):
                    tam = 0
                res.append({
                    "caminho": nome,
                    "nome": os.path.basename(nome),
                    "tamanho": tam,
                    "tamanho_humano": humano(tam),
                    "dm": None, "dc": None,
                    "ext": os.path.splitext(nome)[1],
                    "atrib": 0,
                    "e_file": True,
                })
            return res
        except Exception:
            return []

    def count(self, query):
        if not self.disponivel:
            return 0
        args = [ES_EXE, "-no-header", "-get-result-count"]
        if self.instancia:
            args += ["-instance", self.instancia]
        args.extend(query.split())
        try:
            r = subprocess.run(args, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=60)
            if r.returncode != 0 or not r.stdout.strip():
                return 0
            return int(r.stdout.strip().split()[0])
        except Exception:
            return 0

    def cleanup(self):
        pass


# ============================================================
# OUTPUTS
# ============================================================
def gravar_csv(caminho, items, campos=None):
    if not campos:
        campos = ["caminho", "nome", "tamanho", "tamanho_humano", "ext"]
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for i in items:
            w.writerow({k: i.get(k, "") for k in campos})


def gravar_json(caminho, obj):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=str)


def gravar_yaml(caminho, obj):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    try:
        import yaml
        with open(caminho, "w", encoding="utf-8") as f:
            yaml.safe_dump(obj, f, allow_unicode=True, sort_keys=False)
    except ImportError:
        with open(caminho, "w", encoding="utf-8") as f:
            f.write("# (sem modulo yaml instalado)\n")
            f.write(json.dumps(obj, indent=2, ensure_ascii=False, default=str))

# ============================================================
# COMPATIBILIDADE (funcao usada por duplicados.py)
# ============================================================
def everything_a_correr():
    """Sempre True — es.exe e a fonte."""
    return True

def obter_instancia():
    """Retorna a instancia configurada."""
    return INSTANCIA



