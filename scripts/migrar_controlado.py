#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
migrar_controlado.py
Migra tudo do Desktop para C:\ACERVO\storage + DB
Respeita config_migracao.json
"""

import os
import sys
import json
import hashlib
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

CONFIG_PATH = Path(r"C:\ACERVO\config\migracao.json")

if not CONFIG_PATH.exists():
    print("ERRO: config_migracao.json nao encontrado")
    sys.exit(1)

with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

DESKTOP = Path(CONFIG["origem"]["caminho"])
STORAGE = Path(CONFIG["destino"]["storage"])
DB = Path(CONFIG["destino"]["db"])
PESSOAL = Path(CONFIG["pessoal"]["pasta"])
EXT_PESSOAIS = set(CONFIG["pessoal"]["extensoes"])

LOG_PATH = Path(CONFIG["destino"]["logs"]) / f"migracao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = f"[{ts}] {msg}"
    print(linha)
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(linha + "\n")

log("=" * 70)
log("  MIGRACAO CONTROLADA")
log("=" * 70)
log(f"  Origem:  {DESKTOP}")
log(f"  Destino: {STORAGE}")
log(f"  DB:      {DB}")
log(f"  Pessoal: {PESSOAL}")
log("")

log("[FASE 1/5] Mover ficheiros pessoais")
PESSOAL.mkdir(parents=True, exist_ok=True)

pessoais_movidos = 0
for f in DESKTOP.iterdir():
    if not f.is_file():
        continue
    if f.suffix.lower() in EXT_PESSOAIS:
        destino = PESSOAL / f.name
        if not destino.exists():
            try:
                shutil.move(str(f), str(destino))
                pessoais_movidos += 1
                log(f"  Movido: {f.name}")
            except Exception as e:
                log(f"  ERRO: {f.name} - {e}")

log(f"  Total pessoais: {pessoais_movidos}")
log("")

log("[FASE 2/5] Ligar a DB")
conn = sqlite3.connect(str(DB))
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM ficheiros")
inicial = cur.fetchone()[0]
log(f"  Registos iniciais: {inicial}")
log("")

log("[FASE 3/5] Migrar Desktop")
IGNORAR = {"Pessoal", "$RECYCLE.BIN", "System Volume Information", "desktop.ini"}

total = 0
importados = 0
duplicados = 0
erros = 0
bytes_total = 0

for root, dirs, files in os.walk(DESKTOP):
    dirs[:] = [d for d in dirs if d not in IGNORAR]
    root_path = Path(root)

    if "Pessoal" in root_path.parts:
        continue

    for nome in files:
        if nome in IGNORAR:
            continue

        f = root_path / nome
        total += 1

        try:
            dados = f.read_bytes()
            tamanho = len(dados)

            if tamanho == 0:
                continue

            hash_sha = hashlib.sha256(dados).hexdigest()
            hash_b3 = hashlib.blake2b(dados, digest_size=32).hexdigest()

            cur.execute("SELECT id FROM ficheiros WHERE hash_sha256 = ?", (hash_sha,))
            if cur.fetchone():
                duplicados += 1
                continue

            subdir = hash_sha[:2]
            destino = STORAGE / "files" / subdir / hash_sha
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(dados)

            s3_key = f"files/{subdir}/{hash_sha}"
            cur.execute("""
                INSERT INTO ficheiros (hash_sha256, hash_blake3, nome, s3_key, tamanho)
                VALUES (?, ?, ?, ?, ?)
            """, (hash_sha, hash_b3, f.name, s3_key, tamanho))

            importados += 1
            bytes_total += tamanho

            if total % 500 == 0:
                conn.commit()
                log(f"  {total} processados | {importados} importados | {duplicados} duplicados")

        except Exception as e:
            erros += 1
            if erros < 20:
                log(f"  ERRO: {f.name} - {e}")

conn.commit()

log("")
log(f"  Total processados: {total}")
log(f"  Importados:        {importados}")
log(f"  Duplicados:        {duplicados}")
log(f"  Erros:             {erros}")
log(f"  Bytes migrados:    {bytes_total / 1024 / 1024 / 1024:.2f} GB")
log("")

log("[FASE 4/5] Validar integridade")
cur.execute("SELECT COUNT(*) FROM ficheiros")
final = cur.fetchone()[0]
log(f"  Registos finais: {final}")
log(f"  Novos: {final - inicial}")

cur.execute("PRAGMA integrity_check")
integrity = cur.fetchone()[0]
log(f"  Integridade DB: {integrity}")

storage_files = [f for f in STORAGE.rglob("*") if f.is_file()]
log(f"  Ficheiros no storage: {len(storage_files)}")
log("")

conn.close()

log("[FASE 5/5] Resumo")
log("=" * 70)
log("  MIGRACAO CONCLUIDA")
log("=" * 70)
log(f"  Log: {LOG_PATH}")
log("=" * 70)

resultado = {
    "data": datetime.now().isoformat(),
    "total_processados": total,
    "importados": importados,
    "duplicados": duplicados,
    "erros": erros,
    "bytes_migrados": bytes_total,
    "registos_iniciais": inicial,
    "registos_finais": final,
    "pessoais_movidos": pessoais_movidos,
    "integridade_db": integrity,
    "log": str(LOG_PATH)
}

resultado_path = Path(CONFIG["destino"]["logs"]) / "ultima_migracao.json"
with open(resultado_path, 'w', encoding='utf-8') as f:
    json.dump(resultado, f, indent=2, ensure_ascii=False)

log(f"  Resultado guardado: {resultado_path}")
