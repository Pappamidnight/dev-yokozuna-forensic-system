"""
MIGRAÇÃO EM 3 FASES - VisiLens/ACERVO
Fase 1: CRÍTICO (PROVAS, ACERVO, DOCUMENTOS)
Fase 2: WORKFLOW (CONSOLIDADO, AUDITORIA)
Fase 3: ANÁLISE (TUDO O RESTO)
"""
import asyncio
import hashlib
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import psutil

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

# Setup logging
log_dir = Path(r"C:\ACERVO\logs")
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"migracao_fases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class S3Config:
    """Carrega configuração de .env"""
    def __init__(self, env_path: str = r"C:\ACERVO\.env"):
        self.endpoint = os.getenv("S3_ENDPOINT", "http://localhost:9000")
        self.bucket = os.getenv("S3_BUCKET", "acervo")
        self.region = os.getenv("S3_REGION", "us-east-1")
        self.access_key = os.getenv("S3_ACCESS_KEY", "acervo")
        self.secret_key = os.getenv("S3_SECRET_KEY", "acervo_dev")
        self.db_path = Path(os.getenv("ACERVO_DB", r"C:\ACERVO\db\acervo.db"))
        
        if os.path.exists(env_path):
            self._load_env_file(env_path)
    
    def _load_env_file(self, path: str):
        """Load .env file"""
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key, value = key.strip(), value.strip()
                    if not os.getenv(key):
                        os.environ[key] = value


class MigrationPhase:
    """Gerencia uma fase de migração"""
    
    def __init__(self, phase_name: str, config: S3Config, dry_run: bool = False):
        self.phase_name = phase_name
        self.config = config
        self.dry_run = dry_run
        self.s3 = self._init_s3_client() if not dry_run else None
        self.db = self._init_db()
        self.stats = {
            "files_processed": 0,
            "files_uploaded": 0,
            "files_duplicated": 0,
            "files_errors": 0,
            "files_skipped": 0,
            "bytes_uploaded": 0,
            "bytes_duplicated": 0,
            "duration_seconds": 0,
        }
        self.start_time = None
    
    def _init_s3_client(self):
        """Inicializa cliente S3"""
        try:
            client = boto3.client(
                's3',
                endpoint_url=self.config.endpoint,
                region_name=self.config.region,
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
                config=Config(
                    retries={'max_attempts': 5, 'mode': 'standard'},
                    max_pool_connections=32,
                    connect_timeout=30,
                    read_timeout=60
                )
            )
            if not self.dry_run:
                client.head_bucket(Bucket=self.config.bucket)
            logger.info(f"✓ S3 conectado: {self.config.endpoint}")
            return client
        except Exception as e:
            logger.error(f"✗ Falha ao conectar S3: {e}")
            raise
    
    def _init_db(self):
        """Inicializa banco de dados SQLite"""
        self.config.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.config.db_path), timeout=60)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS s3_uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phase TEXT,
                hash_sha256 TEXT,
                s3_key TEXT,
                file_size INTEGER,
                source_path TEXT,
                upload_timestamp TIMESTAMP,
                validation_status TEXT
            )
        """)
        
        conn.commit()
        return conn
    
    def _calculate_hash(self, file_path: Path) -> str:
        """Calcula SHA-256"""
        hash_obj = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192 * 1024), b''):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    
    def _s3_key_from_hash(self, hash_sha256: str) -> str:
        """Gera S3 key"""
        return f"files/{hash_sha256[:2]}/{hash_sha256}"
    
    def _check_s3_exists(self, s3_key: str, expected_size: int) -> bool:
        """Verifica se já existe em S3"""
        if self.dry_run or not self.s3:
            return False
        
        try:
            response = self.s3.head_object(Bucket=self.config.bucket, Key=s3_key)
            return response.get('ContentLength', 0) == expected_size
        except ClientError:
            return False
    
    def _upload_to_s3(self, file_path: Path, s3_key: str) -> bool:
        """Upload para S3"""
        if self.dry_run:
            logger.info(f"[DRY-RUN] 📤 {file_path.name}")
            return True
        
        try:
            with open(file_path, 'rb') as f:
                self.s3.put_object(
                    Bucket=self.config.bucket,
                    Key=s3_key,
                    Body=f,
                    ContentType='application/octet-stream'
                )
            
            # Validar
            response = self.s3.head_object(Bucket=self.config.bucket, Key=s3_key)
            if response.get('ContentLength', 0) == file_path.stat().st_size:
                logger.info(f"✓ Upload OK: {file_path.name}")
                return True
            else:
                logger.error(f"✗ Validação falhou: {file_path.name}")
                return False
        except Exception as e:
            logger.error(f"✗ Erro upload: {file_path.name} - {e}")
            return False
    
    def process_file(self, file_path: Path) -> bool:
        """Processa um ficheiro"""
        try:
            if not file_path.exists():
                return False
            
            file_size = file_path.stat().st_size
            if file_size == 0:
                return False
            
            self.stats["files_processed"] += 1
            
            # Hash
            hash_sha256 = self._calculate_hash(file_path)
            s3_key = self._s3_key_from_hash(hash_sha256)
            
            # Check duplicate
            if self._check_s3_exists(s3_key, file_size):
                self.stats["files_duplicated"] += 1
                self.stats["bytes_duplicated"] += file_size
                self._record_db(hash_sha256, s3_key, file_size, str(file_path), "DUPLICATE")
                return True
            
            # Upload
            if self._upload_to_s3(file_path, s3_key):
                self.stats["files_uploaded"] += 1
                self.stats["bytes_uploaded"] += file_size
                self._record_db(hash_sha256, s3_key, file_size, str(file_path), "UPLOADED")
                return True
            else:
                self.stats["files_errors"] += 1
                return False
        
        except Exception as e:
            logger.error(f"✗ Erro: {file_path} - {e}")
            self.stats["files_errors"] += 1
            return False
    
    def _record_db(self, hash_sha256: str, s3_key: str, size: int, source: str, status: str):
        """Registra na DB"""
        try:
            self.db.execute(
                """INSERT INTO s3_uploads (phase, hash_sha256, s3_key, file_size, source_path, upload_timestamp, validation_status)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (self.phase_name, hash_sha256, s3_key, size, source, datetime.now().isoformat(), status)
            )
            self.db.commit()
        except Exception as e:
            logger.error(f"✗ DB error: {e}")
    
    def migrate_folder(self, folder_path: Path, workers: int = 4):
        """Migra uma pasta"""
        folder_path = Path(folder_path)
        
        if not folder_path.exists():
            logger.warning(f"⚠ Pasta não existe: {folder_path}")
            return
        
        logger.info(f"\n{'='*80}")
        logger.info(f"📂 {self.phase_name} | {folder_path.name}")
        logger.info(f"{'='*80}")
        
        self.start_time = time.time()
        
        # Listar ficheiros
        files = list(folder_path.rglob("*"))
        files = [f for f in files if f.is_file() and f.stat().st_size > 0]
        
        logger.info(f"📊 Ficheiros: {len(files)}")
        
        # Processar com workers
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(self.process_file, f): f for f in files}
            
            for i, future in enumerate(as_completed(futures), 1):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"✗ Worker error: {e}")
                
                if i % 100 == 0:
                    self._print_progress(i, len(files))
        
        self.stats["duration_seconds"] = time.time() - self.start_time
        self._print_summary()
    
    def _print_progress(self, current: int, total: int):
        """Imprime progresso"""
        pct = 100 * current / total
        logger.info(f"   {current}/{total} ({pct:.1f}%)")
    
    def _print_summary(self):
        """Imprime resumo"""
        logger.info(f"\n{'='*80}")
        logger.info(f"✅ {self.phase_name} - CONCLUÍDO")
        logger.info(f"{'='*80}")
        logger.info(f"✓ Uploads:      {self.stats['files_uploaded']}")
        logger.info(f"⊘ Duplicados:   {self.stats['files_duplicated']}")
        logger.info(f"❌ Erros:        {self.stats['files_errors']}")
        logger.info(f"📊 Total:       {self.stats['files_processed']}")
        logger.info(f"💾 Enviado:     {self.stats['bytes_uploaded'] / 1e9:.2f} GB")
        logger.info(f"⏱️ Tempo:        {self.stats['duration_seconds']:.1f}s")
        logger.info(f"{'='*80}\n")
    
    def cleanup(self):
        """Fecha conexões"""
        if self.db:
            self.db.close()


