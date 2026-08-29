import os
from pathlib import Path

root = Path(r"C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO\04_DOCUMENTOS_CITIUS_E_PECAS\ARQUIVO_OFICIAL_TRIBUNAL")
print("=" * 85)
print(f"{'PROCESSO DO TRIBUNAL':<35} | {'TOTAL FICHEIROS':<16} | {'TAMANHO TOTAL (MB)':<18}")
print("=" * 85)

total_files_global = 0
total_bytes_global = 0

for d in sorted(root.iterdir()):
    if d.is_dir():
        files = list(d.glob("*"))
        n_files = len([f for f in files if f.is_file()])
        sz_mb = sum(f.stat().st_size for f in files if f.is_file()) / (1024 * 1024)
        total_files_global += n_files
        total_bytes_global += sum(f.stat().st_size for f in files if f.is_file())
        print(f"{d.name:<35} | {n_files:<16} | {sz_mb:<18.2f} MB")

print("=" * 85)
print(f"{'TOTAL CONSOLIDADO':<35} | {total_files_global:<16} | {total_bytes_global / (1024 * 1024):<18.2f} MB")
print("=" * 85)
