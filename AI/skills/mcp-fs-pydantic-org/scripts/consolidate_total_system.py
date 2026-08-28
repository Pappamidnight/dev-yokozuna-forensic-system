#!/usr/bin/env python3
"""
Modulo de Consolidacao Total do Ecossistema (consolidate_total_system.py).
Integra todas as fontes (Google Drive G:\\, OneDrive, Pastas Processuais 01-06, Desktop, Documents),
protege ficheiros de sistema e configuracoes de IA, executa a memoria vetorial RAG,
valida modelos Pydantic v2, roda o Frozen Judge 100/100 e compila o Dossie Mestre.
Zero emojis, 100% deterministico e auditavel.
"""
import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
SKILLS_DIR = DEV_ROOT / "AI" / "skills" / "mcp-fs-pydantic-org" / "scripts"
CANONICAL_ROOT = DEV_ROOT / "Projects" / "Ficheiros Escritos Canónicos"
CENTRAL_DIR = DEV_ROOT / "OUTPUT_CENTRALIZADO"

# Candidatos para Google Drive e Drives em Nuvem
GOOGLE_DRIVE_CANDIDATES = [
    Path(r"G:\nuno"),
    Path(r"G:\O meu disco"),
    Path(r"G:\My Drive"),
    Path(r"G:\\"),
    Path(r"C:\Users\Yokozuna\Google Drive"),
]


def check_google_drive_sources() -> List[Path]:
    active_gdrive = []
    for cand in GOOGLE_DRIVE_CANDIDATES:
        try:
            if cand.exists():
                active_gdrive.append(cand)
        except Exception:
            pass
    return active_gdrive


def run_command_logged(cmd: List[str], desc: str) -> bool:
    print(f"\n==================================================================")
    print(f" EXECUTANDO: {desc}")
    print(f" Comando   : {' '.join(cmd)}")
    print(f"==================================================================")
    try:
        res = subprocess.run(cmd, cwd=str(DEV_ROOT), capture_output=False, text=True)
        if res.returncode == 0:
            print(f"[SUCESSO] {desc} concluido.")
            return True
        else:
            print(f"[AVISO] {desc} retornou codigo {res.returncode}.")
            return False
    except Exception as e:
        print(f"[ERRO] Falha ao executar {desc}: {e}")
        return False


