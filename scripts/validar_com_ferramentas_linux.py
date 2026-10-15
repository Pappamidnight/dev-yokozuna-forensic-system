#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validar_com_ferramentas_linux.py
Integra fdupes, rdfind e rmlint (via WSL) na validacao cruzada forense.
Nao apaga ficheiros: gera relatorios de auditoria e valida os candidatos a duplicados.
"""

import sys
import subprocess
import json
from pathlib import Path

DISTRO = "Ubuntu-26.04"
BASE = Path(r"C:\ACERVO")
LOGS = BASE / "logs" / "deduplicado"

def converter_caminho_wsl(win_path):
    p = str(win_path).replace("\\", "/")
    if len(p) >= 2 and p[1] == ":":
        drive = p[0].lower()
        return f"/mnt/{drive}{p[2:]}"
    return p

def auditar_com_fdupes(pasta_alvo):
    wsl_path = converter_caminho_wsl(pasta_alvo)
    cmd = ["wsl", "-d", DISTRO, "--", "fdupes", "-r", "-q", "-S", wsl_path]
    print(f"[INFO] A executar fdupes em {pasta_alvo}...")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return res.stdout
    except Exception as e:
        return f"[ERRO] fdupes: {e}"

def auditar_com_rdfind(pasta_alvo, output_txt):
    wsl_path = converter_caminho_wsl(pasta_alvo)
    wsl_out = converter_caminho_wsl(output_txt)
    # rdfind em modo dry-run / makehardlinks false
    cmd = ["wsl", "-d", DISTRO, "--", "rdfind", "-dryrun", "true", "-outputname", wsl_out, wsl_path]
    print(f"[INFO] A executar rdfind (dry-run) em {pasta_alvo}...")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return res.stdout
    except Exception as e:
        return f"[ERRO] rdfind: {e}"

def auditar_com_rmlint(pasta_alvo, output_json):
    wsl_path = converter_caminho_wsl(pasta_alvo)
    wsl_out = converter_caminho_wsl(output_json)
    # rmlint gera script e json de analise sem executar remocao
    cmd = ["wsl", "-d", DISTRO, "--", "rmlint", "-o", f"json:{wsl_out}", wsl_path]
    print(f"[INFO] A executar rmlint em {pasta_alvo}...")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return res.stdout
    except Exception as e:
        return f"[ERRO] rmlint: {e}"

def main():
    if len(sys.argv) < 2:
        print("Uso: python validar_com_ferramentas_linux.py <pasta_alvo>")
        print("Exemplo: python validar_com_ferramentas_linux.py C:\\ACERVO\\storage")
        sys.exit(1)

    pasta = Path(sys.argv[1])
    if not pasta.exists():
        print(f"[ERRO] Pasta nao encontrada: {pasta}")
        sys.exit(1)

    print("=" * 70)
    print("  ACERVO V8 - AUDITORIA FORENSE CRUZADA (fdupes / rdfind / rmlint)")
    print(f"  Pasta Alvo: {pasta}")
    print("=" * 70)

    out_dir = LOGS / "auditoria_linux"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. fdupes
    log_fdupes = out_dir / "fdupes_report.txt"
    out_fdupes = auditar_com_fdupes(pasta)
    log_fdupes.write_text(out_fdupes, encoding="utf-8")
    print(f"  [OK] Relatorio fdupes gerado: {log_fdupes.name}")

    # 2. rdfind
    log_rdfind = out_dir / "rdfind_results.txt"
    auditar_com_rdfind(pasta, log_rdfind)
    print(f"  [OK] Relatorio rdfind gerado: {log_rdfind.name}")

    # 3. rmlint
    log_rmlint = out_dir / "rmlint.json"
    auditar_com_rmlint(pasta, log_rmlint)
    print(f"  [OK] Relatorio rmlint gerado: {log_rmlint.name}")

    print("=" * 70)
    print("[CONCLUIDO] Validacao forense tripla concluida em modo READ-ONLY.")
    print("=" * 70)

if __name__ == "__main__":
    main()
