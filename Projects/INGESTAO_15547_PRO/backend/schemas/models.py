from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class EstadoProbatorio(StrEnum):
    FACTO_DOCUMENTADO = "FACTO_DOCUMENTADO"
    ALEGACAO = "ALEGACAO"
    INFERENCIA = "INFERENCIA"
    TESE_DEFESA = "TESE_DEFESA"
    POR_VALIDAR = "POR_VALIDAR"


class Severidade(StrEnum):
    INFO = "INFO"
    ALERTA = "ALERTA"
    CRITICO = "CRITICO"


class EvidenceFile(BaseModel):
    evidence_id: str
    processo_id: str = "15547/26.0T8LSB"
    path: str
    filename: str
    extension: str
    size_bytes: int
    sha256: str
    modified_at: datetime
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_read_only: bool = True

    @field_validator("sha256")
    @classmethod
    def validate_sha256(cls, value: str) -> str:
        if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value.lower()):
            raise ValueError("sha256 invalido")
        return value.lower()


class TextFragment(BaseModel):
    fragment_id: str
    evidence_id: str
    source_path: str
    line_start: int
    line_end: int
    text: str


class Claim(BaseModel):
    claim_id: str
    processo_id: str = "15547/26.0T8LSB"
    estado: EstadoProbatorio
    tema: str
    descricao: str
    suporte: list[str] = Field(default_factory=list)
    pessoas: list[str] = Field(default_factory=list)
    locais: list[str] = Field(default_factory=list)
    valores: list[str] = Field(default_factory=list)
    datas: list[str] = Field(default_factory=list)
    confianca_deterministica: float = Field(ge=0, le=1)
    notas_validacao: list[str] = Field(default_factory=list)


class TimelineEvent(BaseModel):
    event_id: str
    processo_id: str = "15547/26.0T8LSB"
    data: str
    estado: EstadoProbatorio
    titulo: str
    descricao: str
    suporte: list[str]
    ordenacao: str


class Gap(BaseModel):
    gap_id: str
    processo_id: str = "15547/26.0T8LSB"
    severidade: Severidade
    tema: str
    descricao: str
    acao_recomendada: str
    evidencias_relacionadas: list[str] = Field(default_factory=list)


class RouteDecision(BaseModel):
    item_id: str
    item_type: str
    route: str
    accepted: bool
    reason: str
    required_actions: list[str] = Field(default_factory=list)


class GraphNode(BaseModel):
    node_id: str
    kind: str
    label: str
    source_ids: list[str] = Field(default_factory=list)


class GraphEdge(BaseModel):
    edge_id: str
    source: str
    target: str
    relation: str
    evidence_ids: list[str] = Field(default_factory=list)


class EvalResult(BaseModel):
    eval_id: str
    passed: bool
    total: int
    failures: list[str] = Field(default_factory=list)


class PipelineManifest(BaseModel):
    processo_id: str
    generated_at: datetime
    raw_root: str
    outputs: dict[str, str]
    counts: dict[str, int]
    warnings: list[str] = Field(default_factory=list)
    config: dict[str, Any] = Field(default_factory=dict)


def safe_rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
