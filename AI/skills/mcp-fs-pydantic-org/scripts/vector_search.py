#!/usr/bin/env python3
"""
Motor de Busca Vetorial Factual Deterministico (vector_search.py).
Permite consultas semanticas com filtros de processo judicial e nivel de prova.
"""
import os
import sys
import json
import argparse
from typing import List, Dict, Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEV_ROOT = "C:\\Users\\Yokozuna\\Dev"
INDEX_DIR = os.path.join(DEV_ROOT, "Projects", "Ficheiros Escritos Canónicos", "_index")
DEFAULT_INDEX = os.path.join(INDEX_DIR, "vector_index.jsonl")

try:
    from vector_index import deterministic_embedding
except ImportError:
    sys.path.insert(0, SCRIPT_DIR)
    from vector_index import deterministic_embedding


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    return round(dot, 4)


def search_vector(query: str, process_filter: str = None, top_k: int = 5, index_path: str = DEFAULT_INDEX):
    print("==================================================================")
    print(f"BUSCA VETORIAL FACTUAL: '{query}'")
    if process_filter:
        print(f"Filtro de Processo: {process_filter}")
    print("==================================================================")

    if not os.path.exists(index_path):
        print(f"[ERRO] Indice vetorial nao encontrado em: {index_path}")
        print("[INFO] Execute 'python scripts/vector_index.py' primeiro.")
        return

    q_vec = deterministic_embedding(query, dim=256)
    results = []

    with open(index_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                doc = json.loads(line.strip())
                if process_filter:
                    doc_pid = doc.get("process_id", "")
                    if not doc_pid or (process_filter not in doc_pid and doc_pid not in process_filter):
                        continue
                
                doc_vec = doc.get("embedding", [])
                if doc_vec and len(doc_vec) == len(q_vec):
                    sim = cosine_similarity(q_vec, doc_vec)
                    results.append((sim, doc))
            except Exception:
                pass

    results.sort(key=lambda x: x[0], reverse=True)
    top_results = results[:top_k]

    if not top_results:
        print("[INFO] Nenhum resultado encontrado com os filtros fornecidos.")
        return

    print(f"\nTop {len(top_results)} Resultados Encontrados:")
    print("-" * 80)
    for idx, (sim, doc) in enumerate(top_results, 1):
        print(f"[{idx}] Score: {sim:.4f} | Tipo: {doc.get('tipo_cpc')} | Processo: {doc.get('process_id')}")
        print(f"    Ficheiro: {doc.get('filename')}")
        print(f"    Suporte: {doc.get('suporte')} | Prova: {doc.get('evidence_level')}")
        print(f"    SHA-256: {doc.get('sha256')[:32]}...")
        print("-" * 80)


def main():
    parser = argparse.ArgumentParser(description="Busca Vetorial Factual")
    parser.add_argument("--query", required=True, help="Texto da consulta")
    parser.add_argument("--processo", default=None, help="Filtrar por numero de processo")
    parser.add_argument("--k", type=int, default=5, help="Numero de resultados")
    parser.add_argument("--index", default=DEFAULT_INDEX, help="Caminho do vector_index.jsonl")
    args = parser.parse_args()

    search_vector(args.query, process_filter=args.processo, top_k=args.k, index_path=args.index)


if __name__ == "__main__":
    main()
