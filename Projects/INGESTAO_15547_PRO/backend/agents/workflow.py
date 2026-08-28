from __future__ import annotations

from pathlib import Path


class WorkflowAgent:
    """Garante estrutura esperada e politica RAW read-only."""

    REQUIRED_DIRS = [
        "raw",
        "outputs/jsonl",
        "outputs/markdown",
        "outputs/graph",
        "outputs/evals",
        "logs",
        "state",
        "gold_dataset",
        "evals",
        "graph",
        "quarantine",
        "runtime",
    ]

    def __init__(self, root: Path) -> None:
        self.root = root

    def prepare(self) -> list[str]:
        warnings: list[str] = []
        for directory in self.REQUIRED_DIRS:
            (self.root / directory).mkdir(parents=True, exist_ok=True)

        raw = self.root / "raw"
        if not any(raw.rglob("*")):
            warnings.append("raw/ esta vazio. Coloque fontes originais antes de esperar cronologia rica.")
        return warnings
