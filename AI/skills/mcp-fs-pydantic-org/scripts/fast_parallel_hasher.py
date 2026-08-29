#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fast_parallel_hasher.py - Motor de Alta Velocidade para Scan e Calculo Criptografico de Hashes (SHA-256 e MD5).
Utiliza processamento paralelo multi-core (ProcessPoolExecutor), streaming de buffers optimizado (1MB chunks)
e suporte total a Windows Long Paths (\\?\\).
"""
import os
import sys
import time
import hashlib
import sqlite3
import concurrent.futures
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional, Dict

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
DB_PATH = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "02_DADOS_ESTRUTURADOS" / "memoria_forense_unificada.db"
OUTPUT_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "01_INDEX_E_RELATORIOS"

TARGET_ROOTS = [
    r"C:\Users\Yokozuna\Dev\Projects\Ficheiros Escritos Canónicos",
    r"C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO",
    r"C:\Users\Yokozuna\OneDrive\GESTAO",
    r"C:\Users\Yokozuna\OneDrive\Imagens",
    r"J:\SP      LEA      FINP - Cópia",
    r"J:\SPARK LEGAL",
    r"J:\audios",
    r"F:\defesa",
    r"F:\defesa providencia cautelar"
]

VALID_EXTS = {
    '.pdf', '.docx', '.doc', '.odt', '.txt', '.md', '.xlsx', '.xls', '.csv',
    '.jpg', '.jpeg', '.png', '.webp', '.heic', '.mp4', '.opus', '.mp3',
    '.eml', '.msg', '.json', '.sql'
}

IGNORE_DIRS = {'.git', '$recycle.bin', 'system volume information', '__pycache__', '.tmp.driveupload'}


def make_long_path(p: str) -> str:
    ap = os.path.abspath(p)
    if ap.startswith("\\\\?\\"): return ap
    if ap.startswith("\\\\"): return "\\\\?\\UNC\\" + ap[2:]
    return "\\\\?\\" + ap


def hash_single_file(filepath: str) -> Optional[Tuple[str, str, str, int, str]]:
    """Calcula SHA-256 e MD5 com buffer de 1MB por ficheiro."""
    try:
        lp = make_long_path(filepath)
        stat = os.stat(lp)
        sz = stat.st_size
        if sz < 50 or sz > 1024 * 1024 * 1024:  # Ignora vazios ou > 1GB para ultra-velocidade
            return None

        sha256 = hashlib.sha256()
        md5 = hashlib.md5()
        with open(lp, "rb", buffering=1048576) as f:
            while chunk := f.read(1048576):
                sha256.update(chunk)
                md5.update(chunk)

        clean_p = filepath.replace("\\\\?\\", "")
        filename = os.path.basename(clean_p)
        ext = os.path.splitext(filename.lower())[1]

        return (clean_p, filename, ext, sz, sha256.hexdigest(), md5.hexdigest())
    except Exception:
        return None


def collect_file_list(roots: List[str]) -> List[str]:
    file_list = []
    print("[SCAN] A varrer diretorios das raizes forenses...")
    for r in roots:
        p = Path(r)
        if not p.exists():
            continue
        print(f" -> A indexar: {r}")
        for root, dirs, files in os.walk(make_long_path(str(p))):
            dirs[:] = [d for d in dirs if d.lower() not in IGNORE_DIRS]
            for f in files:
                ext = os.path.splitext(f.lower())[1]
                if ext in VALID_EXTS:
                    file_list.append(os.path.join(root, f))
    return file_list


def run_fast_hasher():
    t0 = time.time()
    print("=" * 80)
    print(" MOTOR PARALELO DE SCAN E HASH FORENSE (ULTRA-FAST MULTI-CORE)")
    print(f" Base SQLite: {DB_PATH}")
    print("=" * 80)

    files_to_process = collect_file_list(TARGET_ROOTS)
    total_files = len(files_to_process)
    print(f"\n[+] Total de ficheiros elegiveis para hashing rapido: {total_files}")

    if total_files == 0:
        print("[-] Nenhum ficheiro encontrado.")
        return

    # Processamento Paralelo Multi-Core
    workers = min(os.cpu_count() or 4, 16)
    print(f"[*] A iniciar calculo paralelo de SHA-256 e MD5 com {workers} cores...")

    manifest_csv = OUTPUT_DIR / "MANIFESTO_GLOBAL_HASHES_RAPIDO.csv"
    results = []
    processed_count = 0
    total_bytes = 0

    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(hash_single_file, f): f for f in files_to_process}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            processed_count += 1
            if res:
                results.append(res)
                total_bytes += res[3]

            if processed_count % 500 == 0 or processed_count == total_files:
                elapsed = time.time() - t0
                fps = processed_count / (elapsed or 1)
                sys.stdout.write(f"\r -> Hashes calculados: {processed_count}/{total_files} ({fps:.1f} ficheiros/seg)...")
                sys.stdout.flush()

    elapsed = time.time() - t0
    print(f"\n\n[+] Concluido em {elapsed:.2f} segundos ({len(results)} hashes gerados com sucesso).")

    # Persistencia no Manifesto CSV de Alta Velocidade
    print(f"[*] A gravar manifesto CSV: {manifest_csv}...")
    with open(manifest_csv, "w", encoding="utf-8") as f:
        f.write("filepath,filename,extension,size_bytes,sha256,md5,timestamp\n")
        now_iso = datetime.now().isoformat()
        for r in results:
            clean_path = r[0].replace('"', '""')
            clean_name = r[1].replace('"', '""')
            f.write(f'"{clean_path}","{clean_name}",{r[2]},{r[3]},{r[4]},{r[5]},{now_iso}\n')

    # Persistencia em SQLite
    if DB_PATH.exists():
        print(f"[*] A atualizar base relacional SQLite...")
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        now_iso = datetime.now().isoformat()
        db_batch = []
        for r in results:
            ev_id = f"EV_{r[4][:16]}"
            db_batch.append((
                ev_id,
                "GERAL_ACERVO",
                r[0],
                os.path.basename(r[0]),
                r[1],
                r[2],
                r[4],
                r[3],
                "DOCUMENTO_GERAL",
                None,
                "PROVA_DOCUMENTAL",
                "OFICIAL",
                0,
                "",
                now_iso
            ))
        cur.executemany("""
        INSERT OR REPLACE INTO evidencias (
            evidence_id, process_id, filepath, rel_path, filename, extension,
            sha256, size_bytes, categoria, data_canonica, tipo_cpc,
            evidence_level, is_duplicate, ocr_text, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, db_batch)
        conn.commit()
        conn.close()
        print(f"[+] {len(db_batch)} registos consolidados na base SQLite.")

    print("=" * 80)
    print(" HASHING CRIPTOGRÁFICO CONCLUÍDO COM SUCESSO")
    print(f" Total Processado : {len(results)} ficheiros ({total_bytes / (1024*1024):.2f} MB)")
    print(f" Manifesto CSV    : {manifest_csv}")
    print(f" Base SQLite      : {DB_PATH}")
    print("=" * 80)


if __name__ == "__main__":
    run_fast_hasher()
