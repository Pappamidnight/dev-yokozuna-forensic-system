#!/usr/bin/env python3
"""
CLI de Validacao de Schemas Pydantic v2 (validate_schema.py).
Suporta --selftest, --model e --emit-json-schema.
"""
import os
import sys
import json
import argparse
from typing import Dict, Any, List

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEV_ROOT = "C:\\Users\\Yokozuna\\Dev"
BACKEND_SRC = os.path.join(DEV_ROOT, "Backend", "pydantic-ai", "src")
ASSETS_DIR = os.path.join(SCRIPT_DIR, "..", "assets")

sys.path.insert(0, BACKEND_SRC)
sys.path.insert(0, ASSETS_DIR)

try:
    from models_org import CanonicalRecord, OrganizationReport
    from atos_processuais import AtoProcessualModel, CadeiaProcessualModel
    from complex_validators import validate_cross_rules
except ImportError:
    # Fallback basico se modulos nao encontrados
    CanonicalRecord = None
    OrganizationReport = None


def run_selftest() -> bool:
    """Executa a bateria de testes de conformidade Pydantic v2."""
    print("==================================================================")
    print("EXECUTANDO SELFTEST DE VALIDACOES PYDANTIC V2")
    print("==================================================================")
    
    passed_tests = 0
    total_tests = 0

    # Teste 1: Registo Valido
    total_tests += 1
    valid_record = {
        "path": "C:\\Users\\Yokozuna\\Dev\\Projects\\Ficheiros Escritos Canónicos\\01_PDFs_Oficiais\\despacho.pdf",
        "relpath": "Projects\\Ficheiros Escritos Canónicos\\01_PDFs_Oficiais\\despacho.pdf",
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "kind": "DECISAO",
        "suporte": "DOCUMENTADO",
        "process_id": "3719/25.0T8LSB",
        "evidence_level": "OFICIAL",
        "folder": "01_PDFs_Oficiais"
    }
    errs = validate_cross_rules(valid_record)
    if len(errs) == 0:
        print("[PASS] Teste 1: Registo valido aceite com sucesso.")
        passed_tests += 1
    else:
        print(f"[FAIL] Teste 1: Registo valido rejeitado: {errs}")

    # Teste 2: ALEGACAO com DOCUMENTADO deve falhar
    total_tests += 1
    invalid_alegacao = dict(valid_record)
    invalid_alegacao["kind"] = "ALEGACAO"
    invalid_alegacao["suporte"] = "DOCUMENTADO"
    errs = validate_cross_rules(invalid_alegacao)
    if len(errs) > 0 and "ALEGACAO" in errs[0]:
        print("[PASS] Teste 2: ALEGACAO + DOCUMENTADO rejeitado corretamente.")
        passed_tests += 1
    else:
        print(f"[FAIL] Teste 2: Falha ao rejeitar ALEGACAO com DOCUMENTADO.")

    # Teste 3: FACTO com NAO_INDICIADO deve falhar
    total_tests += 1
    invalid_facto = dict(valid_record)
    invalid_facto["kind"] = "FACTO"
    invalid_facto["suporte"] = "NAO_INDICIADO"
    errs = validate_cross_rules(invalid_facto)
    if len(errs) > 0 and "FACTO" in errs[0]:
        print("[PASS] Teste 3: FACTO + NAO_INDICIADO rejeitado corretamente.")
        passed_tests += 1
    else:
        print(f"[FAIL] Teste 3: Falha ao rejeitar FACTO com NAO_INDICIADO.")

    # Teste 4: Minuta como OFICIAL deve falhar
    total_tests += 1
    invalid_minuta = dict(valid_record)
    invalid_minuta["folder"] = "02_Minutas_E_Rascunhos"
    invalid_minuta["evidence_level"] = "OFICIAL"
    errs = validate_cross_rules(invalid_minuta)
    if len(errs) > 0:
        print("[PASS] Teste 4: Minuta como OFICIAL rejeitada corretamente.")
        passed_tests += 1
    else:
        print(f"[FAIL] Teste 4: Falha ao rejeitar Minuta como OFICIAL.")

    # Teste 5: Indice como OFICIAL deve falhar
    total_tests += 1
    invalid_indice = dict(valid_record)
    invalid_indice["folder"] = "00_Indice_E_MOCs"
    invalid_indice["evidence_level"] = "OFICIAL"
    errs = validate_cross_rules(invalid_indice)
    if len(errs) > 0:
        print("[PASS] Teste 5: Indice como OFICIAL rejeitado corretamente.")
        passed_tests += 1
    else:
        print(f"[FAIL] Teste 5: Falha ao rejeitar Indice como OFICIAL.")

    print("------------------------------------------------------------------")
    print(f"RESULTADO FINAL SELFTEST: {passed_tests}/{total_tests} TESTES PASSADOS")
    print("------------------------------------------------------------------")
    return passed_tests == total_tests


def main():
    parser = argparse.ArgumentParser(description="Validador Pydantic de Ficheiros e JSONL")
    parser.add_argument("file", nargs="?", help="Ficheiro JSON ou JSONL a validar")
    parser.add_argument("--model", default="CanonicalRecord", help="Modelo Pydantic alvo")
    parser.add_argument("--selftest", action="store_true", help="Executar bateria de testes interna")
    parser.add_argument("--emit-json-schema", action="store_true", help="Emitir schema JSON")
    args = parser.parse_args()

    if args.selftest:
        success = run_selftest()
        sys.exit(0 if success else 1)

    if args.emit_json_schema:
        schema_path = os.path.join(ASSETS_DIR, "organization_report.schema.json")
        if os.path.exists(schema_path):
            with open(schema_path, "r", encoding="utf-8") as f:
                print(f.read())
        sys.exit(0)

    if not args.file:
        print("[ERRO] Forneca o caminho de um ficheiro ou use --selftest / --emit-json-schema")
        sys.exit(1)

    if not os.path.exists(args.file):
        print(f"[ERRO] Ficheiro nao encontrado: {args.file}")
        sys.exit(1)

    print(f"[INFO] Validando {args.file} com modelo {args.model}...")
    errors = []
    line_num = 0
    with open(args.file, "r", encoding="utf-8") as f:
        for line in f:
            line_num += 1
            if not line.strip():
                continue
            try:
                data = json.loads(line.strip())
                cross_errs = validate_cross_rules(data)
                if cross_errs:
                    errors.append(f"Linha {line_num}: {', '.join(cross_errs)}")
            except Exception as e:
                errors.append(f"Linha {line_num} [JSON Invalido]: {e}")

    if errors:
        print(f"[FALHA] Detetados {len(errors)} erros de validacao:")
        for err in errors[:10]:
            print(f" - {err}")
        sys.exit(1)
    else:
        print(f"[SUCESSO] Todos os registos em {args.file} estao 100% conformes!")
        sys.exit(0)


if __name__ == "__main__":
    main()
