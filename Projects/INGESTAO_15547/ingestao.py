from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from backend.agents.frozen_judge import FrozenJudgeAgent
from backend.agents.graphify import GraphifyAgent
from backend.agents.judge_auditor import JudgeAuditorAgent
from backend.agents.observabilidade import ObservabilidadeAgent
from backend.agents.validade import ValidadeAgent
from backend.agents.workflow import WorkflowAgent
from backend.extractors import extract_from_file
from backend.io_utils import iter_files, sha256_file, write_json, write_jsonl
from backend.reporting import render_markdown
from backend.schemas.models import EvidenceFile, PipelineManifest


DEFAULT_PROCESSO_ID = "15547/26.0T8LSB"


def load_config(root: Path) -> dict:
    config_path = root / "config" / "processo_15547.json"
    if not config_path.exists():
        return {"processo_id": DEFAULT_PROCESSO_ID}
    return json.loads(config_path.read_text(encoding="utf-8"))


def build_evidence(path: Path, raw_root: Path, index: int, processo_id: str) -> EvidenceFile:
    stat = path.stat()
    return EvidenceFile(
        evidence_id=f"EVD-15547-{index:05d}",
        processo_id=processo_id,
        path=str(path),
        filename=path.name,
        extension=path.suffix.lower(),
        size_bytes=stat.st_size,
        sha256=sha256_file(path),
        modified_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
        raw_read_only=True,
    )


def run(root: Path) -> PipelineManifest:
    processo_id = DEFAULT_PROCESSO_ID
    config = load_config(root)
    processo_id = config.get("processo_id", processo_id)

    workflow = WorkflowAgent(root)
    warnings = workflow.prepare()

    observer = ObservabilidadeAgent(root / "logs" / "ingestao.log", root / "logs" / "errors.log")
    observer.info(f"Inicio pipeline {processo_id}")

    raw_root = root / "raw"
    judge = FrozenJudgeAgent()
    evidences: list[EvidenceFile] = []
    routes = []
    fragments = []
    claims = []
    timeline = []

    for index, file_path in enumerate(iter_files(raw_root), start=1):
        try:
            evidence = build_evidence(file_path, raw_root, index, processo_id)
            evidences.append(evidence)
            evidence_route = judge.route_evidence(evidence)
            routes.append(evidence_route)
            observer.info(f"Indexada evidencia {evidence.evidence_id}: {file_path} -> {evidence_route.route}")

            if evidence_route.accepted:
                extraction = extract_from_file(file_path, evidence.evidence_id)
                fragments.extend(extraction.fragments)
                claims.extend(extraction.claims)
                timeline.extend(extraction.timeline)
        except Exception as exc:
            observer.error(f"Erro ao processar {file_path}: {exc}", exc_info=True)
            warnings.append(f"Erro ao processar {file_path}. Ver logs/errors.log.")

    validity = ValidadeAgent()
    claims, gaps = validity.validate_claims(claims)
    for claim in claims:
        routes.append(judge.route_claim(claim))
    timeline.sort(key=lambda event: event.ordenacao)

    graph_nodes, graph_edges = GraphifyAgent().build(claims)
    eval_result = JudgeAuditorAgent(judge).run_gold_checks(evidences)
    if not eval_result.passed:
        warnings.append("Frozen Judge falhou gold/eval checks. Ver outputs/evals/frozen_judge_eval.json.")

    outputs = {
        "evidencias": str(root / "outputs" / "jsonl" / "evidencias.jsonl"),
        "fragmentos": str(root / "outputs" / "jsonl" / "fragmentos.jsonl"),
        "claims": str(root / "outputs" / "jsonl" / "claims.jsonl"),
        "cronologia": str(root / "outputs" / "jsonl" / "cronologia.jsonl"),
        "lacunas": str(root / "outputs" / "jsonl" / "lacunas.jsonl"),
        "rotas": str(root / "outputs" / "jsonl" / "rotas_workflow.jsonl"),
        "graph_nodes": str(root / "outputs" / "graph" / "nodes.jsonl"),
        "graph_edges": str(root / "outputs" / "graph" / "edges.jsonl"),
        "frozen_judge_eval": str(root / "outputs" / "evals" / "frozen_judge_eval.json"),
        "relatorio": str(root / "outputs" / "markdown" / "RELATORIO_15547.md"),
    }

    write_jsonl(Path(outputs["evidencias"]), evidences)
    write_jsonl(Path(outputs["fragmentos"]), fragments)
    write_jsonl(Path(outputs["claims"]), claims)
    write_jsonl(Path(outputs["cronologia"]), timeline)
    write_jsonl(Path(outputs["lacunas"]), gaps)
    write_jsonl(Path(outputs["rotas"]), routes)
    write_jsonl(Path(outputs["graph_nodes"]), graph_nodes)
    write_jsonl(Path(outputs["graph_edges"]), graph_edges)
    write_json(Path(outputs["frozen_judge_eval"]), eval_result)
    render_markdown(Path(outputs["relatorio"]), evidences, claims, timeline, gaps)

    manifest = PipelineManifest(
        processo_id=processo_id,
        generated_at=datetime.now(timezone.utc),
        raw_root=str(raw_root),
        outputs=outputs,
        counts={
            "evidencias": len(evidences),
            "fragmentos": len(fragments),
            "claims": len(claims),
            "cronologia": len(timeline),
            "lacunas": len(gaps),
            "rotas": len(routes),
            "graph_nodes": len(graph_nodes),
            "graph_edges": len(graph_edges),
            "eval_failures": len(eval_result.failures),
        },
        warnings=warnings,
        config=config,
    )
    write_json(root / "state" / "manifest.json", manifest)

    for warning in warnings:
        observer.warning(warning)
    observer.info(f"Fim pipeline {processo_id}: {manifest.counts}")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline deterministico de ingestao do processo 15547.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent), help="Pasta raiz do projeto.")
    args = parser.parse_args()

    manifest = run(Path(args.root).resolve())
    print(json.dumps(manifest.model_dump(mode="json"), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
