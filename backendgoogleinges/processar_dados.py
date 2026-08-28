#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
processar_dados.py - Pipeline de Processamento, Renomeacao e Organizacao por Grupos Forenses
Analisa e categoriza todos os ficheiros em:
1. Ordem Cronologica Estrita
2. Tipologia Documental
3. Grupos Tematicos Forenses (Tribunal, Provas WhatsApp, Societario/Spark, Imoveis, Servicos)
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
    format="%(asctime)s - [PROCESSADOR-GRUPOS] - %(levelname)s - %(message)s"
)
logger = logging.getLogger("processar_dados")

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHRONO_DIR = PROCESSED_DIR / "01_CRONOLOGICO"
TYPOLOGY_DIR = PROCESSED_DIR / "02_POR_TIPOLOGIA"
GROUPS_DIR = PROCESSED_DIR / "03_POR_GRUPOS_TEMATICOS"
INDEX_DIR = PROCESSED_DIR / "_index"

for d in [CHRONO_DIR, TYPOLOGY_DIR, GROUPS_DIR, INDEX_DIR]:
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


def detect_thematic_group(filepath: Path, content_sample: str = "") -> str:
    """Classifica o documento num grupo tematico/operacional."""
    text = (filepath.name + " " + content_sample).lower()

    if any(k in text for k in ["15547", "3719", "citius", "citacao", "notificacao", "oficio", "tribunal"]):
        return "01_PROCESSO_JUDICIAL_15547"
    elif any(k in text for k in ["whatsapp", "filipe delgado", "nuno duarte", "chat", "confissao"]):
        return "02_PROVAS_CONFISSAO_WHATSAPP"
    elif any(k in text for k in ["spark", "celtis", "scr", "holding", "quota", "capital", "societario", "sociedade"]):
        return "03_SOCIETARIO_SPARK_VENTURE"
    elif any(k in text for k in ["palmeira", "cecilio", "sky", "heaven", "family", "penthouse", "arrendamento", "imovel", "propriedade"]):
        return "04_IMOVEIS_E_PATRIMONIO"
    elif any(k in text for k in ["agua", "epal", "edp", "luz", "gas", "contador", "fatura", "recibo", "despesa"]):
        return "05_DESPESAS_E_SERVICOS"
    return "06_DOCUMENTACAO_E_SUPORTE_GERAL"


def safe_copy(src: Path, dst: Path):
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
    logger.info("🚀 A INICIAR PROCESSAMENTO E ORGANIZACAO POR GRUPOS FORENSES")
    logger.info(f"📂 Origem: {RAW_DIR}")
    logger.info(f"📂 Destino: {PROCESSED_DIR}")
    logger.info("=" * 70)

    all_raw_files = [f for f in RAW_DIR.rglob("*") if f.is_file() and not f.name.endswith(".json")]
    if not all_raw_files:
        logger.warning("⚠️ Nenhum ficheiro encontrado em data/raw/ para processar.")
        return

    logger.info(f"Encontrados {len(all_raw_files)} ficheiros para análise e agrupamento.")

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
        doc_group = detect_thematic_group(f, sample_text)
        sha256 = get_sha256(f)
        clean_name = sanitize(f.stem)

        standard_name = f"{date_str}_{doc_type}_{clean_name}{ext}"

        records.append({
            "original_path": str(f),
            "original_name": f.name,
            "standard_name": standard_name,
            "date": date_str,
            "type": doc_type,
            "group": doc_group,
            "size_bytes": f.stat().st_size if f.exists() else 0,
            "sha256": sha256
        })

    # Ordenacao cronologica estrita
    records.sort(key=lambda r: (r["date"], r["group"], r["type"], r["standard_name"]))

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

        # 3. Copia por Grupo Tematico
        group_target_dir = GROUPS_DIR / r["group"]
        group_target_dir.mkdir(parents=True, exist_ok=True)
        safe_copy(Path(r["original_path"]), group_target_dir / chrono_name)

    # Gravar Master Chronology JSONL com Grupos
    master_jsonl = INDEX_DIR / "MASTER_CHRONOLOGY.jsonl"
    with open(master_jsonl, "w", encoding="utf-8") as out_f:
        for r in records:
            out_f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Gerar HTML Interativo com Filtros por Grupo
    generate_html_report(records, INDEX_DIR / "CRONOLOGIA_INTERATIVA.html")

    logger.info("=" * 70)
    logger.info(f"🎉 CONCLUIDO! {len(records)} ficheiros organizados em 3 vistas (Cronológica, Tipologia e Grupos Temáticos).")
    logger.info(f"📄 Indice Mestre: {master_jsonl}")
    logger.info(f"🌐 Relatorio Visual: {INDEX_DIR / 'CRONOLOGIA_INTERATIVA.html'}")
    logger.info("=" * 70)


