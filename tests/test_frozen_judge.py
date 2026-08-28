#!/usr/bin/env python3
"""
Testes Unitarios para o Frozen Judge (test_frozen_judge.py).
Valida score 100/100, integridade da Regra 0, ordenacao cronologica e as 5 Clausulas Petreas.
"""
import unittest
import os
import sys
import json

DEV_ROOT = "C:\\Users\\Yokozuna\\Dev"
SKILLS_DIR = os.path.join(DEV_ROOT, "AI", "skills", "mcp-fs-pydantic-org", "scripts")
INDEX_DIR = os.path.join(DEV_ROOT, "Projects", "Ficheiros Escritos Canónicos", "_index")
sys.path.insert(0, SKILLS_DIR)

from frozen_judge import run_frozen_judge, FROZEN_CLAUSES


class TestFrozenJudge(unittest.TestCase):

    def test_frozen_clauses_definition(self):
        self.assertEqual(len(FROZEN_CLAUSES), 5)
        clause_ids = [c["id"] for c in FROZEN_CLAUSES]
        self.assertIn("CLAUSULA_1_INEXIGIBILIDADE", clause_ids)
        self.assertIn("CLAUSULA_2_NULIDADE_CITACAO", clause_ids)
        self.assertIn("CLAUSULA_3_PROPRIEDADE_LITISCONSORCIO", clause_ids)
        self.assertIn("CLAUSULA_4_TUTELA_CAUTELAR", clause_ids)
        self.assertIn("CLAUSULA_5_REGRA_0_CRIPTOGRAFICA", clause_ids)

    def test_frozen_judge_execution_score_100(self):
        report = run_frozen_judge(INDEX_DIR)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["frozen_judge_score"], 100)
        self.assertEqual(report["score_max"], 100)

    def test_audit_ledger_exists(self):
        ledger_path = os.path.join(INDEX_DIR, "audit_ledger.jsonl")
        self.assertTrue(os.path.exists(ledger_path))
        self.assertGreater(os.path.getsize(ledger_path), 0)


if __name__ == "__main__":
    unittest.main()
