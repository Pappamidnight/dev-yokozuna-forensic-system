#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline_heuristica_tipo_a_tipo.py
Execucao Heuristica e Atomica: 1 Tipo de Cada Vez.
Garante isolamento absoluto de processamento e validacao matematica.

Ordem recomendada:
  1. pdf
  2. imagem
  3. audio
  4. video

Uso:
  python pipeline_heuristica_tipo_a_tipo.py --tipo pdf
  python pipeline_heuristica_tipo_a_tipo.py --tipo imagem
  python pipeline_heuristica_tipo_a_tipo.py --tipo audio
  python pipeline_heuristica_tipo_a_tipo.py --tipo video
"""

import os
import sys
import csv
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Catalogo estrito de extensoes por tipo
MAPA_EXTENSOES = {
    "pdf": {".pdf"},
    "imagem": {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".gif"},
    "audio": {".mp3", ".wav", ".m4a", ".ogg", ".aac", ".opus", ".flac", ".wma"},
    "video": {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm"},
    "excel": {".xlsx", ".xls", ".ods", ".csv"},
    "word": {".docx", ".doc", ".odt"},
    "database": {".sqlite", ".sqlite3", ".db", ".duckdb"}
}

PASTAS_PROVA = [
    Path(r"C:\Users\Yokozuna\Desktop\PROVAS_15547"),
    Path(r"C:\Users\Yokozuna\Desktop\PROVAS_3719"),
    Path(r"C:\Users\Yokozuna\Desktop\PROVAS_10153"),
    Path(r"C:\Users\Yokozuna\Desktop\PROVAS_20203"),
    Path(r"C:\Users\Yokozuna\Desktop\PROVAS_23142"),
    Path(r"C:\Users\Yokozuna\Desktop\DOSSIER_15547"),
    Path(r"C:\Users\Yokozuna\Desktop\00_DOCUMENTOS_OFICIAIS_TRIBUNAL"),
    Path(r"C:\Users\Yokozuna\Desktop\RECUPERADOS_JURIDICO"),
    Path(r"C:\Users\Yokozuna\Desktop\ACERVO_FORENSE"),
    Path(r"C:\Users\Yokozuna\Desktop\LEA"),
    Path(r"C:\Users\Yokozuna\Desktop\SPARK"),
    Path(r"C:\Users\Yokozuna\Desktop\whatsapp_backup"),
]

PASTAS_IGNORAR = {
    ".git", ".venv", "node_modules", "__pycache__", "site-packages",
    "quarentena", "AppData", "$Recycle.Bin"
}

SAIDA_BASE = Path(r"C:\ACERVO\logs\heuristica_v8")
SAIDA_BASE.mkdir(parents=True, exist_ok=True)


def formatar_tamanho(bytes_total: int) -> str:
    for unidade in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_total < 1024:
            return f"{bytes_total:.2f} {unidade}"
        bytes_total /= 1024
    return f"{bytes_total:.2f} PB"


def recolher_ficheiros_tipo(tipo: str):
    """
    Varre estritamente os ficheiros pertencentes ao tipo indicado.
    Protegido contra ficheiros bloqueados ou corrompidos pelo SO.
    """
    extensoes_alvo = MAPA_EXTENSOES[tipo]
    ficheiros_encontrados = []
    erros = 0

    print(f"[FASE 1/3] A rastrear exclusivamente ficheiros [{tipo.upper()}]...")
    for pasta in PASTAS_PROVA:
        if not pasta.exists():
            continue

        try:
            for raiz, dirs, ficheiros in os.walk(pasta):
                dirs[:] = [d for d in dirs if d not in PASTAS_IGNORAR]

                for nome in ficheiros:
                    ext = Path(nome).suffix.lower()
                    if ext not in extensoes_alvo:
                        continue

                    caminho_completo = Path(raiz) / nome
                    try:
                        tam = caminho_completo.stat().st_size
                        if tam <= 0:
                            continue
                        mod_time = datetime.fromtimestamp(caminho_completo.stat().st_mtime).isoformat()
                    except OSError:
                        erros += 1
                        continue

                    ficheiros_encontrados.append({
                        "tipo": tipo,
                        "nome": nome,
                        "stem": caminho_completo.stem.lower(),
                        "ext": ext,
                        "tamanho": tam,
                        "caminho": str(caminho_completo),
                        "mtime": mod_time,
                        "profundidade": len(caminho_completo.parts)
                    })
        except OSError:
            erros += 1
            continue

    return ficheiros_encontrados, erros


def segregar_e_validar(tipo: str, registos: list, erros: int):
    """
    Agrupa por identidade (stem + tamanho + ext) e elege o original por soberania.
    Executa a equacao de conservacao e validacao matematica.
    """
    print(f"[FASE 2/3] A agrupar e calcular duplicados para [{tipo.upper()}]...")

    grupos = defaultdict(list)
    for r in registos:
        chave = (r["stem"], r["tamanho"], r["ext"])
        grupos[chave].append(r)

    originais = []
    duplicados = []

    for chave, lista in grupos.items():
        if len(lista) == 1:
            originais.append(lista[0])
            continue

        lista.sort(key=lambda x: (x["profundidade"], len(x["caminho"]), x["caminho"]))
        originais.append(lista[0])

        for dup in lista[1:]:
            item_dup = dict(dup)
            item_dup["original_eleito"] = lista[0]["caminho"]
            duplicados.append(item_dup)

    total_entrada = len(registos)
    total_saida = len(originais) + len(duplicados)
    diferenca = total_entrada - total_saida

    if diferenca != 0 or len(grupos) != len(originais):
        estado = "FALHA_CONSERVACAO"
        print(f"[ERRO CRITICO] Quebra de conservacao matematica em {tipo.upper()}!")
        print(f"Entrada: {total_entrada} | Saida: {total_saida} | Diferenca: {diferenca}")
    else:
        estado = "VALIDADO"

    return originais, duplicados, len(grupos), estado


def persistir_artefactos(tipo: str, originais: list, duplicados: list, grupos_count: int, total: int, erros: int, estado: str, tempo_gasto: float):
    """
    Persiste CSVs de originais, duplicados e o manifesto JSON de auditoria.
    """
    print(f"[FASE 3/3] A gravar artefactos canonicos para [{tipo.upper()}]...")

    colunas = ["tipo", "nome", "stem", "ext", "tamanho", "caminho", "mtime", "profundidade"]

    path_orig = SAIDA_BASE / f"originais_{tipo}.csv"
    with open(path_orig, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=colunas, extrasaction="ignore")
        w.writeheader()
        w.writerows(originais)

    path_dup = SAIDA_BASE / f"duplicados_{tipo}.csv"
    colunas_dup = colunas + ["original_eleito"]
    with open(path_dup, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=colunas_dup, extrasaction="ignore")
        w.writeheader()
        w.writerows(duplicados)

    espaco_recuperavel = sum(d["tamanho"] for d in duplicados)
    manifesto = {
        "tipo": tipo,
        "timestamp": datetime.now().isoformat(),
        "estado": estado,
        "total_analisado": total,
        "grupos_unicos": grupos_count,
        "originais_eleitos": len(originais),
        "duplicados_identificados": len(duplicados),
        "erros_io": erros,
        "espaco_recuperavel_bytes": espaco_recuperavel,
        "espaco_recuperavel_humano": formatar_tamanho(espaco_recuperavel),
        "tempo_execucao_segundos": round(tempo_gasto, 2),
        "equacao_conservacao": {
            "diferenca": total - (len(originais) + len(duplicados)),
            "conservacao_cumprida": (total == len(originais) + len(duplicados))
        }
    }

    path_man = SAIDA_BASE / f"manifesto_{tipo}.json"
    with open(path_man, "w", encoding="utf-8") as f:
        json.dump(manifesto, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 70)
    print(f"RESUMO DO TIPO [{tipo.upper()}]: {estado}")
    print("=" * 70)
    print(f"Total Analisado:       {total:>8,}")
    print(f"Originais Eleitos:     {len(originais):>8,}")
    print(f"Duplicados Detetados:  {len(duplicados):>8,}")
    print(f"Espaco Redundante:     {formatar_tamanho(espaco_recuperavel)}")
    print(f"Tempo Total:           {tempo_gasto:.2f}s")
    print(f"Manifesto Gerado:      {path_man}")
    print("=" * 70)

    if estado != "VALIDADO":
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Triagem Unitaria V8: 1 Tipo de Cada Vez")
    parser.add_argument("--tipo", required=True, choices=list(MAPA_EXTENSOES.keys()),
                        help="Tipo especifico a processar (ex: pdf, imagem, audio, video)")
    args = parser.parse_args()

    inicio = time.time()
    tipo = args.tipo.lower()

    print(f"\nINICIANDO PROCESSAMENTO UNITARIO DO TIPO: [{tipo.upper()}]")
    print("-" * 70)

    registos, erros = recolher_ficheiros_tipo(tipo)
    if not registos:
        print(f"[AVISO] Nenhum ficheiro do tipo '{tipo}' encontrado.")
        return

    originais, duplicados, grupos_count, estado = segregar_e_validar(tipo, registos, erros)
    tempo_total = time.time() - inicio

    persistir_artefactos(tipo, originais, duplicados, grupos_count, len(registos), erros, estado, tempo_total)


if __name__ == "__main__":
    main()
