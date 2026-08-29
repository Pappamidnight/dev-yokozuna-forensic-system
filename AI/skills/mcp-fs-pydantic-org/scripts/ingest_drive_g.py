#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ingest_drive_g.py - Ingestao e Deduplicacao Criptografica das Pastas da Unidade G:/
Processa:
- G:\\nuno (Acervo Matriz de Processos, J-LAW, Minutas e PDFs)
- G:\\SP      LEA      FINP (Dossies SPARK, LEA Providencia Cautelar e Financeiro Pessoal)
"""
import os
import sys
import re
import json
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
DB_PATH = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "02_DADOS_ESTRUTURADOS" / "memoria_forense_unificada.db"
REPORTS_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "01_INDEX_E_RELATORIOS"

G_SOURCES = [
    Path(r"G:\nuno"),
    Path(r"G:\SP      LEA      FINP")
]

PROC_PATTERNS = [
    (re.compile(r'15547[\-_/\.]26', re.I), "15547/26.0T8LSB"),
    (re.compile(r'3719[\-_/\.]25', re.I), "3719/25.0T8LSB"),
    (re.compile(r'23142[\-_/\.]22', re.I), "23142/22.7T8LSB"),
    (re.compile(r'10153[\-_/\.]24', re.I), "10153/24.7T8LSB"),
    (re.compile(r'20203[\-_/\.]22', re.I), "20203/22.6T8LSB"),
    (re.compile(r'(lea|providencia|palmeira|cecilio)', re.I), "3719/25.0T8LSB"),
    (re.compile(r'(spark|venture|cmvm|finp|parassocial)', re.I), "CLUSTER_SOCIETARIO"),
]

IMG_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.heic'}
AUDIO_EXTS = {'.opus', '.mp3', '.m4a', '.wav'}
DOC_EXTS = {'.pdf', '.docx', '.doc', '.odt', '.txt', '.md', '.xlsx', '.xls', '.csv', '.eml', '.msg'}

IGNORE_CONTAINERS = {'.tibx', '.iso', '.vmdk', '.exe', '.msi', '.dll'}
IGNORE_DIRS = {'.git', '$RECYCLE.BIN', 'System Volume Information'}

DATE_REGEX = re.compile(r'\b(20\d{2})[-/.](0[1-9]|1[0-2])[-/.](0[1-9]|[12]\d|3[01])\b')


def make_long_path(p: str) -> str:
    ap = os.path.abspath(p)
    if ap.startswith("\\\\?\\"): return ap
    if ap.startswith("\\\\"): return "\\\\?\\UNC\\" + ap[2:]
    return "\\\\?\\" + ap


def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    try:
        lp = make_long_path(filepath)
        with open(lp, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""


def detect_proc(path_str: str) -> str:
    for pat, proc_id in PROC_PATTERNS:
        if pat.search(path_str):
            return proc_id
    return "GERAL_ACERVO"


def detect_cat(filename: str, path_str: str, ext: str) -> Tuple[str, str, str]:
    fl = filename.lower()
    pl = path_str.lower()
    
    if ext in IMG_EXTS:
        if 'whatsapp' in fl or 'img-202' in fl or 'chat' in pl:
            return "IMAGEM_WHATSAPP", "CORRESPONDENCIA", "MEDIA"
        if any(w in fl or w in pl for w in ['palmeira', 'cecilio', 'imovel', 'posse', 'vistoria']):
            return "IMAGEM_VISTORIA_IMOVEL", "PROVA_DOCUMENTAL", "ALTA"
        return "IMAGEM_GERAL", "PROVA_DOCUMENTAL", "GERAL"
        
    if ext in AUDIO_EXTS:
        return "AUDIO_VOZ", "CORRESPONDENCIA", "ALTA"
        
    if any(w in fl or w in pl for w in ['unicre', 'tpa', 'extrato', 'banco', 'fatura', 'recibo', 'iva', 'finp']):
        return "FINANCEIRO_COMPROVATIVO", "PROVA_DOCUMENTAL", "ALTA"
        
    if any(w in fl or w in pl for w in ['requerimento', 'citacao', 'oposicao', 'despacho', 'sentenca', 'recurso', 'citius']):
        return "PECA_JUDICIAL_CITIUS", "ATO_PROCESSUAL", "OFICIAL"
        
    if any(w in fl or w in pl for w in ['contrato', 'escritura', 'certidao', 'acordo', 'parassocial']):
        return "CONTRATO_OU_ESCRITURA", "PROVA_DOCUMENTAL", "OFICIAL"
        
    return "DOCUMENTO_GERAL", "DOCUMENTO_GERAL", "GERAL"


def run_drive_g_ingestion():
    print("=" * 80)
    print(" INGESTÃO FORENSE DA UNIDADE G:/ (G:\\nuno & G:\\SP LEA FINP)")
    print(f" Base SQLite : {DB_PATH}")
    print("=" * 80)

    if not DB_PATH.exists():
        print("[ERRO] Base de dados SQLite nao encontrada.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute("SELECT sha256 FROM evidencias WHERE sha256 IS NOT NULL AND sha256 != ''")
    seen_hashes = {r[0] for r in cur.fetchall()}

    total_scanned = 0
    total_inserted = 0
    total_dupes = 0
    now_iso = datetime.now().isoformat()

    batch = []
    stats_proc = {}
    stats_cat = {}

    valid_exts = IMG_EXTS | AUDIO_EXTS | DOC_EXTS

    for src_folder in G_SOURCES:
        if not src_folder.exists():
            print(f"[-] Pasta {src_folder} nao acessivel.")
            continue

        print(f"\n[SCAN] A processar pasta: {src_folder}...")

        for root, dirs, files in os.walk(make_long_path(str(src_folder))):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for f in files:
                ext = os.path.splitext(f.lower())[1]
                if ext in IGNORE_CONTAINERS or ext not in valid_exts:
                    continue

                full_p = os.path.join(root, f)
                clean_p = full_p.replace("\\\\?\\", "")

                try:
                    sz = os.path.getsize(full_p)
                except Exception:
                    sz = 0

                if sz < 100 or sz > 500 * 1024 * 1024:
                    continue

                total_scanned += 1
                sha = compute_sha256(full_p)
                if not sha:
                    continue

                is_dupe = 0
                if sha in seen_hashes:
                    is_dupe = 1
                    total_dupes += 1
                else:
                    seen_hashes.add(sha)

                proc_id = detect_proc(clean_p)
                cat, tipo_cpc, evidence_level = detect_cat(f, clean_p, ext)
                
                m_date = DATE_REGEX.search(f)
                data_canonica = f"{m_date.group(1)}-{m_date.group(2)}-{m_date.group(3)}" if m_date else None

                evidence_id = f"EV_{sha[:16]}"
                rel_p = f"Drive_G/{clean_p.replace('G:\\\\', '').replace('G:/', '')}"

                batch.append((
                    evidence_id,
                    proc_id,
                    clean_p,
                    rel_p,
                    f,
                    ext,
                    sha,
                    sz,
                    cat,
                    data_canonica,
                    tipo_cpc,
                    evidence_level,
                    is_dupe,
                    "",
                    now_iso
                ))

                stats_proc[proc_id] = stats_proc.get(proc_id, 0) + 1
                stats_cat[cat] = stats_cat.get(cat, 0) + 1
                total_inserted += 1

                if len(batch) >= 500:
                    cur.executemany("""
                    INSERT OR REPLACE INTO evidencias (
                        evidence_id, process_id, filepath, rel_path, filename, extension,
                        sha256, size_bytes, categoria, data_canonica, tipo_cpc,
                        evidence_level, is_duplicate, ocr_text, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, batch)
                    conn.commit()
                    batch = []
                    sys.stdout.write(f"\r -> Processados de G:/: {total_inserted} registos...")
                    sys.stdout.flush()

    if batch:
        cur.executemany("""
        INSERT OR REPLACE INTO evidencias (
            evidence_id, process_id, filepath, rel_path, filename, extension,
            sha256, size_bytes, categoria, data_canonica, tipo_cpc,
            evidence_level, is_duplicate, ocr_text, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, batch)
        conn.commit()

    conn.close()

    print(f"\n\n{'=' * 80}")
    print(" INGESTÃO DA UNIDADE G:/ CONCLUÍDA")
    print(f"{'=' * 80}")
    print(f" Total de Documentos/Fotos Analisados : {total_scanned}")
    print(f" Registos Inseridos no SQLite         : {total_inserted}")
    print(f" Duplicados Identificados              : {total_dupes}")
    print("\n DISTRIBUIÇÃO POR PROCESSO:")
    for pid, count in sorted(stats_proc.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {pid:<25}: {count:>6} registos")
    print("\n DISTRIBUIÇÃO POR CATEGORIA:")
    for cat, count in sorted(stats_cat.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {cat:<30}: {count:>6} registos")
    print(f"{'=' * 80}\n")

    report_file = REPORTS_DIR / "relatorio_ingestao_drive_g.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": now_iso,
            "total_scanned": total_scanned,
            "total_inserted": total_inserted,
            "duplicates": total_dupes,
            "by_process": stats_proc,
            "by_category": stats_cat
        }, f, indent=2, ensure_ascii=False)
    print(f"Relatório gravado em: {report_file}")


if __name__ == "__main__":
    run_drive_g_ingestion()
