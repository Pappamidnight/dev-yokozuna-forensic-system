#!/usr/bin/env python3
"""
Diagnóstico Completo de Ambiente, Ferramentas, PATH, WSL, Bash e Pydantic AI.
(check_system_environment.py) - Enterprise Full Stack Check
"""
import os
import sys
import shutil
import sqlite3
import subprocess
import platform

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5, shell=True)
        return res.stdout.strip() if res.returncode == 0 else f"Erro ({res.returncode}): {res.stderr.strip()}"
    except Exception as exc:
        return f"Excecao: {exc}"

def check_pkg(pkg_name, import_name=None):
    imp = import_name or pkg_name
    try:
        mod = __import__(imp)
        ver = getattr(mod, "__version__", "OK")
        return f"{ver} (INSTALADO - OK)"
    except ImportError:
        return "NAO INSTALADO"

def main():
    print("==================================================================")
    print("DIAGNOSTICO COMPLETO DO ECOSSISTEMA FORENSE & DEV (YOKOZUNA)")
    print("==================================================================")

    # 1. Sistema Operativo
    print(f"\n[1] SISTEMA OPERATIVO & KERNEL:")
    print(f" - OS Platform : {platform.system()} {platform.release()} (Build {platform.version()})")
    print(f" - Arquitetura : {platform.machine()} ({platform.architecture()[0]})")
    print(f" - Computador  : {platform.node()}")

    # 2. Python & Pydantic AI Core
    print(f"\n[2] PYTHON & PYDANTIC AI STACK:")
    print(f" - Executavel  : {sys.executable}")
    print(f" - Python Ver  : {sys.version.split()[0]}")
    print(f" - Pydantic v2 : {check_pkg('pydantic')}")
    print(f" - Pydantic AI : {check_pkg('pydantic_ai_slim', 'pydantic_ai')}")
    print(f" - PyGraph AI  : {check_pkg('pydantic_graph')}")
    print(f" - PyYAML      : {check_pkg('pyyaml', 'yaml')}")
    print(f" - Watchdog    : {check_pkg('watchdog')}")

    # 3. Data Science, ML & NLP
    print(f"\n[3] DATA SCIENCE, MACHINE LEARNING & GRAFOS:")
    print(f" - NumPy       : {check_pkg('numpy')}")
    print(f" - Pandas      : {check_pkg('pandas')}")
    print(f" - Scikit-Learn: {check_pkg('scikit-learn', 'sklearn')}")
    print(f" - SciPy       : {check_pkg('scipy')}")
    print(f" - NetworkX    : {check_pkg('networkx')} (Engine Graphify)")

    # 4. Bases de Dados e Motores de Busca
    print(f"\n[4] BASES DE DADOS E MOTORES DE BUSCA:")
    print(f" - SQLite3 Lib : {sqlite3.sqlite_version} (Nativo Python)")
    print(f" - PostgreSQL  : {check_pkg('psycopg2-binary', 'psycopg2')}")
    print(f" - ElasticSrch : {check_pkg('elasticsearch')}")

    # 5. Git & Controlo de Versao
    print(f"\n[5] CONTROLO DE VERSAO (GIT):")
    git_path = shutil.which("git") or r"C:\Program Files\Git\cmd\git.exe"
    if os.path.exists(git_path):
        print(f" - Git Path    : {git_path}")
        print(f" - Git Version : {run_cmd(f'\"{git_path}\" --version')}")
    else:
        print(f" - Git         : Nao encontrado no PATH padrao.")

    # 6. WSL2 & Distros (Ubuntu / Kali)
    print(f"\n[6] AMBIENTE LINUX (WSL2 / UBUNTU / KALI):")
    wsl_path = r"C:\Windows\System32\wsl.exe"
    if os.path.exists(wsl_path):
        print(f" - WSL Path    : {wsl_path}")
        wsl_list = run_cmd(f'"{wsl_path}" --list')
        print(f" - Distros     : {wsl_list if wsl_list else 'Nenhuma instalada ainda. Execute wsl --install Ubuntu'}")
    else:
        print(f" - WSL2        : Nao detetado em System32.")

    # 7. Suporte a Windows Long Paths
    print(f"\n[7] SUPORTE A WINDOWS LONG PATHS (\\\\?\\):")
    test_long_path = r"\\?\C:\Users\Yokozuna\Dev"
    print(f" - Teste \\\\?\\C:\\Users\\Yokozuna\\Dev : {'OK (HABILITADO)' if os.path.exists(test_long_path) else 'FALHA'}")

    print("\n==================================================================")
    print("DIAGNOSTICO FULL STACK CONCLUIDO")
    print("==================================================================")

if __name__ == "__main__":
    main()
