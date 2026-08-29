#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extrator_excertos_forenses.py - Extrator Inteligente de Excertos, Confissões e Citações para Peças Processuais.
Processa transcrições de WhatsApp, emails e despachos Citius, extraindo citações formatadas para o Tribunal.
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import List, Dict, Any

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
OUTPUT_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO"
EXCERPTS_FILE = OUTPUT_DIR / "01_INDEX_E_RELATORIOS" / "EXCERTOS_PROBATORIOS_PARA_CONTESTACAO.md"

# Categorias tematicas de extracao
KEYWORDS_MAP = {
    "CORTE_DE_AGUA_E_COACAO": ["água", "epal", "hotel", "olho de boi", "heaven", "cortar", "ligar"],
    "CREDITOS_E_FALTA_PAGAMENTO_NUNO": ["renda", "5000", "garantida", "receber", "contas", "apartamento", "hipotequei"],
    "GESTAO_DIARIA_E_POSSE": ["video", "visita", "sky", "family", "reserva", "clientes", "escadas", "setembro"],
    "FATURAS_E_DIVERGENCIAS_FINANCAS": ["fatura", "finanças", "tinta azul", "82k", "33k", "lea", "suprimentos"]
}

def extrair_excertos_texto(texto: str) -> Dict[str, List[str]]:
    linhas = texto.strip().split("\n")
    excertos_por_categoria = {cat: [] for cat in KEYWORDS_MAP}
    
    # Padrao WhatsApp: DD/MM/AAAA, HH:MM - Emissor: Mensagem
    wa_pattern = re.compile(r"^(\d{2}/\d{2}/\d{4},\s*\d{2}:\d{2})\s*-\s*([^:]+):\s*(.*)$")

    for idx, l in enumerate(linhas):
        match = wa_pattern.match(l.strip())
        if match:
            dt, emissor, msg = match.groups()
            msg_lower = msg.lower()
            
            for cat, words in KEYWORDS_MAP.items():
                if any(w in msg_lower for w in words):
                    bloco_citacao = f"> **[{dt}] {emissor}**: *\"{msg}\"*"
                    excertos_por_categoria[cat].append(bloco_citacao)

    return excertos_por_categoria

def processar_transcricao_para_peça(texto_transcricao: str):
    print("=" * 80)
    print(" EXTRATOR FORENSE DE EXCERTOS E CONFISSÕES PARA A CONTESTAÇÃO")
    print("=" * 80)

    excertos = extrair_excertos_texto(texto_transcricao)
    
    md_output = [
        "# COMPILAÇÃO DE EXCERTOS E CONFISSÕES TRANSCRITAS (PARA ARTICULAR EM JUÍZO)",
        "",
        "**Data de Compilação**: 2026-08-28  ",
        "**Autoridade**: PROTOCOL.md e AGENTS.md (Dev Yokozuna)  ",
        "**Finalidade**: Inclusão direta na Contestação do Proc. 15547/26.0T8LSB e na Reclamação CAAJ.",
        "",
        "---",
        ""
    ]

    titulos_humanos = {
        "CORTE_DE_AGUA_E_COACAO": "1. PROVA DO CORTE DE ÁGUA E COAÇÃO HABITACIONAL (FILHAS NO HOTEL / EPAL)",
        "CREDITOS_E_FALTA_PAGAMENTO_NUNO": "2. CONFISSÕES DE CRÉDITOS RETIDOS E RENDA GARANTIDA A NUNO DUARTE",
        "GESTAO_DIARIA_E_POSSE": "3. PROVA DA POSSE PÚBLICA, GESTÃO DIÁRIA E MANUTENÇÃO DAS FRAÇÕES",
        "FATURAS_E_DIVERGENCIAS_FINANCAS": "4. DIVERGÊNCIAS FISCAIS E CONTRATOS REAIS (TINTA AZUL)"
    }

    total_excertos = 0
    for cat, items in excertos.items():
        if items:
            md_output.append(f"## {titulos_humanos.get(cat, cat)}")
            md_output.append("")
            for it in items[:15]: # Limite de amostragem mais forte
                md_output.append(it)
                md_output.append("")
                total_excertos += 1
            md_output.append("---")
            md_output.append("")

    EXCERPTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EXCERPTS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(md_output))

    print(f"[+] Total de excertos judiciais extraídos e formatados: {total_excertos}")
    print(f"[+] Documento gravado em: {EXCERPTS_FILE}")
    print("=" * 80)

if __name__ == "__main__":
    # Exemplo com o texto do chat
    raw_chat = """
23/08/2022, 08:30 - Filipe Delgado: Tens água ?
23/08/2022, 08:39 - Nuno Duarte: Nao
23/08/2022, 08:40 - Nuno Duarte: E a hevean tb nao
23/08/2022, 11:50 - Filipe Delgado: Epal só fez merda
23/08/2022, 12:19 - Nuno Duarte: tenho as miudas num Hotel
23/08/2022, 12:34 - Filipe Delgado: Não tenho dinheiro para pagar esses agora
23/08/2022, 12:42 - Filipe Delgado: Tinhas enviado o vídeo e tinha entrado 5000 para as contas e para uma casa para ti garantida
23/08/2022, 12:46 - Nuno Duarte: To a 1 mes a pedir agua
23/08/2022, 12:53 - Nuno Duarte: Tive aqui todos os dias. Hipotequei a minha vida
23/08/2022, 13:22 - Filipe Delgado: Ia pagar a heaven mas la com tanta coisa senhor pagou a Famíly e penthouse , já não dava para reverter , já não havia mais dinheiro
23/08/2022, 19:19 - Filipe Delgado: Mês setembro e suficiente para arranjar um apartamento , e primeiro tem de entrar dinheiro para garantir a renda e mensalmente para garantir a tua renda
23/08/2022, 19:21 - Filipe Delgado: Garantia da tua casa para viver só e possível com renda da sky e equilibrar as contas
    """
    processar_transcricao_para_peça(raw_chat)
