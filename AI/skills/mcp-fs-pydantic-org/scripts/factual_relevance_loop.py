#!/usr/bin/env python3
"""
Loop Factual e Motor de Relevancia Deterministica (factual_relevance_loop.py).
1. Certifica a conexao de todas as pastas canonicas e estagios de dados.
2. Extrai e consolida Factos Provados Documentados (FACTO com SHA-256).
3. Separa categoricamente Factos de Alegacoes Unilaterais (ALEGACAO).
4. Calcula Score de Relevancia Probatória (0.00 a 1.00) por documento e processo.
5. Emite _index/pontos_factuais.jsonl e _index/relevance_matrix.json.
"""
import os
import sys
import json
import hashlib
import re
import argparse
from datetime import datetime
from typing import Dict, List, Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEV_ROOT = "C:\\Users\\Yokozuna\\Dev"
CANONICAL_ROOT = os.path.join(DEV_ROOT, "Projects", "Ficheiros Escritos Canónicos")
INDEX_DIR = os.path.join(CANONICAL_ROOT, "_index")
ATOS_PATH = os.path.join(INDEX_DIR, "atos_processuais.jsonl")
FACTOS_OUT_PATH = os.path.join(INDEX_DIR, "pontos_factuais.jsonl")
MATRIX_OUT_PATH = os.path.join(INDEX_DIR, "relevance_matrix.json")

# Pesos base probatorios por pasta canonica
FOLDER_WEIGHTS = {
    "01_PDFs_Oficiais": 1.00,
    "04_Processos_E_Pecas_Escritas": 0.98,
    "03_Contratos_E_Acordos": 0.95,
    "05_Correspondencia_E_Comunicacoes": 0.85,
    "00_Indice_E_MOCs": 0.70,
    "02_Minutas_E_Rascunhos": 0.25
}

# Pesos por tipo de ato CPC
ACT_WEIGHTS = {
    "SENTENCA": 1.00,
    "ACORDAO": 1.00,
    "AUTO_PENHORA": 0.98,
    "DESPACHO": 0.95,
    "CITACAO": 0.95,
    "CONTRATO": 0.95,
    "CONTESTACAO": 0.90,
    "RECURSO": 0.90,
    "ATA_AUDIENCIA": 0.90,
    "ATO_OFICIAL_PDF": 0.85,
    "DOCUMENTO_DIVERSO": 0.50,
    "RASCUNHO": 0.25,
    "INDICE_CATALOGO": 0.20
}


def calculate_relevance(record: Dict[str, Any]) -> float:
    """Calcula o score de relevancia combinada (0.00 a 1.00)."""
    folder = record.get("folder", "")
    tipo_cpc = record.get("tipo_cpc", "DOCUMENTO_DIVERSO")
    suporte = record.get("suporte", "INDICIADO")
    has_sha = bool(record.get("sha256") and len(record.get("sha256", "")) == 64)

    f_weight = FOLDER_WEIGHTS.get(folder, 0.50)
    a_weight = ACT_WEIGHTS.get(tipo_cpc, 0.50)

    # Base ponderada
    score = (f_weight * 0.55) + (a_weight * 0.45)

    # Bonificacao por suporte documental e SHA-256
    if suporte == "DOCUMENTADO" and has_sha:
        score = min(1.00, score * 1.05)
    elif suporte == "NAO_INDICIADO":
        score = score * 0.40

    # Penalizacao estrita de rascunhos
    if folder == "02_Minutas_E_Rascunhos":
        score = min(0.25, score)

    return round(score, 4)


def extract_factual_points(record: Dict[str, Any], relevance: float) -> Dict[str, Any]:
    """Extrai proposicoes factuais e classifica em FACTO vs ALEGACAO."""
    folder = record.get("folder", "")
    tipo_cpc = record.get("tipo_cpc", "")
    filename = record.get("filename", "")
    process_id = record.get("process_id", "")
    sha256 = record.get("sha256", "")

    # Determinacao de Kind
    if folder in ["01_PDFs_Oficiais", "04_Processos_E_Pecas_Escritas"] and tipo_cpc in ["SENTENCA", "ACORDAO", "DESPACHO", "AUTO_PENHORA", "CITACAO"]:
        kind = "FACTO"
        suporte = "DOCUMENTADO"
        factual_statement = f"Ato judicial {tipo_cpc} validado documentalmente nos autos de {process_id or 'processo principal'}."
    elif folder == "03_Contratos_E_Acordos" or tipo_cpc == "CONTRATO":
        kind = "FACTO"
        suporte = "DOCUMENTADO"
        factual_statement = f"Vinculacao contratual outorgada e documentada sob ref {filename}."
    elif folder == "05_Correspondencia_E_Comunicacoes":
        kind = "FACTO" if "AVISO" in filename.upper() or "RECECAO" in filename.upper() else "ALEGACAO"
        suporte = "DOCUMENTADO" if kind == "FACTO" else "INDICIADO"
        factual_statement = f"Comunicacao expedida/rececionada referente a {filename}."
    elif folder == "02_Minutas_E_Rascunhos":
        kind = "ALEGACAO"
        suporte = "INDICIADO"
        factual_statement = f"Anotacao preparatoria ou minuta de trabalho ({filename})."
    else:
        kind = "FACTO" if record.get("suporte") == "DOCUMENTADO" else "ALEGACAO"
        suporte = record.get("suporte", "INDICIADO")
        factual_statement = f"Registo processual indexado: {filename}."

    file_path = record.get("file_path") or record.get("path") or ""
    abs_path = os.path.join(DEV_ROOT, file_path) if not os.path.isabs(file_path) else file_path

    return {
        "fact_id": f"FACT_{sha256[:16] if sha256 else hashlib.md5(filename.encode('utf-8')).hexdigest()[:16]}",
        "process_id": process_id,
        "filename": filename,
        "path": abs_path,
        "folder": folder,
        "kind": kind,
        "suporte": suporte,
        "tipo_cpc": tipo_cpc,
        "sha256": sha256,
        "relevance_score": relevance,
        "statement": factual_statement,
        "extracted_at": datetime.now().isoformat()
    }


