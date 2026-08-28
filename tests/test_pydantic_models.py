#!/usr/bin/env python3
"""
Testes Unitarios para Modelos Pydantic (test_pydantic_models.py).
Valida tipos, campos obrigatorios, restricoes de hash e validadores semanticos de models_org.py.
"""
import unittest
import os
import sys

DEV_ROOT = "C:\\Users\\Yokozuna\\Dev"
sys.path.insert(0, os.path.join(DEV_ROOT, "Backend", "pydantic-ai", "src"))

from pydantic import ValidationError
from models_org import CanonicalRecord, OrganizationReport, ItemTypeEnum, SupportLevelEnum, CanonicalCategoryEnum


class TestPydanticModels(unittest.TestCase):

    def test_canonical_record_valid(self):
        sample = {
            "file_path": "C:\\Users\\Yokozuna\\Dev\\Projects\\Ficheiros Escritos Canónicos\\01_PDFs_Oficiais\\doc1.pdf",
            "file_name": "doc1.pdf",
            "extension": ".pdf",
            "size_bytes": 1024,
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "item_type": ItemTypeEnum.FACTO,
            "support_level": SupportLevelEnum.DOCUMENTADO,
            "target_category": CanonicalCategoryEnum.PROCESSOS,
            "process_id": "3719/25.0T8LSB",
            "tags": ["processo", "oficial"]
        }
        rec = CanonicalRecord(**sample)
        self.assertEqual(rec.file_name, "doc1.pdf")
        self.assertEqual(rec.extension, ".pdf")
        self.assertEqual(len(rec.sha256), 64)

    def test_alegacao_cannot_be_documentado(self):
        sample = {
            "file_path": "C:\\Users\\Yokozuna\\Dev\\Projects\\minuta.md",
            "file_name": "minuta.md",
            "extension": ".md",
            "size_bytes": 500,
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "item_type": ItemTypeEnum.ALEGACAO,
            "support_level": SupportLevelEnum.DOCUMENTADO, # Violacao semantica!
            "target_category": CanonicalCategoryEnum.PROCESSOS
        }
        with self.assertRaises(ValidationError):
            CanonicalRecord(**sample)

    def test_facto_cannot_be_nao_indiciado(self):
        sample = {
            "file_path": "C:\\Users\\Yokozuna\\Dev\\Projects\\doc.pdf",
            "file_name": "doc.pdf",
            "extension": ".pdf",
            "size_bytes": 500,
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "item_type": ItemTypeEnum.FACTO,
            "support_level": SupportLevelEnum.NAO_INDICIADO, # Proibido para FACTO
            "target_category": CanonicalCategoryEnum.PROCESSOS
        }
        with self.assertRaises(ValidationError):
            CanonicalRecord(**sample)

    def test_invalid_sha256_format(self):
        sample = {
            "file_path": "C:\\Users\\Yokozuna\\Dev\\Projects\\doc.pdf",
            "file_name": "doc.pdf",
            "extension": ".pdf",
            "size_bytes": 500,
            "sha256": "invalid_hash_too_short",
            "item_type": ItemTypeEnum.FACTO,
            "support_level": SupportLevelEnum.DOCUMENTADO,
            "target_category": CanonicalCategoryEnum.PROCESSOS
        }
        with self.assertRaises(ValidationError):
            CanonicalRecord(**sample)


if __name__ == "__main__":
    unittest.main()
