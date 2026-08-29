#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai_forensic_ingestor.py - Ingestor Universal Continuo de Documentos e Provas Forenses.
Monitoriza, cataloga metadados, calcula hashes SHA-256 e alimenta a memoria unificada SQLite.
Zero emojis conforme PROTOCOL.md e AGENTS.md.
"""

import os
import sys
import hashlib
import sqlite3
from pathlib import Path
from typing import Dict, List, Any

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
OUTPUT_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO"
DB_PATH = OUTPUT_DIR / "02_DADOS_ESTRUTURADOS" / "memoria_forense_unificada.db"
WATCH_DIRS = [
    OUTPUT_DIR / "04_DOCUMENTOS_CITIUS_E_PECAS",
    OUTPUT_DIR / "03_PROVAS_SELECIONADAS_POR_PROCESSO",
    OUTPUT_DIR / "05_PDFS_GERADOS_PARA_IMPRESSAO",
    OUTPUT_DIR / "01_INDEX_E_RELATORIOS"
]

def calcular_sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""

def classificar_categoria(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    name = file_path.name.lower()
    if ext == ".pdf":
        if any(w in name for w in ["despacho", "acordao", "citacao", "notificacao", "sentenca"]):
            return "ATO_JUDICIAL_CITIUS"
        return "DOCUMENTO_PDF_OFICIAL"
    elif ext in [".xls", ".xlsx", ".csv"]:
        return "REGISTO_FINANCEIRO_CONTRATOS"
    elif ext in [".png", ".jpg", ".jpeg"]:
        return "PROVA_FOTOGRAFICA_IMAGEM"
    elif ext in [".mp4", ".mov"]:
        return "PROVA_VIDEO_VISTORIA"
    elif ext in [".mp3", ".wav", ".m4a", ".opus"]:
        return "PROVA_AUDIO_TRANSCRICAO"
    elif ext == ".docx":
        return "PECA_JUDICIAL_EDITAVEL"
    elif ext in [".md", ".txt"]:
        return "RELATORIO_PERICIAL_MARKDOWN"
    return "EVIDENCIA_DIVERSA"

def executar_ingestao():
    print("=" * 80, flush=True)
    print(" INGESTOR UNIVERSAL FORENSE: A ATUALIZAR ACERVO DOCUMENTAL", flush=True)
    print("=" * 80, flush=True)

    if not DB_PATH.exists():
        print(f"[!] Base de dados nao encontrada em: {DB_PATH}", flush=True)
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    novos = 0
    atualizados = 0

    for d in WATCH_DIRS:
        if not d.exists():
            continue
        for f in d.rglob("*"):
            if f.is_file() and "node_modules" not in str(f) and ".git" not in str(f):
                try:
                    rel = str(f.relative_to(DEV_ROOT))
                    sha = calcular_sha256(f)
                    size = f.stat().st_size
                    cat = classificar_categoria(f)
                    ext = f.suffix.lower()
                    
                    cur.execute("SELECT sha256 FROM evidencias WHERE rel_path = ?", (rel,))
                    row = cur.fetchone()

                    if row is None:
                        cur.execute("""
                            INSERT INTO evidencias (evidence_id, process_id, filepath, filename, sha256, size_bytes, tipo_cpc, evidence_level, raw_read_only, created_at, rel_path, extension, categoria, is_duplicate)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, datetime('now'), ?, ?, ?, 0)
                        """, (f"EV_{sha[:12]}", "MULTI_PROCESSO", str(f), f.name, sha, size, "DOCUMENTO", "OFICIAL", rel, ext, cat))
                        novos += 1
                    elif row[0] != sha:
                        cur.execute("UPDATE evidencias SET sha256 = ?, size_bytes = ?, categoria = ? WHERE rel_path = ?", (sha, size, cat, rel))
                        atualizados += 1
                except Exception:
                    pass

    conn.commit()
    conn.close()

    print(f"[+] Ingestao concluida com sucesso.", flush=True)
    print(f"[+] Novos ficheiros catalogados: {novos}", flush=True)
    print(f"[+] Ficheiros atualizados com novos hashes: {atualizados}", flush=True)
    print("=" * 80, flush=True)

if __name__ == "__main__":
    executar_ingestao()
