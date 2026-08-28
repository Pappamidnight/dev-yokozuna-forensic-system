"""
Mapeamento de zonas e caminhos autorizados para agentes no diretorio Dev.
"""
import os
from typing import List, Dict

DEV_ROOT = "C:\\Users\\Yokozuna\\Dev"
CANONICAL_ROOT = os.path.join(DEV_ROOT, "Projects", "Ficheiros Escritos Canónicos")
INDEX_OUTPUT_DIR = os.path.join(CANONICAL_ROOT, "_index")

AUTHORIZED_ZONES: List[str] = [
    "00_Indice_E_MOCs",
    "01_PDFs_Oficiais",
    "02_Minutas_E_Rascunhos",
    "03_Contratos_E_Acordos",
    "04_Processos_E_Pecas_Escritas",
    "05_Correspondencia_E_Comunicacoes",
]


def is_path_in_dev_root(path: str) -> bool:
    """Valida se o caminho reside estritamente sob C:\\Users\\Yokozuna\\Dev."""
    norm_path = os.path.abspath(path).lower()
    norm_root = os.path.abspath(DEV_ROOT).lower()
    return norm_path.startswith(norm_root)


def is_auto_safe_path(path: str) -> bool:
    """Verifica se o caminho e estritamente a pasta _index/ autorizada para escrita."""
    norm_path = os.path.abspath(path).lower()
    norm_index = os.path.abspath(INDEX_OUTPUT_DIR).lower()
    return norm_path.startswith(norm_index)
