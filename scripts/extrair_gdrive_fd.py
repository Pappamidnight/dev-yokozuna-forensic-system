# -*- coding: utf-8 -*-
import subprocess
import os
import csv
import time
import json

DEST = r"C:\ACERVO\logs\google_drive"
os.makedirs(DEST, exist_ok=True)
OUT = os.path.join(DEST, "google_drive_full.csv")

FONTES = [
    r"G:\O meu disco",
    r"G:\Outros computadores",
]

def main():
    t0 = time.time()
    print("=" * 70)
    print("  EXTRACAO GOOGLE DRIVE - FD (ULTRA-RAPIDO)")
    print("=" * 70)
    print(f"  Fontes:  {FONTES}")
    print(f"  Destino: {OUT}")
    print()

    # Verificar se fd esta instalado
    try:
        v = subprocess.run(["fd", "--version"], capture_output=True, text=True, timeout=10)
        print(f"  [OK] fd: {v.stdout.strip()}")
    except FileNotFoundError:
        print("  [ERRO] fd nao encontrado. Instale: winget install sharkdp.fd")
        return
    except Exception as e:
        print(f"  [ERRO] {e}")
        return

    print()
    print("[1/2] A listar ficheiros com fd...")

    total = 0
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Nome", "Caminho", "Tamanho", "DataMod", "Atributos", "Extensao"])

        for fonte in FONTES:
            if not os.path.isdir(fonte):
                print(f"  [SKIP] {fonte} nao existe")
                continue

            print(f"  A varrer: {fonte}")

            # fd com --absolute-path --type f (apenas ficheiros)
            # e --exclude para pastas de sistema
            cmd = [
                "fd",
                "--type", "f",
                "--absolute-path",
                "--hidden",
                "--no-ignore",
                "--threads", "8",
                "--exclude", "node_modules",
                "--exclude", ".git",
                "--exclude", "__pycache__",
                "--exclude", "venv",
                "--exclude", "site-packages",
                "--exclude", "AppData",
                "--exclude", "ProgramData",
                "--exclude", "$RECYCLE.BIN",
                "--exclude", "System Volume Information",
                ".",
                fonte,
            ]

            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True, encoding="utf-8", errors="replace", bufsize=1)

            n = 0
            for linha in proc.stdout:
                caminho = linha.strip()
                if not caminho:
                    continue
                try:
                    st = os.stat(caminho)
                    nome = os.path.basename(caminho)
                    ext = os.path.splitext(nome)[1].lower()
                    tam = st.st_size
                    dm = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime))
                    attr = "A" if st.st_file_attributes & 0x20 else "-"
                    w.writerow([nome, caminho, tam, dm, attr, ext])
                    n += 1
                    total += 1
                    if n % 10000 == 0:
                        print(f"    ... {n:,} ficheiros", end="\r", flush=True)
                except Exception:
                    continue

            proc.wait()
            print(f"    {n:,} ficheiros de {fonte}")

    print()
    print("[2/2] A finalizar...")
    sz = os.path.getsize(OUT) / 1024 / 1024
    print(f"  [OK] {OUT}")
    print(f"  Tamanho: {sz:.2f} MB")
    print(f"  Total registos: {total:,}")
    print(f"  Tempo total: {time.time()-t0:.2f}s")
    print("=" * 70)

if __name__ == "__main__":
    main()
