#!/usr/bin/env python3
"""
Watchdog Indexer em Tempo Real para o Ecossistema Dev.
Monitoriza C:\\Users\\Yokozuna\\Dev (em especial as 6 pastas canonicas e Projects).
Sempre que um ficheiro e adicionado ou modificado:
1. Calcula o hash SHA-256;
2. Extrai processo ID e tipo de ato;
3. Atualiza _index/atos_processuais.jsonl;
4. Atualiza _index/pipeline_report.json;
5. Atualiza o mapa estrutural tree_dirs.md.
"""
import os
import sys
import time
import json
import hashlib
import re
import argparse
from datetime import datetime
from typing import Dict, Set, Tuple, Optional, List

DEV_ROOT = "C:\\Users\\Yokozuna\\Dev"
CANONICAL_ROOT = os.path.join(DEV_ROOT, "Projects", "Ficheiros Escritos Canónicos")
INDEX_DIR = os.path.join(CANONICAL_ROOT, "_index")
LOG_FILE = os.path.join(INDEX_DIR, "watchdog.log")

PROCESS_PATTERN = re.compile(r'(\d{1,5})[/-](\d{2})[\.-](\d)[A-Z0-9]{3,7}', re.IGNORECASE)

IGNORE_DIRS = {
    ".venv", ".git", ".github", "__pycache__", "node_modules",
    ".pytest_cache", ".ruff_cache", "site-packages", "_index"
}

CANONICAL_WEIGHTS = {
    "00_Indice_E_MOCs": {"agent": "agente-indice-mocs", "weight": 0.70, "level": "INDICE"},
    "01_PDFs_Oficiais": {"agent": "agente-pdfs-oficiais", "weight": 1.00, "level": "OFICIAL"},
    "02_Minutas_E_Rascunhos": {"agent": "agente-minutas", "weight": 0.25, "level": "BAIXA"},
    "03_Contratos_E_Acordos": {"agent": "agente-contratos", "weight": 0.95, "level": "ALTA"},
    "04_Processos_E_Pecas_Escritas": {"agent": "agente-pecas", "weight": 0.98, "level": "OFICIAL"},
    "05_Correspondencia_E_Comunicacoes": {"agent": "agente-correspondencia", "weight": 0.85, "level": "MEDIA"},
}


