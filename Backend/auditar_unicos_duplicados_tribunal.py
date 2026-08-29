#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auditar_unicos_duplicados_tribunal.py - Calcula a contagem exata de ficheiros unicos vs duplicados por hash SHA-256 no arquivo do tribunal.
"""

import hashlib
from pathlib import Path
from collections import defaultdict

tribunal_dir = Path(r"C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\04_DOCUMENTOS_CITIUS_E_PECAS\ARQUIVO_OFICIAL_TRIBUNAL")

total_files = 0
hashes_global = defaultdict(list)
processos_stats = {}

for proc_dir in sorted(tribunal_dir.iterdir()):
    if proc_dir.is_dir():
        p_files = [f for f in proc_dir.rglob("*") if f.is_file()]
        p_hashes = defaultdict(list)
        for f in p_files:
            try:
                data = f.read_bytes()
                h = hashlib.sha256(data).hexdigest()
                p_hashes[h].append(f)
                hashes_global[h].append(f)
            except Exception:
                pass
        total_files += len(p_files)
        unicos = len(p_hashes)
        duplicados = len(p_files) - unicos
        processos_stats[proc_dir.name] = {
            "total": len(p_files),
            "unicos": unicos,
            "duplicados": duplicados
        }

total_unicos = len(hashes_global)
total_duplicados = total_files - total_unicos

print("=" * 80)
print(" RELATÓRIO FORENSE: DOCUMENTOS ÚNICOS VS DUPLICADOS NO ARQUIVO DO TRIBUNAL")
print("=" * 80)
print(f" TOTAL DE FICHEIROS ENCONTRADOS:     {total_files}")
print(f" TOTAL DE DOCUMENTOS ÚNICOS (SHA-256): {total_unicos}")
print(f" TOTAL DE CÓPIAS / REPETIDOS:         {total_duplicados}")
print(f" TAXA DE REDUNDÂNCIA:                 {(total_duplicados / total_files * 100):.1f}%")
print("=" * 80)
print(f"{'PROCESSO':<35} | {'TOTAL':<8} | {'ÚNICOS':<8} | {'REPETIDOS':<10}")
print("-" * 80)
for p, s in processos_stats.items():
    print(f"{p:<35} | {s['total']:>8} | {s['unicos']:>8} | {s['duplicados']:>10}")
print("=" * 80)
