#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_early_whatsapp_2022.py - Extrator cronologico de conversas de WhatsApp de 2021 e 1Q 2022 (Jan-Mar 2022).
"""
import os
import sys
import re
import zipfile
from pathlib import Path

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
OUTPUT_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "01_INDEX_E_RELATORIOS"

def extract_target_messages():
    print("=" * 80)
    print(" EXTRATOR DE CONVERSAS DE WHATSAPP: 2021 E 1.º TRIMESTRE DE 2022 (1Q 2022)")
    print("=" * 80)

    chat_files = [
        r"C:\Users\Yokozuna\OneDrive\GESTAO\00_OBSIDIAN_VAULT\02_PROVAS_E_WHATSAPP\Antonio_Neto\WhatsApp Chat with Antonio Neto.txt",
        r"C:\Users\Yokozuna\OneDrive\GESTAO\00_OBSIDIAN_VAULT\02_PROVAS_E_WHATSAPP\WhatsApp Chat with Filipe Delgado[1].txt",
        r"I:\whatsappchatwithfilipedelgado\WhatsApp Chat with Filipe Delgado.txt",
        r"I:\whatsappchatwithfilipedelgado.zip"
    ]

    # Expressao regular para datas do WhatsApp (dd/mm/aaaa ou dd/mm/yy ou aaaa-mm-dd)
    # Procurar por anos 2021 e 2022 (especialmente 01/2022, 02/2022, 03/2022)
    patterns_1q = [
        re.compile(r'(\d{1,2}/\d{1,2}/21|\d{1,2}/\d{1,2}/2021|\d{1,2}/0[1-3]/22|\d{1,2}/0[1-3]/2022)'),
        re.compile(r'(2021-0[1-9]|2021-1[0-2]|2022-0[1-3])')
    ]

    extracted_messages = []

    for cf in chat_files:
        if not os.path.exists(cf):
            continue
        print(f"\n[+] A processar: {cf}")
        if cf.endswith('.zip'):
            try:
                with zipfile.ZipFile(cf, 'r') as z:
                    for name in z.namelist():
                        if name.endswith('.txt'):
                            with z.open(name) as zf:
                                raw = zf.read().decode('utf-8', errors='ignore')
                                lines = raw.splitlines()
                                print(f"  -> Arquivo ZIP [{name}]: {len(lines)} linhas")
                                parse_lines(lines, name, extracted_messages, patterns_1q)
            except Exception as e:
                print(f"  [-] Erro ao ler zip: {e}")
        else:
            try:
                with open(cf, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                print(f"  -> Ficheiro TXT: {len(lines)} linhas")
                parse_lines(lines, os.path.basename(cf), extracted_messages, patterns_1q)
            except Exception as e:
                print(f"  [-] Erro ao ler txt: {e}")

    # Gravar relatorio consolidado
    out_md = OUTPUT_DIR / "CONVERSAS_WHATSAPP_2021_1Q2022_EXTRAIDAS.md"
    print(f"\n[+] Total de mensagens de 2021 e 1Q 2022 filtradas: {len(extracted_messages)}")
    with open(out_md, 'w', encoding='utf-8') as out:
        out.write("# Registo Pericial de Mensagens WhatsApp: Exercício de 2021 e 1.º Trimestre de 2022 (1Q 2022)\n\n")
        out.write(f"**Data de Extração**: 2026-08-28\n")
        out.write(f"**Critério de Busca**: Mensagens emitidas entre 01/01/2021 e 31/03/2022 (incluindo Filipe Delgado, António Neto, Teresa Martins e LEA)\n")
        out.write(f"**Total de Mensagens Relevantes**: {len(extracted_messages)}\n\n---\n\n")
        for m in extracted_messages[:150]:
            out.write(f"```\n{m['raw']}\n```\n\n")

    print(f"[+] Relatorio gerado com sucesso: {out_md}")

def parse_lines(lines, src_name, target_list, patterns):
    current_match = None
    for l in lines:
        l_str = l.strip()
        if not l_str: continue
        is_date = any(p.search(l_str) for p in patterns)
        if is_date:
            target_list.append({"src": src_name, "raw": l_str})
        elif len(target_list) > 0 and len(l_str) > 0 and not re.match(r'^\d{1,2}/\d{1,2}/\d{2,4}', l_str):
            # Continuacao de mensagem anterior
            if len(target_list[-1]["raw"]) < 2000:
                target_list[-1]["raw"] += "\n" + l_str

if __name__ == "__main__":
    extract_target_messages()
