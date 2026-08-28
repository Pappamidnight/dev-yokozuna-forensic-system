#!/usr/bin/env python3
"""
Testes Unitarios para o Workflow Controller (test_workflow_controller.py).
Valida presenca e integridade dos 8 entregaveis obrigatorios e status APPROVED.
"""
import unittest
import os
import sys

DEV_ROOT = "C:\\Users\\Yokozuna\\Dev"
SKILLS_DIR = os.path.join(DEV_ROOT, "AI", "skills", "mcp-fs-pydantic-org", "scripts")
sys.path.insert(0, SKILLS_DIR)

from workflow_controller import verify_workflow_outputs


class TestWorkflowController(unittest.TestCase):

    def test_workflow_controller_approved(self):
        report = verify_workflow_outputs()
        self.assertEqual(report["status"], "APPROVED")
        self.assertEqual(report["total_deliverables_present"], report["total_deliverables_required"])
        self.assertEqual(report["frozen_judge_score"], 100)
        self.assertEqual(report["eval_pipeline_status"], "PASS")


if __name__ == "__main__":
    unittest.main()
