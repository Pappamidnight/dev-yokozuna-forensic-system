from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.agents.frozen_judge import FrozenJudgeAgent
from backend.schemas.models import EvidenceFile


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    gold_path = root / "gold_dataset" / "frozen_judge_gold.jsonl"
    judge = FrozenJudgeAgent()
    failures: list[str] = []
    total = 0

    for line in gold_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        total += 1
        row = json.loads(line)
        evidence = EvidenceFile(
            evidence_id=row["case_id"],
            path=str(root / "gold_dataset" / row["filename"]),
            filename=row["filename"],
            extension=row["extension"],
            size_bytes=row["size_bytes"],
            sha256="0" * 64,
            modified_at=datetime.now(timezone.utc),
        )
        decision = judge.route_evidence(evidence)
        if decision.route != row["expected_route"] or decision.accepted != row["expected_accepted"]:
            failures.append(
                f"{row['case_id']}: esperado {row['expected_route']}/{row['expected_accepted']}, "
                f"recebido {decision.route}/{decision.accepted}"
            )

    result = {"eval_id": "EVAL-FROZEN-JUDGE-GOLD-FILE", "passed": not failures, "total": total, "failures": failures}
    out = root / "outputs" / "evals" / "gold_dataset_eval.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
