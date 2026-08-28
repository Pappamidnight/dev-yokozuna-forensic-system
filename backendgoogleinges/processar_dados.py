#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
processar_dados.py - Pipeline de Processamento, Renomeacao e Cronologia Forense
Analisa todos os ficheiros descarregados da Google Drive e Gmail,
extrai datas canonicas, renomeia as folhas e organiza cronologicamente.
"""

import os
import re
import sys
import json
import stat
import shutil
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

# Configuracao de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [PROCESSADOR-DADOS] - %(levelname)s - %(message)s"
)
logger = logging.getLogger("processar_dados")

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHRONO_DIR = PROCESSED_DIR / "01_CRONOLOGICO"
TYPOLOGY_DIR = PROCESSED_DIR / "02_POR_TIPOLOGIA"
PAGES_DIR = PROCESSED_DIR / "03_FOLHAS_INDIVIDUAIS"
INDEX_DIR = PROCESSED_DIR / "_index"

for d in [CHRONO_DIR, TYPOLOGY_DIR, PAGES_DIR, INDEX_DIR]:
    d.mkdir(parents=True, exist_ok=True)

DATE_REGEXES = [
    re.compile(r"\b(?P<year>20\d{2})[-/.](?P<month>\d{1,2})[-/.](?P<day>\d{1,2})\b"),
    re.compile(r"\b(?P<day>\d{1,2})[-/.](?P<month>\d{1,2})[-/.](?P<year>20\d{2})\b"),
    re.compile(r"\b(?P<day>\d{1,2})\s+de\s+(?P<month_name>janeiro|fevereiro|março|marco|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s+de\s+(?P<year>20\d{2})\b", re.I)
]

MONTH_MAP = {
    "janeiro": "01", "fevereiro": "02", "março": "03", "marco": "03", "abril": "04",
    "maio": "05", "junho": "06", "julho": "07", "agosto": "08", "setembro": "09",
    "outubro": "10", "novembro": "11", "dezembro": "12"
}


def sanitize(text: str) -> str:
    clean = re.sub(r'[\\/*?:"<>|]', "_", text)
    clean = re.sub(r'\s+', '_', clean.strip())
    return clean[:80]


def get_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""


def detect_canonical_date(filepath: Path, content_sample: str = "") -> str:
    filename = filepath.name
    for rgx in DATE_REGEXES:
        m = rgx.search(filename)
        if m:
            gd = m.groupdict()
            y = gd.get("year")
            if "month_name" in gd and gd["month_name"]:
                mo = MONTH_MAP.get(gd["month_name"].lower(), "01")
            else:
                mo = f"{int(gd.get('month', 1)):02d}"
            d = f"{int(gd.get('day', 1)):02d}"
            return f"{y}-{mo}-{d}"

    if content_sample:
        for rgx in DATE_REGEXES:
            m = rgx.search(content_sample[:2000])
            if m:
                gd = m.groupdict()
                y = gd.get("year")
                if "month_name" in gd and gd["month_name"]:
                    mo = MONTH_MAP.get(gd["month_name"].lower(), "01")
                else:
                    mo = f"{int(gd.get('month', 1)):02d}"
                d = f"{int(gd.get('day', 1)):02d}"
                return f"{y}-{mo}-{d}"

    try:
        mtime = filepath.stat().st_mtime
        return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
    except Exception:
        return "2026-08-28"


def detect_document_type(filepath: Path, content_sample: str = "") -> str:
    text = (filepath.name + " " + content_sample).lower()
    if any(k in text for k in ["citacao", "citação", "notificacao", "notificação", "oficio", "ofício", "tribunal", "citius", "peca", "peça", "despacho"]):
        return "PECA_JUDICIAL"
    elif any(k in text for k in ["whatsapp", "email", "chat", "conversa", "mensagem"]):
        return "COMUNICACAO"
    elif any(k in text for k in ["factos", "prova", "certidao", "certidão", "extrato", "fatura", "recibo", "contrato", "ata"]):
        return "PROVA_DOCUMENTAL"
    elif any(k in text for k in ["spark", "celtis", "scr", "holding", "quota", "sociedade"]):
        return "SOCIETARIO"
    return "DOCUMENTO_GERAL"


def safe_copy(src: Path, dst: Path):
    """Copia ficheiro garantindo que permissões de escrita são tratadas."""
    try:
        if dst.exists():
            try:
                os.chmod(dst, stat.S_IWRITE | stat.S_IREAD)
            except Exception:
                pass
        shutil.copy2(src, dst)
    except Exception as e:
        logger.warning(f"Aviso ao copiar {src.name} para {dst.name}: {e}")


def process_all_files():
    logger.info("=" * 70)
    logger.info("🚀 A INICIAR PROCESSAMENTO E ORGANIZACAO CRONOLOGICA FORENSE")
    logger.info(f"📂 Origem: {RAW_DIR}")
    logger.info(f"📂 Destino: {PROCESSED_DIR}")
    logger.info("=" * 70)

    all_raw_files = [f for f in RAW_DIR.rglob("*") if f.is_file() and not f.name.endswith(".json")]
    if not all_raw_files:
        logger.warning("⚠️ Nenhum ficheiro encontrado em data/raw/ para processar.")
        return

    logger.info(f"Encontrados {len(all_raw_files)} ficheiros brutos em data/raw/ para análise.")

    records = []

    for f in all_raw_files:
        sample_text = ""
        ext = f.suffix.lower()
        if ext in [".txt", ".md", ".jsonl", ".csv"]:
            try:
                with open(f, "r", encoding="utf-8", errors="ignore") as fh:
                    sample_text = fh.read(4000)
            except Exception:
                pass

        date_str = detect_canonical_date(f, sample_text)
        doc_type = detect_document_type(f, sample_text)
        sha256 = get_sha256(f)
        clean_name = sanitize(f.stem)

        standard_name = f"{date_str}_{doc_type}_{clean_name}{ext}"

        records.append({
            "original_path": str(f),
            "original_name": f.name,
            "standard_name": standard_name,
            "date": date_str,
            "type": doc_type,
            "size_bytes": f.stat().st_size if f.exists() else 0,
            "sha256": sha256
        })

    # Ordenacao cronologica estrita
    records.sort(key=lambda r: (r["date"], r["type"], r["standard_name"]))

    for idx, r in enumerate(records, start=1):
        seq_prefix = f"{idx:04d}_"
        chrono_name = seq_prefix + r["standard_name"]
        r["chrono_name"] = chrono_name

        # 1. Copia Cronologica
        chrono_target = CHRONO_DIR / chrono_name
        safe_copy(Path(r["original_path"]), chrono_target)

        # 2. Copia por Tipologia
        type_target_dir = TYPOLOGY_DIR / r["type"]
        type_target_dir.mkdir(parents=True, exist_ok=True)
        safe_copy(Path(r["original_path"]), type_target_dir / r["standard_name"])

    # Gravar Master Chronology JSONL
    master_jsonl = INDEX_DIR / "MASTER_CHRONOLOGY.jsonl"
    with open(master_jsonl, "w", encoding="utf-8") as out_f:
        for r in records:
            out_f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Gerar HTML Interativo
    generate_html_report(records, INDEX_DIR / "CRONOLOGIA_INTERATIVA.html")

    logger.info("=" * 70)
    logger.info(f"🎉 CONCLUIDO! {len(records)} ficheiros organizados com sucesso.")
    logger.info(f"📄 Indice Mestre: {master_jsonl}")
    logger.info(f"🌐 Relatorio Visual: {INDEX_DIR / 'CRONOLOGIA_INTERATIVA.html'}")
    logger.info("=" * 70)


def generate_html_report(records: List[Dict[str, Any]], out_path: Path):
    rows = []
    for r in records:
        rows.append(f"""
        <tr>
            <td><strong>{r['date']}</strong></td>
            <td><span class="badge {r['type']}">{r['type']}</span></td>
            <td><code>{r['chrono_name']}</code></td>
            <td><small>{r['original_name']}</small></td>
            <td>{r['size_bytes'] / 1024:.1f} KB</td>
            <td><small title="{r['sha256']}">{r['sha256'][:12]}...</small></td>
        </tr>
        """)

    html_content = f"""<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Cronologia Mestre Forense - YKF</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }}
        h1 {{ color: #38bdf8; margin-bottom: 8px; }}
        .subtitle {{ color: #94a3b8; margin-bottom: 24px; }}
        .stats {{ display: flex; gap: 16px; margin-bottom: 24px; }}
        .stat-card {{ background: #1e293b; padding: 16px 24px; border-radius: 8px; border-left: 4px solid #38bdf8; }}
        .stat-val {{ font-size: 24px; font-weight: bold; color: #fff; }}
        .stat-lbl {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; }}
        table {{ width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ background: #0f172a; color: #94a3b8; font-weight: 600; text-transform: uppercase; font-size: 12px; }}
        tr:hover {{ background: #243247; }}
        .badge {{ padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
        .PECA_JUDICIAL {{ background: #dc2626; color: #fff; }}
        .PROVA_DOCUMENTAL {{ background: #2563eb; color: #fff; }}
        .COMUNICACAO {{ background: #16a34a; color: #fff; }}
        .SOCIETARIO {{ background: #d97706; color: #fff; }}
        .DOCUMENTO_GERAL {{ background: #64748b; color: #fff; }}
        code {{ background: #0f172a; padding: 2px 6px; border-radius: 4px; color: #38bdf8; font-size: 13px; }}
    </style>
</head>
<body>
    <h1>📋 Cronologia Mestre e Indice Forense</h1>
    <div class="subtitle">Processamento e Organizacao Cronologica de Provas e Folhas do Tribunal</div>
    <div class="stats">
        <div class="stat-card"><div class="stat-val">{len(records)}</div><div class="stat-lbl">Total de Documentos</div></div>
        <div class="stat-card"><div class="stat-val">{len(set(r['date'] for r in records))}</div><div class="stat-lbl">Datas Distintas</div></div>
        <div class="stat-card"><div class="stat-val">{sum(r['size_bytes'] for r in records) / (1024*1024):.2f} MB</div><div class="stat-lbl">Volume Total</div></div>
    </div>
    <table>
        <thead>
            <tr>
                <th>Data Canónica</th>
                <th>Tipologia</th>
                <th>Nome Renomeado (Cronológico)</th>
                <th>Ficheiro Original</th>
                <th>Tamanho</th>
                <th>Hash SHA-256</th>
            </tr>
        </thead>
        <tbody>
            {"".join(rows)}
        </tbody>
    </table>
</body>
</html>
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)


if __name__ == "__main__":
    process_all_files()
