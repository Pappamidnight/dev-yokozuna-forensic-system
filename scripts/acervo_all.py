# -*- coding: utf-8 -*-
"""
acervo_all.py - Orquestrador do pipeline completo
==================================================
Corre tudo: scan -> process -> filtros -> relatorio
NUNCA apaga. Só move para quarentena (opcional).

Uso:
    python acervo_all.py                 # pipeline completo (dry-run)
    python acervo_all.py --executar      # executa higienizacao
    python acervo_all.py --so-scan       # so inventario
    python acervo_all.py --so-report     # so relatorio
"""
import os
import sys
import argparse
import subprocess
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SCRIPTS_DIR = r"C:\ACERVO\scripts"


def correr(script, args=None, verbose=True):
    """Corre um script Python e devolve sucesso."""
    cmd = [sys.executable, "-u", os.path.join(SCRIPTS_DIR, script)]
    if args:
        cmd.extend(args)
    if verbose:
        print(f"\n{'='*88}")
        print(f"  >> {script} {' '.join(args or [])}")
        print('='*88)
    try:
        r = subprocess.run(cmd, check=False)
        return r.returncode == 0
    except Exception as e:
        print(f"[ERRO] {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Pipeline completo ACERVO")
    parser.add_argument("--executar", action="store_true",
                        help="Executar higienizacao (senao dry-run)")
    parser.add_argument("--so-scan", action="store_true", help="So inventario")
    parser.add_argument("--so-report", action="store_true", help="So relatorio")
    parser.add_argument("--heuristica", action="store_true", help="Ativar heuristica")
    parser.add_argument("--quiet", action="store_true", help="Modo silencioso")
    args = parser.parse_args()

    t0 = time.time()
    verbose = not args.quiet

    print()
    print("=" * 88)
    print("  ACERVO - PIPELINE COMPLETO")
    print(f"  Modo: {'EXECUTAR' if args.executar else 'DRY-RUN'}")
    print("=" * 88)

    # 1) Scan
    if not args.so_report:
        correr("acervo_scan.py", ["--snapshot"], verbose)

    # 2) Process (1 tipo de cada vez)
    if not args.so_report and not args.so_scan:
        cmd_args = ["--all", "--quiet"]
        if args.heuristica:
            cmd_args.append("--heuristica")
        correr("acervo_process.py", cmd_args, verbose)

    # 3) Relatorio
    if not args.so_scan:
        correr("acervo_report.py", ["--html", "--json", "--snapshot"], verbose)

    # 4) Higienizar (dry-run por defeito)
    if not args.so_report and not args.so_scan:
        cmd_args = ["--executar"] if args.executar else []
        for tipo in ["pdf", "video", "imagem"]:
            correr("acervo_higienizar.py",
                   ["--tipo", tipo] + cmd_args, verbose)

    print()
    print("=" * 88)
    print(f"  PIPELINE CONCLUIDO em {time.time()-t0:.2f}s")
    print("=" * 88)
    print()
    print("  Outputs em:")
    print(f"    - {os.path.join(SCRIPTS_DIR, '..', 'logs', 'relatorios')}")
    print(f"    - {os.path.join(SCRIPTS_DIR, '..', 'logs', 'filtros')}")
    print(f"    - {os.path.join(SCRIPTS_DIR, '..', 'manifests')}")
    print(f"    - {os.path.join(SCRIPTS_DIR, '..', 'quarentena')}")
    print()


if __name__ == "__main__":
    main()
