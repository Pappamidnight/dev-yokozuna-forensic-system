#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
database.py - Backend Estruturado Minimo do CORE-5 FORENSE (8 Tabelas Fortes).
Mantem o modelo cientifico: Documento -> Entidade -> Evento -> Prova -> Relacao -> Acao.
Zero emojis conforme PROTOCOL.md e AGENTS.md.
"""

import sqlite3
from pathlib import Path

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
DB_CORE5_PATH = DEV_ROOT / "03_RESULTADOS" / "02_DADOS_ESTRUTURADOS" / "memoria_core5_forense.db"

def inicializar_banco_core5():
    DB_CORE5_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_CORE5_PATH)
    cur = conn.cursor()

    # 1. Tabela documents
    cur.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        doc_id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        filepath TEXT NOT NULL,
        sha256 TEXT NOT NULL UNIQUE,
        size_bytes INTEGER,
        doc_type TEXT,
        mime_type TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )
    """)

    # 2. Tabela entities
    cur.execute("""
    CREATE TABLE IF NOT EXISTS entities (
        entity_id TEXT PRIMARY KEY,
        nome TEXT NOT NULL,
        tipo TEXT,
        nif TEXT,
        papel_principal TEXT
    )
    """)

    # 3. Tabela processes
    cur.execute("""
    CREATE TABLE IF NOT EXISTS processes (
        process_id TEXT PRIMARY KEY,
        numero TEXT NOT NULL UNIQUE,
        tribunal TEXT,
        juizo TEXT,
        especie TEXT,
        valor_eur REAL,
        estado_atual TEXT
    )
    """)

    # 4. Tabela events
    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        event_id TEXT PRIMARY KEY,
        process_id TEXT,
        data_evento TEXT,
        tipo_evento TEXT,
        entidade_origem TEXT,
        documento_fonte TEXT,
        sha256 TEXT,
        forca_probatoria TEXT,
        estado_validacao TEXT,
        FOREIGN KEY (process_id) REFERENCES processes(process_id)
    )
    """)

    # 5. Tabela evidence_links
    cur.execute("""
    CREATE TABLE IF NOT EXISTS evidence_links (
        link_id TEXT PRIMARY KEY,
        event_id TEXT,
        doc_id TEXT,
        facto_provado TEXT,
        norma_legal TEXT,
        grau_certeza REAL,
        FOREIGN KEY (event_id) REFERENCES events(event_id),
        FOREIGN KEY (doc_id) REFERENCES documents(doc_id)
    )
    """)

    # 6. Tabela relations
    cur.execute("""
    CREATE TABLE IF NOT EXISTS relations (
        relation_id TEXT PRIMARY KEY,
        entity_a TEXT,
        entity_b TEXT,
        tipo_relacao TEXT,
        detalhes TEXT
    )
    """)

    # 7. Tabela actions
    cur.execute("""
    CREATE TABLE IF NOT EXISTS actions (
        action_id TEXT PRIMARY KEY,
        process_id TEXT,
        event_id TEXT,
        prioridade TEXT,
        acao_recomendada TEXT,
        estado TEXT,
        peca_destino TEXT
    )
    """)

    # 8. Tabela runs
    cur.execute("""
    CREATE TABLE IF NOT EXISTS runs (
        run_id TEXT PRIMARY KEY,
        timestamp TEXT DEFAULT (datetime('now')),
        versao_core TEXT,
        total_eventos INTEGER,
        score_conformidade INTEGER,
        resumo_json TEXT
    )
    """)

    conn.commit()
    conn.close()
    print(f"[+] Base de Dados CORE-5 Forense inicializada em: {DB_CORE5_PATH}")

if __name__ == "__main__":
    inicializar_banco_core5()
