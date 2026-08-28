#!/usr/bin/env python3
"""
Indexador Vetorial Factual Deterministico (vector_index.py).
Gera embeddings deterministicos (256-d) e ancora chunks a hashes SHA-256 e processos.
"""
import os
import sys
import json
import hashlib
import argparse
from typing import List, Dict, Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEV_ROOT = "C:\\Users\\Yokozuna\\Dev"
INDEX_DIR = os.path.join(DEV_ROOT, "Projects", "Ficheiros Escritos Canónicos", "_index")
DEFAULT_ATOS = os.path.join(INDEX_DIR, "atos_processuais.jsonl")
DEFAULT_OUT = os.path.join(INDEX_DIR, "vector_index.jsonl")


def deterministic_embedding(text: str, dim: int = 256) -> List[float]:
    """Gera um vetor normalizado de dimensoes fixas atraves de hash deterministico."""
    vec = [0.0] * dim
    words = text.lower().split()
    for w in words:
        h = int(hashlib.md5(w.encode('utf-8')).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 1.0
    # Normalizacao L2
    norm = sum(x * x for x in vec) ** 0.5
    if norm > 0:
        vec = [round(x / norm, 4) for x in vec]
    return vec


def build_vector_index(atos_path: str = DEFAULT_ATOS, out_path: str = DEFAULT_OUT):
    print("==================================================================")
    print("CONSTRUINDO INDICE VETORIAL FACTUAL DETERMINISTICO (P4b)")
    print(f"Fonte de Atos: {atos_path}")
    print(f"Destino Index: {out_path}")
    print("==================================================================")

    if not os.path.exists(atos_path):
        print(f"[ERRO] Ficheiro {atos_path} nao encontrado.")
        return

    count = 0
    with open(atos_path, "r", encoding="utf-8") as f_in, open(out_path, "w", encoding="utf-8") as f_out:
        for line in f_in:
            if not line.strip():
                continue
            try:
                data = json.loads(line.strip())
                text_to_embed = f"{data.get('filename', '')} {data.get('tipo_cpc', '')} {data.get('process_id', '')} {data.get('folder', '')}"
                embedding = deterministic_embedding(text_to_embed, dim=256)
                
                chunk = {
                    "filename": data.get("filename"),
                    "path": data.get("path"),
                    "process_id": data.get("process_id"),
                    "tipo_cpc": data.get("tipo_cpc"),
                    "folder": data.get("folder"),
                    "sha256": data.get("sha256"),
                    "suporte": data.get("suporte"),
                    "evidence_level": data.get("evidence_level"),
                    "embedding": embedding
                }
                f_out.write(json.dumps(chunk, ensure_ascii=False) + "\n")
                count += 1
            except Exception:
                pass

    print(f"[SUCESSO] Indice vetorial gerado com {count} chunks indexados!")


def main():
    parser = argparse.ArgumentParser(description="Indexador Vetorial Factual")
    parser.add_argument("--atos", default=DEFAULT_ATOS, help="Caminho do atos_processuais.jsonl")
    parser.add_argument("--out", default=DEFAULT_OUT, help="Caminho de saida do vector_index.jsonl")
    args = parser.parse_args()

    build_vector_index(args.atos, args.out)


if __name__ == "__main__":
    main()
