#!/usr/bin/env python3
"""
Script de Ingestao, Copia e Organizacao de Ficheiros Escritos Canonicos.
Suporte total a Windows Long Paths (\\\\?\\), higienizacao de nomes,
deduplicacao por SHA-256 e geracao de Indice Mestre MOC em 00_Indice_E_MOCs.
"""
import os
import sys
import shutil
import hashlib
import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DEFAULT_SOURCE_ROOT = Path(r"G:\nuno")
DEFAULT_DEST_ROOT = Path(r"C:\Users\Yokozuna\Dev\Projects\Ficheiros Escritos Canónicos")


def make_win_long_path(path: Path) -> Path:
    """Converte um caminho absoluto Windows para a sintaxe de caminho longo (\\\\?\\)."""
    abs_str = str(path.resolve())
    if abs_str.startswith("\\\\?\\"):
        return Path(abs_str)
    if abs_str.startswith("\\\\"):  # UNC path
        return Path("\\\\?\\UNC\\" + abs_str[2:])
    return Path("\\\\?\\" + abs_str)


def sanitize_name(name: str) -> str:
    name_stem, ext = os.path.splitext(name)
    replacements = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c', 'ñ': 'n',
        'Á': 'A', 'À': 'A', 'Ã': 'A', 'Â': 'A', 'Ä': 'A',
        'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
        'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ï': 'I',
        'Ó': 'O', 'Ò': 'O', 'Õ': 'O', 'Ô': 'O', 'Ö': 'O',
        'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ü': 'U',
        'Ç': 'C', 'Ñ': 'N'
    }
    for char, repl in replacements.items():
        name_stem = name_stem.replace(char, repl)
    
    clean_stem = re.sub(r'[^a-zA-Z0-9_\-]', '_', name_stem)
    clean_stem = re.sub(r'_+', '_', clean_stem).strip('_')
    
    if len(clean_stem) > 100:
        clean_stem = clean_stem[:100]
        
    return f"{clean_stem}{ext.lower()}"


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""


