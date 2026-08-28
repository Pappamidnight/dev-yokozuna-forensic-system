#!/usr/bin/env python3
"""
Testes Unitarios para o Eval Pipeline (test_eval_pipeline.py).
Valida comparacao contra o Golden Dataset e cumprimento dos thresholds de qualidade.
"""
import unittest
import os
import sys

DEV_ROOT = "C:\\Users\\Yokozuna\\Dev"
SKILLS_DIR = os.path.join(DEV_ROOT, "AI", "skills", "mcp-fs-pydantic-org", "scripts")
sys.path.insert(0, SKILLS_DIR)

from eval_pipeline import run_evaluation


class TestEvalPipeline(unittest.TestCase):

    def test_eval_pipeline_pass(self):
        report = run_evaluation()
        self.assertEqual(report["status"], "PASS")
        metrics = report.get("metrics", {})
        self.assertGreaterEqual(metrics.get("f1_score", 0), 0.92)
        self.assertGreaterEqual(metrics.get("precision", 0), 0.95)
        self.assertGreaterEqual(metrics.get("recall", 0), 0.90)
        self.assertEqual(metrics.get("pydantic_validity_rate", 0), 1.00)
        self.assertEqual(report.get("negative_rule_violations_count", 1), 0)


if __name__ == "__main__":
    unittest.main()
