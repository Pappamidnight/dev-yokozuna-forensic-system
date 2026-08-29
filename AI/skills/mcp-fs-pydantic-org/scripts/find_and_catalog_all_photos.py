#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
find_and_catalog_all_photos.py - Localizador, Recuperador e Catalogo de Todas as Fotografias Forenses.
Identifica fotos em todas as drives (OneDrive, Dev, I:, F:, J:) e gera galeria visual HTML.
"""

import os
import sys
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
PHOTO_CENTRAL = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "02_DADOS_ESTRUTURADOS" / "GALERIA_FOTOS_COMPLETA"
HTML_GALLERY = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "01_INDEX_E_RELATORIOS" / "GALERIA_FOTOS_FORENSES.html"
DB_PATH = DEV_ROOT / "OUTPUT_CENTRALIZADO" / "02_DADOS_ESTRUTURADOS" / "memoria_forense_unificada.db"

SEARCH_ROOTS = [
    DEV_ROOT / "OUTPUT_CENTRALIZADO",
    DEV_ROOT / "Projects",
    Path(r"C:\Users\Yokozuna\OneDrive\GESTAO"),
    Path(r"I:\whatsappchatwithfilipedelgado"),
    Path(r"I:\RECUPERADO"),
    Path(r"I:\Backup"),
    Path(r"J:\audios"),
    Path(r"J:\SPARK LEGAL"),
    Path(r"F:\defesa")
]

VALID_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".bmp"}

def catalog_photos():
    print("=" * 80)
    print(" LOCALIZADOR E COMPILADOR DE FOTOGRAFIAS FORENSES")
    print(f" Destino: {PHOTO_CENTRAL}")
    print("=" * 80)

    PHOTO_CENTRAL.mkdir(parents=True, exist_ok=True)

    found_images = []
    seen_hashes = set()

    for sroot in SEARCH_ROOTS:
        if not sroot.exists():
            continue
        print(f"\n[+] A varrer imagens em: {sroot} ...")
        for root, dirs, files in os.walk(str(sroot)):
            if "GALERIA_FOTOS_COMPLETA" in root:
                continue

            for f in files:
                ext = os.path.splitext(f.lower())[1]
                if ext in VALID_EXTS:
                    fp = os.path.join(root, f)
                    try:
                        sz = os.path.getsize(fp)
                        if sz < 1000: # Ignorar icones minusculos
                            continue
                        
                        # Copiar imagem para a galeria central
                        dest_f = PHOTO_CENTRAL / f
                        if not dest_f.exists():
                            shutil.copy2(fp, dest_f)

                        mtime = datetime.fromtimestamp(os.path.getmtime(fp)).strftime("%Y-%m-%d %H:%M")
                        found_images.append({
                            "name": f,
                            "path": fp,
                            "rel_path": f"../02_DADOS_ESTRUTURADOS/GALERIA_FOTOS_COMPLETA/{f}",
                            "size_kb": f"{sz / 1024:.1f}",
                            "mtime": mtime
                        })
                    except Exception:
                        pass

    print(f"\n[+] Total de Fotografias Identificadas e Centralizadas: {len(found_images)}")

    # Gerar Galeria Visual HTML
    generate_html_gallery(found_images)

def generate_html_gallery(images):
    html_content = """<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Galeria Forense de Fotografias e Vistorias - Dev Yokozuna</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: #090d16; color: #f9fafb; padding: 24px; }
        .container { max-width: 1400px; margin: 0 auto; }
        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid #374151; }
        h1 { font-size: 22px; font-weight: 800; color: #fff; }
        .count-badge { background: rgba(6, 182, 212, 0.15); color: #06b6d4; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 700; border: 1px solid #06b6d4; }
        
        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: 18px;
        }
        .img-card {
            background: #111827;
            border: 1px solid #374151;
            border-radius: 10px;
            overflow: hidden;
            transition: transform 0.2s, border-color 0.2s;
        }
        .img-card:hover { transform: translateY(-3px); border-color: #06b6d4; }
        .img-preview {
            width: 100%;
            height: 180px;
            object-fit: cover;
            background: #000;
            display: block;
        }
        .img-meta {
            padding: 12px;
        }
        .img-name { font-size: 12px; font-weight: 700; color: #fff; margin-bottom: 4px; word-break: break-all; }
        .img-sub { font-size: 11px; color: #9ca3af; display: flex; justify-content: space-between; }
    </style>
</head>
<body>
<div class="container">
    <header>
        <div>
            <h1>Galeria Forense de Fotografias e Provas Materiais</h1>
            <p style="color:#9ca3af; font-size:13px; margin-top:4px;">Fotos de Vistoria, Anexos Judiciais, Imóveis e WhatsApp</p>
        </div>
        <div class="count-badge">""" + f"{len(images)} FOTOGRAFIAS RECUPERADAS" + """</div>
    </header>

    <div class="gallery-grid">
"""

    for img in images[:300]: # Mostrar ate 300 imagens
        html_content += f"""
        <div class="img-card">
            <a href="{img['rel_path']}" target="_blank">
                <img src="{img['rel_path']}" class="img-preview" alt="{img['name']}" loading="lazy">
            </a>
            <div class="img-meta">
                <div class="img-name">{img['name']}</div>
                <div class="img-sub">
                    <span>{img['mtime']}</span>
                    <span>{img['size_kb']} KB</span>
                </div>
            </div>
        </div>
"""

    html_content += """
    </div>
</div>
</body>
</html>
"""

    with open(HTML_GALLERY, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[+] Galeria Visual HTML criada com sucesso: {HTML_GALLERY}")

if __name__ == "__main__":
    catalog_photos()
