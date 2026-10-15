#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verificar_acesso.py
Verifica que todos os ficheiros da DB estao acessiveis no storage
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime

CONFIG_PATH = Path(r"C:\ACERVO\config\migracao.json")
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

DB = Path(CONFIG["destino"]["db"])
STORAGE = Path(CONFIG["destino"]["storage"])
LOG_PATH = Path(CONFIG["destino"]["logs"]) / f"verificacao_acesso_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f"[{ts}] {msg}\n")

log("=" * 70)
log("  VERIFICACAO DE ACESSO")
log("=" * 70)

conn = sqlite3.connect(str(DB))
cur = conn.cursor()
cur.execute("SELECT id, nome, s3_key, tamanho FROM ficheiros")
registos = cur.fetchall()

log(f"  Registos na DB: {len(registos)}")

acessiveis = 0
ausentes = 0
tamanho_errado = 0
erros = []

for id_, nome, s3_key, tamanho_db in registos:
    caminho = STORAGE / s3_key

    if not caminho.exists():
        ausentes += 1
        erros.append({"id": id_, "nome": nome, "erro": "ausente"})
        continue

    try:
        tamanho_real = caminho.stat().st_size
        if tamanho_real != tamanho_db:
            tamanho_errado += 1
            erros.append({"id": id_, "nome": nome, "erro": "tamanho"})
            continue
        acessiveis += 1
    except Exception as e:
        erros.append({"id": id_, "nome": nome, "erro": str(e)})

conn.close()

log("")
log("  Resultado:")
log(f"    Acessiveis:      {acessiveis}")
log(f"    Ausentes:        {ausentes}")
log(f"    Tamanho errado:  {tamanho_errado}")
log(f"    Total erros:     {len(erros)}")

if erros:
    log("")
    log("  Primeiros 20 erros:")
    for e in erros[:20]:
        log(f"    {e['nome']}: {e['erro']}")

resultado = {
    "data": datetime.now().isoformat(),
    "total_registos": len(registos),
    "acessiveis": acessiveis,
    "ausentes": ausentes,
    "tamanho_errado": tamanho_errado,
    "erros": erros[:100]
}

resultado_path = Path(CONFIG["destino"]["logs"]) / "verificacao_acesso.json"
with open(resultado_path, 'w', encoding='utf-8') as f:
    json.dump(resultado, f, indent=2, ensure_ascii=False)

log("")
log("=" * 70)
log(f"  Resultado: {resultado_path}")
log(f"  Log: {LOG_PATH}")
log("=" * 70)

if ausentes == 0 and tamanho_errado == 0:
    log("")
    log("  STATUS: OK - Todos os ficheiros acessiveis")
else:
    log("")
    log("  STATUS: ATENCAO - Existem erros")
