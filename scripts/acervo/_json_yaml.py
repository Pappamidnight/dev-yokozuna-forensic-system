# -*- coding: utf-8 -*-
r"""
_json_yaml.py - Saidas estruturadas JSON + YAML
================================================
"""
import os
import json
from datetime import datetime


def exportar(items, base_path, formato="both", meta=None):
    """
    Grava items em JSON e/ou YAML.
    Retorna lista de ficheiros gravados.
    """
    os.makedirs(os.path.dirname(base_path), exist_ok=True)
    gravados = []
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    payload = {
        "data": datetime.now().isoformat(),
        "meta": meta or {},
        "total": len(items),
        "items": items,
    }

    if formato in ("json", "both"):
        p = f"{base_path}_{ts}.json"
        with open(p, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False, default=str)
        gravados.append(p)

    if formato in ("yaml", "both"):
        p = f"{base_path}_{ts}.yaml"
        try:
            import yaml
            with open(p, "w", encoding="utf-8") as f:
                yaml.safe_dump(payload, f, allow_unicode=True, sort_keys=False)
            gravados.append(p)
        except ImportError:
            # fallback simples
            with open(p, "w", encoding="utf-8") as f:
                f.write(f"# JSON (sem modulo yaml instalado)\n")
                f.write(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
            gravados.append(p)

    return gravados
