# -*- coding: utf-8 -*-
"""es_diag.py - Diagnostico completo do es.exe"""
import os, sys, subprocess, time

ES = r"C:\ACERVO\bin\es.exe"
INST = "1.5a"

def linha(titulo, valor, cor=""):
    print(f"  {titulo:<40} {valor}")

def diag():
    print()
    print("=" * 78)
    print("  DIAGNOSTICO ES.EXE")
    print("=" * 78)
    print()

    # 1) Ficheiro
    linha("1) es.exe existe?", "OK" if os.path.isfile(ES) else "FALHA")
    if not os.path.isfile(ES):
        print("   Path:", ES)
        return

    # 2) Versao
    try:
        r = subprocess.run([ES, "-version"], capture_output=True, text=True, timeout=10)
        linha("2) Versao", r.stdout.strip())
    except Exception as e:
        linha("2) Versao", f"ERRO: {e}")

    # 3) GUI a correr
    try:
        r = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq Everything64.exe", "/NH", "/FO", "CSV"],
            capture_output=True, timeout=10
        )
        out = r.stdout.decode("utf-8", errors="replace")
        if not out.strip():
            out = r.stdout.decode("cp850", errors="replace")
        running = "Everything64" in out or "Everything" in out
        linha("3) GUI a correr?", "OK" if running else "FALHA")
    except Exception as e:
        linha("3) GUI a correr?", f"ERRO: {e}")

    # 4-6) Testar instancias
    for inst in ["1.5a", "1.5b", "1.5", ""]:
        nome = f"4) Teste instancia '{inst}'"
        try:
            args = [ES]
            if inst:
                args += ["-instance", inst]
            args += ["-get-result-count", "ext:pdf"]
            r = subprocess.run(args, capture_output=True, text=True, timeout=30)
            n = r.stdout.strip()
            if n and n.isdigit():
                linha(nome, f"OK: {n} PDFs")
            else:
                linha(nome, f"FALHA: {n[:50]}")
        except Exception as e:
            linha(nome, f"ERRO: {e}")

    # 7) Python
    linha("7) Python", sys.version.split()[0])

    # 8) Paths com espacos
    for p in [
        r"C:\Users\Yokozuna",
        r"C:\Users\Yokozuna\Dev",
        r"C:\Users\Yokozuna\OneDrive\Ficheiros do Microsoft Copilot Chat",
        r"C:\Users\Yokozuna\OneDrive\Microsoft Copilot Chat Files\Copilot Notebook Uploads",
        "G:\\",
    ]:
        try:
            q = f'path:"{p}"'
            r = subprocess.run(
                [ES, "-instance", INST, "-get-result-count", q],
                capture_output=True, text=True, timeout=30
            )
            n = r.stdout.strip()
            status = f"OK: {n}" if n.isdigit() else f"FALHA: {n[:30]}"
            linha(f"8) {p[:45]}", status)
        except Exception as e:
            linha(f"8) {p[:45]}", f"ERRO: {e}")

    print()
    print("=" * 78)


if __name__ == "__main__":
    diag()
