#!/usr/bin/env python3
"""
Servico de Sistema Automatico Continuo: Watchdog + Auto-Otimizacao + Atualizacao.
Combina em um unico processo:
1. Monitorizacao em tempo real de novos ficheiros e alteracoes (Watchdog).
2. Indexacao imediata com hash SHA-256 e qualificacao de atos processuais.
3. Execucao periodica ou disparada do Loop de Otimizacao e Validacao (Loops A-D).
4. Regeneracao automatica do mapa estrutural tree_dirs.md.
"""
import os
import sys
import time
import json
import argparse
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEV_ROOT = "C:\\Users\\Yokozuna\\Dev"
CANONICAL_ROOT = os.path.join(DEV_ROOT, "Projects", "Ficheiros Escritos Canónicos")
INDEX_DIR = os.path.join(CANONICAL_ROOT, "_index")
LOG_FILE = os.path.join(INDEX_DIR, "auto_system.log")

# Importar modulos locais
try:
    from watchdog_indexer import DevSnapshotWatcher, index_single_file, update_tree_document
    from optimize_and_validate_loop import run_optimization_loop
    from factual_relevance_loop import run_factual_relevance_loop
    from error_remediation_handler import auto_remediate_atos_index, log_error
except ImportError:
    sys.path.insert(0, SCRIPT_DIR)
    from watchdog_indexer import DevSnapshotWatcher, index_single_file, update_tree_document
    from optimize_and_validate_loop import run_optimization_loop
    from factual_relevance_loop import run_factual_relevance_loop
    from error_remediation_handler import auto_remediate_atos_index, log_error


def sys_log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [AUTO_SYSTEM] {msg}"
    print(line)
    try:
        os.makedirs(INDEX_DIR, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def run_auto_system(poll_interval: int = 3, optimize_interval: int = 60):
    """Executa o ciclo continuo de monitorizacao, indexacao e otimizacao."""
    sys_log("==================================================================")
    sys_log("INICIANDO SISTEMA AUTOMATICO DE INDEXACAO, OTIMIZACAO E WATCHDOG")
    sys_log(f"Raiz Dev: {DEV_ROOT}")
    sys_log(f"Polling Interval: {poll_interval}s | Otimizacao Interval: {optimize_interval}s")
    sys_log("==================================================================")

    roots_to_watch = [
        CANONICAL_ROOT,
        os.path.join(DEV_ROOT, "Projects"),
        os.path.join(DEV_ROOT, "AI"),
        os.path.join(DEV_ROOT, "Backend"),
        os.path.join(DEV_ROOT, "Labs"),
        os.path.join(DEV_ROOT, "Sandbox")
    ]

    watcher = DevSnapshotWatcher(roots_to_watch)
    last_optimize_time = time.time()

    # Execucao inicial de otimizacao e arvore
    sys_log("A executar otimizacao inicial, auto-remediacao de erros e motor factual...")
    try:
        auto_remediate_atos_index()
        run_optimization_loop(INDEX_DIR)
        run_factual_relevance_loop(INDEX_DIR)
        update_tree_document()
    except Exception as e:
        sys_log(f"Aviso na otimizacao inicial: {e}")

    sys_log("Sistema automatico ativo e em execucao continua. Aguardando eventos...")

    try:
        while True:
            time.sleep(poll_interval)
            
            # 1. Checagem de alteracoes em ficheiros
            try:
                created, modified, deleted = watcher.check_for_changes()
                if created or modified or deleted:
                    sys_log(f"Detetada atividade no sistema de ficheiros!")
                    watcher.process_changes(created, modified, deleted)
                    
                    # Disparar otimizacao e extracao factual imediata apos mudanca
                    sys_log("A disparar loop de validacao, otimizacao e fatos imediato...")
                    run_optimization_loop(INDEX_DIR)
                    run_factual_relevance_loop(INDEX_DIR)
                    last_optimize_time = time.time()
            except Exception as fe:
                sys_log(f"Erro ao processar mudancas no watcher: {fe}")

            # 2. Execucao periodica de otimizacao e auto-remediacao
            if time.time() - last_optimize_time >= optimize_interval:
                try:
                    sys_log("A executar ciclo periodico de auto-remediacao, fatos e validacao...")
                    auto_remediate_atos_index()
                    run_optimization_loop(INDEX_DIR)
                    run_factual_relevance_loop(INDEX_DIR)
                    update_tree_document()
                    last_optimize_time = time.time()
                except Exception as oe:
                    sys_log(f"Erro no ciclo de otimizacao: {oe}")

    except KeyboardInterrupt:
        sys_log("Sistema automatico encerrado pelo utilizador.")


def main():
    parser = argparse.ArgumentParser(description="Sistema Automatico de Indexacao e Otimizacao")
    parser.add_argument("--poll", type=int, default=3, help="Intervalo do watcher em segundos")
    parser.add_argument("--optimize-interval", type=int, default=60, help="Intervalo de re-otimizacao em segundos")
    args = parser.parse_args()

    run_auto_system(poll_interval=args.poll, optimize_interval=args.optimize_interval)


if __name__ == "__main__":
    main()
