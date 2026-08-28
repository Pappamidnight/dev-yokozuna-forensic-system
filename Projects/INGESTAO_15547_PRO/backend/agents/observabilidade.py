from __future__ import annotations

import logging
from pathlib import Path


class ObservabilidadeAgent:
    def __init__(self, log_path: Path, error_log_path: Path | None = None) -> None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("ingestao_15547")
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()

        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        main_handler = logging.FileHandler(log_path, encoding="utf-8")
        main_handler.setLevel(logging.INFO)
        main_handler.setFormatter(formatter)
        self.logger.addHandler(main_handler)

        if error_log_path:
            error_log_path.parent.mkdir(parents=True, exist_ok=True)
            error_handler = logging.FileHandler(error_log_path, encoding="utf-8")
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            self.logger.addHandler(error_handler)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def error(self, message: str, exc_info: bool = False) -> None:
        self.logger.error(message, exc_info=exc_info)
