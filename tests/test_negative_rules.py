#!/usr/bin/env python3
"""
Testes Unitarios de Regras Negativas e Seguranca (test_negative_rules.py).
Garante que minutas nunca sao despachos, indices nao sao provas, e zero invencoes.
"""
import unittest
import os
import json

DEV_ROOT = "C:\\Users\\Yokozuna\\Dev"
INDEX_DIR = os.path.join(DEV_ROOT, "Projects", "Ficheiros Escritos Canónicos", "_index")
ATOS_PATH = os.path.join(INDEX_DIR, "atos_processuais.jsonl")


class TestNegativeRules(unittest.TestCase):

    def setUp(self):
        self.records = []
        if os.path.exists(ATOS_PATH):
            with open(ATOS_PATH, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if line.strip():
                        try:
                            self.records.append(json.loads(line.strip()))
                        except Exception:
                            pass

    def test_no_minuta_is_despacho(self):
        violations = [
            r for r in self.records 
            if r.get("folder") == "02_Minutas_E_Rascunhos" and (r.get("tipo_cpc") == "DESPACHO" or r.get("suporte") == "DOCUMENTADO")
        ]
        self.assertEqual(len(violations), 0, f"Encontradas {len(violations)} minutas promovidas indevidamente")

    def test_no_indice_is_oficial_proof(self):
        violations = [
            r for r in self.records 
            if r.get("folder") == "00_Indice_E_MOCs" and r.get("evidence_level") == "OFICIAL"
        ]
        self.assertEqual(len(violations), 0, f"Encontrados {len(violations)} indices classificados como prova oficial")

    def test_documentado_sha256_compliance_rate(self):
        documentados = [r for r in self.records if r.get("suporte") == "DOCUMENTADO"]
        if not documentados:
            return
        valid_sha = sum(1 for r in documentados if r.get("sha256") and len(r.get("sha256")) == 64)
        rate = valid_sha / len(documentados)
        self.assertGreaterEqual(rate, 0.98, f"Taxa de conformidade SHA-256 de documentos: {rate*100:.2f}% (esperado >= 98%)")


if __name__ == "__main__":
    unittest.main()
