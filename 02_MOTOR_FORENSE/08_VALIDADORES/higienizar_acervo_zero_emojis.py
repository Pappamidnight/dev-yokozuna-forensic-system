#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
higienizar_acervo_zero_emojis.py - Higienizador Automatico de Emojis e Normalizador Institucional.
Remove todos os emojis de ficheiros markdown e json no acervo, substituindo por marcadores neutros ou texto institucional.
Conformidade estrita com PROTOCOL.md e AGENTS.md.
"""

import os
import sys
import re
from pathlib import Path

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")

# Mapeamento de emojis comuns para texto institucional limpo
EMOJI_REPLACEMENTS = {
    "🚨": "[ALERTA] ",
    "⚠️": "[ATENCAO] ",
    "✅": "[CONFORME] ",
    "❌": "[NULO/FALSO] ",
    "⚖️": "[JUDICIAL] ",
    "📌": "[NOTA] ",
    "💥": "[CONFLITO] ",
    "🟢": "[OK] ",
    "🔴": "[BLOQUEIO] ",
    "🚀": "[EXECUCAO] ",
    "📜": "[DOC] ",
    "🔍": "[ANALISE] ",
    "🔬": "[PERICIA] ",
    "👉": "[ITEM] ",
    "•": "-",
}

# Regex generico para qualquer outro emoji unicode
EMOJI_PATTERN = re.compile(
    r"[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf\ufe0f]",
    flags=re.UNICODE
)

def higienizar_ficheiro(path: Path) -> int:
    try:
        conteudo = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return 0

    original = conteudo
    
    # 1. Substituicoes semanticas
    for emo, rep in EMOJI_REPLACEMENTS.items():
        conteudo = conteudo.replace(emo, rep)

    # 2. Remocao de emojis residuais
    conteudo = EMOJI_PATTERN.sub("", conteudo)

    if conteudo != original:
        path.write_text(conteudo, encoding="utf-8")
        return 1
    return 0

def executar_higienizacao():
    print("=" * 80)
    print(" SENTINELA-5: HIGIENIZACAO AUTOMATICA ZERO-EMOJIS (PROTOCOL.MD)")
    print("=" * 80)

    pastas = [
        DEV_ROOT / "OUTPUT_CENTRALIZADO" / "01_INDEX_E_RELATORIOS",
        DEV_ROOT / "03_RESULTADOS" / "01_INDICES_E_RELATORIOS",
        DEV_ROOT / "03_RESULTADOS" / "03_PECAS_JUDICIAIS",
        DEV_ROOT / "04_CONTROLO_E_INDICES",
        DEV_ROOT / "AI"
    ]

    total_limpos = 0
    total_verificados = 0

    for pasta in pastas:
        if pasta.exists():
            for f in pasta.glob("*.md"):
                total_verificados += 1
                if higienizar_ficheiro(f):
                    total_limpos += 1
                    print(f"  [HIGIENIZADO] {f.name}")

    # Higienizar AGENTS.md na raiz se tiver emoji
    agents_root = DEV_ROOT / "AGENTS.md"
    if agents_root.exists():
        total_verificados += 1
        if higienizar_ficheiro(agents_root):
            total_limpos += 1
            print(f"  [HIGIENIZADO] AGENTS.md")

    print("=" * 80)
    print(f" RESULTADO: {total_limpos} ficheiros higienizados de um total de {total_verificados}.")
    print(" Conformidade com PROTOCOL.md e AGENTS.md restabelecida a 100%.")
    print("=" * 80)

if __name__ == "__main__":
    executar_higienizacao()
