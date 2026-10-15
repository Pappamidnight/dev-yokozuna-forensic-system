"""
S3 Upload Module para VisiLens/ACERVO - v2
Deduplicação + Upload + Validação + Integridade
COM PROTEÇÃO CONTRA PASTAS DO SISTEMA
"""
import asyncio
import hashlib
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
import logging
import sys

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

# Setup logging
log_dir = Path(os.environ.get("ACERVO_LOG_DIR", r"C:\ACERVO\logs"))
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"s3_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
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
        
        # Load from .env if not in environment
        if os.path.exists(env_path):
            self._load_env_file(env_path)
        
        # Valida configuração
        self._validate_config()
    
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
                        # Update self
                        if key == "S3_ENDPOINT":
                            self.endpoint = value
                        elif key == "S3_BUCKET":
                            self.bucket = value
                        elif key == "S3_REGION":
                            self.region = value
                        elif key == "S3_ACCESS_KEY":
                            self.access_key = value
                        elif key == "S3_SECRET_KEY":
                            self.secret_key = value
    
    def _validate_config(self):
        """Valida configuração"""
        if not self.endpoint:
            raise ValueError("S3_ENDPOINT não configurado")
        if not self.bucket:
            raise ValueError("S3_BUCKET não configurado")
        logger.info(f"✓ Config S3: endpoint={self.endpoint}, bucket={self.bucket}")


class PathValidator:
    """Valida se um caminho deve ser processado"""
    
    # Pastas que NUNCA devem ser processadas
    SYSTEM_PATHS = {
        "Windows", "Program Files", "Program Files (x86)", "System32", "SysWOW64",
        "ProgramData", "$Recycle.Bin", "System Volume Information", ".git", "node_modules",
        "target", "__pycache__", ".venv", "venv", ".env", "AppData", "Users",
        "Documents and Settings", "All Users", "$RECYCLE.BIN",
    }
    
    FORBIDDEN_PREFIXES = {
        r"C:\Windows",
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        r"C:\ProgramData",
        r"C:\$Recycle.Bin",
        r"C:\System Volume Information",
        r"C:\Recovery",
        r"C:\$SysReset",
        r"C:\ProgramData",
    }
    
    # Extensões perigosas (system files)
    DANGEROUS_EXTENSIONS = {
        ".sys", ".dll", ".exe", ".scr", ".drv", ".bin", ".msi", ".cab"
    }
    
    @classmethod
    def is_valid_path(cls, path: Path) -> bool:
        """Verifica se um caminho é seguro para processar"""
        try:
            path_str = str(path).upper()
            
            # Check forbidden prefixes
            for forbidden in cls.FORBIDDEN_PREFIXES:
                if path_str.startswith(forbidden.upper()):
                    logger.warning(f"⚠ Caminho do sistema bloqueado: {path}")
                    return False
            
            # Check forbidden folder names
            for part in path.parts:
                if part in cls.SYSTEM_PATHS:
                    logger.warning(f"⚠ Pasta do sistema detectada: {part} em {path}")
                    return False
            
            # Check hidden system files
            if path.name.startswith("~"):
                logger.warning(f"⚠ Ficheiro temporário: {path}")
                return False
            
            # Check dangerous extensions (warn but don't block)
            if path.suffix.lower() in cls.DANGEROUS_EXTENSIONS:
                logger.warning(f"⚠ Extensão potencialmente perigosa: {path}")
                # Pode ser processado, mas com cuidado
            
            return True
        except Exception as e:
            logger.error(f"✗ Erro ao validar caminho {path}: {e}")
            return False
    
    @classmethod
    def should_skip_directory(cls, directory: Path) -> bool:
        """Verifica se um diretório deve ser pulado completamente"""
        try:
            dir_str = str(directory).upper()
            dir_name = directory.name.upper()
            
            # Skip system directories
            if dir_name in cls.SYSTEM_PATHS:
                return True
            
            # Skip by absolute prefix
            for forbidden in cls.FORBIDDEN_PREFIXES:
                if dir_str.startswith(forbidden.upper()):
                    return True
            
            return False
        except Exception:
            return True


