#!/usr/bin/env python3
"""
Executor Geral da Suite de Testes Forenses (run_all_tests.py).
Executa todos os modulos de teste em unittest e exibe o sumario consolidado.
"""
import unittest
import sys
import os

DEV_ROOT = "C:\\Users\\Yokozuna\\Dev"
TESTS_DIR = os.path.join(DEV_ROOT, "tests")
sys.path.insert(0, TESTS_DIR)


def run_all():
    print("==================================================================")
    print("INICIANDO SUITE DE TESTES FORENSES DETERMINISTICOS (DEV YOKOZUNA)")
    print(f"Diretorio de Testes: {TESTS_DIR}")
    print("==================================================================")

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=TESTS_DIR, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n------------------------------------------------------------------")
    print(f"RESUMO DOS TESTES: {'PASS' if result.wasSuccessful() else 'FAIL'}")
    print(f" - Testes Executados : {result.testsRun}")
    print(f" - Falhas            : {len(result.failures)}")
    print(f" - Erros             : {len(result.errors)}")
    print("------------------------------------------------------------------\n")

    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    run_all()
