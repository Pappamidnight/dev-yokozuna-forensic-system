# -*- coding: utf-8 -*-
"""
acervo_higienizar.py - Move duplicados para quarentena (NUNCA apaga)
=====================================================================
Uso:
    python acervo_higienizar.py --tipo pdf --dry-run
    python acervo_higienizar.py --tipo pdf --executar --raiz-only "C:\ACERVO"
    python acervo_higienizar.py --tipo pdf --executar --force  # sem confirmacao
    python acervo_higienizar.py --lixo --dry-run
    python acervo_higienizar.py --listar
"""
import os
import sys
import json
import shutil
import argparse
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from acervo_core import (
    carregar_csv, gravar_csv, gravar_json, garantir_dirs, humano,
    segregar, timestamp, agora_str, e_lixo, e_protegido,
    TIPOS, DIR_QUAR, DIR_MANIF, Filtro,
)


def criar_batch_dir(tipo):
    ts = timestamp()
    bdir = os.path.join(DIR_QUAR, tipo or "lixo", ts)
    os.makedirs(bdir, exist_ok=True)
    return bdir


def mover_para_quarentena(caminho, batch_dir, preservar_estrutura=True):
    if not os.path.isfile(caminho):
        return False, None
    if preservar_estrutura:
        rel = caminho
        for prefixo in [r"C:\ACERVO\\", "C:\\ACERVO\\", "\\\\?\\C:\\ACERVO\\"]:
            if rel.startswith(prefixo):
                rel = rel[len(prefixo):]
                break
        rel = rel.lstrip("\\/").replace(":", "_")
        destino = os.path.join(batch_dir, rel)
    else:
        destino = os.path.join(batch_dir, os.path.basename(caminho))
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    if os.path.exists(destino):
        base, ext = os.path.splitext(destino)
        destino = f"{base}_{timestamp()}{ext}"
    try:
        shutil.move(caminho, destino)
        return True, destino
    except (OSError, PermissionError, shutil.Error) as e:
        return False, str(e)


