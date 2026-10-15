# -*- coding: utf-8 -*-
"""
gerar_metadata.py - Gera .metadata.efu para ficheiros
======================================================
Uso:
    python gerar_metadata.py --path "C:\ACERVO\caso_15547\docs" --caso 15547
    python gerar_metadata.py --path "C:\ACERVO\caso_15547" --recursive
"""
import os
import sys
import csv
import argparse
from datetime import datetime


def gerar_metadata(path, caso=None, tags=None):
    """Gera .metadata.efu para um ficheiro."""
    if not os.path.isfile(path):
        return None

    st = os.stat(path)
    nome = os.path.basename(path)
    stem, ext = os.path.splitext(nome)

    meta_path = path + ".metadata.efu"

    with open(meta_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Filename", "Size", "Date Modified", "Date Created",
                    "Attributes", "Tags", "Comment", "Rating"])
        w.writerow([
            path,
            st.st_size,
            datetime.fromtimestamp(st.st_mtime).isoformat(),
            datetime.fromtimestamp(st.st_ctime).isoformat(),
            "A",
            tags or "",
            "",
            "",
        ])

    return meta_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True)
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--caso", help="Numero do caso (ex: 15547)")
    parser.add_argument("--tags", help="Tags separadas por ;")
    args = parser.parse_args()

    gerados = 0
    if os.path.isfile(args.path):
        r = gerar_metadata(args.path, args.caso, args.tags)
        if r:
            print(f"  [OK] {r}")
            gerados = 1
    elif os.path.isdir(args.path):
        for dirpath, dirnames, filenames in os.walk(args.path):
            for f in filenames:
                if f.endswith(".metadata.efu"):
                    continue
                p = os.path.join(dirpath, f)
                r = gerar_metadata(p, args.caso, args.tags)
                if r:
                    gerados += 1
                    if gerados % 100 == 0:
                        print(f"  ... {gerados}")

    print()
    print(f"[OK] {gerados} ficheiros .metadata.efu gerados")


if __name__ == "__main__":
    main()
