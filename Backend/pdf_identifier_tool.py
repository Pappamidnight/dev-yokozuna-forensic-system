#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pdf_identifier_tool.py - Ferramenta Leve de Identificacao de Texto e Palavras em Ficheiros PDF (Conceito PDF-ID).
Funciona com a biblioteca padrao do Python (sem dependencias externas), fazendo busca direta e ultra-rapida.
Zero emojis conforme PROTOCOL.md.
"""

import os
import sys
import re
import zlib
import hashlib
from pathlib import Path
from typing import List, Dict, Any

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
PDFS_GEN_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "05_PDFS_GERADOS_PARA_IMPRESSAO"
PROVAS_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "03_PROVAS_SELECIONADAS_POR_PROCESSO"
TRIBUNAL_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "04_DOCUMENTOS_CITIUS_E_PECAS" / "ARQUIVO_OFICIAL_TRIBUNAL"

def extrair_texto_pdf_rapido(content: bytes) -> str:
    """Extrai texto e strings descomprimindo streams FlateDecode de forma resiliente."""
    chunks = []
    
    # 1. Strings literais diretas
    for match in re.finditer(rb"\(([^)]{2,100})\)", content):
        try:
            chunks.append(match.group(1).decode("latin1", errors="ignore"))
        except Exception:
            pass

    # 2. Streams comprimidos
    for match in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", content, re.DOTALL):
        raw_stream = match.group(1)
        try:
            decomp = zlib.decompress(raw_stream)
            chunks.append(decomp.decode("latin1", errors="ignore"))
        except Exception:
            try:
                # Tentativa com raw inflate sem cabeçalho zlib
                decomp = zlib.decompress(raw_stream, -15)
                chunks.append(decomp.decode("latin1", errors="ignore"))
            except Exception:
                pass

    return " ".join(chunks)

def buscar_palavra_nos_pdfs(termo_busca: str, max_resultados=20):
    print("=" * 80, flush=True)
    print(f" PDF-ID LOCATOR: A PESQUISAR POR '{termo_busca}' NOS DOCUMENTOS PDF", flush=True)
    print("=" * 80, flush=True)

    pastas = [PDFS_GEN_DIR, PROVAS_DIR, TRIBUNAL_DIR]
    ficheiros = []
    for p in pastas:
        if p.exists():
            ficheiros.extend(list(p.rglob("*.pdf")))

    # Remover duplicados
    unicos = sorted(list({f.resolve(): f for f in ficheiros if "node_modules" not in str(f)}.values()), key=lambda x: x.name)
    print(f"[*] Total de ficheiros PDF indexados para busca: {len(unicos)}\n", flush=True)

    termo_l = termo_busca.lower()
    encontrados = 0

    for pdf in unicos:
        try:
            match_nome = termo_l in pdf.name.lower()
            data = pdf.read_bytes()
            texto = extrair_texto_pdf_rapido(data)
            match_texto = termo_l in texto.lower()

            if match_nome or match_texto:
                encontrados += 1
                sha = hashlib.sha256(data).hexdigest()[:16]
                tipo = "Nome e Texto" if (match_nome and match_texto) else ("Texto Interno" if match_texto else "Nome do Ficheiro")
                
                print(f"[{encontrados:02d}] PDF: {pdf.name}", flush=True)
                print(f"     Caminho: {pdf}", flush=True)
                print(f"     Match:   {tipo} | SHA-256: {sha}...", flush=True)
                
                if match_texto:
                    pos = texto.lower().find(termo_l)
                    ini = max(0, pos - 35)
                    fim = min(len(texto), pos + len(termo_busca) + 35)
                    snip = texto[ini:fim].replace("\n", " ").replace("\r", " ").strip()
                    print(f"     Excerto: \"...{snip}...\"", flush=True)
                print("-" * 80, flush=True)

                if encontrados >= max_resultados:
                    break
        except Exception:
            pass

    print("=" * 80, flush=True)
    print(f" SUCESSO: {encontrados} documentos PDF identificados com o termo '{termo_busca}'.", flush=True)
    print("=" * 80, flush=True)

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "419855940"
    buscar_palavra_nos_pdfs(q)