def confirmar(pergunta, force=False):
    """Pede confirmacao ao utilizador."""
    if force:
        print(f"  [FORCE] {pergunta} -> SIM")
        return True
    try:
        r = input(f"  {pergunta} [s/N]: ").strip().lower()
        return r in ("s", "sim", "y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False


def higienizar_tipo(tipo, dry_run=True, rank_max=None,
                    raiz_only=None, force=False):
    print()
    print("=" * 88)
    print(f"  HIGIENIZAR: {tipo.upper()}  |  {'DRY-RUN' if dry_run else 'EXECUTAR'}")
    print(f"  Data: {agora_str()}")
    if raiz_only:
        print(f"  Raiz (so dentro): {raiz_only}")
    print("=" * 88)

    filtro = Filtro(tipo=tipo, rank_max=rank_max)
    regs = carregar_csv(filtro, verbose=False)
    if not regs:
        print(f"  [VAZIO] Nenhum registo para '{tipo}'.")
        return None

    # Filtro por raiz
    if raiz_only:
        raiz_lower = raiz_only.lower().rstrip("\\")
        antes = len(regs)
        regs = [r for r in regs if r["caminho"].lower().startswith(raiz_lower)]
        print(f"\n  Filtro por raiz: {antes:,} -> {len(regs):,}")

    originais, duplicados, n_grupos = segregar(regs)
    print(f"\n  Total: {len(regs):,}  |  Grupos: {n_grupos:,}  |  "
          f"Orig: {len(originais):,}  |  Dup: {len(duplicados):,}")

    # Mostrar aviso se ficheiros fora de C:\ACERVO
    fora = [r for r in duplicados if not r["caminho"].lower().startswith("c:\\acervo")]
    if fora and not raiz_only:
        print(f"\n  ⚠️  ATENCAO: {len(fora):,} duplicados estao FORA de C:\\ACERVO")
        print(f"     Primeiros 3:")
        for r in fora[:3]:
            print(f"       {r['caminho']}")

    if dry_run:
        print(f"\n  [DRY-RUN] Nada sera movido.")
        print(f"  Candidatos: {len(duplicados):,}")
        espaco = sum(r["tamanho"] for r in duplicados)
        print(f"  Espaco recuperavel: {humano(espaco)}")
        print(f"\n  Primeiros 10:")
        for r in duplicados[:10]:
            print(f"    {r['caminho']}")
        return {"dry_run": True, "duplicados": len(duplicados), "espaco": espaco}

    # Executar
    if not duplicados:
        print("  Nada a mover.")
        return None

    # Confirmacao para batches grandes
    espaco = sum(r["tamanho"] for r in duplicados)
    if len(duplicados) > 100:
        print(f"\n  ⚠️  Vais mover {len(duplicados):,} ficheiros ({humano(espaco)})")
        if not confirmar("Confirmar?", force):
            print("  Cancelado.")
            return None

    batch_dir = criar_batch_dir(tipo)
    manifest_path = os.path.join(batch_dir, "_manifest.json")

    movidos = falhas = 0
    espaco_mov = 0
    registos = []

    print(f"\n  Batch: {batch_dir}")
    print(f"  A mover {len(duplicados):,} ficheiros...\n")

    for i, r in enumerate(duplicados, 1):
        caminho = r["caminho"]
        if e_protegido(os.path.basename(caminho)):
            continue
        sucesso, destino = mover_para_quarentena(caminho, batch_dir)
        if sucesso:
            movidos += 1
            espaco_mov += r["tamanho"]
            registos.append({
                "origem": caminho,
                "destino": destino,
                "tamanho": r["tamanho"],
                "tipo": tipo,
            })
        else:
            falhas += 1

        if i % 100 == 0:
            print(f"    ... {i:,}/{len(duplicados):,}  "
                  f"(movidos={movidos:,} falhas={falhas:,})")

    manifesto = {
        "data": agora_str(),
        "tipo": tipo,
        "dry_run": False,
        "raiz_only": raiz_only,
        "batch_dir": batch_dir,
        "movidos": movidos,
        "falhas": falhas,
        "espaco_recuperado_bytes": espaco_mov,
        "espaco_recuperado_humano": humano(espaco_mov),
        "ficheiros": registos,
    }
    gravar_json(manifest_path, manifesto)

    print()
    print("-" * 88)
    print(f"  Movidos:   {movidos:>10,}")
    print(f"  Falhas:    {falhas:>10,}")
    print(f"  Espaco:    {humano(espaco_mov):>10}")
    print(f"  Manifesto: {manifest_path}")
    print("-" * 88)
    print(f"\n  Para restaurar: python acervo_restaurar.py --batch \"{batch_dir}\"")

    return manifesto


def higienizar_lixo(dry_run=True, raiz_only=None, force=False):
    print()
    print("=" * 88)
    print(f"  HIGIENIZAR LIXO  |  {'DRY-RUN' if dry_run else 'EXECUTAR'}")
    print("=" * 88)

    raiz = raiz_only or r"C:\ACERVO"
    candidatos = []
    for dirpath, dirnames, filenames in os.walk(raiz, onerror=lambda e: None):
        if "quarentena" in dirpath.lower():
            continue
        for f in filenames:
            if e_protegido(f):
                continue
            if e_lixo(f):
                candidatos.append(os.path.join(dirpath, f))

    print(f"\n  Encontrados: {len(candidatos):,} ficheiros de lixo")
    if not candidatos:
        return None

    espaco = sum(os.path.getsize(c) for c in candidatos if os.path.isfile(c))

    if dry_run:
        print(f"  Espaco: {humano(espaco)}")
        print(f"\n  Primeiros 20:")
        for c in candidatos[:20]:
            print(f"    {c}")
        return {"dry_run": True, "total": len(candidatos), "espaco": espaco}

    if not confirmar(f"Mover {len(candidatos)} ficheiros de lixo?", force):
        print("  Cancelado.")
        return None

    batch_dir = criar_batch_dir("lixo")
    movidos = 0
    for c in candidatos:
        sucesso, _ = mover_para_quarentena(c, batch_dir)
        if sucesso:
            movidos += 1

    manifesto = {
        "data": agora_str(),
        "tipo": "lixo",
        "movidos": movidos,
        "espaco_recuperado": humano(espaco),
        "batch_dir": batch_dir,
    }
    gravar_json(os.path.join(batch_dir, "_manifest.json"), manifesto)
    print(f"\n  Movidos: {movidos:,}  |  Espaco: {humano(espaco)}")
    return manifesto


def listar_batches():
    if not os.path.isdir(DIR_QUAR):
        print("  (sem batches)")
        return
    print()
    print("=" * 88)
    print("  BATCHES DE QUARENTENA")
    print("=" * 88)
    for tipo in sorted(os.listdir(DIR_QUAR)):
        tipo_dir = os.path.join(DIR_QUAR, tipo)
        if not os.path.isdir(tipo_dir):
            continue
        for batch in sorted(os.listdir(tipo_dir)):
            bdir = os.path.join(tipo_dir, batch)
            man = os.path.join(bdir, "_manifest.json")
            n = tam = 0
            if os.path.isfile(man):
                with open(man, encoding="utf-8") as f:
                    n = json.load(f).get("movidos", 0)
            for dp, dn, fn in os.walk(bdir):
                for f in fn:
                    if f == "_manifest.json":
                        continue
                    try:
                        tam += os.path.getsize(os.path.join(dp, f))
                    except OSError:
                        pass
            print(f"  {tipo:<12} {batch:<20} {n:>6} ficheiros  {humano(tam):>12}")
    print("=" * 88)


def main():
    parser = argparse.ArgumentParser(description="Higienizar ACERVO")
    parser.add_argument("--tipo", choices=TIPOS, help="Tipo a higienizar")
    parser.add_argument("--lixo", action="store_true", help="So lixo")
    parser.add_argument("--dry-run", action="store_true", help="Simulacao (default)")
    parser.add_argument("--executar", action="store_true", help="Executar")
    parser.add_argument("--rank-max", type=int, help="Rank maximo")
    parser.add_argument("--raiz-only", help="So mover ficheiros dentro desta raiz")
    parser.add_argument("--force", action="store_true", help="Sem confirmacao")
    parser.add_argument("--listar", action="store_true", help="Listar batches")
    args = parser.parse_args()

    garantir_dirs()

    if args.listar:
        listar_batches()
        return

    dry = not args.executar

    if args.lixo:
        higienizar_lixo(dry_run=dry, raiz_only=args.raiz_only, force=args.force)
    elif args.tipo:
        higienizar_tipo(args.tipo, dry_run=dry, rank_max=args.rank_max,
                        raiz_only=args.raiz_only, force=args.force)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
