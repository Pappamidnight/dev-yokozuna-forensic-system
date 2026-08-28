#!/usr/bin/env python3
"""
Sessao de Ingestao, Reuniao de Informacao e Consolidacao de 15 Minutos (session_15min_gatherer.py).
Executa uma sessao intensiva de 15 minutos de monitorizacao, indexacao, extracao factual,
ordenacao cronologica e avaliacao continua de conformidade com o Frozen Judge.
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
SESSION_LOG = os.path.join(INDEX_DIR, "session_15min.log")

# Modulos locais
sys.path.insert(0, SCRIPT_DIR)
from run_act_agents import scan_canonical_folders, build_chains, save_index_outputs
from optimize_and_validate_loop import run_optimization_loop
from factual_relevance_loop import run_factual_relevance_loop
from frozen_judge import run_frozen_judge
from agent_quality_factuality import run_quality_and_factuality_check
from workflow_controller import verify_workflow_outputs
from watchdog_indexer import DevSnapshotWatcher, update_tree_document


def log_session(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [SESSAO_15MIN] {msg}"
    print(line)
    try:
        os.makedirs(INDEX_DIR, exist_ok=True)
        with open(SESSION_LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def run_15min_session(duration_minutes: int = 15, cycle_interval: int = 45):
    total_seconds = duration_minutes * 60
    start_time = time.time()
    end_time = start_time + total_seconds

    log_session("==================================================================")
    log_session(f"INICIANDO SESSAO DE REUNIAO DE INFORMACAO DE {duration_minutes} MINUTOS")
    log_session(f"Hora de Inicio : {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")
    log_session(f"Hora de Termino: {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')}")
    log_session("==================================================================")

    roots_to_watch = [
        CANONICAL_ROOT,
        os.path.join(DEV_ROOT, "Projects"),
        os.path.join(DEV_ROOT, "AI"),
        os.path.join(DEV_ROOT, "Backend"),
        os.path.join(DEV_ROOT, "Sandbox")
    ]
    watcher = DevSnapshotWatcher(roots_to_watch)

    pass_number = 1

    try:
        while time.time() < end_time:
            remaining = int(end_time - time.time())
            mins = remaining // 60
            secs = remaining % 60
            log_session(f"\n--- [PASSO {pass_number}] TEMPO RESTANTE: {mins:02d}m:{secs:02d}s ---")

            # 1. Checar se novos ficheiros foram adicionados
            created, modified, deleted = watcher.check_for_changes()
            if created or modified or deleted:
                log_session(f"Detetadas alteracoes no acervo! (+{len(created)} criados, ~{len(modified)} modificados)")
                watcher.process_changes(created, modified, deleted)

            # 2. Executar Loop de Otimizacao e Validacao
            log_session("Executando Loop de Otimizacao e Deduplicacao (Loops A-D)...")
            run_optimization_loop(INDEX_DIR)

            # 3. Executar Loop Factual e Matriz de Relevancia
            log_session("Executando Loop Factual e Calculo de Relevancia...")
            run_factual_relevance_loop(INDEX_DIR)

            # 4. Executar Frozen Judge (Cronologia e Contrato Congelado)
            log_session("Executando Frozen Judge (Ordenacao Cronologica Mestre)...")
            run_frozen_judge(INDEX_DIR)

            # 5. Executar Agente de Qualidade e Factualidade
            log_session("Executando Agente de Qualidade e Factualidade...")
            run_quality_and_factuality_check(sample_size=300)

            # 6. Atualizar arvore de diretorios
            update_tree_document()

            pass_number += 1

            # Pausa ate o proximo ciclo ou fim da sessao
            sleep_time = min(cycle_interval, max(1, int(end_time - time.time())))
            if sleep_time > 0 and time.time() < end_time:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        log_session("[AVISO] Sessao interrompida antecipadamente pelo utilizador.")

    # Consolidacao Final e Verificacao de Resultados
    log_session("\n==================================================================")
    log_session("CONSOLIDACAO FINAL DA SESSAO DE 15 MINUTOS")
    log_session("==================================================================")
    
    # Executar Controlador de Workflow Final
    status = verify_workflow_outputs()
    
    log_session(f"Status Final do Workflow: {status.get('status')}")
    log_session(f"Frozen Judge Score: {status.get('frozen_judge_score')}/100")
    log_session(f"Eval Pipeline: {status.get('eval_pipeline_status')}")
    log_session("SESSAO DE 15 MINUTOS CONCLUIDA COM SUCESSO ABSOLUTO.")


def main():
    parser = argparse.ArgumentParser(description="Sessao de 15 Minutos de Reuniao de Informacao")
    parser.add_argument("--minutes", type=int, default=15, help="Duracao em minutos (padrao: 15)")
    parser.add_argument("--interval", type=int, default=45, help="Intervalo entre ciclos em segundos")
    args = parser.parse_args()

    run_15min_session(duration_minutes=args.minutes, cycle_interval=args.interval)


if __name__ == "__main__":
    main()
