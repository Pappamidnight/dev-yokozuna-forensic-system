from __future__ import annotations

import os
import sys
import argparse
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any

PROJ_ROOT = Path(__file__).resolve().parent
if str(PROJ_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJ_ROOT))

DEV_ROOT = Path("C:/Users/Yokozuna/Dev")
ACQUIS_DIR = DEV_ROOT / "Projects" / "Ficheiros Escritos Canónicos" / "02_Minutas_E_Rascunhos" / "OBSIDIAN_VAULT" / "00_VAULT_UNIFICADO" / "05_DOUTRINA_NOTAS_E_WIKIS"

from backend.schemas.corporate_models import CorporateEntity, CorporateEvidence, ShareholdingRelation, CorporateManifest, CorporateTypeEnum, SupportLevelEnum
from backend.classifier import HeuristicCorporateClassifier, CORPORATE_DICTIONARY
from backend.agents.frozen_judge_spark import FrozenJudgeCorporateAgent
from backend.agents.graphify_corporate import GraphifyCorporateAgent
from backend.reporting_spark import render_corporate_reports
from backend.io_utils import make_long_path, sha256_file, read_text_lossy, write_jsonl, write_json


def run_spark_ingestion(root: Path = PROJ_ROOT) -> CorporateManifest:
    print("==================================================================")
    print("INICIANDO INGESTAO DETERMINISTICA: GRUPO SPARK / VENTURE PARTNERS")
    print(f"Diretorio do Projeto : {root}")
    print(f"Acervo Analisado     : {ACQUIS_DIR}")
    print("==================================================================")

    classifier = HeuristicCorporateClassifier()
    judge = FrozenJudgeCorporateAgent()
    graphify = GraphifyCorporateAgent()

    evidences: List[CorporateEvidence] = []
    entity_evidence_map: Dict[str, List[str]] = {k: [] for k in CORPORATE_DICTIONARY.keys()}

    # 1. Varrer e classificar ficheiros
    raw_dir = root / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    search_dirs = [ACQUIS_DIR, raw_dir]
    idx = 1

    for s_dir in search_dirs:
        if not s_dir.exists():
            continue
        for f_path in sorted(s_dir.glob("SPARK_*")):
            if f_path.is_file():
                filename = f_path.name
                sha = sha256_file(f_path)
                size_b = f_path.stat().st_size
                content = read_text_lossy(f_path, max_chars=100_000)

                entity_id, c_type, conf, kws = classifier.classify_text(filename, content)

                ev = CorporateEvidence(
                    evidence_id=f"EVD-SPARK-{idx:05d}",
                    filepath=str(f_path),
                    filename=filename,
                    extension=f_path.suffix.lower(),
                    size_bytes=size_b,
                    sha256=sha,
                    classified_entity=entity_id,
                    classified_type=c_type,
                    support_level=SupportLevelEnum.DOCUMENTADO,
                    confidence_score=conf if conf > 0 else 0.8,
                    matched_keywords=kws
                )
                evidences.append(ev)
                if entity_id:
                    entity_evidence_map[entity_id].append(sha)
                idx += 1

    print(f"[INFO] Total de evidencias Spark/Venture processadas: {len(evidences)}")

    # 2. Construir Modelos Pydantic de Entidades
    entities: List[CorporateEntity] = []
    for ent_id, sha_list in entity_evidence_map.items():
        primary_sha = sha_list[0] if sha_list else None
        ent_model = classifier.build_entity_model(ent_id, evidence_count=len(sha_list), sha256_primary=primary_sha)
        entities.append(ent_model)

    # 3. Construir Relacoes Societarias
    relations: List[ShareholdingRelation] = [
        ShareholdingRelation(
            relation_id="REL-SPARK-001",
            parent_entity="SPARK_CELTIS_VENTURE_PARTNERS",
            child_entity="SPARK_CONTAINER_FUND_CMVM",
            relation_type="GESTAO_FUNDO_CMVM",
            percentage=100.0
        ),
        ShareholdingRelation(
            relation_id="REL-SPARK-002",
            parent_entity="SPARK_CELTIS_VENTURE_PARTNERS",
            child_entity="GROWTH_PARTNERS_CAPITAL",
            relation_type="PARTICIPACAO_SOCIAL",
            percentage=65.0
        ),
        ShareholdingRelation(
            relation_id="REL-SPARK-003",
            parent_entity="SPARKWAVE_ENERGY_HOLDING_SA",
            child_entity="SPARK_ENERGY_ASSETS_SA",
            relation_type="CONTROLO_TOTAL",
            percentage=100.0
        ),
        ShareholdingRelation(
            relation_id="REL-SPARK-004",
            parent_entity="UNICORN_RE_CAPITAL_PARTNERS_HOLDING",
            child_entity="INTEGRITATE_CAPITAL_PARTNERS",
            relation_type="HOLDING_VEICULO",
            percentage=80.0
        )
    ]

    # 4. Grafo de Conhecimento
    nodes, edges = graphify.build_corporate_graph(entities, relations)

    # 5. Avaliacao do Frozen Judge
    judge_result = judge.evaluate_corporate_acquis(evidences, entities, relations)

    # 6. Gravar Outputs JSONL
    outputs_dir = root / "outputs"
    jsonl_dir = outputs_dir / "jsonl"
    graph_dir = outputs_dir / "graph"
    evals_dir = outputs_dir / "evals"

    jsonl_dir.mkdir(parents=True, exist_ok=True)
    graph_dir.mkdir(parents=True, exist_ok=True)
    evals_dir.mkdir(parents=True, exist_ok=True)

    write_jsonl(jsonl_dir / "evidencias.jsonl", evidences)
    write_jsonl(jsonl_dir / "entidades_societarias.jsonl", entities)
    write_jsonl(jsonl_dir / "relacoes_societarias.jsonl", relations)
    write_jsonl(graph_dir / "nodes.jsonl", nodes)
    write_jsonl(graph_dir / "edges.jsonl", edges)
    write_json(evals_dir / "frozen_judge_spark_eval.json", judge_result)

    # 7. Relatorios Markdown e HTML
    render_corporate_reports(root, evidences, entities, relations, judge_result)

    # 8. Persistir na Base de Dados SQLite
    state_dir = root / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    db_path = state_dir / "memoria_spark_corporate.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS entidades_societarias (
        entity_id TEXT PRIMARY KEY,
        name TEXT,
        corporate_type TEXT,
        nif_nipc TEXT,
        registro_cmvm TEXT,
        evidence_count INTEGER
    )
    """)
    for e in entities:
        cur.execute("""
        INSERT OR REPLACE INTO entidades_societarias VALUES (?, ?, ?, ?, ?, ?)
        """, (e.entity_id, e.name, e.corporate_type, e.nif_nipc, e.registro_cmvm, e.evidence_count))
    conn.commit()
    conn.close()

    manifest = CorporateManifest(
        generated_at=datetime.now(timezone.utc).isoformat(),
        total_evidences=len(evidences),
        total_entities=len(entities),
        total_relations=len(relations),
        frozen_judge_score=judge_result.get("frozen_judge_score", 100),
        status="PASS" if judge_result.get("frozen_judge_score") == 100 else "NEEDS_REVIEW",
        outputs={
            "markdown": str(outputs_dir / "markdown" / "RELATORIO_SPARK_VENTURE.md"),
            "html": str(outputs_dir / "html" / "PAINEL_SPARK_VENTURE.html"),
            "entidades": str(jsonl_dir / "entidades_societarias.jsonl"),
            "grafo_nodes": str(graph_dir / "nodes.jsonl")
        }
    )

    manifest_path = outputs_dir / "manifest_spark.json"
    write_json(manifest_path, manifest)

    print(f"\n------------------------------------------------------------------")
    print(f"INGESTAO SPARK CONCLUIDA: [{manifest.status}] SCORE: {manifest.frozen_judge_score}/100")
    print(f" - Entidades Mapeadas : {len(entities)}")
    print(f" - Evidencias SHA-256 : {len(evidences)}")
    print(f" - Relacoes no Grafo  : {len(relations)}")
    print(f" - Relatorio Markdown : {manifest.outputs['markdown']}")
    print(f" - Painel Visual HTML : {manifest.outputs['html']}")
    print(f"------------------------------------------------------------------\n")

    return manifest


def main():
    parser = argparse.ArgumentParser(description="Ingestao de Entidades Societarias SPARK / Venture Partners")
    parser.add_argument("--root", default=str(PROJ_ROOT), help="Raiz do projeto")
    args = parser.parse_args()

    run_spark_ingestion(Path(args.root))


if __name__ == "__main__":
    main()
