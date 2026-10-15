# -*- coding: utf-8 -*-
r"""
pipeline.py - Orquestrador
==========================
1. Analise
2. Duplicados
3. Filtros (video, imagem, pdf)
"""
import os
import sys
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import banner, everything_a_correr

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def correr_script(nome, args_extra=None):
    import subprocess
    script = os.path.join(SCRIPTS_DIR, nome)
    cmd = [sys.executable, "-u", script]
    if args_extra:
        cmd += args_extra
    print("\n>> " + " ".join(cmd))
    return subprocess.run(cmd, check=False).returncode == 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--santuario", default=r"C:\ACERVO\storage")
    p.add_argument("--top", type=int, default=100)
    args = p.parse_args()

    if not everything_a_correr():
        banner("PIPELINE - AVISO")
        print("  Everything GUI nao esta a correr.")
        print("  Abre o Everything e volta a tentar.")
        return

    t0 = time.time()
    banner("PIPELINE ACERVO")

    correr_script("analise.py", ["--top", str(args.top), "--quiet"])
    correr_script("duplicados.py",
                  ["--tipos", "video", "audio", "imagem", "pdf", "--quiet"])
    correr_script("duplicados.py",
                  ["--tipo", "geral", "--santuario", args.santuario, "--quiet"])
    correr_script("filtros.py", ["--tipo", "video", "--tam-min", "100MB"])

    banner("PIPELINE CONCLUIDO", f"Tempo total: {time.time()-t0:.2f}s")


if __name__ == "__main__":
    main()