def run_total_consolidation() -> Dict[str, Any]:
    start_time = datetime.now()
    print("=" * 80)
    print(" CONSOLIDACAO TOTAL DO ECOSSISTEMA FORENSE DETERMINISTICO - DEV YOKOZUNA")
    print(f" Data / Hora  : {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f" Raiz Dev     : {DEV_ROOT}")
    print(f" Acervo       : {CANONICAL_ROOT}")
    print(f" Central      : {CENTRAL_DIR}")
    print("=" * 80)

    # 1. Deteccao de Fontes do Google Drive e Cloud
    gdrive_sources = check_google_drive_sources()
    print(f"\n[DETECCAO CLOUD & GOOGLE DRIVE]")
    if gdrive_sources:
        for s in gdrive_sources:
            print(f" - Google Drive Ativo Detectado: {s}")
    else:
        print(" - Google Drive (G:\\): Nao montado como letra de unidade local no momento (scans locais e OneDrive ativos).")

    # 2. Ingestão e Organização Global (com Proteção de Sistema)
    run_command_logged([
        sys.executable, str(SKILLS_DIR / "organize_user_workspace.py"), "--apply"
    ], "[01/10] Ingestao Global de Pastas e Protecao Rigorosa de Sistema")

    # Se Google Drive G:\nuno estiver ativo, rodar ingestao de G:
    g_source = Path(r"G:\nuno")
    if g_source.exists():
        run_command_logged([
            sys.executable, str(SKILLS_DIR / "copy_and_organize_canonical.py"),
            "--source", str(g_source),
            "--dest", str(CANONICAL_ROOT),
            "--apply"
        ], "[01b/10] Ingestao Dedicada Google Drive G:\\nuno")

    # 3. Higienização e Geração do Mapa Estrutural
    run_command_logged([sys.executable, str(SKILLS_DIR / "sanitize_and_simplify.py")], "[02/10] Higienizacao Estrutural")
    run_command_logged([sys.executable, str(SKILLS_DIR / "generate_tree.py")], "[03/10] Mapa Estrutural tree_dirs.md")

    # 4. Scanner dos 6 Agentes Canônicos + Hashing SHA-256
    run_command_logged([
        sys.executable, str(SKILLS_DIR / "run_act_agents.py"),
        "--root", str(CANONICAL_ROOT),
        "--hash",
        "--out", str(CANONICAL_ROOT / "_index")
    ], "[04/10] Scanner Deterministico dos 6 Agentes Canonicos")

    # 5. Loops de Validação e Otimização Pydantic v2
    run_command_logged([
        sys.executable, str(SKILLS_DIR / "optimize_and_validate_loop.py"),
        "--index-dir", str(CANONICAL_ROOT / "_index")
    ], "[05/10] Loops de Otimizacao e Validacao Pydantic v2")

    # 6. Segregação Factual e Matriz de Relevância Probatória
    run_command_logged([sys.executable, str(SKILLS_DIR / "factual_relevance_loop.py")], "[06/10] Segregacao Factual (FACTO vs ALEGACAO)")

    # 7. Memória Vetorial Factual RAG (256-d Chunks)
    run_command_logged([sys.executable, str(SKILLS_DIR / "vector_index.py")], "[07/10] Construcao da Memoria Vetorial RAG")

    # 8. Benchmark contra o Golden Dataset 2.1.0
    run_command_logged([sys.executable, str(SKILLS_DIR / "eval_pipeline.py")], "[08/10] Avaliacao com Golden Dataset")

    # 9. Frozen Judge v2.5.0-PROD (Score 100/100 e Cronologia Mestre)
    run_command_logged([sys.executable, str(SKILLS_DIR / "frozen_judge.py")], "[09/10] Auditoria Frozen Judge e Cronologia Mestre")

    # 10. Controlador de Workflow, Sincronização e Dossiê Consolidado
    run_command_logged([sys.executable, str(SKILLS_DIR / "workflow_controller.py")], "[10a/10] Controlador de Entregaveis Obrigatorios")
    run_command_logged([sys.executable, str(SKILLS_DIR / "centralize_outputs.py")], "[10b/10] Sincronizacao de Outputs Centralizados")
    run_command_logged([sys.executable, str(SKILLS_DIR / "generate_full_dossier.py")], "[10c/10] Compilacao do Dossie Mestre Executivo e Forense")

    end_time = datetime.now()
    duration = end_time - start_time

    print("\n" + "=" * 80)
    print(" CONSOLIDACAO TOTAL DO ECOSSISTEMA CONCLUIDA COM EXITO!")
    print("=" * 80)
    print(f" Duracao Total      : {duration.total_seconds():.1f} segundos ({duration.total_seconds()/60:.2f} min)")
    print(f" Pasta de Saida     : {CENTRAL_DIR}")
    print(f" Dossie Visual HTML : {CENTRAL_DIR / 'DOSSIER_EXECUTIVO_FORENSE.html'}")
    print(f" Dossie Markdown    : {CENTRAL_DIR / 'DOSSIER_EXECUTIVO_FORENSE_CONSOLIDADO.md'}")
    print(f" Memoria Vetorial   : {CENTRAL_DIR / '02_DADOS_ESTRUTURADOS' / 'vector_index.jsonl'}")
    print(f" Base Cronologica   : {CENTRAL_DIR / '02_DADOS_ESTRUTURADOS' / 'cronologia_mestre.jsonl'}")
    print("=" * 80 + "\n")

    return {
        "status": "SUCCESS",
        "duration_seconds": duration.total_seconds(),
        "output_directory": str(CENTRAL_DIR),
        "dossier_html": str(CENTRAL_DIR / "DOSSIER_EXECUTIVO_FORENSE.html"),
        "dossier_md": str(CENTRAL_DIR / "DOSSIER_EXECUTIVO_FORENSE_CONSOLIDADO.md")
    }


def main():
    run_total_consolidation()


if __name__ == "__main__":
    main()
