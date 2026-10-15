#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
proteger_sistema.py
Protege ficheiros criticos do sistema antes de qualquer limpeza
"""

import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime

CONFIG_PATH = Path(r"C:\ACERVO\config\migracao.json")
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

BASE = Path(CONFIG["destino"]["base"])
BACKUPS = Path(CONFIG["protecoes"]["backup_destino"])
LOG_PATH = Path(CONFIG["destino"]["logs"]) / f"protecao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f"[{ts}] {msg}\n")

log("=" * 70)
log("  PROTECAO DO SISTEMA")
log("=" * 70)

BACKUPS.mkdir(parents=True, exist_ok=True)
data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = BACKUPS / f"backup_{data_hora}"
backup_dir.mkdir(parents=True, exist_ok=True)

criticos = [
    BASE / "config" / "migracao.json",
    BASE / "config" / "s3.yaml",
    BASE / "config" / "database.yaml",
    BASE / "config" / "logging.yaml",
    BASE / ".env",
    BASE / "db" / "acervo.db",
]

log("")
log("  Ficheiros a proteger:")

hashes = {}
for f in criticos:
    if not f.exists():
        log(f"    AUSENTE: {f}")
        continue

    h = hashlib.sha256(f.read_bytes()).hexdigest()
    hashes[str(f)] = h

    destino = backup_dir / f.name
    shutil.copy2(f, destino)
    log(f"    OK: {f.name} ({h[:16]}...)")

manifesto = {
    "data": datetime.now().isoformat(),
    "backup_dir": str(backup_dir),
    "ficheiros": hashes
}

manifesto_path = backup_dir / "manifesto.json"
with open(manifesto_path, 'w', encoding='utf-8') as f:
    json.dump(manifesto, f, indent=2, ensure_ascii=False)

log("")
log("=" * 70)
log(f"  Backup: {backup_dir}")
log(f"  Manifesto: {manifesto_path}")
log(f"  Log: {LOG_PATH}")
log("=" * 70)

log("")
log("  STATUS: Ficheiros criticos protegidos")
log("  Pode agora executar limpeza com seguranca")
