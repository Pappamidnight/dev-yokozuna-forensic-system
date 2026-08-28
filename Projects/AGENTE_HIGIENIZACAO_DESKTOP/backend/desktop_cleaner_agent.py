from __future__ import annotations

import os
import sys
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Tuple, Any

PROJ_ROOT = Path(__file__).resolve().parent.parent
DESKTOP_DIR = Path("C:/Users/Yokozuna/Desktop")
DEV_ROOT = Path("C:/Users/Yokozuna/Dev")


def make_long_path(path_str: str) -> str:
    abs_str = os.path.abspath(path_str)
    if abs_str.startswith("\\\\?\\"):
        return abs_str
    if abs_str.startswith("\\\\"):
        return "\\\\?\\UNC\\" + abs_str[2:]
    return "\\\\?\\" + abs_str


def sha256_file(filepath: Path | str) -> str:
    digest = hashlib.sha256()
    lp = make_long_path(str(filepath))
    try:
        with open(lp, "rb") as handle:
            while chunk := handle.read(1024 * 1024):
                digest.update(chunk)
        return digest.hexdigest()
    except Exception:
        return "0" * 64


def read_text_lossy(filepath: Path | str) -> str:
    lp = make_long_path(str(filepath))
    try:
        with open(lp, "rb") as handle:
            data = handle.read(500_000)
        for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue
        return data.decode("utf-8", errors="replace")
    except Exception:
        return ""


# Dicionario de Intervenientes Nucleares
INTERVENIENTES_CONHECIDOS = {
    "Nuno Miguel Silva Duarte": ["nuno duarte", "nuno silva duarte", "nuno miguel"],
    "Maria Teresa Castro Bangueses": ["maria teresa", "bangueses", "requerente maria teresa"],
    "Teresa de Jesus Martins": ["teresa de jesus", "teresa martins", "proprietaria teresa"],
    "Filipe Delgado": ["filipe delgado", "delgado", "gestor de facto"],
    "Nuno Forra": ["nuno forra", "mandatario forra"],
    "Spark Celtis SCR, S.A.": ["spark celtis", "celtis venture", "scr"],
    "Unicre / TPA": ["unicre", "retencao tpa", "terminal tpa"],
    "EPAL": ["epal", "agua epal", "contador epal"],
    "Seguranca Social": ["seguranca social", "protecao juridica", "citacao negativa"]
}

PROCESSOS_CONHECIDOS = [
    "15547/26.0T8LSB",
    "3719/25.0T8LSB",
    "10153/24.7T8LSB",
    "23142/22.7T8LSB"
]