class MigrationOrchestrator:
    """Orquestra as 3 fases"""
    
    def __init__(self, config: S3Config, dry_run: bool = False):
        self.config = config
        self.dry_run = dry_run
        
        # Definir fases
        self.phases = {
            "FASE_1_CRITICO": {
                "description": "CRÍTICO: PROVAS, ACERVO, DOCUMENTOS",
                "folders": [
                    r"C:\Users\Yokozuna\Desktop\PROVAS_15547",
                    r"C:\Users\Yokozuna\Desktop\PROVAS_10153",
                    r"C:\Users\Yokozuna\Desktop\PROVAS_20203",
                    r"C:\Users\Yokozuna\Desktop\PROVAS_23142",
                    r"C:\Users\Yokozuna\Desktop\PROVAS_3719",
                    r"C:\Users\Yokozuna\Desktop\ACERVO_FINAL_ORGANIZADO",
                    r"C:\Users\Yokozuna\Desktop\ACERVO_FORENSE",
                    r"C:\Users\Yokozuna\Desktop\00_DOCUMENTOS_OFICIAIS_TRIBUNAL",
                    r"C:\Users\Yokozuna\Desktop\JURIDICO",
                    r"C:\Users\Yokozuna\LEGAL",
                    r"C:\Users\Yokozuna\ARCHIVE",
                ],
                "workers": 6,
            },
            "FASE_2_WORKFLOW": {
                "description": "WORKFLOW: CONSOLIDADO, AUDITORIA, PIPELINE",
                "folders": [
                    r"C:\Users\Yokozuna\Desktop\_CONSOLIDADO_FORENSE_20261008_150229",
                    r"C:\Users\Yokozuna\Desktop\_AUDITORIA_FORENSE_20261011_113004",
                    r"C:\Users\Yokozuna\Desktop\_AUDITORIA_DESKTOP_20261011_113854",
                    r"C:\Users\Yokozuna\Desktop\_CONSOLIDADO_PROJETOS",
                    r"C:\Users\Yokozuna\Desktop\_CONSOLIDADO_SEGURO",
                    r"C:\Users\Yokozuna\EVAL_PIPELINE",
                    r"C:\Users\Yokozuna\WORKFLOW",
                ],
                "workers": 4,
            },
            "FASE_3_ANALISE": {
                "description": "ANÁLISE: TUDO O RESTO (HERMES, SPARK, etc)",
                "folders": [
                    r"C:\Users\Yokozuna\Desktop\HERMES_CODIGO",
                    r"C:\Users\Yokozuna\Desktop\HERMES",
                    r"C:\Users\Yokozuna\Desktop\SPARK",
                    r"C:\Users\Yokozuna\Desktop\LEA",
                    r"C:\Users\Yokozuna\Desktop\PROJETO_15547",
                    r"C:\Users\Yokozuna\Desktop\audit-minmop",
                    r"C:\Users\Yokozuna\Desktop\dev-yokozuna-forensic-system",
                    r"C:\Users\Yokozuna\Desktop\_BACKUP_PROJETOS",
                    r"C:\Users\Yokozuna\Desktop\_BACKUP_SEGURO",
                    r"C:\Users\Yokozuna\Desktop\_ANALISE_SEGURA",
                ],
                "workers": 4,
            },
        }
    
    def run(self, phases_to_run: List[str] = None):
        """Executa migrações"""
        if phases_to_run is None:
            phases_to_run = ["FASE_1_CRITICO", "FASE_2_WORKFLOW", "FASE_3_ANALISE"]
        
        logger.info("\n" + "="*80)
        logger.info(f"🚀 MIGRAÇÃO EM {len(phases_to_run)} FASES")
        logger.info(f"   Dry-run: {self.dry_run}")
        logger.info("="*80 + "\n")
        
        total_stats = {
            "total_uploaded": 0,
            "total_duplicated": 0,
            "total_errors": 0,
            "total_processed": 0,
            "total_bytes": 0,
        }
        
        for phase_name in phases_to_run:
            if phase_name not in self.phases:
                logger.error(f"✗ Fase desconhecida: {phase_name}")
                continue
            
            phase_config = self.phases[phase_name]
            logger.info(f"\n🔄 {phase_config['description']}")
            
            phase = MigrationPhase(phase_name, self.config, dry_run=self.dry_run)
            
            for folder in phase_config["folders"]:
                folder_path = Path(folder)
                if folder_path.exists():
                    phase.migrate_folder(folder_path, workers=phase_config["workers"])
                else:
                    logger.warning(f"⚠ Pasta não encontrada: {folder}")
            
            # Accumulate stats
            total_stats["total_uploaded"] += phase.stats["files_uploaded"]
            total_stats["total_duplicated"] += phase.stats["files_duplicated"]
            total_stats["total_errors"] += phase.stats["files_errors"]
            total_stats["total_processed"] += phase.stats["files_processed"]
            total_stats["total_bytes"] += phase.stats["bytes_uploaded"]
            
            phase.cleanup()
        
        # Final summary
        self._print_final_summary(total_stats)
    
    def _print_final_summary(self, stats: Dict):
        """Imprime resumo final"""
        logger.info("\n" + "="*80)
        logger.info("📊 RESUMO GERAL - TODAS AS FASES")
        logger.info("="*80)
        logger.info(f"✓ Total Uploads:    {stats['total_uploaded']:,}")
        logger.info(f"⊘ Total Duplicados: {stats['total_duplicated']:,}")
        logger.info(f"❌ Total Erros:      {stats['total_errors']:,}")
        logger.info(f"📊 Total Ficheiros: {stats['total_processed']:,}")
        logger.info(f"💾 Total Enviado:   {stats['total_bytes'] / 1e9:.2f} GB")
        logger.info("="*80 + "\n")


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migração em 3 Fases")
    parser.add_argument("--dry-run", action="store_true", help="Só simula")
    parser.add_argument("--fase", choices=["1", "2", "3", "todas"], default="todas", help="Qual fase?")
    
    args = parser.parse_args()
    
    # Config
    config = S3Config()
    
    # Orquestrador
    orchestrator = MigrationOrchestrator(config, dry_run=args.dry_run)
    
    # Executar
    if args.fase == "1":
        orchestrator.run(["FASE_1_CRITICO"])
    elif args.fase == "2":
        orchestrator.run(["FASE_2_WORKFLOW"])
    elif args.fase == "3":
        orchestrator.run(["FASE_3_ANALISE"])
    else:
        orchestrator.run()
    
    logger.info("✅ Migração concluída!")


if __name__ == "__main__":
    main()
