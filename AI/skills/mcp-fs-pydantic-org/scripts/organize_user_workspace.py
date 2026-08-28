#!/usr/bin/env python3
"""
Modulo de Organizacao e Ingestao Global do Workspace (organize_user_workspace.py).
Varre as pastas de trabalho e pecas processuais do utilizador, filtra documentos juridicos,
protege rigorosamente pastas de sistema/IA/configuracoes, calcula SHA-256,
deduplica e organiza nos 6 Agentes Canonicos de C:\\Users\\Yokozuna\\Dev\\Projects\\Ficheiros Escritos Canónicos.
Suporte completo a Windows Long Paths (\\\\?\\) e tratamento de erros de caminhos extensos.
"""
import os
import sys
import shutil
import hashlib
import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Any, Tuple

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

USER_HOME = Path(r"C:\Users\Yokozuna")
DEV_ROOT = Path(r"C:\Users\Yokozuna\Dev")
CANONICAL_ROOT = DEV_ROOT / "Projects" / "Ficheiros Escritos Canónicos"
OUTPUT_CENTRAL = DEV_ROOT / "OUTPUT_CENTRALIZADO"
REPORTS_DIR = OUTPUT_CENTRAL / "01_INDEX_E_RELATORIOS"

# 1. Pastas do Sistema e IA estritamente PROTEGIDAS (NUNCA TOCAR / NUNCA MOVER / TOTALMENTE IMUTAVEIS)
PROTECTED_SYSTEM_PATHS = [
    USER_HOME / ".codex",
    USER_HOME / ".gemini",
    USER_HOME / ".antigravity-ide",
    USER_HOME / ".kimi-work",
    USER_HOME / ".kimi-webbridge",
    USER_HOME / ".cache",
    USER_HOME / "AppData",
    USER_HOME / "Searches",
    USER_HOME / "Favorites",
    USER_HOME / "Links",
    USER_HOME / "Saved Games",
    USER_HOME / "Music",
    USER_HOME / "Videos",
    USER_HOME / "Pictures",
    DEV_ROOT / ".agents",
    DEV_ROOT / ".git",
    DEV_ROOT / "node_modules",
    DEV_ROOT / "__pycache__",
    DEV_ROOT / "OUTPUT_CENTRALIZADO",
]

# 2. Mapeamento de Pastas Processuais para os 6 Agentes Canonicos
PROCESS_MAPPINGS = [
    (USER_HOME / "01_INICIAL", CANONICAL_ROOT / "04_Processos_E_Pecas_Escritas" / "04.01_Pecas_Iniciais", "04_Processos_E_Pecas_Escritas"),
    (USER_HOME / "02_CONTESTACAO", CANONICAL_ROOT / "04_Processos_E_Pecas_Escritas" / "04.02_Contestacoes", "04_Processos_E_Pecas_Escritas"),
    (USER_HOME / "03_PROVAS", CANONICAL_ROOT / "01_PDFs_Oficiais" / "01.03_Provas_Documentais", "01_PDFs_Oficiais"),
    (USER_HOME / "04_ALEGACOES", CANONICAL_ROOT / "04_Processos_E_Pecas_Escritas" / "04.04_Alegacoes", "04_Processos_E_Pecas_Escritas"),
    (USER_HOME / "05_SENTENCA", CANONICAL_ROOT / "01_PDFs_Oficiais" / "01.05_Sentencas_Decisoes", "01_PDFs_Oficiais"),
    (USER_HOME / "06_RECURSOS", CANONICAL_ROOT / "04_Processos_E_Pecas_Escritas" / "04.06_Recursos", "04_Processos_E_Pecas_Escritas"),
]

# 3. Pastas de Documentos Gerais para Varredura e Extracao Documental Segura
GENERAL_SCAN_FOLDERS = [
    (USER_HOME / "Desktop", "Desktop"),
    (USER_HOME / "Documents", "Documents"),
    (USER_HOME / "Downloads", "Downloads"),
    (USER_HOME / "OneDrive", "OneDrive"),
]

# Extensoes qualificadas como documentos juridicos/provas
DOCUMENT_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".odt", ".rtf", ".txt", ".md",
    ".msg", ".eml", ".xlsx", ".xls", ".csv", ".jpg", ".jpeg", ".png", ".tiff"
}

