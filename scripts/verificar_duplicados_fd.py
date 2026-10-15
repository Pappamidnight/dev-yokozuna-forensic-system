# -*- coding: utf-8 -*-
"""
Audita os duplicados em C:\ACERVO\logs\csv\
Verifica: existem no disco? estao em pastas de lixo?
"""
import subprocess
import os
import csv
import time
from collections import defaultdict

# PASTA CORRETA (sem subpastas por tipo)
CSV_DIR = r"C:\ACERVO\logs\csv"
TIPOS = ["database","video","excel","audio","word","pdf",
         "imagem","json","texto","yaml","csv","markdown"]

# Pastas de LIXO
LIXO_PATHS = [
    "$recycle.bin", "system volume information",
    "\\temp\\", "\\tmp\\", "\\cache\\", "\\caches\\",
    "\\appdata\\local\\temp", "\\windows\\temp",
    "\\node_modules\\", "\\.git\\", "\\__pycache__\\",
    "\\venv\\", "\\site-packages\\", "\\programdata\\",
    "\\.cache\\", "\\.thumbnails\\", "\\internet cache",
    "\\microsoft\\windows\\inetcache",
]

def eh_lixo(caminho):
    c = caminho.lower()
    for p in LIXO_PATHS:
        if p in c:
            return True
    return False

def main():
    t0 = time.time()
    print("=" * 78)
    print("  AUDITORIA DE DUPLICADOS - C:\\ACERVO\\logs\\csv")
    print("=" * 78)
    print()

    try:
        v = subprocess.run(["fd", "--version"], capture_output=True, text=True, timeout=10)
        print(f"  [OK] fd: {v.stdout.strip()}")
    except FileNotFoundError:
        print("  [ERRO] fd nao instalado")
        return

    print()

    total_geral = 0
    total_ok = 0
    total_lixo = 0
    total_inexistente = 0

    for tipo in TIPOS:
        p = os.path.join(CSV_DIR, f"duplicados_{tipo}.csv")
        if not os.path.isfile(p):
            print(f"  [{tipo.upper()}] SKIP - ficheiro nao existe")
            continue

        print(f"  [{tipo.upper()}] A analisar...")
        t_it = time.time()

        n_total = 0
        n_ok = 0
        n_lixo = 0
        n_inexistente = 0
        amostra_lixo = []
        amostra_ok = []

        with open(p, "r", encoding="utf-8", errors="replace", newline="") as f:
            r = csv.reader(f)
            header = next(r, None)
            # Detetar indice da coluna Caminho
            idx_caminho = 1
            if header:
                for i, h in enumerate(header):
                    if "caminho" in h.lower():
                        idx_caminho = i
                        break

            for row in r:
                if len(row) <= idx_caminho:
                    continue
                caminho = row[idx_caminho].strip()
                if not caminho:
                    continue
                n_total += 1

                if eh_lixo(caminho):
                    n_lixo += 1
                    if len(amostra_lixo) < 2:
                        amostra_lixo.append(caminho[:100])
                elif os.path.isfile(caminho):
                    n_ok += 1
                    if len(amostra_ok) < 2:
                        amostra_ok.append(caminho[:100])
                else:
                    n_inexistente += 1

        total_geral += n_total
        total_ok += n_ok
        total_lixo += n_lixo
        total_inexistente += n_inexistente

        pct_ok = (n_ok / n_total * 100) if n_total else 0
        pct_lixo = (n_lixo / n_total * 100) if n_total else 0

        print(f"    Total:        {n_total:>10,}")
        print(f"    OK (real):    {n_ok:>10,}  ({pct_ok:>5.1f}%)")
        print(f"    LIXO:         {n_lixo:>10,}  ({pct_lixo:>5.1f}%)")
        print(f"    Inexistente:  {n_inexistente:>10,}")
        print(f"    Tempo:        {time.time()-t_it:.2f}s")
        if amostra_lixo:
            print(f"    ex lixo:      {amostra_lixo[0]}")
        if amostra_ok:
            print(f"    ex ok:        {amostra_ok[0]}")
        print()

    print("=" * 78)
    print("  RESUMO GERAL")
    print("=" * 78)
    print(f"  Total analisado: {total_geral:,}")
    if total_geral:
        print(f"  Reais (OK):      {total_ok:,}  ({total_ok/total_geral*100:.1f}%)")
        print(f"  Lixo:            {total_lixo:,}  ({total_lixo/total_geral*100:.1f}%)")
        print(f"  Inexistente:     {total_inexistente:,}  ({total_inexistente/total_geral*100:.1f}%)")
    print(f"  Tempo total:     {time.time()-t0:.2f}s")
    print("=" * 78)

if __name__ == "__main__":
    main()
