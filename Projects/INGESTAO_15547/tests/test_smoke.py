from pathlib import Path

from backend.extractors import extract_from_file
from backend.agents.frozen_judge import FrozenJudgeAgent
from backend.schemas.models import EvidenceFile
from datetime import datetime, timezone


def test_extract_chat_line(tmp_path: Path) -> None:
    sample = tmp_path / "whatsapp.txt"
    sample.write_text("23/08/2022, 08:30 - Filipe Delgado: Tens agua na Heaven?\n", encoding="utf-8")

    result = extract_from_file(sample, "EVD-15547-00001")

    assert len(result.claims) == 1
    assert result.claims[0].estado == "FACTO_DOCUMENTADO"
    assert result.timeline[0].data == "2022-08-23 08:30"


def test_frozen_judge_rejects_empty_file() -> None:
    evidence = EvidenceFile(
        evidence_id="EVD-TEST-EMPTY",
        path="raw/empty.txt",
        filename="empty.txt",
        extension=".txt",
        size_bytes=0,
        sha256="0" * 64,
        modified_at=datetime.now(timezone.utc),
    )

    decision = FrozenJudgeAgent().route_evidence(evidence)

    assert decision.accepted is False
    assert decision.route == "quarantine/empty_file"
