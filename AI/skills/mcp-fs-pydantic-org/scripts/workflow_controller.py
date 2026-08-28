#!/usr/bin/env python3
"""
Controlador Deterministico de Workflow e Conformidade de Resultados (workflow_controller.py).
Garante que todos os entregaveis obrigatorios foram gerados com exatidao absoluta (100% de conformidade).
"""
import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEV_ROOT = "C:\\Users\\Yokozuna\\Dev"
CANONICAL_ROOT = os.path.join(DEV_ROOT, "Projects", "Ficheiros Escritos Canónicos")
INDEX_DIR = os.path.join(CANONICAL_ROOT, "_index")
CONTROLLER_REPORT_OUT = os.path.join(INDEX_DIR, "workflow_controller_status.json")

MANDATORY_DELIVERABLES = [
    ("pipeline_report.json", "Relatorio do Scanner Deterministico"),
    ("atos_processuais.jsonl", "Atos Processuais Normalizados CPC"),
    ("pontos_factuais.jsonl", "Pontos Factuais e Proposicoes"),
    ("cronologia_mestre.jsonl", "Cronologia Ordenada ISO-8601"),
    ("relevance_matrix.json", "Matriz de Relevancia Probatoria"),
    ("frozen_judge_report.json", "Relatorio do Frozen Judge (100/100)"),
    ("eval_report.json", "Relatorio do Eval Pipeline (PASS)"),
    ("quality_factuality_report.json", "Relatorio do Agente de Factualidade")
]


def verify_workflow_outputs() -> Dict[str, Any]:
    print("==================================================================")
    print("INICIANDO CONTROLADOR DETERMINISTICO DE RESULTADOS E WORKFLOW")
    print(f"Diretorio Index Auditado: {INDEX_DIR}")
    print("==================================================================")

    results = []
    missing_count = 0
    all_valid = True

    for fname, desc in MANDATORY_DELIVERABLES:
        fpath = os.path.join(INDEX_DIR, fname)
        exists = os.path.exists(fpath)
        size = os.path.getsize(fpath) if exists else 0
        
        status = "OK" if (exists and size > 0) else "MISSING"
        if status == "MISSING":
            missing_count += 1
            all_valid = False

        results.append({
            "entregavel": fname,
            "descricao": desc,
            "tamanho_bytes": size,
            "status": status
        })

    # Verificar score do Frozen Judge
    fj_path = os.path.join(INDEX_DIR, "frozen_judge_report.json")
    fj_score = 0
    if os.path.exists(fj_path):
        try:
            with open(fj_path, "r", encoding="utf-8") as f:
                fj_data = json.load(f)
                fj_score = fj_data.get("frozen_judge_score", 0)
        except Exception:
            pass

    # Verificar status do Eval Pipeline
    eval_path = os.path.join(INDEX_DIR, "eval_report.json")
    eval_status = "UNKNOWN"
    if os.path.exists(eval_path):
        try:
            with open(eval_path, "r", encoding="utf-8") as f:
                ev_data = json.load(f)
                eval_status = ev_data.get("status", "UNKNOWN")
        except Exception:
            pass

    overall_pass = (all_valid and fj_score == 100 and eval_status == "PASS")

    report = {
        "status": "APPROVED" if overall_pass else "NEEDS_REFINEMENT",
        "verified_at": datetime.now().isoformat(),
        "total_deliverables_required": len(MANDATORY_DELIVERABLES),
        "total_deliverables_present": len(MANDATORY_DELIVERABLES) - missing_count,
        "frozen_judge_score": fj_score,
        "eval_pipeline_status": eval_status,
        "deliverables": results
    }

    with open(CONTROLLER_REPORT_OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Sincronizar outputs na pasta centralizada C:\Users\Yokozuna\Dev\OUTPUT_CENTRALIZADO
    try:
        from centralize_outputs import sync_centralized_outputs
        sync_centralized_outputs()
    except Exception as se:
        print(f"[AVISO] Nao foi possivel sincronizar pasta centralizada: {se}")

    print("\n------------------------------------------------------------------")
    print(f"STATUS DO CONTROLADOR DE RESULTADOS: [{report['status']}]")
    print("------------------------------------------------------------------")
    for r in results:
        print(f" - [{r['status']:<7}] {r['entregavel']:<30} ({r['tamanho_bytes']} bytes)")
    print("------------------------------------------------------------------")
    print(f" - Frozen Judge Score: {fj_score}/100")
    print(f" - Eval Pipeline     : {eval_status}")
    print(f"[INFO] Relatorio persistido em: {CONTROLLER_REPORT_OUT}\n")

    return report


def main():
    verify_workflow_outputs()


if __name__ == "__main__":
    main()
