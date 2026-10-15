#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validacao_cruzada_tripla.py
Modulo de Validacao Cruzada Forense: rmlint + fdupes + rdfind.
Garante Modo DRY-RUN OBRIGATORIO por defeito (ACERVO_MODE=DRYRUN).
Compara resultados das 3 ferramentas antes de qualquer decisao.
Acao executada durante DRYRUN: rigorosamente NENHUMA.
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime

DISTRO = "Ubuntu-26.04"
BASE_DIR = Path(r"C:\ACERVO")
LOGS_DIR = BASE_DIR / "logs" / "deduplicado"

EXTENSOES_MAP = {
    "database": "db,sqlite,mdb,accdb",
    "video":    "mp4,mkv,avi,mov,wmv",
    "excel":    "xls,xlsx,xlsm",
    "audio":    "mp3,wav,flac,m4a,aac",
    "word":     "doc,docx",
    "pdf":      "pdf",
    "imagem":   "jpg,jpeg,png,gif,webp,bmp,tiff",
    "json":     "json",
    "texto":    "txt",
    "yaml":     "yml,yaml",
    "csv":      "csv",
    "markdown": "md"
}

def to_wsl_path(win_path):
    p = str(win_path).replace("\\", "/")
    if len(p) >= 2 and p[1] == ":":
        drive = p[0].lower()
        return f"/mnt/{drive}{p[2:]}"
    return p

def executar_wsl(comando):
    cmd = ["wsl", "-d", DISTRO, "--", "bash", "-c", comando]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        return res.returncode, res.stdout, res.stderr
    except Exception as e:
        return 1, "", str(e)

def parse_rmlint_json(json_path):
    """Extrai originais e duplicados do output do rmlint."""
    originais = 0
    duplicados = 0
    bytes_recuperaveis = 0
    if not json_path.exists():
        return originais, duplicados, bytes_recuperaveis

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("[") or line.startswith("]"):
                    continue
                if line.endswith(","):
                    line = line[:-1]
                try:
                    obj = json.loads(line)
                    if obj.get("is_original") is True:
                        originais += 1
                    elif obj.get("is_duplicate") is True:
                        duplicados += 1
                        bytes_recuperaveis += obj.get("size", 0)
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return originais, duplicados, bytes_recuperaveis

def parse_rdfind_txt(txt_path):
    """Conta duplicados detetados pelo rdfind (results.txt)."""
    dups = 0
    if not txt_path.exists():
        return dups
    try:
        with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue
                partes = line.split()
                if len(partes) >= 2 and partes[0] == "DUPTYPE_FIRST_OCCURRENCE":
                    pass
                elif len(partes) >= 2 and "DUPTYPE" in partes[0]:
                    dups += 1
    except Exception:
        pass
    return dups

def parse_fdupes_txt(txt_path):
    """Conta ficheiros duplicados no relatorio fdupes."""
    dups = 0
    grupos = 0
    if not txt_path.exists():
        return grupos, dups
    try:
        with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
            linhas_grupo = 0
            for line in f:
                line = line.strip()
                if not line:
                    if linhas_grupo > 1:
                        grupos += 1
                        dups += (linhas_grupo - 1)
                    linhas_grupo = 0
                else:
                    linhas_grupo += 1
            if linhas_grupo > 1:
                grupos += 1
                dups += (linhas_grupo - 1)
    except Exception:
        pass
    return grupos, dups

