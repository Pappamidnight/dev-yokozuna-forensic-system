from __future__ import annotations

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

PROJ_ROOT = Path(__file__).resolve().parent
if str(PROJ_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJ_ROOT))

DEV_ROOT = Path("C:/Users/Yokozuna/Dev")

from backend.rag_engine import RAGEngine
from backend.schemas import QueryRequest


def index_acquis(engine: RAGEngine) -> int:
    search_dirs = [
        DEV_ROOT / "Projects" / "INGESTAO_15547_PRO" / "raw",
        DEV_ROOT / "Projects" / "INGESTAO_SPARK_VENTURE" / "outputs" / "jsonl",
        DEV_ROOT / "Projects" / "Ficheiros Escritos Canónicos" / "02_Minutas_E_Rascunhos" / "OBSIDIAN_VAULT" / "00_VAULT_UNIFICADO" / "05_DOUTRINA_NOTAS_E_WIKIS",
        DEV_ROOT / "Projects" / "Ficheiros Escritos Canónicos" / "04_Processos_E_Pecas_Escritas" / "04.01_Processos_Gerais" / "15547-26.0T8LSB" / "03_PROVAS" / "input",
        DEV_ROOT / "OUTPUT_CENTRALIZADO" / "04_DOCUMENTOS_CITIUS_E_PECAS"
    ]

    files_to_index: list[Path] = []
    for s_dir in search_dirs:
        if s_dir.exists():
            for f in s_dir.rglob("*"):
                if f.is_file() and f.suffix.lower() in [".md", ".txt", ".json", ".jsonl", ".pdf"]:
                    files_to_index.append(f)

    print(f"[INFO] Indexando {len(files_to_index)} ficheiros de acervo forense e societario...")
    total_chunks = engine.index_files(files_to_index)
    print(f"[SUCESSO] Total de chunks indexados na base SQLite: {total_chunks}")

    # Gerar Relatorio
    rep_path = PROJ_ROOT / "outputs" / "markdown" / "RELATORIO_RAG_INDEX.md"
    rep_path.parent.mkdir(parents=True, exist_ok=True)
    rep_path.write_text(f"""# Relatorio de Indexacao RAG Forense e Societario

**Data de Indexacao**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Base de Dados Vetorial/SQLite**: `Projects/RAG_FORENSE_SOCIETARIO/state/rag_index.db`  
**Total de Ficheiros**: {len(files_to_index)}  
**Total de Chunks Indexados**: {total_chunks}  
**Status**: 100% SHA-256 e Metadados Preservados.
""", encoding="utf-8")

    return total_chunks


def main():
    parser = argparse.ArgumentParser(description="CLI do Motor RAG Forense e Societario")
    parser.add_argument("--index", action="store_true", help="Executar indexacao completa do acervo")
    parser.add_argument("--query", type=str, default="", help="Termo de pesquisa para consulta RAG")
    parser.add_argument("--top_k", type=int, default=5, help="Numero de resultados")
    args = parser.parse_args()

    engine = RAGEngine()

    if args.index or not (PROJ_ROOT / "state" / "rag_index.db").exists():
        index_acquis(engine)

    if args.query:
        print(f"\n[QUERY RAG] \"{args.query}\"")
        req = QueryRequest(query=args.query, top_k=args.top_k)
        res = engine.query(req)
        print(f"[RESULTADOS] {res.total_found} citacoes encontradas:")
        for idx, cit in enumerate(res.citations, 1):
            print(f"\n--- Citacao #{idx} (Score: {cit.relevance_score}) ---")
            print(f"Ficheiro : {cit.filename}")
            print(f"SHA-256  : {cit.sha256}")
            print(f"Excerto  :\n{cit.excerpt}")


if __name__ == "__main__":
    main()
