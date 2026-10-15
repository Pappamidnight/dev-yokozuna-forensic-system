#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
classificar_tudo.py
Classifica todos os ficheiros na DB
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime

CONFIG_PATH = Path(r"C:\ACERVO\config\migracao.json")
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

DB = Path(CONFIG["destino"]["db"])
LOG_PATH = Path(CONFIG["destino"]["logs"]) / f"classificacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f"[{ts}] {msg}\n")

log("=" * 70)
log("  CLASSIFICACAO")
log("=" * 70)

conn = sqlite3.connect(str(DB))
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE ficheiros ADD COLUMN categoria TEXT")
except:
    pass

cur.execute("SELECT id, nome FROM ficheiros WHERE categoria IS NULL")
pendentes = cur.fetchall()
log(f"  Pendentes: {len(pendentes)}")

def classificar_tipo(nome):
    nome = nome.lower()
    ext = Path(nome).suffix

    if ext in ['.pdf', '.docx']:
        if any(x in nome for x in ['sentenca', 'acordao', 'tribunal']):
            return 'DOC_OFICIAL'
        return 'DOC_JURIDICO'
    if ext in ['.json', '.yaml', '.yml']:
        if 'schema' in nome: return 'SCHEMA'
        if 'config' in nome: return 'CONFIG'
        return 'METADADOS'
    if ext in ['.py', '.js', '.ps1', '.sh']: return 'CODIGO_FONTE'
    if ext == '.md': return 'DOCUMENTACAO'
    if ext in ['.db', '.sqlite', '.duckdb']: return 'BASE_DADOS'
    if ext in ['.jpg', '.png', '.mp4', '.mp3', '.wav']: return 'MEDIA'
    if ext in ['.xlsx', '.csv']: return 'DADOS'
    return 'DESCONHECIDO'

atualizados = 0
for id_, nome in pendentes:
    cat = classificar_tipo(nome)
    cur.execute("UPDATE ficheiros SET categoria = ? WHERE id = ?", (cat, id_))
    atualizados += 1

conn.commit()

cur.execute("SELECT categoria, COUNT(*) FROM ficheiros GROUP BY categoria ORDER BY COUNT(*) DESC")
stats = cur.fetchall()

log("")
log("  Distribuicao por categoria:")
for cat, count in stats:
    log(f"    {cat:20} {count:6}")

conn.close()

log("")
log("=" * 70)
log(f"  Classificados: {atualizados}")
log(f"  Log: {LOG_PATH}")
log("=" * 70)
