#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_official_court_docs.py - Auditoria exaustiva de todos os documentos oficiais do Tribunal (Citius, Notificacoes, Despachos, Citacoes, Acordaos).
"""
import os
import sys
import sqlite3
from pathlib import Path

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
DB_PATH = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "02_DADOS_ESTRUTURADOS" / "memoria_forense_unificada.db"
OUT_MD = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "01_INDEX_E_RELATORIOS" / "AUDITORIA_DOCUMENTOS_OFICIAIS_TRIBUNAL.md"

def audit_court_docs():
    print("=" * 80)
    print(" AUDITORIA DE DOCUMENTOS OFICIAIS DO TRIBUNAL (CITIUS / ATOS FORMAIS)")
    print("=" * 80)

    if not DB_PATH.exists():
        print("[-] Base SQLite nao encontrada.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    # Pesquisar documentos oficiais por processos
    processos = [
        ("23142/22.7T8LSB", "%23142%"),
        ("3719/25.0T8LSB", "%3719%"),
        ("10153/24.7T8LSB", "%10153%"),
        ("15547/26.0T8LSB", "%15547%"),
        ("20203/22.6T8LSB", "%20203%")
    ]

    report_lines = []
    report_lines.append("# Auditoria Forense: Documentos Oficiais do Tribunal (Citius / Atos Formais)\n")
    report_lines.append("**Data de Emissão**: 2026-08-28\n")
    report_lines.append("**Autoridade**: `memoria_forense_unificada.db` e Ficheiros Escritos Canónicos\n\n---\n")

    for proc_name, pattern in processos:
        cur.execute("""
        SELECT filename, filepath, size_bytes, categoria
        FROM evidencias
        WHERE (filename LIKE ? OR filepath LIKE ?)
          AND (filename LIKE '%.pdf%' OR filename LIKE '%notificacao%' OR filename LIKE '%despacho%' OR filename LIKE '%citacao%' OR filename LIKE '%oficio%' OR filename LIKE '%acordao%')
        ORDER BY filename
        """, (pattern, pattern))
        rows = cur.fetchall()
        print(f"\n[+] {proc_name}: {len(rows)} documentos oficiais do tribunal identificados.")
        report_lines.append(f"## Processo: {proc_name}\n")
        report_lines.append(f"- **Total de Documentos Oficiais Encontrados**: {len(rows)}\n\n")
        
        if rows:
            report_lines.append("| Documento Oficial / Citius | Tamanho (Bytes) | Caminho no Acervo |\n|---|---|---|\n")
            for r in rows[:25]:
                report_lines.append(f"| `{r[0]}` | {r[2]:,} | `{r[1]}` |\n")
            report_lines.append("\n")
        else:
            report_lines.append("*Nenhum documento oficial Citius diretamente indexado com este padrão.*\n\n")

    conn.close()

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.writelines(report_lines)

    print(f"\n[+] Relatorio gravado em: {OUT_MD}")

if __name__ == "__main__":
    audit_court_docs()
