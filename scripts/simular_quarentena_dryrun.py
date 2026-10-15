#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
simular_quarentena_dryrun.py
Simulador de Quarentena Forense V8 (100% DRY-RUN).
Modo: READ-ONLY (NENHUM FICHEIRO E MOVIDO OU APAGADO).
Processa exclusivamente 1 tipo de cada vez a partir do CSV de Ultra-Confiança.
Filtro: Score de Confiança == 100 (Identidade Cripto Provavel).
Gera manifesto JSON de simulacao e calcula o espaco exato recuperavel em MB/GB.
"""

import csv
import sys
import json
import time
from pathlib import Path
from datetime import datetime

DIR_CRUZADO = Path(r"C:\ACERVO\logs\csv_max_confidence\cruzamento_ultra_confianca_v8.csv")
OUT_DIR = Path(r"C:\ACERVO\logs\quarentena_dryrun")
OUT_DIR.mkdir(parents=True, exist_ok=True)

QUARENTENA_ALVO = Path(r"C:\ACERVO\quarentena")

def formatar_tamanho(bytes_total):
    if bytes_total >= 1024**3:
        return f"{bytes_total / (1024**3):.2f} GB"
    elif bytes_total >= 1024**2:
        return f"{bytes_total / (1024**2):.2f} MB"
    elif bytes_total >= 1024:
        return f"{bytes_total / 1024:.2f} KB"
    return f"{bytes_total} B"

def simular_tipo(tipo_alvo):
    tipo_alvo = tipo_alvo.lower().strip()
    manifesto_path = OUT_DIR / f"manifesto_quarentena_dryrun_{tipo_alvo}.json"
    csv_simulado = OUT_DIR / f"candidatos_quarentena_{tipo_alvo}.csv"

    print("=" * 75)
    print(f"  ACERVO V8 - SIMULAÇÃO DE QUARENTENA DRY-RUN: [{tipo_alvo.upper()}]")
    print(f"  Modo Operacional:  DRY-RUN (ESTRITAMENTE READ-ONLY)")
    print(f"  Ação em Disco:     ZERO FICHEIROS MOVIDOS / ZERO APAGADOS")
    print(f"  Filtro de Decisão: Score de Confiança == 100")
    print("=" * 75)

    if not DIR_CRUZADO.exists():
        print(f"[ERRO] CSV de ultra-confiança não encontrado em: {DIR_CRUZADO}")
        sys.exit(1)

    t0 = time.time()
    candidatos_quarentena = []
    bytes_recuperaveis = 0
    originais_protegidos = set()
    duplicados_mapeados = set()

    with open(DIR_CRUZADO, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            orig_tipo = (row.get("orig_tipo") or "").lower()
            dup_tipo = (row.get("dup_tipo") or "").lower()

            # Filtrar pelo tipo solicitado
            if orig_tipo != tipo_alvo and dup_tipo != tipo_alvo:
                continue

            score = int(row.get("score_confianca") or 0)
            if score < 100:
                continue

            orig_path = row.get("orig_caminho")
            orig_nome = row.get("orig_nome")
            dup_path = row.get("dup_caminho")
            dup_nome = row.get("dup_nome")
            tam = int(row.get("tamanho_bytes") or 0)

            orig_completo = str(Path(orig_path) / orig_nome) if orig_path and orig_nome else ""
            dup_completo = str(Path(dup_path) / dup_nome) if dup_path and dup_nome else ""

            if not dup_completo or dup_completo in duplicados_mapeados:
                continue

            duplicados_mapeados.add(dup_completo)
            originais_protegidos.add(orig_completo)
            bytes_recuperaveis += tam

            # Definir destino projetado em quarentena (preservando estrutura segura)
            sub_destino = f"{tipo_alvo}/{Path(dup_nome).name}"
            caminho_quarentena_projetado = str(QUARENTENA_ALVO / sub_destino)

            candidatos_quarentena.append({
                "id_par": row.get("id_par"),
                "score_confianca": score,
                "orig_vencedor": orig_completo,
                "orig_rank": row.get("orig_rank"),
                "dup_candidato_quarentena": dup_completo,
                "dup_rank": row.get("dup_rank"),
                "destino_quarentena_projetado": caminho_quarentena_projetado,
                "tamanho_bytes": tam,
                "tamanho_formatado": formatar_tamanho(tam),
                "sinais": row.get("sinais_detetados")
            })

    duracao = time.time() - t0

    # Gravar CSV de Candidatos Mapeados
    if candidatos_quarentena:
        with open(csv_simulado, "w", newline="", encoding="utf-8-sig") as f_csv:
            writer = csv.DictWriter(f_csv, fieldnames=list(candidatos_quarentena[0].keys()))
            writer.writeheader()
            writer.writerows(candidatos_quarentena)

    # Gerar Manifesto JSON Formal V8
    manifesto = {
        "modo": "DRYRUN",
        "tipo": tipo_alvo,
        "timestamp_simulacao": datetime.now().isoformat(),
        "duracao_segundos": round(duracao, 2),
        "total_candidatos_quarentena": len(candidatos_quarentena),
        "total_originais_protegidos": len(originais_protegidos),
        "bytes_recuperaveis": bytes_recuperaveis,
        "espaco_recuperavel_formatado": formatar_tamanho(bytes_recuperaveis),
        "acao_executada": "NENHUMA",
        "ficheiros_fisicamente_movidos": 0,
        "ficheiros_apagados": 0,
        "ficheiro_origem_auditoria": DIR_CRUZADO.name,
        "manifesto_csv": csv_simulado.name,
        "status_validacao": "SIMULACAO_BEM_SUCEDIDA"
    }

    with open(manifesto_path, "w", encoding="utf-8") as f_json:
        json.dump(manifesto, f_json, indent=2, ensure_ascii=False)

    print("-" * 75)
    print("  RESULTADO DA SIMULAÇÃO (DRY-RUN):")
    print(f"  Originais Protegidos no Hub:       {len(originais_protegidos):7}")
    print(f"  Cópias Mapeadas para Quarentena:   {len(candidatos_quarentena):7}")
    print(f"  Espaço Recuperável Projetado:      {formatar_tamanho(bytes_recuperaveis)}")
    print(f"  Tempo de Análise:                  {duracao:.2f}s")
    print(f"  Ficheiros Fisicamente Alterados:   0 (INTEGRIDADE TOTAL)")
    print("-" * 75)
    print(f"  Manifesto JSON: {manifesto_path}")
    print(f"  Lista CSV:      {csv_simulado}")
    print("=" * 75)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python simular_quarentena_dryrun.py <tipo>")
        print("Exemplo: python simular_quarentena_dryrun.py database")
        print("Exemplo: python simular_quarentena_dryrun.py pdf")
        sys.exit(1)
    simular_tipo(sys.argv[1])