def generate_html_report(records: List[Dict[str, Any]], out_path: Path):
    rows = []
    groups_count = {}
    for r in records:
        g = r["group"]
        groups_count[g] = groups_count.get(g, 0) + 1
        rows.append(f"""
        <tr data-group="{r['group']}" data-type="{r['type']}">
            <td><strong>{r['date']}</strong></td>
            <td><span class="group-tag">{r['group']}</span></td>
            <td><span class="badge {r['type']}">{r['type']}</span></td>
            <td><code>{r['chrono_name']}</code></td>
            <td><small>{r['original_name']}</small></td>
            <td>{r['size_bytes'] / 1024:.1f} KB</td>
            <td><small title="{r['sha256']}">{r['sha256'][:12]}...</small></td>
        </tr>
        """)

    group_cards = []
    for g, count in sorted(groups_count.items()):
        group_cards.append(f"""
        <div class="stat-card" onclick="filterGroup('{g}')" style="cursor:pointer;" title="Clique para filtrar">
            <div class="stat-val">{count}</div>
            <div class="stat-lbl">{g}</div>
        </div>
        """)

    html_content = f"""<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Cronologia e Grupos Temáticos Forenses - YKF</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }}
        h1 {{ color: #38bdf8; margin-bottom: 8px; }}
        .subtitle {{ color: #94a3b8; margin-bottom: 24px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }}
        .stat-card {{ background: #1e293b; padding: 16px; border-radius: 8px; border-left: 4px solid #38bdf8; transition: transform 0.2s, background 0.2s; }}
        .stat-card:hover {{ background: #293548; transform: translateY(-2px); }}
        .stat-val {{ font-size: 24px; font-weight: bold; color: #fff; }}
        .stat-lbl {{ font-size: 11px; color: #94a3b8; text-transform: uppercase; margin-top: 4px; }}
        .filters {{ margin-bottom: 16px; display: flex; gap: 10px; align-items: center; }}
        input[type="text"] {{ background: #1e293b; border: 1px solid #334155; color: #fff; padding: 8px 12px; border-radius: 6px; width: 300px; }}
        button {{ background: #38bdf8; color: #0f172a; font-weight: bold; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; }}
        button:hover {{ background: #7dd3fc; }}
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
        .group-tag {{ background: #334155; color: #38bdf8; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 600; }}
        code {{ background: #0f172a; padding: 2px 6px; border-radius: 4px; color: #38bdf8; font-size: 13px; }}
    </style>
</head>
<body>
    <h1>📋 Cronologia e Grupos Temáticos Forenses</h1>
    <div class="subtitle">Organização Automatizada de Documentos, Peças e Provas em 3 Vistas Estruturadas</div>
    
    <div class="stats">
        <div class="stat-card" onclick="resetFilter()" style="cursor:pointer; border-left-color: #4ade80;">
            <div class="stat-val">{len(records)}</div>
            <div class="stat-lbl">Todos os Documentos</div>
        </div>
        {"".join(group_cards)}
    </div>

    <div class="filters">
        <input type="text" id="search" placeholder="🔍 Pesquisar em todos os campos..." onkeyup="filterTable()">
        <button onclick="resetFilter()">Ver Todos</button>
    </div>

    <table id="docTable">
        <thead>
            <tr>
                <th>Data Canónica</th>
                <th>Grupo Temático</th>
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

    <script>
        function filterTable() {{
            let input = document.getElementById("search").value.toLowerCase();
            let rows = document.querySelectorAll("#docTable tbody tr");
            rows.forEach(r => {{
                r.style.display = r.innerText.toLowerCase().includes(input) ? "" : "none";
            }});
        }}
        function filterGroup(groupName) {{
            document.getElementById("search").value = groupName;
            filterTable();
        }}
        function resetFilter() {{
            document.getElementById("search").value = "";
            filterTable();
        }}
    </script>
</body>
</html>
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)


if __name__ == "__main__":
    process_all_files()