# Extensoes de sistema/binarios ignoradas
SYSTEM_IGNORE_EXTENSIONS = {
    ".exe", ".dll", ".sys", ".dat", ".ini", ".bin", ".msi", ".iso",
    ".vmdk", ".tmp", ".lock", ".pyc", ".pyd", ".cmd", ".lnk", ".url"
}


def make_win_long_path(path: Path) -> str:
    """Converte caminho absoluto para sintaxe long path (\\\\?\\) compativel com Windows."""
    try:
        abs_str = os.path.abspath(str(path))
        if abs_str.startswith("\\\\?\\"):
            return abs_str
        if abs_str.startswith("\\\\"):
            return "\\\\?\\UNC\\" + abs_str[2:]
        return "\\\\?\\" + abs_str
    except Exception:
        return str(path)


def sanitize_name(name: str) -> str:
    name_stem, ext = os.path.splitext(name)
    replacements = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c', 'ñ': 'n',
        'Á': 'A', 'À': 'A', 'Ã': 'A', 'Â': 'A', 'Ä': 'A',
        'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
        'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ï': 'I',
        'Ó': 'O', 'Ò': 'O', 'Õ': 'O', 'Ô': 'O', 'Ö': 'O',
        'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ü': 'U',
        'Ç': 'C', 'Ñ': 'N'
    }
    for char, repl in replacements.items():
        name_stem = name_stem.replace(char, repl)
    
    clean_stem = re.sub(r'[^a-zA-Z0-9_\-]', '_', name_stem)
    clean_stem = re.sub(r'_+', '_', clean_stem).strip('_')
    if len(clean_stem) > 70:
        clean_stem = clean_stem[:70]
    return f"{clean_stem}{ext.lower()}"


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    long_path = make_win_long_path(filepath)
    try:
        with open(long_path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        try:
            with open(str(filepath), "rb") as f:
                while chunk := f.read(65536):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return ""


def get_file_size_safe(filepath: Path) -> int:
    long_path = make_win_long_path(filepath)
    try:
        return os.path.getsize(long_path)
    except Exception:
        try:
            return os.path.getsize(str(filepath))
        except Exception:
            return 0


def is_protected_path(path: Path) -> bool:
    try:
        path_str = str(path).lower()
        for p in PROTECTED_SYSTEM_PATHS:
            p_str = str(p).lower()
            if path_str == p_str or path_str.startswith(p_str + os.sep) or path_str.startswith(p_str + "/"):
                return True
    except Exception:
        pass
    return False


def classify_general_file(file_path: Path) -> Tuple[Path, str]:
    ext = file_path.suffix.lower()
    name = file_path.name.lower()
    
    if ext == ".pdf":
        if any(w in name for w in ["despacho", "sentenca", "certidao", "ata", "notificacao", "oficio"]):
            return (CANONICAL_ROOT / "01_PDFs_Oficiais" / "01.01_Atos_Oficiais", "01_PDFs_Oficiais")
        return (CANONICAL_ROOT / "01_PDFs_Oficiais" / "01.02_Documentos_PDF", "01_PDFs_Oficiais")
    
    if ext in [".docx", ".doc", ".odt", ".rtf", ".txt"]:
        if any(w in name for w in ["rascunho", "minuta", "nota", "esboco", "draft"]):
            return (CANONICAL_ROOT / "02_Minutas_E_Rascunhos" / "02.01_Rascunhos_Gerais", "02_Minutas_E_Rascunhos")
        if any(w in name for w in ["contrato", "acordo", "cpcv", "arrendamento", "clausula"]):
            return (CANONICAL_ROOT / "03_Contratos_E_Acordos" / "03.01_Contratos_Gerais", "03_Contratos_E_Acordos")
        if any(w in name for w in ["email", "carta", "comunicacao", "notificacao", "msg"]):
            return (CANONICAL_ROOT / "05_Correspondencia_E_Comunicacoes" / "05.01_Emails_E_Cartas", "05_Correspondencia_E_Comunicacoes")
        return (CANONICAL_ROOT / "04_Processos_E_Pecas_Escritas" / "04.09_Articulados_Diversos", "04_Processos_E_Pecas_Escritas")
    
    if ext in [".msg", ".eml"]:
        return (CANONICAL_ROOT / "05_Correspondencia_E_Comunicacoes" / "05.02_Mensagens_EML_MSG", "05_Correspondencia_E_Comunicacoes")
    
    if ext in [".jpg", ".jpeg", ".png", ".tiff"]:
        return (CANONICAL_ROOT / "01_PDFs_Oficiais" / "01.09_Imagens_E_Provas_Visuais", "01_PDFs_Oficiais")

    return (CANONICAL_ROOT / "00_Indice_E_MOCs" / "00.09_Outros", "00_Indice_E_MOCs")


def load_existing_canonical_hashes() -> Set[str]:
    seen = set()
    index_atos = CANONICAL_ROOT / "_index" / "atos_processuais.jsonl"
    if index_atos.exists():
        try:
            with open(make_win_long_path(index_atos), "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            d = json.loads(line.strip())
                            h = d.get("sha256")
                            if h and len(h) == 64:
                                seen.add(h)
                        except Exception:
                            pass
        except Exception:
            pass
    return seen


def run_organization(dry_run: bool = True) -> Dict[str, Any]:
    print("==================================================================")
    print(" ORGANIZACAO E INGESTAO GLOBAL DO WORKSPACE (LONG PATH SAFE)")
    print(f" Modo      : {'[SIMULACAO / DRY-RUN] (Sem alteracoes em disco)' if dry_run else '[EXECUCAO REAL] (Copia Segura para Ficheiros Canonicos)'}")
    print(f" Destino   : {CANONICAL_ROOT}")
    print("==================================================================")

    existing_hashes = load_existing_canonical_hashes()
    print(f"[INFO] Hashes SHA-256 pre-existentes no acervo: {len(existing_hashes)}")

    protected_status = []
    for p in PROTECTED_SYSTEM_PATHS:
        exists = p.exists()
        protected_status.append({
            "path": str(p),
            "existe": exists,
            "status": "PROTEGIDO_IMUTAVEL"
        })

    planned_actions = []
    stats = {
        "pastas_processuais_analisadas": 0,
        "pastas_gerais_analisadas": 0,
        "ficheiros_encontrados": 0,
        "ficheiros_qualificados": 0,
        "ficheiros_sistema_protegidos": 0,
        "duplicados_sha256_identificados": 0,
        "novos_documentos_para_ingestao": 0,
        "bytes_totais": 0,
        "erros": 0
    }

    # 1. Processar Pastas Processuais (01_INICIAL a 06_RECURSOS)
    for src_dir, target_dir, folder_name in PROCESS_MAPPINGS:
        if not src_dir.exists():
            continue
        
        stats["pastas_processuais_analisadas"] += 1
        print(f"\n[SCAN PROCESSUAL] {src_dir.name} -> {target_dir.relative_to(CANONICAL_ROOT)}")
        
        long_src = make_win_long_path(src_dir)
        for root, dirs, files in os.walk(long_src):
            for f in files:
                stats["ficheiros_encontrados"] += 1
                fpath = Path(root) / f
                
                if is_protected_path(fpath):
                    stats["ficheiros_sistema_protegidos"] += 1
                    continue
                
                ext = fpath.suffix.lower()
                if ext in SYSTEM_IGNORE_EXTENSIONS:
                    stats["ficheiros_sistema_protegidos"] += 1
                    continue
                
                if ext not in DOCUMENT_EXTENSIONS:
                    continue

                try:
                    stats["ficheiros_qualificados"] += 1
                    fsize = get_file_size_safe(fpath)
                    stats["bytes_totais"] += fsize
                    
                    fhash = compute_sha256(fpath)
                    is_dup = fhash in existing_hashes if fhash else False
                    
                    if is_dup:
                        stats["duplicados_sha256_identificados"] += 1
                    else:
                        stats["novos_documentos_para_ingestao"] += 1
                        if fhash:
                            existing_hashes.add(fhash)

                    clean_fname = sanitize_name(f)
                    dest_fpath = target_dir / clean_fname

                    planned_actions.append({
                        "origem": str(fpath),
                        "origem_tipo": "PASTA_PROCESSUAL",
                        "pasta_origem": src_dir.name,
                        "destino_planeado": str(dest_fpath),
                        "pasta_canonica": folder_name,
                        "filename_original": f,
                        "filename_higienizado": clean_fname,
                        "tamanho_bytes": fsize,
                        "sha256": fhash,
                        "is_duplicado": is_dup,
                        "acao": "SKIPPED_DUPLICATE" if is_dup else ("COPIED" if not dry_run else "PLANNED_COPY")
                    })

                    if not dry_run and not is_dup:
                        os.makedirs(make_win_long_path(target_dir), exist_ok=True)
                        shutil.copy2(make_win_long_path(fpath), make_win_long_path(dest_fpath))
                except Exception:
                    stats["erros"] += 1

    # 2. Processar Pastas Gerais do Utilizador (Desktop, Documents, Downloads, OneDrive)
    for src_folder, label in GENERAL_SCAN_FOLDERS:
        if not src_folder.exists():
            continue
        
        stats["pastas_gerais_analisadas"] += 1
        print(f"\n[SCAN GERAL] {label} ({src_folder})")

        long_src_folder = make_win_long_path(src_folder)
        for root, dirs, files in os.walk(long_src_folder):
            dirs[:] = [d for d in dirs if not is_protected_path(Path(root) / d) and d.lower() not in [".git", "node_modules", "$recycle.bin", "appdata", ".cache"]]
            
            for f in files:
                stats["ficheiros_encontrados"] += 1
                fpath = Path(root) / f
                
                if is_protected_path(fpath):
                    stats["ficheiros_sistema_protegidos"] += 1
                    continue
                
                ext = fpath.suffix.lower()
                if ext in SYSTEM_IGNORE_EXTENSIONS:
                    stats["ficheiros_sistema_protegidos"] += 1
                    continue
                
                if ext not in DOCUMENT_EXTENSIONS:
                    continue

                try:
                    name_lower = f.lower()
                    is_judicial = any(w in name_lower for w in [
                        "processo", "tribunal", "despacho", "sentenca", "citius", "execucao", "requerimento",
                        "cpc", "arrentela", "penhora", "citacao", "habita", "lea", "spark", "contrato",
                        "recibo", "declaracao", "certidao", "seguranca_social", "tpa", "unicre", "banco",
                        "extrato", "recurso", "alegacao", "provas", "contestacao", "inicial", "teresa", "nuno"
                    ])

                    if not is_judicial and ext not in [".pdf", ".msg", ".eml"]:
                        continue

                    stats["ficheiros_qualificados"] += 1
                    fsize = get_file_size_safe(fpath)
                    stats["bytes_totais"] += fsize

                    fhash = compute_sha256(fpath)
                    is_dup = fhash in existing_hashes if fhash else False

                    if is_dup:
                        stats["duplicados_sha256_identificados"] += 1
                    else:
                        stats["novos_documentos_para_ingestao"] += 1
                        if fhash:
                            existing_hashes.add(fhash)

                    target_dir, folder_name = classify_general_file(fpath)
                    clean_fname = sanitize_name(f)
                    dest_fpath = target_dir / clean_fname

                    planned_actions.append({
                        "origem": str(fpath),
                        "origem_tipo": f"PASTA_GERAL_{label.upper()}",
                        "pasta_origem": label,
                        "destino_planeado": str(dest_fpath),
                        "pasta_canonica": folder_name,
                        "filename_original": f,
                        "filename_higienizado": clean_fname,
                        "tamanho_bytes": fsize,
                        "sha256": fhash,
                        "is_duplicado": is_dup,
                        "acao": "SKIPPED_DUPLICATE" if is_dup else ("COPIED" if not dry_run else "PLANNED_COPY")
                    })

                    if not dry_run and not is_dup:
                        os.makedirs(make_win_long_path(target_dir), exist_ok=True)
                        shutil.copy2(make_win_long_path(fpath), make_win_long_path(dest_fpath))
                except Exception:
                    stats["erros"] += 1

    # 3. Gerar Relatórios em OUTPUT_CENTRALIZADO
    os.makedirs(make_win_long_path(REPORTS_DIR), exist_ok=True)
    report_json_path = REPORTS_DIR / "relatorio_organizacao_global.json"
    protected_map_path = REPORTS_DIR / "mapa_pastas_protegidas.md"

    report_payload = {
        "timestamp": datetime.now().isoformat(),
        "modo_execucao": "DRY_RUN_SIMULACAO" if dry_run else "EXECUCAO_REAL_COPIA_SEGURA",
        "estatisticas": stats,
        "pastas_protegidas": protected_status,
        "amostra_acoes": planned_actions[:100],
        "total_acoes": len(planned_actions)
    }

    with open(make_win_long_path(report_json_path), "w", encoding="utf-8") as f:
        json.dump(report_payload, f, ensure_ascii=False, indent=2)

    # Gerar Markdown de Proteção
    md_lines = [
        "# Mapa de Protecao Rigorosa de Ficheiros do Sistema e IA",
        f"\n**Data de Auditoria**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "**Diretriz Canonica**: `AGENTS.md` e `PROTOCOL.md` (Zero Acoes Destrutivas)\n",
        "## 1. Pastas do Sistema e IA Protegidas (Imutaveis)\n",
        "| Pasta de Sistema / IA | Status de Protecao | Regra de Seguranca |",
        "|---|---|---|"
    ]
    for p in protected_status:
        md_lines.append(f"| `{p['path']}` | **PROTEGIDO** | Leitura restrita / Sem remocao ou alteracao |")

    md_lines.extend([
        "\n## 2. Resumo da Ingestao e Organizacao Segura\n",
        f"- **Ficheiros Totais Encontrados**: {stats['ficheiros_encontrados']:,}".replace(",", "."),
        f"- **Documentos Juridicos Qualificados**: {stats['ficheiros_qualificados']:,}".replace(",", "."),
        f"- **Ficheiros de Sistema Protegidos e Ignorados**: {stats['ficheiros_sistema_protegidos']:,}".replace(",", "."),
        f"- **Duplicados SHA-256 Identificados**: {stats['duplicados_sha256_identificados']:,}".replace(",", "."),
        f"- **Novos Documentos Ingeridos**: {stats['novos_documentos_para_ingestao']:,}".replace(",", "."),
        f"- **Volume de Dados Processado**: {stats['bytes_totais'] / (1024*1024):.2f} MB\n",
        "## 3. Destinos Canonicos nos 6 Agentes\n",
        "- `00_Indice_E_MOCs`: Indices, catalogos e mapas MOC",
        "- `01_PDFs_Oficiais`: Certidoes, sentencas, atas e PDFs autenticados",
        "- `02_Minutas_E_Rascunhos`: Rascunhos de trabalho (isolamento estrito)",
        "- `03_Contratos_E_Acordos`: Contratos, acordos e termos",
        "- `04_Processos_E_Pecas_Escritas`: Articulados, iniciais, contestacoes e recursos",
        "- `05_Correspondencia_E_Comunicacoes`: Emails, notificacoes e mensagens"
    ])

    with open(make_win_long_path(protected_map_path), "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print("\n" + "=" * 80)
    print(" RESUMO DA ORGANIZACAO E PROTECAO GLOBAL")
    print("=" * 80)
    print(f" - Ficheiros encontrados       : {stats['ficheiros_encontrados']:,}".replace(",", "."))
    print(f" - Documentos qualificados     : {stats['ficheiros_qualificados']:,}".replace(",", "."))
    print(f" - Ficheiros sistema protegidos: {stats['ficheiros_sistema_protegidos']:,}".replace(",", "."))
    print(f" - Duplicados SHA-256 evitados : {stats['duplicados_sha256_identificados']:,}".replace(",", "."))
    print(f" - Novos documentos ingeridos  : {stats['novos_documentos_para_ingestao']:,}".replace(",", "."))
    print(f" - Relatorio JSON              : {report_json_path}")
    print(f" - Mapa de Protecao Markdown   : {protected_map_path}")
    print("=" * 80 + "\n")

    return report_payload


def main():
    parser = argparse.ArgumentParser(description="Organizador e Ingestor Global do Workspace com Protecao de Sistema")
    parser.add_argument("--dry-run", action="store_true", help="Simulacao sem escrita")
    parser.add_argument("--apply", action="store_true", help="Execucao real com copia segura")
    args = parser.parse_args()

    dry_run = not args.apply
    run_organization(dry_run=dry_run)


if __name__ == "__main__":
    main()
