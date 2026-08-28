from __future__ import annotations

import os
import sys
from pathlib import Path

PROJ_ROOT = Path(__file__).resolve().parent
if str(PROJ_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJ_ROOT))

from backend.desktop_cleaner_agent import DesktopConsolidationAgent


def main():
    agent = DesktopConsolidationAgent()
    report = agent.run_hygiene_and_consolidation()

    print("\n------------------------------------------------------------------")
    print("CONSOLIDACAO E HIGIENIZACAO DO DESKTOP CONCLUIDA:")
    print(f" - Ficheiros Analisados : {report['total_files']}")
    print(f" - Relacoes Cruzadas    : {report['total_relations']}")
    print(f" - Datas Identificadas  : {report['total_dates_mapped']}")
    print("------------------------------------------------------------------\n")


if __name__ == "__main__":
    main()
