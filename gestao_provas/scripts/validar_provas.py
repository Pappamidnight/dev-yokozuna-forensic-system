# -*- coding: utf-8 -*-
"""validar_provas.py - Valida YAML contra schema"""
import os, sys, json
try:
    import yaml
except ImportError:
    print("[ERRO] pip install pyyaml")
    sys.exit(1)

try:
    import jsonschema
except ImportError:
    print("[AVISO] pip install jsonschema (opcional)")
    jsonschema = None

GESTAO = r"C:\ACERVO\gestao_provas"
SCHEMA = os.path.join(GESTAO, "schemas", "prova_schema.json")
PROVAS = os.path.join(GESTAO, "provas")

with open(SCHEMA, "r", encoding="utf-8") as f:
    schema = json.load(f)

def validar():
    if not os.path.isdir(PROVAS):
        print("[ERRO] Pasta de provas nao existe:", PROVAS)
        return
    total, ok, fail = 0, 0, 0
    for f in sorted(os.listdir(PROVAS)):
        if not f.endswith((".yaml", ".yml")):
            continue
        total += 1
        path = os.path.join(PROVAS, f)
        try:
            with open(path, "r", encoding="utf-8") as fp:
                dados = yaml.safe_load(fp)
            if jsonschema:
                jsonschema.validate(dados, schema)
            print(f"  [OK] {f}")
            ok += 1
        except Exception as e:
            print(f"  [FAIL] {f}: {e}")
            fail += 1
    print()
    print(f"  Total: {total}  |  OK: {ok}  |  FAIL: {fail}")

if __name__ == "__main__":
    validar()
