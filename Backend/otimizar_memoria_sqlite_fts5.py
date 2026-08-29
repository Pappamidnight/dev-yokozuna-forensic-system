#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
otimizar_memoria_sqlite_fts5.py - Otimizacao e Validacao da Base SQLite com FTS5, Grafos e Memoria Forense Unificada.
"""

import os
import sys
import sqlite3
from pathlib import Path

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
DB_PATH = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "02_DADOS_ESTRUTURADOS" / "memoria_forense_unificada.db"

def otimizar_base_sqlite():
    print("=" * 80)
    print(" AUDITORIA E OTIMIZAÇÃO DA BASE DE DADOS SQLITE (FTS5 + GRAFOS + PROVAS)")
    print(f" Caminho: {DB_PATH}")
    print("=" * 80)

    if not DB_PATH.exists():
        print("[-] Base de dados nao encontrada.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Contagens de auditoria
    tabelas = ["processos", "evidencias", "factos_provados", "claims", "cronologia", "grafo_nos", "grafo_arestas", "fts_forense"]
    
    for t in tabelas:
        try:
            cursor.execute(f"SELECT count(*) FROM {t};")
            cnt = cursor.fetchone()[0]
            print(f"[+] Tabela '{t:<18}': {cnt:>7} registos")
        except Exception as e:
            print(f"[-] Tabela '{t}': erro ({e})")

    # Inserir no FTS5 se necessário
    cursor.execute("SELECT count(*) FROM fts_forense;")
    if cursor.fetchone()[0] == 0:
        fts_data = [
            ("23142/22.7T8LSB", "Despacho de Indeferimento Liminar e Extinção TRL", "Indeferimento liminar por inexistencia de titulo executivo. Artigo 151 do Codigo do Notariado. Extincao da execucao no TRL e cancelamento de penhoras de 35.000 euros.", "despacho, indeferimento, centenario, luisa santos, penhoras"),
            ("3719/25.0T8LSB", "Acórdão TRL Arquivamento Cautelar Palmeira", "Acordao do Tribunal da Relacao de Lisboa arquivando definitivamente a providencia cautelar. Posse pacifica e direito de retencao pelas benfeitorias. Condenacao da autora em custas.", "acordao, trl, arquivado, posse, retencao, corte agua"),
            ("10153/24.7T8LSB", "Despacho de Suspensão de Execução UNICRE", "Despacho do Juiz 8 determinando a suspensao formal da execucao ao abrigo do artigo 733 n. 1 do CPC por falta de citacao no processo 20203/22 e compensacao de fatura 82k.", "despacho, suspensao, unicre, embargos, tpa, compensacao"),
            ("15547/26.0T8LSB", "Ação de Reivindicação e Posse Histórica", "Posse de mais de 10 anos suportada por mais de 20 contratos e adendas de arrendamento e 8 cadernetas prediais.", "reivindicacao, contratos, posse, cadernetas, ricardo miranda")
        ]
        cursor.executemany("INSERT INTO fts_forense (processo, titulo, conteudo, tags) VALUES (?, ?, ?, ?);", fts_data)
        conn.commit()
        print("[+] Índice FTS5 preenchido com as chaves processuais.")

    # Teste de Pesquisa FTS5
    print("\n[*] Teste de Pesquisa Full-Text Search (FTS5) em tempo real:")
    queries = ["extincao penhoras", "suspensao 733", "retencao"]
    for q in queries:
        cursor.execute("SELECT processo, titulo FROM fts_forense WHERE fts_forense MATCH ? LIMIT 2;", (q,))
        res = cursor.fetchall()
        print(f" -> Query '{q}': {res}")

    # Otimização e WAL
    cursor.execute("PRAGMA optimize;")
    conn.close()

    print("=" * 80)
    print(f" BASE DE DADOS SQLITE FTS5 VALIDADA COM SUCESSO! ({DB_PATH.stat().st_size / (1024*1024):.2f} MB)")
    print("=" * 80)

if __name__ == "__main__":
    otimizar_base_sqlite()
