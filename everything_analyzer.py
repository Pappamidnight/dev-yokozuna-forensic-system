"""
EXPERIMENTO EVERYTHING + CSV
Exporta, filtra, deduplica e prepara para S3
"""
import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup logging
log_dir = Path(r"C:\ACERVO\logs")
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"everything_experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EverythingCSVAnalyzer:
    """Analisa CSV do Everything"""
    
    # Palavras-chave para DADOS
    DATA_KEYWORDS = {
        "provas", "acervo", "juridico", "documentos", "legal",
        "dossier", "case", "caso", "forense", "audit", "auditoria",
        "consolidado", "organizado", "final", "master", "archive",
        "recovery", "recuperado", "judicial", "tribunal"
    }
    
    # Extensões perigosas (não migrar)
    DANGEROUS_EXT = {
        ".exe", ".dll", ".sys", ".drv", ".scr", ".msi", ".bin"
    }
    
    # Pastas a ignorar
    IGNORE_FOLDERS = {
        "node_modules", "target", "__pycache__", ".git", ".venv",
        ".cache", ".config", ".vscode", "AppData", ".rustup",
        "node_modules", "venv", ".env", ".local", ".docker",
    }
    
    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        self.files = []
        self.stats = {
            "total_files": 0,
            "total_size_gb": 0,
            "data_files": 0,
            "data_size_gb": 0,
            "duplicates": 0,
            "errors": 0,
        }
        self.hashes = defaultdict(list)  # hash -> [files]
    
    def load_csv(self):
        """Carrega CSV do Everything"""
        logger.info(f"📂 Carregando CSV: {self.csv_path}")
        
        if not self.csv_path.exists():
            logger.error(f"✗ CSV não existe: {self.csv_path}")
            return False
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.files.append(row)
                    self.stats["total_files"] += 1
                    
                    # Tamanho
                    try:
                        size = int(row.get('Size', 0))
                        self.stats["total_size_gb"] += size / 1e9
                    except:
                        pass
            
            logger.info(f"✓ Carregados {self.stats['total_files']} ficheiros")
            logger.info(f"✓ Tamanho total: {self.stats['total_size_gb']:.2f} GB")
            return True
        
        except Exception as e:
            logger.error(f"✗ Erro ao carregar CSV: {e}")
            return False
    
    def is_data_file(self, file_dict: dict) -> bool:
        """Verifica se é ficheiro de DADOS"""
        path = file_dict.get('FileName', '')
        path_lower = path.lower()
        
        # Check if any IGNORE folder is in path
        for ignore in self.IGNORE_FOLDERS:
            if f"\\{ignore}\\" in path_lower or f"\\{ignore}" in path_lower:
                return False
        
        # Check dangerous extensions
        for ext in self.DANGEROUS_EXT:
            if path_lower.endswith(ext):
                return False
        
        # Check if any DATA keyword is in path
        for keyword in self.DATA_KEYWORDS:
            if keyword in path_lower:
                return True
        
        return False
    
    def filter_data_files(self):
        """Filtra só ficheiros de DADOS"""
        logger.info("\n🔍 Filtrando ficheiros de DADOS...")
        
        data_files = []
        for file_dict in self.files:
            if self.is_data_file(file_dict):
                data_files.append(file_dict)
                try:
                    size = int(file_dict.get('Size', 0))
                    self.stats["data_size_gb"] += size / 1e9
                except:
                    pass
        
        self.stats["data_files"] = len(data_files)
        logger.info(f"✓ Ficheiros de DADOS: {len(data_files)}")
        logger.info(f"✓ Tamanho DADOS: {self.stats['data_size_gb']:.2f} GB")
        
        return data_files
    
    def calculate_hash(self, file_path: str) -> str:
        """Calcula SHA-256 de um ficheiro"""
        try:
            if not Path(file_path).exists():
                return None
            
            hash_obj = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192 * 1024), b''):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"✗ Erro ao hashear {file_path}: {e}")
            self.stats["errors"] += 1
            return None
    
    def find_duplicates(self, data_files: list, workers: int = 8):
        """Encontra duplicados por SHA-256"""
        logger.info(f"\n🔐 Calculando SHA-256 ({workers} workers)...")
        
        # Filtrar ficheiros válidos
        valid_files = []
        for f in data_files:
            path = f.get('FileName', '')
            if path and Path(path).exists() and Path(path).is_file():
                size = int(f.get('Size', 0))
                if size > 0:
                    valid_files.append((path, f))
        
        logger.info(f"📊 Ficheiros válidos: {len(valid_files)}")
        
        # Calcular hashes em paralelo
        results = {}
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(self.calculate_hash, path): (path, file_dict) 
                      for path, file_dict in valid_files}
            
            for i, future in enumerate(as_completed(futures), 1):
                path, file_dict = futures[future]
                try:
                    hash_sha256 = future.result()
                    if hash_sha256:
                        self.hashes[hash_sha256].append({
                            'path': path,
                            'size': int(file_dict.get('Size', 0)),
                            'file_dict': file_dict
                        })
                        results[path] = hash_sha256
                except Exception as e:
                    logger.error(f"✗ Erro com {path}: {e}")
                
                if i % 500 == 0:
                    logger.info(f"   {i}/{len(valid_files)} ficheiros processados")
        
        # Encontrar duplicados
        duplicates = {h: files for h, files in self.hashes.items() if len(files) > 1}
        self.stats["duplicates"] = sum(len(files) - 1 for files in duplicates.values())
        
        logger.info(f"\n📊 ANÁLISE DE DUPLICADOS")
        logger.info(f"   Hashes únicos: {len(self.hashes)}")
        logger.info(f"   Hashes duplicados: {len(duplicates)}")
        logger.info(f"   Ficheiros duplicados: {self.stats['duplicates']}")
        
        return duplicates
    
    def print_summary(self, data_files: list, duplicates: dict):
        """Imprime resumo"""
        logger.info("\n" + "="*80)
        logger.info("📊 RESUMO EVERYTHING + DEDUPLICAÇÃO")
        logger.info("="*80)
        logger.info(f"Total ficheiros:        {self.stats['total_files']:,}")
        logger.info(f"Total tamanho:          {self.stats['total_size_gb']:.2f} GB")
        logger.info(f"")
        logger.info(f"Ficheiros DADOS:        {self.stats['data_files']:,}")
        logger.info(f"Tamanho DADOS:          {self.stats['data_size_gb']:.2f} GB")
        logger.info(f"")
        logger.info(f"Hashes únicos:          {len(self.hashes):,}")
        logger.info(f"Ficheiros duplicados:   {self.stats['duplicates']:,}")
        logger.info(f"Erros:                  {self.stats['errors']}")
        logger.info("="*80)
        
        # Top 10 maiores duplicados
        if duplicates:
            logger.info("\n🔴 TOP 10 MAIORES DUPLICADOS")
            top_dups = sorted(duplicates.items(), 
                            key=lambda x: x[1][0]['size'], 
                            reverse=True)[:10]
            for hash_val, files in top_dups:
                size_mb = files[0]['size'] / 1e6
                count = len(files)
                waste = size_mb * (count - 1)
                logger.info(f"   {hash_val[:8]}... | {size_mb:.2f} MB x {count} = {waste:.2f} MB waste")
    
    def export_results(self, data_files: list, duplicates: dict):
        """Exporta resultados em JSON"""
        report_file = Path(r"C:\ACERVO\reports") / f"everything_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Preparar dados para export
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": self.stats,
            "duplicates": {}
        }
        
        for hash_val, files in duplicates.items():
            export_data["duplicates"][hash_val] = [
                {
                    "path": f["path"],
                    "size_mb": f["size"] / 1e6,
                }
                for f in files
            ]
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n✅ Relatório exportado: {report_file}")
        return report_file


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Experimento Everything + Deduplicação")
    parser.add_argument("csv_path", help="Caminho do CSV do Everything")
    parser.add_argument("--workers", type=int, default=8, help="Número de workers")
    
    args = parser.parse_args()
    
    logger.info("🚀 EVERYTHING + DEDUPLICAÇÃO EXPERIMENT")
    logger.info(f"   CSV: {args.csv_path}")
    logger.info(f"   Workers: {args.workers}\n")
    
    # Carregar e analisar
    analyzer = EverythingCSVAnalyzer(args.csv_path)
    
    if not analyzer.load_csv():
        return
    
    data_files = analyzer.filter_data_files()
    duplicates = analyzer.find_duplicates(data_files, workers=args.workers)
    
    analyzer.print_summary(data_files, duplicates)
    analyzer.export_results(data_files, duplicates)
    
    logger.info("✅ Análise concluída!")


if __name__ == "__main__":
    main()
