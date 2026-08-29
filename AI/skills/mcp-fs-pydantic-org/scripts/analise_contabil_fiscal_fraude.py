#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analise_contabil_fiscal_fraude.py - Auditoria Pericial Contabilistica, Fiscal e Bancaria
Analisa:
1. Impostos (IVA, Retencoes, Declaracoes Modelo 2 da AT)
2. Rendimentos prediais e fluxos de rendas
3. Faturas emitidas a Nuno Duarte sem consentimento
4. Transferencias e pagamentos da Lisbon Experience (LEA) para a senhoria Teresa de Jesus Martins
"""
import os
import sys
import sqlite3
import re
from pathlib import Path

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
DB_PATH = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "02_DADOS_ESTRUTURADOS" / "memoria_forense_unificada.db"
OUTPUT_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "01_INDEX_E_RELATORIOS"

def audit_financial_records():
    print("=" * 80)
    print(" AUDITORIA FORENSE: MAPAS CONTABILÍSTICOS, IMPOSTOS E TRANSFERÊNCIAS LEA -> TERESA")
    print("=" * 80)

    if not DB_PATH.exists():
        print("[-] Base de dados SQLite nao encontrada.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    # 1. Pesquisa de Transferencias / Pagamentos para Teresa Martins
    cur.execute("""
    SELECT filename, filepath, size_bytes, categoria
    FROM evidencias
    WHERE filepath LIKE '%teresa%' OR filename LIKE '%teresa%' OR filename LIKE '%senhoria%'
    LIMIT 25
    """)
    teresa_records = cur.fetchall()
    print(f"\n[1] Registos Associados a Teresa de Jesus Martins / Senhoria: {len(teresa_records)} encontrados")
    for r in teresa_records[:8]:
        print(f"  - {r[0]} ({r[3]})")

    # 2. Pesquisa de Impostos (IVA, Guias de Pagamento AT, Modelo 2)
    cur.execute("""
    SELECT filename, filepath, size_bytes, categoria
    FROM evidencias
    WHERE filename LIKE '%iva%' OR filename LIKE '%finan%' OR filename LIKE '%imposto%' OR filename LIKE '%retenc%'
    LIMIT 25
    """)
    tax_records = cur.fetchall()
    print(f"\n[2] Registos de Impostos, Guias de IVA e Autoridade Tributaria: {len(tax_records)} encontrados")
    for r in tax_records[:8]:
        print(f"  - {r[0]} ({r[3]})")

    # 3. Pesquisa de Faturas e Recibos Emitidos
    cur.execute("""
    SELECT filename, filepath, size_bytes, categoria
    FROM evidencias
    WHERE filename LIKE '%fatura%' OR filename LIKE '%recibo%' OR filename LIKE '%invoice%'
    LIMIT 25
    """)
    invoice_records = cur.fetchall()
    print(f"\n[3] Faturas, Recibos e Invoices Identificados no Acervo: {len(invoice_records)} encontrados")
    for r in invoice_records[:8]:
        print(f"  - {r[0]} ({r[3]})")

    # 4. Pesquisa de Mapas Contabilisticos e Cash-Flow
    cur.execute("""
    SELECT filename, filepath, size_bytes, categoria
    FROM evidencias
    WHERE filename LIKE '%listarecibo%' OR filename LIKE '%listacontrato%' OR filename LIKE '%cash-flow%' OR filename LIKE '%contabilidade%'
    LIMIT 25
    """)
    accounting_records = cur.fetchall()
    print(f"\n[4] Mapas Contabilisticos e Listagens de Rendas: {len(accounting_records)} encontrados")
    for r in accounting_records[:8]:
        print(f"  - {r[0]} ({r[3]})")

    conn.close()

if __name__ == "__main__":
    audit_financial_records()