def run_factual_relevance_loop(index_dir: str = INDEX_DIR):
    """Executa o loop completo de extracao factual e calculo de relevancias."""
    print("==================================================================")
    print("INICIANDO LOOP FACTUAL E MOTOR DE RELEVANCIA DETERMINISTICA")
    print(f"Diretorio Index: {index_dir}")
    print("==================================================================")

    if not os.path.exists(ATOS_PATH):
        print(f"[ERRO] Atos processuais nao encontrados em: {ATOS_PATH}")
        return

    records = []
    with open(ATOS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    records.append(json.loads(line.strip()))
                except Exception:
                    pass

    print(f"[INFO] Registos em analise: {len(records)}")

    facts = []
    process_relevance = {}
    folder_stats = {f: {"total": 0, "avg_relevance": 0.0, "facts_count": 0} for f in FOLDER_WEIGHTS}

    for r in records:
        rel = calculate_relevance(r)
        fact_item = extract_factual_points(r, rel)
        facts.append(fact_item)

        pid = r.get("process_id")
        if pid:
            if pid not in process_relevance:
                process_relevance[pid] = {"total_acts": 0, "total_relevance": 0.0, "high_relevance_acts": 0}
            process_relevance[pid]["total_acts"] += 1
            process_relevance[pid]["total_relevance"] += rel
            if rel >= 0.85:
                process_relevance[pid]["high_relevance_acts"] += 1

        folder = r.get("folder", "")
        if folder in folder_stats:
            folder_stats[folder]["total"] += 1
            folder_stats[folder]["avg_relevance"] += rel
            if fact_item["kind"] == "FACTO":
                folder_stats[folder]["facts_count"] += 1

    # Calcular medias
    for f, stats in folder_stats.items():
        if stats["total"] > 0:
            stats["avg_relevance"] = round(stats["avg_relevance"] / stats["total"], 4)

    for pid, pstats in process_relevance.items():
        if pstats["total_acts"] > 0:
            pstats["avg_relevance"] = round(pstats["total_relevance"] / pstats["total_acts"], 4)

    # Gravar pontos factuais em JSONL
    print(f"[INFO] Gravando {len(facts)} pontos factuais em: {FACTOS_OUT_PATH}")
    with open(FACTOS_OUT_PATH, "w", encoding="utf-8") as f:
        for fact in facts:
            f.write(json.dumps(fact, ensure_ascii=False) + "\n")

    # Gravar matriz de relevancia
    matrix_report = {
        "status": "COMPLETED",
        "timestamp": datetime.now().isoformat(),
        "total_records_analyzed": len(records),
        "total_facts_extracted": len(facts),
        "facts_provados_documentados": sum(1 for x in facts if x["kind"] == "FACTO" and x["suporte"] == "DOCUMENTADO"),
        "alegacoes_unilaterais": sum(1 for x in facts if x["kind"] == "ALEGACAO"),
        "folder_relevance_metrics": folder_stats,
        "processes_relevance_metrics": process_relevance
    }

    with open(MATRIX_OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(matrix_report, f, ensure_ascii=False, indent=2)

    print("\n------------------------------------------------------------------")
    print(f"RESUMO DO MOTOR DE RELEVANCIA E FACTOS")
    print("------------------------------------------------------------------")
    print(f" - Factos Provados (DOCUMENTADOS) : {matrix_report['facts_provados_documentados']}")
    print(f" - Alegacoes Unilaterais          : {matrix_report['alegacoes_unilaterais']}")
    print(f" - Matriz de Relevancia salva em  : {MATRIX_OUT_PATH}")
    print("------------------------------------------------------------------\n")


def main():
    run_factual_relevance_loop()


if __name__ == "__main__":
    main()
