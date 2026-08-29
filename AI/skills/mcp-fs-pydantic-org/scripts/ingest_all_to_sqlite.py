#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ingestor Mestre Forense SQLite (ingest_all_to_sqlite.py).
Varre integralmente todo o acervo do ecossistema Yokozuna Dev:
- Documentos Judiciais e Oficiais (PDF, DOCX, TXT, MD)
- Imagens e Fotografias de Vistorias/Posse (JPG, PNG, WEBP)
- Filmagens e Videos de Diligencias (MP4, MKV, MOV)
- Mensagens e Comunicacoes (WhatsApp, SMS, E-mails)
- Extratos Bancarios, Unicre/TPA e Societario
Deduplica por SHA-256, categoriza por processo judicial e persiste na base SQLite:
C:\\Users\\Yokozuna\\Dev\\OUTPUT_CENTRALIZADO\\02_DADOS_ESTRUTURADOS\\memoria_forense_unificada.db
"""
import os
import sys
import re
import json
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
CENTRAL_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO"
DATA_DIR = CENTRAL_DIR / "02_DADOS_ESTRUTURADOS"
REPORTS_DIR = CENTRAL_DIR / "01_INDEX_E_RELATORIOS"
DB_PATH = DATA_DIR / "memoria_forense_unificada.db"

# Pastas protegidas ou que nao contem provas
EXCLUDE_DIRS = {
    '.git', 'node_modules', '__pycache__', '.gemini', '.codex', 
    '.cache', '.kimi-work', '.kimi-webbridge', 'AppData'
}

# Regex de deteccao de processos judiciais
PROC_PATTERNS = [
    (re.compile(r'15547[\-_/\.]26', re.I), "15547/26.0T8LSB", "Acao de Reivindicacao e Propriedade Plena"),
    (re.compile(r'3719[\-_/\.]25', re.I), "3719/25.0T8LSB", "Providencia Cautelar e Tutela de Posse / Habitacao"),
    (re.compile(r'23142[\-_/\.]22', re.I), "23142/22.7T8LSB", "Nulidade Absoluta da Citacao e Domicilio Fiscal"),
    (re.compile(r'10153[\-_/\.]24', re.I), "10153/24.7T8LSB", "Oposicao a Execucao e Compensacao Unicre"),
    (re.compile(r'(spark|venture|cmvm|centenario|acordo_parassocial)', re.I), "CLUSTER_SOCIETARIO", "Procedimentos Societarios e Comerciais"),
]

# Regex de datas ISO e canonicas
DATE_REGEXES = [
    re.compile(r'\b(20\d{2})[-/.](0[1-9]|1[0-2])[-/.](0[1-9]|[12]\d|3[01])\b'),
    re.compile(r'\b(0[1-9]|[12]\d|3[01])[-/.](0[1-9]|1[0-2])[-/.](20\d{2})\b'),
]

IMG_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.heic'}
VID_EXTS = {'.mp4', '.avi', '.mkv', '.mov', '.3gp', '.wmv'}
DOC_EXTS = {'.pdf', '.docx', '.doc', '.odt', '.rtf', '.txt', '.md', '.msg', '.eml', '.xlsx', '.xls', '.csv'}

FIN_TERMS = ['unicre', 'tpa', 'banco', 'bancario', 'extrato', 'retencao', 'fatura', 'recibo', 'comprovativo', '105', '52', 'transferencia', 'iban', 'irs', 'irc']


def make_long_path(p: str) -> str:
    ap = os.path.abspath(p)
    if ap.startswith("\\\\?\\"):
        return ap
    if ap.startswith("\\\\"):
        return "\\\\?\\UNC\\" + ap[2:]
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


def detect_process(path_str: str) -> Tuple[str, str]:
    for pat, proc_id, proc_name in PROC_PATTERNS:
        if pat.search(path_str):
            return proc_id, proc_name
    return "GERAL_ACERVO", "Documentacao Geral do Acervo Forense"


def detect_date(filename: str, path_str: str) -> Optional[str]:
    for rgx in DATE_REGEXES:
        m = rgx.search(filename)
        if m:
            groups = m.groups()
            if len(groups[0]) == 4: # YYYY-MM-DD
                return f"{groups[0]}-{groups[1]}-{groups[2]}"
            else: # DD-MM-YYYY
                return f"{groups[2]}-{groups[1]}-{groups[0]}"
    return None


def detect_category(filename: str, path_str: str, ext: str) -> str:
    fl = filename.lower()
    pl = path_str.lower()
    
    if ext in IMG_EXTS:
        if any(w in fl or w in pl for w in ['whatsapp', 'msg', 'chat', 'screenshot', 'convers']):
            return "IMAGEM_WHATSAPP"
        if any(w in fl or w in pl for w in ['imovel', 'casa', 'obra', 'vistoria', 'posse', 'cecilio', 'palmeira', 'porta', 'fechadura', 'hotel']):
            return "IMAGEM_VISTORIA_IMOVEL"
        if any(w in fl or w in pl for w in ['citius', 'tribunal', 'financas', 'seguranca_social', 'portal']):
            return "IMAGEM_PORTAL_OFICIAL"
        return "IMAGEM_GERAL"
        
    if ext in VID_EXTS:
        if any(w in fl or w in pl for w in ['diligencia', 'esbulho', 'psp', 'policia', 'arrombamento', 'hotel', 'vistoria']):
            return "VIDEO_DILIGENCIA"
        return "VIDEO_GERAL"
        
    if any(w in fl or w in pl for w in FIN_TERMS):
        if 'unicre' in fl or 'tpa' in fl:
            return "FINANCEIRO_UNICRE_TPA"
        if 'extrato' in fl or 'banco' in fl:
            return "FINANCEIRO_EXTRATO_BANCARIO"
        return "FINANCEIRO_GERAL"
        
    if any(w in fl or w in pl for w in ['whatsapp', 'convers', 'chat']):
        return "COMUNICACAO_WHATSAPP"
    if any(w in fl or w in pl for w in ['email', 'e-mail', 'mail', 'notificacao']):
        return "COMUNICACAO_EMAIL"
        
    if any(w in fl or w in pl for w in ['citius', 'despacho', 'citacao', 'peticao', 'contestacao', 'oposicao', 'embargos', 'recurso', 'sentenca']):
        return "PECA_JUDICIAL_CITIUS"
        
    if any(w in fl or w in pl for w in ['contrato', 'escritura', 'acordo', 'parassocial', 'procuracao']):
        return "CONTRATO_OU_ESCRITURA"
        
    return "DOCUMENTO_GERAL"


def init_db(conn: sqlite3.Connection):
    cur = conn.cursor()
    
    # 1. Processos
    cur.execute("""
    CREATE TABLE IF NOT EXISTS processos (
        process_id TEXT PRIMARY KEY,
        nome TEXT,
        tribunal TEXT,
        juizo TEXT,
        objeto TEXT,
        titular TEXT,
        clausula_petrea TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    # 2. Tabela Mestra de Evidencias
    cur.execute("""
    CREATE TABLE IF NOT EXISTS evidencias (
        evidence_id TEXT PRIMARY KEY,
        process_id TEXT,
        filepath TEXT,
        rel_path TEXT,
        filename TEXT,
        extension TEXT,
        sha256 TEXT,
        size_bytes INTEGER,
        categoria TEXT,
        data_canonica TEXT,
        tipo_cpc TEXT,
        evidence_level TEXT,
        is_duplicate INTEGER DEFAULT 0,
        ocr_text TEXT,
        created_at TEXT,
        FOREIGN KEY (process_id) REFERENCES processos (process_id)
    )
    """)

    # Migrar colunas caso tabela ja existisse com schema antigo
    cur.execute("PRAGMA table_info(evidencias)")
    existing_cols = {row[1] for row in cur.fetchall()}
    
    expected_cols = {
        "rel_path": "TEXT",
        "extension": "TEXT",
        "categoria": "TEXT",
        "data_canonica": "TEXT",
        "is_duplicate": "INTEGER DEFAULT 0",
        "ocr_text": "TEXT"
    }
    for col, col_type in expected_cols.items():
        if col not in existing_cols:
            try:
                cur.execute(f"ALTER TABLE evidencias ADD COLUMN {col} {col_type}")
            except Exception:
                pass

    # Indices para pesquisa ultrarrapida
    cur.execute("CREATE INDEX IF NOT EXISTS idx_evidencias_proc ON evidencias(process_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_evidencias_cat ON evidencias(categoria);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_evidencias_data ON evidencias(data_canonica);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_evidencias_sha ON evidencias(sha256);")

    # Inserir processos nucleares
    processes = [
        ("15547/26.0T8LSB", "Acao de Reivindicacao e Propriedade Plena", "Comarca de Lisboa", "Juizo Central Civel", "Propriedade Plena, Direito Sucessorio e Litisconsorcio", "Teresa de Jesus Martins", "CLAUSULA_3_PROPRIEDADE_LITISCONSORCIO", "ATIVO", datetime.now().isoformat()),
        ("3719/25.0T8LSB", "Providencia Cautelar e Tutela de Posse / Habitacao", "Tribunal da Relacao de Lisboa", "6.ª Seccao", "Tutela Cautelar Urgente e Direito a Habitacao", "Nuno Miguel Silva Duarte", "CLAUSULA_4_TUTELA_CAUTELAR", "ATIVO", datetime.now().isoformat()),
        ("10153/24.7T8LSB", "Oposicao a Execucao e Compensacao Unicre", "Comarca de Lisboa", "Juizo de Execucao", "Inexigibilidade de Titulo e Retencao na Fonte TPA", "Nuno Miguel Silva Duarte", "CLAUSULA_1_INEXIGIBILIDADE", "ATIVO", datetime.now().isoformat()),
        ("23142/22.7T8LSB", "Nulidade Absoluta da Citacao e Domicilio Fiscal", "Comarca de Lisboa", "Juizo de Execucao", "Nulidade de Citacao por Morada Forjada perante Seguranca Social", "Nuno Miguel Silva Duarte", "CLAUSULA_2_NULIDADE_CITACAO", "ATIVO", datetime.now().isoformat()),
        ("CLUSTER_SOCIETARIO", "Dossie Societario SPARK / Venture Partners / CMVM", "N/A", "Comercial / Extrajudicial", "Acordos Parassociais, Quotas e Fluxos Financeiros", "Nuno Miguel Silva Duarte", "SOCIETARIO_SPARK", "ATIVO", datetime.now().isoformat()),
        ("GERAL_ACERVO", "Acervo Documental Geral Forense", "Geral", "Geral", "Provas Documentais e Suportes Diversos", "Dev Yokozuna", "GERAL", "ATIVO", datetime.now().isoformat()),
    ]
    for p in processes:
        cur.execute("""
        INSERT OR REPLACE INTO processos (process_id, nome, tribunal, juizo, objeto, titular, clausula_petrea, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, p)

    conn.commit()


def run_full_ingestion():
    print("=" * 80)
    print(" INGESTÃO TOTAL DO ACERVO FORENSE PARA BASE DE DADOS SQLITE UNIFICADA")
    print(f" Base SQLite : {DB_PATH}")
    print(f" Raiz Dev    : {DEV_ROOT}")
    print("=" * 80)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    init_db(conn)
    cur = conn.cursor()

    valid_exts = IMG_EXTS | VID_EXTS | DOC_EXTS | {'.bin'}

    # Pastas raiz a varrer
    scan_roots = [
        DEV_ROOT / "Projects",
        DEV_ROOT / "OUTPUT_CENTRALIZADO",
        DEV_ROOT / "backendgoogleinges",
        DEV_ROOT / "Backend"
    ]

    total_scanned = 0
    total_inserted = 0
    total_duplicates = 0
    now_iso = datetime.now().isoformat()

    stats_by_proc = {}
    stats_by_cat = {}

    batch = []
    seen_hashes = set()

    # Carregar hashes ja conhecidos da base
    cur.execute("SELECT sha256 FROM evidencias WHERE sha256 IS NOT NULL AND sha256 != ''")
    for r in cur.fetchall():
        seen_hashes.add(r[0])

    for root_dir in scan_roots:
        if not root_dir.exists():
            continue
        print(f"\n[SCAN] A varrer pasta: {root_dir}...")
        
        for root, dirs, files in os.walk(make_long_path(str(root_dir))):
            # Filtrar pastas excluidas
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for f in files:
                ext = os.path.splitext(f.lower())[1]
                if ext not in valid_exts and not f.startswith("File_"):
                    continue

                total_scanned += 1
                full_path = os.path.join(root, f)
                # remover prefixo Windows long path para caminho relativo legivel
                clean_full_path = full_path.replace("\\\\?\\", "")
                
                try:
                    rel_path = os.path.relpath(clean_full_path, str(DEV_ROOT))
                except Exception:
                    rel_path = clean_full_path

                # Ignorar ficheiros muito pequenos de sistema (< 100 bytes)
                try:
                    sz = os.path.getsize(full_path)
                except Exception:
                    sz = 0

                if sz < 100:
                    continue

                # Calculo de Hash
                sha = compute_sha256(full_path)
                if not sha:
                    continue

                is_dupe = 0
                if sha in seen_hashes:
                    is_dupe = 1
                    total_duplicates += 1
                else:
                    seen_hashes.add(sha)

                # Deteccao de Metadados
                proc_id, _ = detect_process(clean_full_path)
                data_canonica = detect_date(f, clean_full_path)
                categoria = detect_category(f, clean_full_path, ext)
                
                # Nivel probatorio CPC
                if categoria.startswith("PECA_JUDICIAL") or categoria.startswith("CONTRATO"):
                    evidence_level = "OFICIAL"
                    tipo_cpc = "ATO_PROCESSUAL"
                elif categoria.startswith("FINANCEIRO") or categoria.startswith("IMAGEM_VISTORIA"):
                    evidence_level = "ALTA"
                    tipo_cpc = "PROVA_DOCUMENTAL"
                elif categoria.startswith("COMUNICACAO") or categoria.startswith("IMAGEM_WHATSAPP"):
                    evidence_level = "MEDIA"
                    tipo_cpc = "CORRESPONDENCIA"
                else:
                    evidence_level = "GERAL"
                    tipo_cpc = "DOCUMENTO_GERAL"

                evidence_id = f"EV_{sha[:16]}"

                batch.append((
                    evidence_id,
                    proc_id,
                    clean_full_path,
                    rel_path,
                    f,
                    ext,
                    sha,
                    sz,
                    categoria,
                    data_canonica,
                    tipo_cpc,
                    evidence_level,
                    is_dupe,
                    "", # OCR
                    now_iso
                ))

                stats_by_proc[proc_id] = stats_by_proc.get(proc_id, 0) + 1
                stats_by_cat[categoria] = stats_by_cat.get(categoria, 0) + 1
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
                    sys.stdout.write(f"\r -> Processados e ingeridos: {total_inserted} ficheiros...")
                    sys.stdout.flush()

    # Inserir remanescentes
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
    print(" INGESTÃO CONCLUÍDA COM SUCESSO")
    print(f"{'=' * 80}")
    print(f" Total de Ficheiros Analisados : {total_scanned}")
    print(f" Total Inseridos na Base SQLite: {total_inserted}")
    print(f" Hashes Unicos Registados     : {len(seen_hashes)}")
    print(f" Duplicados Identificados      : {total_duplicates}")
    print("\n DISTRIBUIÇÃO POR PROCESSO JUDICIAL:")
    for pid, count in sorted(stats_by_proc.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {pid:<25}: {count:>6} registos")
    print("\n DISTRIBUIÇÃO POR TIPOLOGIA PROBATÓRIA:")
    for cat, count in sorted(stats_by_cat.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {cat:<30}: {count:>6} registos")
    print(f"{'=' * 80}\n")

    # Gerar relatorio JSON
    report_data = {
        "timestamp": now_iso,
        "database_path": str(DB_PATH),
        "total_scanned": total_scanned,
        "total_inserted": total_inserted,
        "unique_hashes": len(seen_hashes),
        "duplicates": total_duplicates,
        "by_process": stats_by_proc,
        "by_category": stats_by_cat
    }
    report_file = REPORTS_DIR / "relatorio_ingestao_sqlite_unificada.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    print(f"Relatorio estruturado gravado em: {report_file}")


if __name__ == "__main__":
    run_full_ingestion()
