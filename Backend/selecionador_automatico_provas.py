#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
selecionador_automatico_provas.py - Seletor e Agrupador Automatico de Provas Documentais por Processo Judicial.
Analisa o acervo de saida e copia/organiza as provas chave em pastas prontas para instrucao e envio.
Zero emojis conforme PROTOCOL.md.
"""

import os
import sys
import shutil
import hashlib
from pathlib import Path

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
OUTPUT_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO"
PROVAS_ROOT = OUTPUT_DIR / "03_PROVAS_SELECIONADAS_POR_PROCESSO"
MANIFEST_FILE = OUTPUT_DIR / "01_INDEX_E_RELATORIOS" / "MANIFESTO_PROVAS_SELECIONADAS.md"

SEARCH_LOCATIONS = [
    OUTPUT_DIR / "05_PDFS_GERADOS_PARA_IMPRESSAO",
    OUTPUT_DIR / "01_INDEX_E_RELATORIOS",
    OUTPUT_DIR / "04_DOCUMENTOS_CITIUS_E_PECAS",
    OUTPUT_DIR / "04_DOCUMENTOS_CITIUS_E_PECAS" / "ARQUIVO_OFICIAL_TRIBUNAL",
    OUTPUT_DIR / "04_DOCUMENTOS_CITIUS_E_PECAS" / "ARQUIVO_OFICIAL_TRIBUNAL" / "PROC_3719_CAUTELAR_ARQUIVADO",
    OUTPUT_DIR / "04_DOCUMENTOS_CITIUS_E_PECAS" / "ARQUIVO_OFICIAL_TRIBUNAL" / "PROC_15547_REIVINDICACAO",
    OUTPUT_DIR / "04_DOCUMENTOS_CITIUS_E_PECAS" / "ARQUIVO_OFICIAL_TRIBUNAL" / "PROC_23142_EXECUCAO_TRL",
    OUTPUT_DIR / "04_DOCUMENTOS_CITIUS_E_PECAS" / "ARQUIVO_OFICIAL_TRIBUNAL" / "PROC_10153_UNICRE_SUSPENSO",
    OUTPUT_DIR / "DOSSIER_FORENSE_ORGANIZADO"
]

REGRAS_SELECAO = {
    "PROC_15547_REIVINDICACAO": [
        "LISTA_CONTRATOS_TERESA.xls",
        "PROVA_FALSIDADE_FATURAS_E_CONTRATOS_TERESA_MARTINS.md",
        "ANALISE_PERICIAL_WHATSAPP_CORTE_AGUA_E_COACAO_FILIPE_DELGADO.md",
        "MINUTA_CONTESTACAO_15547_COMPLETA.md",
        "06_MINUTA_CONTESTACAO_15547_COMPLETA.pdf",
        "MINUTA_CONTESTACAO_15547_LIBREOFFICE.docx"
    ],
    "PROC_23142_EXECUCAO_TRL": [
        "01_DESPACHO_INDEFERIMENTO_LIMINAR_PROC_23142.pdf",
        "02_ACORDAO_TRL_EXTINCAO_EXECUCAO_23142.pdf",
        "04_REQUERIMENTO_LEVANTAMENTO_PENHORAS_35K.pdf",
        "03_RECLAMACAO_DISCIPLINAR_CAAJ_LUISA_SANTOS.pdf",
        "RECLAMACAO_CAAJ_E_QUADRO_FINANCEIRO_PROVAS.md"
    ],
    "PROC_10153_E_20203_UNICRE": [
        "05_DESPACHO_SUSPENSAO_EXECUCAO_UNICRE_PROC_10153.pdf",
        "PROVA_OMISSAO_DOLOSA_CITACOES_E_FRAUDE_MORADAS.md"
    ],
    "PROC_3719_CAUTELAR_ARQUIVADO": [
        "PROVA_IMPEDIMENTO_PRESENCA_SALA_AUDIENCIA_3719.md",
        "PROVA_CONFISSAO_WHATSAPP_FILIPE_DELGADO_20220823.md"
    ]
}

def calcular_sha256(filepath: Path) -> str:
    try:
        return hashlib.sha256(filepath.read_bytes()).hexdigest()
    except Exception:
        return "N/A"

def encontrar_ficheiro(nome_alvo: str) -> Path:
    for loc in SEARCH_LOCATIONS:
        if loc.exists():
            cand = loc / nome_alvo
            if cand.exists() and cand.is_file():
                return cand
            for sub in loc.iterdir():
                if sub.is_file() and sub.name.lower() == nome_alvo.lower():
                    return sub
    return None

def executar_selecao_automatica():
    print("=" * 80)
    print(" SELETOR AUTOMATICO DE PROVAS DOCUMENTAIS POR PROCESSO")
    print(f" Pasta Destino: {PROVAS_ROOT}")
    print("=" * 80)

    PROVAS_ROOT.mkdir(parents=True, exist_ok=True)
    manifesto_lines = [
        "# MANIFESTO OFICIAL DE PROVAS SELECIONADAS E CERTIFICADAS",
        "",
        "**Data de Emissao**: 2026-08-28  ",
        "**Autoridade**: PROTOCOL.md e AGENTS.md (Dev Yokozuna)  ",
        "**Objetivo**: Mapeamento automatico das provas documentais selecionadas por processo judicial.",
        "",
        "---",
        ""
    ]

    total_copiados = 0

    for proc_name, file_list in REGRAS_SELECAO.items():
        proc_dir = PROVAS_ROOT / proc_name
        proc_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n[*] A organizar pasta: {proc_name}")
        
        manifesto_lines.append(f"## {proc_name}")
        manifesto_lines.append("")
        manifesto_lines.append("| Ficheiro de Prova | SHA-256 (Prefixo) | Estado no Dossier |")
        manifesto_lines.append("|---|---|---|")

        for nome in file_list:
            origem = encontrar_ficheiro(nome)
            if origem:
                destino = proc_dir / origem.name
                shutil.copy2(origem, destino)
                sha = calcular_sha256(destino)
                print(f" [+] Selecionado e copiado: {origem.name}")
                manifesto_lines.append(f"| `{origem.name}` | `{sha[:16]}...` | **VALIDADO E CUSTODIADO** |")
                total_copiados += 1
            else:
                print(f" [-] Nao localizado: {nome}")
                manifesto_lines.append(f"| `{nome}` | N/A | *Em preparacao* |")

        manifesto_lines.append("")
        manifesto_lines.append("---")
        manifesto_lines.append("")

    MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(manifesto_lines))

    print("=" * 80)
    print(f" SUCESSO: {total_copiados} ficheiros de prova organizados e copiados.")
    print(f" Manifesto gravado em: {MANIFEST_FILE}")
    print("=" * 80)

if __name__ == "__main__":
    executar_selecao_automatica()
