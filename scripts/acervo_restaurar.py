# -*- coding: utf-8 -*-
"""acervo_restaurar.py - Restaura batches de quarentena"""
import os, sys, json, shutil, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from acervo_core import humano, DIR_QUAR

def restaurar(batch_dir, dry_run=True):
    man_path = os.path.join(batch_dir, "_manifest.json")
    if not os.path.isfile(man_path):
        print(f"[ERRO] Manifesto nao encontrado: {man_path}")
        return
    with open(man_path, encoding="utf-8") as f:
        manifesto = json.load(f)
    ficheiros = manifesto.get("ficheiros", [])
    print()
    print("=" * 88)
    print(f"  RESTAURAR: {batch_dir}")
    print(f"  Modo: {'DRY-RUN' if dry_run else 'EXECUTAR'}")
    print(f"  Ficheiros no manifesto: {len(ficheiros):,}")
    print("=" * 88)
    restaurados = falhas = 0
    for i, reg in enumerate(ficheiros, 1):
        origem = reg.get("origem")
        destino = reg.get("destino")
        if not os.path.isfile(destino):
            falhas += 1
            continue
        if dry_run:
            print(f"  {destino}")
            print(f"    -> {origem}")
            restaurados += 1
            continue
        try:
            os.makedirs(os.path.dirname(origem), exist_ok=True)
            if os.path.exists(origem):
                base, ext = os.path.splitext(origem)
                origem = f"{base}_restaurado{ext}"
            shutil.move(destino, origem)
            restaurados += 1
        except (OSError, PermissionError, shutil.Error) as e:
            falhas += 1
            print(f"  [FALHA] {destino}: {e}")
    print()
    print("-" * 88)
    print(f"  Restaurados: {restaurados:,}")
    print(f"  Falhas:      {falhas:,}")
    print("-" * 88)

def listar():
    if not os.path.isdir(DIR_QUAR):
        print("Sem batches.")
        return
    for tipo in sorted(os.listdir(DIR_QUAR)):
        td = os.path.join(DIR_QUAR, tipo)
        if not os.path.isdir(td): continue
        for b in sorted(os.listdir(td)):
            bd = os.path.join(td, b)
            man = os.path.join(bd, "_manifest.json")
            n = 0
            if os.path.isfile(man):
                with open(man, encoding="utf-8") as f:
                    n = json.load(f).get("movidos", 0)
            print(f"  {tipo:<10} {b:<20}  {n:>6} ficheiros")
            print(f"    -> {bd}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--listar", action="store_true")
    p.add_argument("--batch")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    if a.listar: listar(); return
    if a.batch: restaurar(a.batch, a.dry_run); return
    p.print_help()

if __name__ == "__main__":
    main()
