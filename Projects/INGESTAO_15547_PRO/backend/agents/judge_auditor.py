from __future__ import annotations

from backend.agents.frozen_judge import FrozenJudgeAgent
from backend.schemas.models import EvalResult, EvidenceFile


class JudgeAuditorAgent:
    """Confirma que o Frozen Judge mantem qualidade contra casos dourados."""

    def __init__(self, judge: FrozenJudgeAgent) -> None:
        self.judge = judge

    def run_gold_checks(self, gold_evidences: list[EvidenceFile]) -> EvalResult:
        failures: list[str] = []
        for evidence in gold_evidences:
            decision = self.judge.route_evidence(evidence)
            if evidence.extension.lower() in FrozenJudgeAgent.SUPPORTED_TEXT_EXTENSIONS and not decision.accepted:
                failures.append(f"{evidence.evidence_id}: texto suportado foi rejeitado")
            if evidence.size_bytes <= 0 and decision.accepted:
                failures.append(f"{evidence.evidence_id}: ficheiro vazio foi aceite")

        return EvalResult(
            eval_id="EVAL-FROZEN-JUDGE-GOLD-001",
            passed=not failures,
            total=len(gold_evidences),
            failures=failures,
        )