def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] [WATCHDOG] {msg}"
    print(formatted)
    try:
        os.makedirs(INDEX_DIR, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass


def calculate_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        return f"ERROR_{str(e)}"


def extract_process_id(text: str) -> Optional[str]:
    match = PROCESS_PATTERN.search(text)
    if match:
        p1, p2, p3 = match.group(1), match.group(2), match.group(3)
        return f"{p1}/{p2}.{p3.upper()}"
    return None


def detect_act_type(filename: str, folder: str) -> str:
    if folder == "02_Minutas_E_Rascunhos":
        return "RASCUNHO"
    if folder == "00_Indice_E_MOCs":
        return "INDICE_CATALOGO"
    fn_upper = filename.upper()
    if "DESPACHO" in fn_upper:
        return "DESPACHO"
    if "CITACAO" in fn_upper or "NOTIFICACAO" in fn_upper:
        return "CITACAO"
    if "CONTESTACAO" in fn_upper or "OPOSICAO" in fn_upper:
        return "CONTESTACAO"
    if "SENTENCA" in fn_upper or "DECISAO" in fn_upper:
        return "SENTENCA"
    if "ACORDAO" in fn_upper:
        return "ACORDAO"
    if "RECURSO" in fn_upper:
        return "RECURSO"
    if "CONTRATO" in fn_upper or "ACORDO" in fn_upper:
        return "CONTRATO"
    if "PENHORA" in fn_upper:
        return "AUTO_PENHORA"
    if "ATA" in fn_upper:
        return "ATA_AUDIENCIA"
    if folder == "01_PDFs_Oficiais":
        return "ATO_OFICIAL_PDF"
    return "DOCUMENTO_DIVERSO"


def index_single_file(filepath: str) -> Optional[Dict]:
    if not os.path.exists(filepath):
        return None
    try:
        filename = os.path.basename(filepath)
        rel_path = os.path.relpath(filepath, CANONICAL_ROOT) if CANONICAL_ROOT in filepath else os.path.relpath(filepath, DEV_ROOT)
        parts = rel_path.split(os.sep)
        folder = parts[0] if parts else "00_Indice_E_MOCs"
        
        file_hash = calculate_sha256(filepath)
        proc_id = extract_process_id(filename) or extract_process_id(rel_path)
        act_type = detect_act_type(filename, folder)
        
        support = "DOCUMENTADO"
        if folder == "02_Minutas_E_Rascunhos":
            support = "INDICIADO"
            
        record = {
            "file_path": filepath,
            "rel_path": rel_path,
            "filename": filename,
            "folder": folder,
            "process_id": proc_id,
            "tipo_cpc": act_type,
            "sha256": file_hash,
            "suporte": support,
            "weight": CANONICAL_WEIGHTS.get(folder, {}).get("weight", 0.50),
            "evidence_level": CANONICAL_WEIGHTS.get(folder, {}).get("level", "BAIXA"),
            "indexed_at": datetime.now().isoformat()
        }
        return record
    except Exception as e:
        log(f"Erro ao indexar {filepath}: {e}")
        return None


def update_tree_document():
    """Regenera tree_dirs.md de forma automatica."""
    try:
        script_dir = os.path.dirname(__file__)
        gen_tree_script = os.path.join(script_dir, "generate_tree.py")
        if os.path.exists(gen_tree_script):
            import subprocess
            subprocess.run([sys.executable, gen_tree_script], capture_output=True, check=False)
            log("Mapa estrutural tree_dirs.md atualizado.")
    except Exception as e:
        log(f"Erro ao atualizar tree_dirs.md: {e}")


class DevSnapshotWatcher:
    """Monitor de snapshot eficiente para o diretorio Dev."""
    def __init__(self, watch_roots: list):
        self.watch_roots = watch_roots
        self.snapshot: Dict[str, float] = {}
        self.known_hashes: Set[str] = set()
        self.load_initial_state()

    def get_file_state(self) -> Dict[str, float]:
        state = {}
        for root in self.watch_roots:
            if not os.path.exists(root):
                continue
            for cur_root, dirs, files in os.walk(root):
                dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
                for f in files:
                    full_p = os.path.join(cur_root, f)
                    try:
                        mtime = os.path.getmtime(full_p)
                        state[full_p] = mtime
                    except OSError:
                        pass
        return state

    def load_initial_state(self):
        log("A carregar estado inicial do acervo...")
        self.snapshot = self.get_file_state()
        # Carregar hashes conhecidos de atos_processuais.jsonl se existir
        atos_path = os.path.join(INDEX_DIR, "atos_processuais.jsonl")
        if os.path.exists(atos_path):
            with open(atos_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        if "sha256" in data:
                            self.known_hashes.add(data["sha256"])
                    except Exception:
                        pass
        log(f"Estado inicial carregado: {len(self.snapshot)} ficheiros monitorizados, {len(self.known_hashes)} hashes indexados.")

    def check_for_changes(self) -> Tuple[List[str], List[str], List[str]]:
        current_state = self.get_file_state()
        created = []
        modified = []
        deleted = []

        for path, mtime in current_state.items():
            if path not in self.snapshot:
                created.append(path)
            elif mtime > self.snapshot[path]:
                modified.append(path)

        for path in self.snapshot:
            if path not in current_state:
                deleted.append(path)

        self.snapshot = current_state
        return created, modified, deleted

    def process_changes(self, created: List[str], modified: List[str], deleted: List[str]):
        changed_files = created + modified
        if not changed_files and not deleted:
            return

        log(f"Detetadas alteracoes: {len(created)} novos, {len(modified)} modificados, {len(deleted)} removidos.")
        
        new_records = []
        for path in changed_files:
            record = index_single_file(path)
            if record:
                new_records.append(record)
                log(f"[NOVO/ATUALIZADO] {record['filename']} -> Processo: {record['process_id']} | Tipo: {record['tipo_cpc']} | SHA: {record['sha256'][:10]}...")

        # Gravar incrementalmente em atos_processuais.jsonl
        if new_records:
            atos_path = os.path.join(INDEX_DIR, "atos_processuais.jsonl")
            with open(atos_path, "a", encoding="utf-8") as f:
                for rec in new_records:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            log(f"{len(new_records)} registos persistidos em _index/atos_processuais.jsonl.")

        # Atualizar tree_dirs.md
        update_tree_document()


def run_watchdog(poll_interval: int = 3, once: bool = False):
    roots_to_watch = [
        CANONICAL_ROOT,
        os.path.join(DEV_ROOT, "Projects"),
        os.path.join(DEV_ROOT, "AI")
    ]
    
    watcher = DevSnapshotWatcher(roots_to_watch)
    log(f"Watchdog ativo em C:\\Users\\Yokozuna\\Dev. Intervalo de polling: {poll_interval}s.")
    
    if once:
        created, modified, deleted = watcher.check_for_changes()
        watcher.process_changes(created, modified, deleted)
        log("Execucao unica conclutida.")
        return

    try:
        while True:
            time.sleep(poll_interval)
            created, modified, deleted = watcher.check_for_changes()
            if created or modified or deleted:
                watcher.process_changes(created, modified, deleted)
    except KeyboardInterrupt:
        log("Watchdog interrompido pelo utilizador.")


def main():
    parser = argparse.ArgumentParser(description="Watchdog Auto-Indexer em Tempo Real")
    parser.add_argument("--poll", type=int, default=3, help="Intervalo de polling em segundos")
    parser.add_argument("--once", action="store_true", help="Executar apenas uma checagem e sair")
    
    args = parser.parse_args()
    run_watchdog(poll_interval=args.poll, once=args.once)


if __name__ == "__main__":
    main()
