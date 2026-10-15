"""
ISOLADOR DE DADOS - Diagnóstico completo
Identifica o que é DADOS vs FERRAMENTAS vs PRIVADO vs TEMPORÁRIO
"""
import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import logging

# Setup logging
log_file = Path(r"C:\ACERVO\logs") / f"isolador_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
log_file.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataIsolator:
    """Classifica pastas em: DADOS / FERRAMENTAS / PRIVADO / TEMPORÁRIO"""
    
    # Pastas que são FERRAMENTAS/CACHE (não migrar para S3)
    TOOLS_PATTERNS = {
        ".vscode", ".docker", ".cargo", ".cache", ".config", ".local",
        ".kube", ".git", "node_modules", "target", "__pycache__",
        ".pytest_cache", ".tox", ".venv", "venv", ".env",
        ".android", ".adk", ".bun", ".dotnet", "bin", "go",
        ".rustup", ".ollama", ".ipython", ".aws", ".azure",
        # IDEs e Editors
        ".aider", ".cline", ".claude", ".copilot", ".continue",
        ".vscode-server", ".jetbrains", ".sublime",
        # LLM/AI tools
        ".gemini", ".grok", ".kimi", ".openai", ".anthropic",
        ".qwen", ".claude", ".codeium", ".tabnine", ".copilot",
        # Build tools
        ".gradle", ".maven", ".npm", ".bower", ".bundler",
    }
    
    # Pastas que são PRIVADO (nunca migrar)
    PRIVATE_PATTERNS = {
        "pessoal", "personal", "private", "privado",
        "family", "famíliar", "confidencial",
    }
    
    # Pastas que são TEMPORÁRIO/TESTE (questionar)
    TEMP_PATTERNS = {
        "temp", "tmp", "test", "testes", "tests",
        "triagem", "sandbox", "quarentena",
        "temp_", "_temp", "~", "$",
        "backup", "copy", "cópia", "old", "obsoleto",
    }
    
    # Pastas que são DADOS REAIS (migrar)
    DATA_PATTERNS = {
        "provas", "acervo", "juridico", "documentos",
        "legal", "dossier", "case", "caso", "forense",
        "audit", "auditoria", "consolidado", "organizado",
        "final", "master", "archive", "recovery", "recuperado",
    }
    
    def __init__(self):
        self.results = {
            "DADOS": [],
            "FERRAMENTAS": [],
            "PRIVADO": [],
            "TEMPORÁRIO": [],
            "INDECISO": [],
        }
        self.sizes = defaultdict(int)
        self.file_count = defaultdict(int)
    
    def classify_folder(self, folder_name: str) -> str:
        """Classifica uma pasta"""
        folder_lower = folder_name.lower().replace(" - cópia", "").strip()
        
        # Check private first (priority)
        for pattern in self.PRIVATE_PATTERNS:
            if pattern in folder_lower:
                return "PRIVADO"
        
        # Check tools
        for pattern in self.TOOLS_PATTERNS:
            if pattern in folder_lower:
                return "FERRAMENTAS"
        
        # Check temporary
        for pattern in self.TEMP_PATTERNS:
            if pattern in folder_lower:
                return "TEMPORÁRIO"
        
        # Check data
        for pattern in self.DATA_PATTERNS:
            if pattern in folder_lower:
                return "DADOS"
        
        # Default: indeciso
        return "INDECISO"
    
    def get_folder_size(self, folder_path: Path) -> int:
        """Calcula tamanho total da pasta"""
        try:
            total = 0
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        pass
            return total
        except Exception as e:
            logger.warning(f"Erro ao calcular tamanho de {folder_path}: {e}")
            return 0
    
    def count_files(self, folder_path: Path) -> int:
        """Conta ficheiros totais"""
        try:
            count = 0
            for dirpath, dirnames, filenames in os.walk(folder_path):
                count += len(filenames)
            return count
        except Exception as e:
            logger.warning(f"Erro ao contar ficheiros em {folder_path}: {e}")
            return 0
    
    def scan_user_directory(self, user_path: Path):
        """Varre directório do utilizador"""
        logger.info(f"\n📁 Analisando: {user_path}")
        logger.info("=" * 80)
        
        try:
            # Listar tudo
            items = list(user_path.iterdir())
            folders = [item for item in items if item.is_dir()]
            
            logger.info(f"📊 Total de pastas: {len(folders)}")
            
            for i, folder in enumerate(folders, 1):
                folder_name = folder.name
                classification = self.classify_folder(folder_name)
                
                # Calcular tamanho e ficheiros
                size = self.get_folder_size(folder)
                files = self.count_files(folder)
                
                # Guardar
                self.results[classification].append({
                    "path": str(folder),
                    "name": folder_name,
                    "size_gb": size / 1e9,
                    "size_bytes": size,
                    "files": files,
                })
                
                self.sizes[classification] += size
                self.file_count[classification] += files
                
                # Log
                emoji = {
                    "DADOS": "📦",
                    "FERRAMENTAS": "🔧",
                    "PRIVADO": "🔐",
                    "TEMPORÁRIO": "⏱️",
                    "INDECISO": "❓",
                }[classification]
                
                logger.info(f"{emoji} [{i:3d}] {classification:15s} | {size/1e9:8.2f} GB | {files:6d} files | {folder_name}")
        
        except Exception as e:
            logger.error(f"Erro ao escanear {user_path}: {e}")
    
    def print_summary(self):
        """Imprime resumo final"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 RESUMO ISOLAÇÃO DE DADOS")
        logger.info("=" * 80)
        
        for category in ["DADOS", "FERRAMENTAS", "PRIVADO", "TEMPORÁRIO", "INDECISO"]:
            folders = self.results[category]
            total_size = self.sizes[category]
            total_files = self.file_count[category]
            
            emoji = {
                "DADOS": "📦",
                "FERRAMENTAS": "🔧",
                "PRIVADO": "🔐",
                "TEMPORÁRIO": "⏱️",
                "INDECISO": "❓",
            }[category]
            
            logger.info(f"\n{emoji} {category}")
            logger.info(f"   Pastas: {len(folders)}")
            logger.info(f"   Tamanho: {total_size/1e9:.2f} GB")
            logger.info(f"   Ficheiros: {total_files:,}")
            
            # Top 5 maiores
            if folders:
                top_5 = sorted(folders, key=lambda x: x['size_gb'], reverse=True)[:5]
                for item in top_5:
                    logger.info(f"      - {item['name']:50s} {item['size_gb']:8.2f} GB")
        
        # Summary by action
        logger.info("\n" + "=" * 80)
        logger.info("✅ AÇÕES RECOMENDADAS")
        logger.info("=" * 80)
        
        logger.info(f"\n1️⃣ MIGRAR PARA S3 (DADOS):")
        logger.info(f"   Total: {self.sizes['DADOS']/1e9:.2f} GB em {len(self.results['DADOS'])} pastas")
        logger.info(f"   Ficheiros: {self.file_count['DADOS']:,}")
        
        logger.info(f"\n2️⃣ IGNORAR (FERRAMENTAS):")
        logger.info(f"   Total: {self.sizes['FERRAMENTAS']/1e9:.2f} GB em {len(self.results['FERRAMENTAS'])} pastas")
        logger.info(f"   ➜ Estas são cache/config, não precisam de backup")
        
        logger.info(f"\n3️⃣ NÃO TOCAR (PRIVADO):")
        logger.info(f"   Total: {self.sizes['PRIVADO']/1e9:.2f} GB em {len(self.results['PRIVADO'])} pastas")
        logger.info(f"   ➜ Dados pessoais/confidenciais, decisão sua")
        
        logger.info(f"\n4️⃣ QUESTIONAR (TEMPORÁRIO):")
        logger.info(f"   Total: {self.sizes['TEMPORÁRIO']/1e9:.2f} GB em {len(self.results['TEMPORÁRIO'])} pastas")
        logger.info(f"   ➜ Podia ser teste/draft, verificar manualmente")
        
        logger.info(f"\n5️⃣ MANUAL (INDECISO):")
        logger.info(f"   Total: {self.sizes['INDECISO']/1e9:.2f} GB em {len(self.results['INDECISO'])} pastas")
        logger.info(f"   ➜ Precisa de decisão manual")
        
        # Grand total
        grand_total = sum(self.sizes.values())
        logger.info(f"\n📊 TOTAL GERAL: {grand_total/1e9:.2f} GB")
    
    def save_report(self):
        """Salva relatório em JSON"""
        report_file = Path(r"C:\ACERVO\reports") / f"isolacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "DADOS": {
                    "folders": len(self.results["DADOS"]),
                    "size_gb": self.sizes["DADOS"] / 1e9,
                    "files": self.file_count["DADOS"],
                },
                "FERRAMENTAS": {
                    "folders": len(self.results["FERRAMENTAS"]),
                    "size_gb": self.sizes["FERRAMENTAS"] / 1e9,
                    "files": self.file_count["FERRAMENTAS"],
                },
                "PRIVADO": {
                    "folders": len(self.results["PRIVADO"]),
                    "size_gb": self.sizes["PRIVADO"] / 1e9,
                    "files": self.file_count["PRIVADO"],
                },
                "TEMPORÁRIO": {
                    "folders": len(self.results["TEMPORÁRIO"]),
                    "size_gb": self.sizes["TEMPORÁRIO"] / 1e9,
                    "files": self.file_count["TEMPORÁRIO"],
                },
                "INDECISO": {
                    "folders": len(self.results["INDECISO"]),
                    "size_gb": self.sizes["INDECISO"] / 1e9,
                    "files": self.file_count["INDECISO"],
                },
            },
            "details": self.results,
        }
        
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n✅ Relatório salvo: {report_file}")


def main():
    """Função principal"""
    logger.info("🔍 ISOLADOR DE DADOS v1")
    logger.info(f"   Iniciado: {datetime.now()}")
    
    # Scanning
    isolator = DataIsolator()
    isolator.scan_user_directory(Path(r"C:\Users\Yokozuna"))
    
    # Reports
    isolator.print_summary()
    isolator.save_report()
    
    logger.info("\n✅ Análise completa!")


if __name__ == "__main__":
    main()
