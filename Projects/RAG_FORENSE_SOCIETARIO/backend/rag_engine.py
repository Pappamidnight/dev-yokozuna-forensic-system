from __future__ import annotations

import os
import sys
import math
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Tuple, Optional, Any

PROJ_ROOT = Path(__file__).resolve().parent.parent
if str(PROJ_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJ_ROOT))

from backend.schemas import DocumentChunk, ChunkMetadata, QueryRequest, CitationSource, RAGResponse


def make_long_path(path_str: str) -> str:
    abs_str = os.path.abspath(path_str)
    if abs_str.startswith("\\\\?\\"):
        return abs_str
    if abs_str.startswith("\\\\"):
        return "\\\\?\\UNC\\" + abs_str[2:]
    return "\\\\?\\" + abs_str


def sha256_file(filepath: Path | str) -> str:
    digest = hashlib.sha256()
    lp = make_long_path(str(filepath))
    try:
        with open(lp, "rb") as handle:
            while chunk := handle.read(1024 * 1024):
                digest.update(chunk)
        return digest.hexdigest()
    except Exception:
        return "0" * 64


def read_text_lossy(filepath: Path | str) -> str:
    lp = make_long_path(str(filepath))
    try:
        with open(lp, "rb") as handle:
            data = handle.read(2_000_000)
        for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue
        return data.decode("utf-8", errors="replace")
    except Exception:
        return ""


class RAGEngine:
    """Motor Deterministico de Indexacao e Recuperacao Semantica RAG."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (PROJ_ROOT / "state" / "rag_index.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id TEXT PRIMARY KEY,
            source_path TEXT,
            filename TEXT,
            doc_type TEXT,
            processo_id TEXT,
            entity_id TEXT,
            sha256 TEXT,
            chunk_index INTEGER,
            total_chunks INTEGER,
            text TEXT,
            token_estimate INTEGER
        )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_processo ON chunks (processo_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_entity ON chunks (entity_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_sha ON chunks (sha256)")
        conn.commit()
        conn.close()

    def chunk_text(self, text: str, chunk_size: int = 1500, overlap: int = 200) -> List[str]:
        words = text.split()
        if not words:
            return []
        chunks = []
        i = 0
        while i < len(words):
            chunk_words = words[i:i + chunk_size]
            chunks.append(" ".join(chunk_words))
            i += (chunk_size - overlap)
            if i >= len(words):
                break
        return chunks

    def index_files(self, file_paths: List[Path]) -> int:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        total_chunks = 0

        for path in file_paths:
            if not path.is_file():
                continue
            text = read_text_lossy(path)
            if not text.strip():
                continue

            sha = sha256_file(path)
            raw_chunks = self.chunk_text(text)
            if not raw_chunks:
                continue

            # Deteccao de Metadados
            proc_id = None
            if "15547" in path.name or "15547" in text:
                proc_id = "15547/26.0T8LSB"
            elif "3719" in path.name or "3719" in text:
                proc_id = "3719/25.0T8LSB"
            elif "10153" in path.name or "10153" in text:
                proc_id = "10153/24.7T8LSB"
            elif "23142" in path.name or "23142" in text:
                proc_id = "23142/22.7T8LSB"

            ent_id = None
            if "SPARK" in path.name.upper() or "CELTIS" in path.name.upper():
                ent_id = "SPARK_GROUP"

            for c_idx, c_text in enumerate(raw_chunks):
                chunk_id = f"CHK-{sha[:8]}-{c_idx:04d}"
                tok_est = len(c_text.split())
                cur.execute("""
                INSERT OR REPLACE INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    chunk_id,
                    str(path),
                    path.name,
                    "FORENSE_SOCIETARIO",
                    proc_id,
                    ent_id,
                    sha,
                    c_idx,
                    len(raw_chunks),
                    c_text,
                    tok_est
                ))
                total_chunks += 1

        conn.commit()
        conn.close()
        return total_chunks

    def query(self, req: QueryRequest) -> RAGResponse:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        query_terms = [t.lower() for t in re.findall(r'\w+', req.query) if len(t) > 2]
        if not query_terms:
            return RAGResponse(
                query=req.query,
                total_found=0,
                citations=[],
                synthesized_answer="Termo de pesquisa vazio ou insuficiente.",
                generated_at=datetime.now(timezone.utc).isoformat()
            )

        # Buscar todos os chunks (ou filtrados)
        sql = "SELECT chunk_id, filename, source_path, sha256, text, processo_id, entity_id FROM chunks WHERE 1=1"
        params = []
        if req.filter_processo:
            sql += " AND processo_id = ?"
            params.append(req.filter_processo)
        if req.filter_entity:
            sql += " AND entity_id = ?"
            params.append(req.filter_entity)

        cur.execute(sql, params)
        rows = cur.fetchall()
        conn.close()

        scored_chunks = []
        for r in rows:
            chunk_id, filename, path, sha, text, proc_id, ent_id = r
            text_lower = text.lower()

            # Calculo de TF-IDF e BM25 Simplificado
            score = 0.0
            for term in query_terms:
                count = text_lower.count(term)
                if count > 0:
                    score += (1.0 + math.log(count)) * (2.0 if term in filename.lower() else 1.0)

            if score >= req.min_score:
                scored_chunks.append((score, chunk_id, filename, path, sha, text))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_chunks = scored_chunks[:req.top_k]

        citations: List[CitationSource] = []
        answer_parts = []

        for score, chunk_id, filename, path, sha, text in top_chunks:
            # Extrair excerto representativo
            excerpt = text[:300] + "..." if len(text) > 300 else text
            citations.append(CitationSource(
                chunk_id=chunk_id,
                filename=filename,
                filepath=path,
                sha256=sha,
                relevance_score=round(score, 2),
                excerpt=excerpt
            ))
            answer_parts.append(f"[{filename} | SHA-256 {sha[:8]}]: {excerpt}")

        synthesized = "\n\n".join(answer_parts) if answer_parts else "Nenhum documento encontrado com suporte factual para a consulta."

        return RAGResponse(
            query=req.query,
            total_found=len(citations),
            citations=citations,
            synthesized_answer=synthesized,
            generated_at=datetime.now(timezone.utc).isoformat()
        )
