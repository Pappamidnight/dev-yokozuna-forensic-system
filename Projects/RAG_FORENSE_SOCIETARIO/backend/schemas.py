from __future__ import annotations

import re
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ChunkMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", strip_whitespace=True)

    source_path: str
    filename: str
    doc_type: str = "JURIDICO_OU_SOCIETARIO"
    processo_id: Optional[str] = None
    entity_id: Optional[str] = None
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    chunk_index: int = Field(ge=0)
    total_chunks: int = Field(ge=1)


class DocumentChunk(BaseModel):
    model_config = ConfigDict(extra="forbid", strip_whitespace=True)

    chunk_id: str
    text: str
    token_estimate: int = Field(ge=0)
    metadata: ChunkMetadata
    keywords: List[str] = Field(default_factory=list)


class QueryRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=50)
    filter_processo: Optional[str] = None
    filter_entity: Optional[str] = None
    min_score: float = Field(default=0.1, ge=0.0, le=1.0)


class CitationSource(BaseModel):
    chunk_id: str
    filename: str
    filepath: str
    sha256: str
    relevance_score: float
    excerpt: str


class RAGResponse(BaseModel):
    query: str
    total_found: int
    citations: List[CitationSource]
    synthesized_answer: str
    generated_at: str
