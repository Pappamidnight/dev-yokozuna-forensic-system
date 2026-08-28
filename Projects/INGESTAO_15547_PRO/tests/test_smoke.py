import unittest
import sys
from pathlib import Path
from datetime import datetime, timezone

PROJ_ROOT = str(Path(__file__).resolve().parents[1])
if PROJ_ROOT not in sys.path:
    sys.path.insert(0, PROJ_ROOT)

from backend.extractors import extract_from_file
from backend.agents.frozen_judge import FrozenJudgeAgent
from backend.schemas.models import EvidenceFile


class TestSmoke(unittest.TestCase):

    def test_extract_chat_line(self):
        tmp_dir = Path(PROJ_ROOT) / "runtime" / "test_tmp"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        sample = tmp_dir / "whatsapp.txt"
        sample.write_text("23/08/2022, 08:30 - Filipe Delgado: Tens agua na Heaven?\n", encoding="utf-8")

        result = extract_from_file(sample, "EVD-15547-00001")

        self.assertGreaterEqual(len(result.claims), 1)
        self.assertEqual(result.claims[0].estado, "FACTO_DOCUMENTADO")
        self.assertEqual(result.timeline[0].data, "2022-08-23 08:30")

    def test_frozen_judge_rejects_empty_file(self):
        evidence = EvidenceFile(
            evidence_id="EVD-TEST-EMPTY",
            path="raw/empty.txt",
            filename="empty.txt",
            extension=".txt",
            size_bytes=0,
            sha256="0" * 64,
            modified_at=datetime.now(timezone.utc),
        )
        route = FrozenJudgeAgent().route_evidence(evidence)
        self.assertFalse(route.accepted)
        self.assertTrue(route.route.startswith("quarantine"))


if __name__ == "__main__":
    unittest.main()