def copy_and_organize(source_root: Path = DEFAULT_SOURCE_ROOT, dest_root: Path = DEFAULT_DEST_ROOT, dry_run: bool = False):
    print("=" * 80)
    print(f" COPIANDO E ORGANIZANDO FICHEIROS ESCRITOS CANONICOS (LONG-PATH SAFE \\\\?\\)")
    print(f" Origem : {source_root}")
    print(f" Destino: {dest_root}")
    print(f" Modo   : {'DRY-RUN (Simulacao sem escrita)' if dry_run else 'EXECUCAO REAL'}")
    print("=" * 80)

    if not source_root.exists():
        print(f"[AVISO] Pasta de origem {source_root} nao esta acessivel no momento.")
        return

    long_dest_root = make_win_long_path(dest_root)
    if not dry_run:
        os.makedirs(str(long_dest_root), exist_ok=True)

    mapping_directories = [
        ("01_PDF", dest_root / "01_PDFs_Oficiais"),
        ("02_TEXTO", dest_root / "02_Minutas_E_Rascunhos"),
        ("02_PROCESSOS", dest_root / "04_Processos_E_Pecas_Escritas" / "04.01_Processos_Gerais"),
        ("BASE DADOS  LEA -PROVIDENCIA CAUTELA", dest_root / "04_Processos_E_Pecas_Escritas" / "04.02_Providencia_Cautelar_LEA"),
        ("BASE DADOS LEA -PROVIDENCIA CAUTELA", dest_root / "04_Processos_E_Pecas_Escritas" / "04.02_Providencia_Cautelar_LEA"),
        ("J-LAW", dest_root / "04_Processos_E_Pecas_Escritas" / "04.03_J_LAW"),
        ("providecia processo", dest_root / "04_Processos_E_Pecas_Escritas" / "04.04_Providencia_Processos_Anexos"),
        ("PROCESOO", dest_root / "04_Processos_E_Pecas_Escritas" / "04.05_Outros_Processos")
    ]

    for item in source_root.glob("*TRANSA*"):
        if item.is_dir():
            mapping_directories.append((item.name, dest_root / "03_Contratos_E_Acordos"))

    copied_files_count = 0
    copied_bytes = 0
    seen_hashes = {}
    duplicates_skipped = 0
    errors_count = 0

    for src_folder_name, target_dest_dir in mapping_directories:
        src_dir = source_root / src_folder_name
        if not src_dir.exists():
            continue

        print(f"\n[DIR] A processar: {src_folder_name} -> {target_dest_dir.name}")
        
        long_src_dir = make_win_long_path(src_dir)
        long_dest_dir = make_win_long_path(target_dest_dir)
        if not dry_run:
            os.makedirs(str(long_dest_dir), exist_ok=True)

        for root, dirs, files in os.walk(str(long_src_dir)):
            try:
                rel_parts = Path(root).relative_to(long_src_dir).parts
                clean_rel_parts = [sanitize_name(p)[:40] for p in rel_parts]
                
                target_sub_dir = long_dest_dir
                for part in clean_rel_parts:
                    target_sub_dir = target_sub_dir / part
                
                if not dry_run:
                    os.makedirs(str(target_sub_dir), exist_ok=True)

                for file in files:
                    src_file_path = Path(root) / file
                    
                    file_hash = compute_sha256(src_file_path)
                    if file_hash and file_hash in seen_hashes:
                        duplicates_skipped += 1
                        continue
                    if file_hash:
                        seen_hashes[file_hash] = src_file_path

                    clean_filename = sanitize_name(file)
                    dest_file_path = target_sub_dir / clean_filename

                    if os.path.exists(str(dest_file_path)) and str(dest_file_path) != str(src_file_path):
                        stem = dest_file_path.stem
                        ext = dest_file_path.suffix
                        dest_file_path = target_sub_dir / f"{stem[:30]}_alt{ext}"

                    try:
                        file_size = os.path.getsize(str(src_file_path))
                        if not dry_run:
                            shutil.copy2(str(src_file_path), str(dest_file_path))
                        copied_files_count += 1
                        copied_bytes += file_size
                    except Exception as e:
                        errors_count += 1
            except Exception as e:
                errors_count += 1

    correspondence_dir = dest_root / "05_Correspondencia_E_Comunicacoes"
    long_corr_dir = make_win_long_path(correspondence_dir)
    if not dry_run:
        os.makedirs(str(long_corr_dir), exist_ok=True)

    for item in source_root.glob("*"):
        if item.is_file() and item.suffix.lower() in [".txt", ".docx", ".pdf", ".doc"]:
            long_item = make_win_long_path(item)
            file_hash = compute_sha256(long_item)
            if file_hash and file_hash in seen_hashes:
                duplicates_skipped += 1
                continue
            if file_hash:
                seen_hashes[file_hash] = long_item

            clean_filename = sanitize_name(item.name)
            dest_file_path = long_corr_dir / clean_filename
            try:
                file_size = os.path.getsize(str(long_item))
                if not dry_run:
                    shutil.copy2(str(long_item), str(dest_file_path))
                copied_files_count += 1
                copied_bytes += file_size
            except Exception as e:
                errors_count += 1

    # Criacao do MOC Mestre
    indices_dir = dest_root / "00_Indice_E_MOCs"
    long_indices_dir = make_win_long_path(indices_dir)
    if not dry_run:
        os.makedirs(str(long_indices_dir), exist_ok=True)

    moc_path = long_indices_dir / "INDEX_MESTRE_FICHEIROS_ESCRITOS.md"
    moc_lines = [
        "# Indice Mestre de Ficheiros Escritos Canonicos",
        f"\n**Localizacao do Projeto**: `{dest_root}`",
        f"**Data da Consolidacao**: 2026-08-28",
        f"**Total de Ficheiros Processados**: {copied_files_count}",
        f"**Volume Total**: {copied_bytes / (1024*1024):.2f} MB",
        f"**Duplicados SHA-256 Purgados**: {duplicates_skipped}",
        f"**Erros de Leitura/Copia**: {errors_count}\n",
        "## Estrutura Canonica e Subpastas\n"
    ]

    for sub_dir in sorted(dest_root.glob("*")):
        if sub_dir.is_dir() and sub_dir.name != "00_Indice_E_MOCs":
            file_list = list(sub_dir.rglob("*"))
            file_count = sum(1 for f in file_list if f.is_file())
            moc_lines.append(f"### [DIR] `{sub_dir.name}` ({file_count} ficheiros)")
            for f in sorted(file_list[:50]):
                if f.is_file():
                    try:
                        rel = f.relative_to(dest_root)
                        moc_lines.append(f"- [{f.name}]({f.as_uri()}) - `{rel}`")
                    except Exception:
                        pass
            if file_count > 50:
                moc_lines.append(f"- ... e mais {file_count - 50} ficheiros.")
            moc_lines.append("")

    if not dry_run:
        with open(str(moc_path), "w", encoding="utf-8") as f:
            f.write("\n".join(moc_lines))

    print("\n" + "=" * 80)
    print(" RESUMO DA COPIA E ORGANIZACAO COMPLETA (LONG PATH SAFE)")
    print("=" * 80)
    print(f" - Ficheiros processados          : {copied_files_count}")
    print(f" - Volume de dados                : {copied_bytes / (1024*1024):.2f} MB")
    print(f" - Duplicados SHA-256 eliminados  : {duplicates_skipped}")
    print(f" - Indice Mestre gerado em        : {moc_path}")


def main():
    parser = argparse.ArgumentParser(description="Organizador e Ingestor Canonico com Long Paths")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE_ROOT), help="Pasta de origem")
    parser.add_argument("--dest", default=str(DEFAULT_DEST_ROOT), help="Pasta de destino")
    parser.add_argument("--dry-run", action="store_true", help="Simulacao sem escrita")
    parser.add_argument("--apply", action="store_true", help="Execucao real")
    args = parser.parse_args()

    dry_run = not args.apply
    copy_and_organize(Path(args.source), Path(args.dest), dry_run=dry_run)


if __name__ == "__main__":
    main()