class DesktopConsolidationAgent:
    """Agente de Higienizacao, Consolidacao e Otimizacao de Relacoes Cruzadas."""

    def __init__(self, desktop_path: Path = DESKTOP_DIR):
        self.desktop_path = desktop_path

    def run_hygiene_and_consolidation(self) -> Dict[str, Any]:
        print("==================================================================")
        print("INICIANDO AGENTE DE HIGIENIZACAO, CONSOLIDACAO E GRAFO DE RELACOES")
        print(f"Desktop Alvo : {self.desktop_path}")
        print("==================================================================")

        inventory = []
        relationships = []
        timeline_events = []
        interveniente_links = {k: [] for k in INTERVENIENTES_CONHECIDOS.keys()}
        process_links = {k: [] for k in PROCESSOS_CONHECIDOS}

        date_regex = re.compile(r'\b(201\d|202[0-6])[-/.](0[1-9]|1[0-2])[-/.](0[1-9]|[12]\d|3[01])\b')

        for item in sorted(self.desktop_path.iterdir()):
            if item.is_file():
                sha = sha256_file(item)
                size_b = item.stat().st_size
                text = read_text_lossy(item)
                comb_text = f"{item.name} {text}".lower()

                # 1. Identificar Intervenientes
                matched_interv = []
                for interv_name, aliases in INTERVENIENTES_CONHECIDOS.items():
                    if any(alias in comb_text for alias in aliases):
                        matched_interv.append(interv_name)
                        interveniente_links[interv_name].append(item.name)

                # 2. Identificar Processos
                matched_procs = []
                for proc in PROCESSOS_CONHECIDOS:
                    num_only = proc.split('/')[0]
                    if num_only in comb_text:
                        matched_procs.append(proc)
                        process_links[proc].append(item.name)

                # 3. Identificar Datas
                matched_dates = date_regex.findall(comb_text)
                for d_match in matched_dates:
                    d_str = f"{d_match[0]}-{d_match[1]}-{d_match[2]}"
                    timeline_events.append({
                        "data": d_str,
                        "source_file": item.name,
                        "sha256": sha,
                        "intervenientes": matched_interv,
                        "processos": matched_procs
                    })

                # 4. Criar Relacoes Cruzadas
                for interv in matched_interv:
                    for proc in matched_procs:
                        relationships.append({
                            "interveniente": interv,
                            "processo": proc,
                            "evidence_file": item.name,
                            "sha256": sha
                        })

                inventory.append({
                    "filename": item.name,
                    "filepath": str(item),
                    "sha256": sha,
                    "size_bytes": size_b,
                    "intervenientes": matched_interv,
                    "processos": matched_procs
                })

        # Renderizar Relatorio Consolidado
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_files": len(inventory),
            "total_relations": len(relationships),
            "total_dates_mapped": len(timeline_events),
            "interveniente_links": {k: len(v) for k, v in interveniente_links.items()},
            "process_links": {k: len(v) for k, v in process_links.items()},
            "inventory": inventory,
            "relationships": relationships
        }

        self._save_consolidated_reports(report, interveniente_links, process_links, timeline_events, relationships)
        return report

    def _save_consolidated_reports(
        self,
        report: Dict[str, Any],
        interveniente_links: Dict[str, List[str]],
        process_links: Dict[str, List[str]],
        timeline_events: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]]
    ):
        out_dir = PROJ_ROOT / "outputs" / "markdown"
        out_dir.mkdir(parents=True, exist_ok=True)
        jsonl_dir = PROJ_ROOT / "outputs" / "jsonl"
        jsonl_dir.mkdir(parents=True, exist_ok=True)

        # 1. Salvar JSONL de relacoes
        with open(jsonl_dir / "relacoes_consolidadas.jsonl", "w", encoding="utf-8") as f:
            for r in relationships:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        # 2. Salvar Relatorio Markdown
        rep_path = out_dir / "CONSOLIDACAO_RELACIONAMENTOS_FORENSES.md"
        lines = [
            "# Consolidacao e Otimizacao de Relacoes: Intervenientes, Datas e Processos",
            "",
            f"**Data da Analise**: {report['timestamp']}",
            f"**Ficheiros Analisados no Desktop**: {report['total_files']}",
            f"**Relacoes Cruzadas Estabelecidas**: {report['total_relations']}",
            "",
            "## 1. Mapeamento por Interveniente Nuclear",
            "",
            "| Interveniente / Entidade | Ficheiros e Evidencias Associadas |",
            "|---|---|"
        ]

        for interv, files in interveniente_links.items():
            lines.append(f"| **{interv}** | `{len(files)} ficheiros vinculados` |")

        lines.extend([
            "",
            "## 2. Mapeamento por Processo Judicial",
            "",
            "| Processo Judicial | Ficheiros e Documentos |",
            "|---|---|"
        ])

        for proc, files in process_links.items():
            lines.append(f"| **`{proc}`** | `{len(files)} ficheiros vinculados` |")

        lines.extend([
            "",
            "## 3. Matriz de Relacionamentos Cruzados (Interveniente x Processo x Prova)",
            "",
            "| Interveniente | Processo | Ficheiro de Prova | SHA-256 |",
            "|---|---|---|---|"
        ])

        for rel in relationships[:30]:
            lines.append(f"| **{rel['interveniente']}** | `{rel['processo']}` | `{rel['evidence_file']}` | `{rel['sha256'][:16]}...` |")

        rep_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"[SUCESSO] Relatorio de Consolidacao gravado em: {rep_path}")
