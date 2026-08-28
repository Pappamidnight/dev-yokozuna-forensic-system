import unittest
import sys
from pathlib import Path

PROJ_ROOT = str(Path(__file__).resolve().parents[1])
if PROJ_ROOT not in sys.path:
    sys.path.insert(0, PROJ_ROOT)

from backend.classifier import HeuristicCorporateClassifier, CORPORATE_DICTIONARY
from backend.schemas.corporate_models import CorporateEntity, CorporateTypeEnum


class TestCorporateClassifier(unittest.TestCase):

    def setUp(self):
        self.classifier = HeuristicCorporateClassifier()

    def test_classify_spark_celtis(self):
        filename = "SPARK_CELTIS_VENTURE_PARTNERS_SOCIEDADE_DE_CAPITAL_DE_RISCO_S_A_6.md"
        content = "Registo oficial na CMVM de Sociedade de Capital de Risco Spark Celtis."
        entity_id, c_type, score, kws = self.classifier.classify_text(filename, content)

        self.assertEqual(entity_id, "SPARK_CELTIS_VENTURE_PARTNERS")
        self.assertEqual(c_type, CorporateTypeEnum.SOCIEDADE_CAPITAL_RISCO)
        self.assertGreater(score, 0.5)

    def test_classify_container_fund(self):
        filename = "SPARK_CONTAINER_FUND_CMVM.md"
        content = "Fundo de Capital de Risco Fechado submetido a regulacao da CMVM."
        entity_id, c_type, score, kws = self.classifier.classify_text(filename, content)

        self.assertEqual(entity_id, "SPARK_CONTAINER_FUND_CMVM")
        self.assertEqual(c_type, CorporateTypeEnum.FUNDO_CMVM)

    def test_entity_model_validation(self):
        ent = self.classifier.build_entity_model("SPARK_CELTIS_VENTURE_PARTNERS", evidence_count=5)
        self.assertEqual(ent.name, CORPORATE_DICTIONARY["SPARK_CELTIS_VENTURE_PARTNERS"]["name"])
        self.assertEqual(ent.registro_cmvm, "CMVM-SCR-7241")
        self.assertEqual(ent.evidence_count, 5)


if __name__ == "__main__":
    unittest.main()
