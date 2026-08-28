#!/usr/bin/env python3
"""
Script de Loop Iterativo de Otimizacao e Validacao de Dados.
Executa os Loops A, B, C e D para enriquecer informacoes, calcular scores e eliminar inconsistencias.
"""
import os
import sys
import json
import argparse
from typing import Dict, List, Any


def run_optimization_loop(index_dir: str) -> Dict[str, Any]:
    """Executa o loop de otimizacao e validacao sobre os dados persistidos em _index/."""
    atos_path = os.path.join(index_dir, "atos_processuais.jsonl")
    cadeias_path = os.path.join(index_dir, "cadeias.json")
    
    if not os.path.exists(atos_path):
        return {"status": "ERRO", "mensagem": f"Ficheiro {atos_path} nao encontrado. Execute run_act_agents.py primeiro."}
        
    records = []
    with open(atos_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line.strip()))
                
    print(f"[LOOP A] Hashing e Deduplicacao: Analisando {len(records)} registos...")
    unique_hashes = set()
    dedup_count = 0
    clean_records = []
    
    for r in records:
        h = r.get("sha256")
        if h and h in unique_hashes:
            dedup_count += 1
            r["is_duplicate"] = True
        else:
            if h:
                unique_hashes.add(h)
            r["is_duplicate"] = False
        clean_records.append(r)
        
    print(f"[LOOP B] Validacao Semantica: Corrigindo inconsistencias de suporte e tipo...")
    corrected_count = 0
    for r in clean_records:
        if r.get("folder") == "02_Minutas_E_Rascunhos":
            if r.get("suporte") == "DOCUMENTADO":
                r["suporte"] = "INDICIADO"
                corrected_count += 1
            if r.get("tipo_cpc") == "DESPACHO":
                r["tipo_cpc"] = "RASCUNHO"
                corrected_count += 1

    # Persistir registos limpos e corrigidos de volta ao atos_processuais.jsonl
    with open(atos_path, "w", encoding="utf-8") as f:
        for r in clean_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            
    print(f"[LOOP C] Reconciliacao de Cadeias e Lacunas...")
    process_scores = {}
    by_process = {}
    for r in clean_records:
        pid = r.get("process_id")
        if pid:
            if pid not in by_process:
                by_process[pid] = []
            by_process[pid].append(r)
            
    for pid, acts in by_process.items():
        total_weight = sum(a.get("weight", 0.5) for a in acts)
        avg_weight = total_weight / len(acts) if acts else 0.0
        
        # Penalizacao por falta de atos essenciais
        act_types = set(a.get("tipo_cpc") for a in acts)
        has_despacho = "DESPACHO" in act_types
        has_citacao = "CITACAO" in act_types
        
        confidence_score = avg_weight * 100
        if not has_citacao:
            confidence_score *= 0.85  # penalizacao por lacuna de citacao
            
        process_scores[pid] = {
            "processo": pid,
            "total_atos": len(acts),
            "score_confianca": round(confidence_score, 2),
            "tem_despacho": has_despacho,
            "tem_citacao": has_citacao
        }
        
    print(f"[LOOP D] Otimizacao e Emissao do Relatorio de Qualidade...")
    quality_report = {
        "status": "SUCESSO",
        "total_registos_analisados": len(records),
        "duplicados_identificados": dedup_count,
        "registos_corrigidos": corrected_count,
        "processos_avaliados": len(process_scores),
        "scores_por_processo": process_scores
    }
    
    out_path = os.path.join(index_dir, "quality_loop_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(quality_report, f, ensure_ascii=False, indent=2)
        
    print(f"[SUCESSO] Relatorio de qualidade gravado em: {out_path}")
    return quality_report


def main():
    parser = argparse.ArgumentParser(description="Loop de Otimizacao e Validacao de Dados")
    parser.add_argument("--index-dir", default="C:\\Users\\Yokozuna\\Dev\\Projects\\Ficheiros Escritos Canónicos\\_index", help="Diretorio _index")
    args = parser.parse_args()
    
    run_optimization_loop(args.index_dir)


if __name__ == "__main__":
    main()
