#!/usr/bin/env python3
"""
Gerador deterministico de arvore de diretorios e ficheiros (tree_dirs.md).
Gera mapa hierarquico completo de C:\\Users\\Yokozuna\\Dev, ignorando pastas de pacotes (.venv, .git, __pycache__).
"""
import os
import sys
from datetime import datetime
from typing import List, Tuple

DEV_ROOT = "C:\\Users\\Yokozuna\\Dev"
OUTPUT_FILE = os.path.join(DEV_ROOT, "tree_dirs.md")

IGNORE_DIRS = {
    ".venv", ".git", ".github", "__pycache__", "node_modules",
    ".pytest_cache", ".ruff_cache", "site-packages", ".agents"
}


def build_tree(root_dir: str, max_depth: int = 6) -> Tuple[str, int, int]:
    """Constroi arvore em formato markdown/ascii e retorna contagem de pastas e ficheiros."""
    lines = []
    lines.append(f"# Mapa Estrutural do Ambiente Dev (Tree Reference)")
    lines.append(f"**Raiz**: `{root_dir}`")
    lines.append(f"**Data da Geracao**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Watcher**: Monitorizado ativamente por `watchdog_indexer.py`\n")
    lines.append("```text")
    lines.append(f"{os.path.basename(root_dir)}/")
    
    total_dirs = 0
    total_files = 0

    def walk_dir(current_path: str, prefix: str, depth: int):
        nonlocal total_dirs, total_files
        if depth > max_depth:
            return

        try:
            entries = os.listdir(current_path)
        except PermissionError:
            return

        entries = sorted(entries, key=lambda s: (not os.path.isdir(os.path.join(current_path, s)), s.lower()))
        filtered_entries = [e for e in entries if e not in IGNORE_DIRS]

        count = len(filtered_entries)
        for i, entry in enumerate(filtered_entries):
            full_path = os.path.join(current_path, entry)
            is_last = (i == count - 1)
            connector = "\\-- " if is_last else "|-- "
            sub_prefix = "    " if is_last else "|   "

            if os.path.isdir(full_path):
                total_dirs += 1
                lines.append(f"{prefix}{connector}{entry}/")
                walk_dir(full_path, prefix + sub_prefix, depth + 1)
            else:
                total_files += 1
                size = os.path.getsize(full_path)
                size_str = f"{size / 1024:.1f} KB" if size >= 1024 else f"{size} B"
                lines.append(f"{prefix}{connector}{entry} ({size_str})")

    walk_dir(root_dir, "", 1)
    lines.append("```\n")
    lines.append(f"**Total de Pastas**: {total_dirs} | **Total de Ficheiros Mapeados**: {total_files}\n")
    
    return "\n".join(lines), total_dirs, total_files


def main():
    content, dirs_count, files_count = build_tree(DEV_ROOT)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[SUCESSO] tree_dirs.md gerado com sucesso: {dirs_count} pastas, {files_count} ficheiros.")


if __name__ == "__main__":
    main()