class S3Deduplicator:
    """Deduplicação por SHA-256 com verificação de integridade"""
    
    def __init__(self, config: S3Config, dry_run: bool = False):
        self.config = config
        self.dry_run = dry_run
        self.validator = PathValidator()
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
            "bytes_skipped": 0,
        }
        
        if dry_run:
            logger.info("🔍 MODO DRY-RUN ATIVADO - Nenhum ficheiro será modificado")
    
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
            # Test connection
            client.head_bucket(Bucket=self.config.bucket)
            logger.info(f"✓ S3 conectado: {self.config.endpoint}")
            return client
        except ClientError as e:
            logger.error(f"✗ Falha ao conectar S3: {e}")
            # Create bucket if not exists
            try:
                client.create_bucket(Bucket=self.config.bucket)
                logger.info(f"✓ Bucket criado: {self.config.bucket}")
                return client
            except Exception as create_err:
                logger.error(f"✗ Falha ao criar bucket: {create_err}")
                raise
    
    def _init_db(self):
        """Inicializa banco de dados SQLite"""
        self.config.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.config.db_path), timeout=60)
        
        # Create tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS s3_uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash_sha256 TEXT UNIQUE NOT NULL,
                hash_blake3 TEXT,
                s3_key TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                source_paths TEXT,
                etag TEXT,
                upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                validation_status TEXT,
                validation_timestamp TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS s3_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                source_path TEXT,
                hash_sha256 TEXT,
                result TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        """)
        
        conn.commit()
        logger.info(f"✓ Base de dados inicializada: {self.config.db_path}")
        return conn
    
    def _calculate_hashes(self, file_path: Path) -> Tuple[str, str]:
        """Calcula SHA-256 e Blake3 de um ficheiro"""
        sha256_hash = hashlib.sha256()
        blake3_hash = hashlib.blake2b(digest_size=32)
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192 * 1024), b''):
                    sha256_hash.update(chunk)
                    blake3_hash.update(chunk)
            
            return sha256_hash.hexdigest(), blake3_hash.hexdigest()
        except IOError as e:
            logger.error(f"✗ Erro ao ler ficheiro {file_path}: {e}")
            self.stats["files_errors"] += 1
            raise
    
    def _s3_key_from_hash(self, hash_sha256: str) -> str:
        """Gera S3 key a partir do hash"""
        return f"files/{hash_sha256[:2]}/{hash_sha256}"
    
    def _check_s3_exists(self, s3_key: str, expected_size: int) -> bool:
        """Verifica se ficheiro já existe em S3 com tamanho correto"""
        if self.dry_run or not self.s3:
            return False
        
        try:
            response = self.s3.head_object(Bucket=self.config.bucket, Key=s3_key)
            actual_size = response.get('ContentLength', 0)
            
            if actual_size == expected_size:
                logger.info(f"✓ Duplicado encontrado: {s3_key}")
                return True
            else:
                logger.warning(f"⚠ Tamanho mismatch: {s3_key} (esperado {expected_size}, encontrado {actual_size})")
                return False
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            logger.error(f"✗ Erro ao verificar S3: {e}")
            raise
    
    def _upload_to_s3(self, file_path: Path, s3_key: str) -> Dict:
        """Upload para S3 com validação"""
        if self.dry_run:
            logger.info(f"[DRY-RUN] 📤 Seria enviado: {file_path.name}")
            return {'success': True, 's3_key': s3_key, 'etag': 'DRY_RUN', 'validation': True}
        
        try:
            file_size = file_path.stat().st_size
            
            logger.info(f"📤 Enviando: {file_path.name} ({file_size / 1024 / 1024:.2f} MB)")
            
            # Upload
            with open(file_path, 'rb') as f:
                response = self.s3.put_object(
                    Bucket=self.config.bucket,
                    Key=s3_key,
                    Body=f,
                    ContentType='application/octet-stream',
                    Metadata={
                        'source': str(file_path),
                        'upload-date': datetime.now().isoformat()
                    }
                )
            
            etag = response.get('ETag', '').strip('"')
            
            # Validate
            validation = self._validate_s3_upload(s3_key, file_size)
            
            logger.info(f"✓ Upload bem-sucedido: {s3_key} (ETag: {etag})")
            
            return {
                'success': True,
                's3_key': s3_key,
                'etag': etag,
                'validation': validation
            }
        
        except Exception as e:
            logger.error(f"✗ Erro ao enviar {file_path}: {e}")
            self.stats["files_errors"] += 1
            return {'success': False, 'error': str(e)}
    
    def _validate_s3_upload(self, s3_key: str, expected_size: int) -> bool:
        """Valida integridade do upload"""
        if self.dry_run or not self.s3:
            return True
        
        try:
            response = self.s3.head_object(Bucket=self.config.bucket, Key=s3_key)
            actual_size = response.get('ContentLength', 0)
            
            if actual_size == expected_size:
                logger.info(f"✓ Validação OK: {s3_key}")
                return True
            else:
                logger.error(f"✗ Validação FALHOU: tamanho mismatch")
                return False
        except Exception as e:
            logger.error(f"✗ Erro na validação: {e}")
            return False
    
    def _record_in_db(self, 
                     hash_sha256: str, 
                     hash_blake3: str,
                     s3_key: str,
                     file_size: int,
                     source_path: str,
                     etag: str,
                     validation_status: str):
        """Grava informações no banco de dados"""
        try:
            # Check if hash exists
            cursor = self.db.execute(
                "SELECT source_paths FROM s3_uploads WHERE hash_sha256 = ?",
                (hash_sha256,)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record with new source path
                existing_paths = json.loads(existing[0]) if existing[0] else []
                if source_path not in existing_paths:
                    existing_paths.append(source_path)
                    self.db.execute(
                        "UPDATE s3_uploads SET source_paths = ? WHERE hash_sha256 = ?",
                        (json.dumps(existing_paths), hash_sha256)
                    )
            else:
                # Insert new record
                self.db.execute(
                    """INSERT INTO s3_uploads 
                       (hash_sha256, hash_blake3, s3_key, file_size, source_paths, etag, validation_status, validation_timestamp)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (hash_sha256, hash_blake3, s3_key, file_size, 
                     json.dumps([source_path]), etag, validation_status, datetime.now().isoformat())
                )
            
            # Audit log
            self.db.execute(
                """INSERT INTO s3_audit (action, source_path, hash_sha256, result, details)
                   VALUES (?, ?, ?, ?, ?)""",
                ("UPLOAD" if not existing else "DEDUPLICATE", source_path, hash_sha256, 
                 "SUCCESS", f"S3: {s3_key}")
            )
            
            self.db.commit()
        except Exception as e:
            logger.error(f"✗ Erro ao gravar DB: {e}")
            self.db.rollback()
    
    def process_file(self, file_path: Path) -> bool:
        """Processa um ficheiro: hash → dedup → upload → DB"""
        try:
            file_path = Path(file_path)
            
            # Validação de segurança
            if not self.validator.is_valid_path(file_path):
                logger.warning(f"⚠ Ficheiro bloqueado (segurança): {file_path}")
                self.stats["files_skipped"] += 1
                self.stats["bytes_skipped"] += file_path.stat().st_size if file_path.exists() else 0
                return False
            
            if not file_path.exists():
                logger.error(f"✗ Ficheiro não existe: {file_path}")
                self.stats["files_errors"] += 1
                return False
            
            file_size = file_path.stat().st_size
            
            if file_size == 0:
                logger.warning(f"⚠ Ficheiro vazio: {file_path}")
                self.stats["files_skipped"] += 1
                return False
            
            self.stats["files_processed"] += 1
            
            # Calculate hashes
            logger.info(f"🔐 Hash: {file_path.name}")
            hash_sha256, hash_blake3 = self._calculate_hashes(file_path)
            
            # Generate S3 key
            s3_key = self._s3_key_from_hash(hash_sha256)
            
            # Check if duplicate
            if self._check_s3_exists(s3_key, file_size):
                self.stats["files_duplicated"] += 1
                self.stats["bytes_duplicated"] += file_size
                self._record_in_db(hash_sha256, hash_blake3, s3_key, file_size, 
                                  str(file_path), "", "DUPLICATE")
                return True
            
            # Upload to S3
            result = self._upload_to_s3(file_path, s3_key)
            
            if result['success']:
                self.stats["files_uploaded"] += 1
                self.stats["bytes_uploaded"] += file_size
                self._record_in_db(hash_sha256, hash_blake3, s3_key, file_size,
                                  str(file_path), result['etag'], 
                                  "VALIDATED" if result['validation'] else "VALIDATION_FAILED")
                return True
            else:
                self.stats["files_errors"] += 1
                return False
        
        except Exception as e:
            logger.error(f"✗ Erro ao processar {file_path}: {e}")
            self.stats["files_errors"] += 1
            return False
    
    def process_directory(self, directory: Path, pattern: str = "*", workers: int = 4):
        """Processa diretório completo com workers paralelos"""
        directory = Path(directory)
        
        if not directory.exists():
            logger.error(f"✗ Diretório não existe: {directory}")
            return
        
        # Valida se diretório é seguro
        if self.validator.should_skip_directory(directory):
            logger.error(f"✗ Diretório do sistema bloqueado: {directory}")
            return
        
        logger.info(f"📁 Processando: {directory}")
        logger.info(f"👷 Workers: {workers}")
        
        # Listar ficheiros
        files = []
        for p in directory.rglob(pattern):
            if p.is_file() and self.validator.is_valid_path(p):
                files.append(p)
        
        logger.info(f"📊 Total de ficheiros a processar: {len(files)}")
        
        # Processar com ThreadPoolExecutor
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(self.process_file, f): f for f in files}
            
            for i, future in enumerate(as_completed(futures), 1):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"✗ Erro em worker: {e}")
                
                if i % 50 == 0:
                    self._print_progress(i, len(files))
        
        self._print_summary()
    
    def _print_progress(self, current: int, total: int):
        """Imprime progresso"""
        pct = 100 * current / total
        logger.info(f"📈 Progresso: {current}/{total} ({pct:.1f}%)")
    
    def _print_summary(self):
        """Imprime resumo final"""
        logger.info("\n" + "=" * 70)
        logger.info("📊 RESUMO DA MIGRAÇÃO")
        logger.info("=" * 70)
        logger.info(f"✓ Uploads:      {self.stats['files_uploaded']}")
        logger.info(f"⊘ Duplicados:   {self.stats['files_duplicated']}")
        logger.info(f"⊘ Pulados:      {self.stats['files_skipped']}")
        logger.info(f"❌ Erros:        {self.stats['files_errors']}")
        logger.info(f"📊 Total:       {self.stats['files_processed']}")
        logger.info(f"💾 Enviado:     {self.stats['bytes_uploaded'] / 1e9:.2f} GB")
        logger.info(f"⊘ Duplicado:    {self.stats['bytes_duplicated'] / 1e9:.2f} GB")
        logger.info(f"⊘ Pulado:       {self.stats['bytes_skipped'] / 1e9:.2f} GB")
        logger.info("=" * 70 + "\n")
    
    def cleanup(self):
        """Fecha conexões"""
        if self.db:
            self.db.close()


async def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="S3 Upload com Deduplicação (v2 - Seguro)")
    parser.add_argument("directories", nargs="+", help="Diretórios a processar")
    parser.add_argument("--pattern", default="*", help="Padrão de ficheiros")
    parser.add_argument("--workers", type=int, default=4, help="Número de workers")
    parser.add_argument("--dry-run", action="store_true", help="Só simula (recomendado na primeira vez)")
    
    args = parser.parse_args()
    
    logger.info(f"🚀 S3 Deduplicator v2 iniciado")
    logger.info(f"   Diretórios: {args.directories}")
    logger.info(f"   Workers: {args.workers}")
    logger.info(f"   Dry-run: {args.dry_run}")
    
    # Load config
    config = S3Config()
    
    # Initialize deduplicator
    dedup = S3Deduplicator(config, dry_run=args.dry_run)
    
    # Process directories
    for directory in args.directories:
        try:
            dedup.process_directory(Path(directory), args.pattern, args.workers)
        except Exception as e:
            logger.error(f"✗ Erro ao processar {directory}: {e}")
    
    # Cleanup
    dedup.cleanup()
    
    logger.info("✓ Processo concluído")


if __name__ == "__main__":
    asyncio.run(main())
