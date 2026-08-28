#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_from_links.py - Descarrega documentos, folhas e ficheiros a partir de links do Google
Lê links.txt e exporta Docs -> PDF, Sheets -> XLSX e Ficheiros -> Binário.
"""

import os
import re
import sys
import json
import urllib.request
import urllib.error
import logging
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [DOWNLOAD-LINKS] - %(levelname)s - %(message)s"
)
logger = logging.getLogger("download_links")

BASE_DIR = Path(__file__).resolve().parent
LINKS_FILE = BASE_DIR / "links.txt"
DEST_DIR = BASE_DIR / "data" / "raw" / "google_links"
DEST_DIR.mkdir(parents=True, exist_ok=True)


def extract_id(url: str) -> tuple[Optional[str], str]:
    """Extrai o ID e o tipo a partir de URLs do Google Docs, Sheets, Drive."""
    # Google Docs
    m_doc = re.search(r"/document/d/([a-zA-Z0-9-_]+)", url)
    if m_doc:
        return m_doc.group(1), "document"
    # Google Sheets
    m_sheet = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
    if m_sheet:
        return m_sheet.group(1), "spreadsheet"
    # Google Drive File
    m_file = re.search(r"/file/d/([a-zA-Z0-9-_]+)", url)
    if m_file:
        return m_file.group(1), "file"
    # Open ID param
    m_id = re.search(r"[?&]id=([a-zA-Z0-9-_]+)", url)
    if m_id:
        return m_id.group(1), "file"
    return None, "unknown"


def download_link(url: str, token: str = "") -> Optional[Path]:
    file_id, doc_type = extract_id(url)
    if not file_id:
        return None

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    if doc_type == "document":
        export_url = f"https://docs.google.com/document/d/{file_id}/export?format=pdf"
        target_file = DEST_DIR / f"Doc_{file_id}.pdf"
    elif doc_type == "spreadsheet":
        export_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
        target_file = DEST_DIR / f"Sheet_{file_id}.xlsx"
    else:
        export_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        target_file = DEST_DIR / f"File_{file_id}.bin"

    req = urllib.request.Request(export_url, headers=headers)
    try:
        logger.info(f"⬇️ A descarregar [{doc_type}]: {file_id} ...")
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            with open(target_file, "wb") as f:
                f.write(data)
            logger.info(f"✅ Guardado: {target_file.name} ({len(data)} bytes)")
            return target_file
    except urllib.error.HTTPError as e:
        logger.warning(f"❌ Erro HTTP {e.code} ao descarregar {file_id}: {e.reason}")
    except Exception as e:
        logger.warning(f"❌ Falha ao descarregar {file_id}: {e}")
    return None


def main():
    if not LINKS_FILE.exists():
        logger.warning(f"Ficheiro de links não encontrado: {LINKS_FILE}")
        logger.info("Crie o ficheiro 'links.txt' e cole os links do Google (1 por linha).")
        return

    env_path = BASE_DIR / ".env"
    token = ""
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("GOOGLE_ACCESS_TOKEN="):
                token = line.split("=", 1)[1].strip()

    with open(LINKS_FILE, "r", encoding="utf-8", errors="ignore") as f:
        urls = [l.strip() for l in f if l.strip() and l.strip().startswith("http")]

    logger.info(f"📋 Encontrados {len(urls)} links para download em {LINKS_FILE.name}")
    success_count = 0
    for u in urls:
        res = download_link(u, token)
        if res:
            success_count += 1

    logger.info(f"🎉 Concluído! {success_count}/{len(urls)} ficheiros descarregados com sucesso.")


if __name__ == "__main__":
    main()