def validar_cruzada(tipo, pasta_alvo_win):
    modo = os.environ.get("ACERVO_MODE", "DRYRUN").upper()
    pasta_tipo = LOGS_DIR / tipo
    pasta_tipo.mkdir(parents=True, exist_ok=True)

    out_rmlint_json = pasta_tipo / f"rmlint_{tipo}.json"
    out_rmlint_sh   = pasta_tipo / f"rmlint_{tipo}.sh"
    out_rdfind_txt  = pasta_tipo / f"rdfind_{tipo}_results.txt"
    out_fdupes_txt  = pasta_tipo / f"fdupes_{tipo}.txt"
    resumo_cruzado  = pasta_tipo / f"resumo_cruzado_{tipo}.json"

    wsl_alvo = to_wsl_path(pasta_alvo_win)
    exts = EXTENSOES_MAP.get(tipo, tipo)

    print("=" * 70)
    print(f"  VALIDACAO CRUZADA FORENSE V8: [{tipo.upper()}]")
    print(f"  Modo Operacional:  {modo}")
    print(f"  Diretorio Alvo:    {pasta_alvo_win}")
    print(f"  Acao Executada:    NENHUMA (DRY-RUN ESTREITO)")
    print("=" * 70)

    # 1. Execucao rmlint
    print("[1/3] A executar rmlint (hashing progressivo)...")
    cmd_rmlint = f"rmlint '{wsl_alvo}' --types={exts} -o json:'{to_wsl_path(out_rmlint_json)}' -o sh:'{to_wsl_path(out_rmlint_sh)}'"
    executar_wsl(cmd_rmlint)
    rm_orig, rm_dups, rm_bytes = parse_rmlint_json(out_rmlint_json)
    print(f"      rmlint: {rm_orig} originais | {rm_dups} duplicados")

    # 2. Execucao rdfind (dryrun=true)
    print("[2/3] A executar rdfind (dry-run)...")
    cmd_rdfind = f"rdfind -dryrun true -outputname '{to_wsl_path(out_rdfind_txt)}' '{wsl_alvo}'"
    executar_wsl(cmd_rdfind)
    rdfind_dups = parse_rdfind_txt(out_rdfind_txt)
    print(f"      rdfind: {rdfind_dups} duplicados detetados")

    # 3. Execucao fdupes (-r -f, apenas relatorio)
    print("[3/3] A executar fdupes (relatorio apenas)...")
    cmd_fdupes = f"fdupes -r -f '{wsl_alvo}' > '{to_wsl_path(out_fdupes_txt)}'"
    executar_wsl(cmd_fdupes)
    fdupes_grupos, fdupes_dups = parse_fdupes_txt(out_fdupes_txt)
    print(f"      fdupes: {fdupes_grupos} grupos | {fdupes_dups} duplicados")

    gb_recuperaveis = round(rm_bytes / (1024**3), 2)

    # Coerencia entre as ferramentas
    convergencia = False
    if rm_dups > 0 and (rdfind_dups > 0 or fdupes_dups > 0):
        convergencia = True
    elif rm_dups == 0 and rdfind_dups == 0 and fdupes_dups == 0:
        convergencia = True

    estado = "OK" if convergencia else "DIVERGENCIA"

    dados_resumo = {
        "modo": modo,
        "estado": estado,
        "tipo": tipo,
        "timestamp": datetime.now().isoformat(),
        "ferramentas": {
            "rmlint": {
                "originais": rm_orig,
                "duplicados": rm_dups,
                "bytes_recuperaveis": rm_bytes
            },
            "rdfind": {
                "duplicados": rdfind_dups
            },
            "fdupes": {
                "grupos": fdupes_grupos,
                "duplicados": fdupes_dups
            }
        },
        "espaco_recuperavel_gb": gb_recuperaveis,
        "convergencia_cruzada": convergencia,
        "acao_executada": "NENHUMA",
        "ficheiros_movidos": 0,
        "ficheiros_apagados": 0
    }

    with open(resumo_cruzado, "w", encoding="utf-8") as f:
        json.dump(dados_resumo, f, indent=2, ensure_ascii=False)

    print("-" * 70)
    print(f"  Convergencia Cruzada:  {convergencia}")
    print(f"  Espaco Recuperavel:    {gb_recuperaveis} GB")
    print(f"  Estado Final:          {estado}")
    print(f"  Relatorio:             {resumo_cruzado.name}")
    print("=" * 70)

    if estado != "OK":
        print("[BLOQUEADO] Falha na convergencia cruzada das 3 ferramentas.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python validacao_cruzada_tripla.py <tipo> <pasta_alvo_win>")
        print("Exemplo: python validacao_cruzada_tripla.py database C:\\ACERVO\\storage")
        sys.exit(1)
    validar_cruzada(sys.argv[1].lower(), sys.argv[2])
