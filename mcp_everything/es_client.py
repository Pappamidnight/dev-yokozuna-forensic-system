# -*- coding: utf-8 -*-
"""es_client.py - Cliente es.exe (CLI do Everything)"""
import subprocess
import json
import os
from typing import Optional

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

ES = CONFIG["es_exe"]
INST = CONFIG["instance"]
TIMEOUT = CONFIG["timeout_seconds"]


def _run(args: list, timeout: int = None) -> str:
    """Executa es.exe e devolve stdout."""
    cmd = [ES, "-instance", INST] + args
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout or TIMEOUT,
        )
        return r.stdout
    except subprocess.TimeoutExpired:
        return ""
    except Exception as e:
        return f"ERRO: {e}"


def count(query: str) -> int:
    """Contagem de ficheiros que correspondem à query."""
    out = _run(["-get-result-count", query])
    try:
        return int(out.strip().split()[0])
    except (ValueError, IndexError):
        return 0


def size(query: str) -> int:
    """Tamanho total em bytes."""
    out = _run(["-get-total-size", query])
    try:
        val = int(out.strip().split()[0])
        if val >= 2**53:
            return 0
        return val
    except (ValueError, IndexError):
        return 0


def search(query: str, limit: int = 100, json_output: bool = True) -> list:
    """Pesquisa ficheiros."""
    args = ["-n", str(limit)]
    if json_output:
        args.append("-json")
    args.append(query)
    out = _run(args)
    if not out.strip():
        return []
    if json_output:
        try:
            data = json.loads(out)
            return data if isinstance(data, list) else [data]
        except json.JSONDecodeError:
            return []
    return [l for l in out.splitlines() if l.strip()]


def top(query: str, n: int = 20) -> list:
    """Top N por tamanho."""
    out = _run([
        "-n", str(n),
        "-size", "-dm",
        "-sort", "size-descending",
        query
    ])
    return [l for l in out.splitlines() if l.strip()]


def efu(query: str) -> str:
    """Exporta como EFU."""
    return _run(["-efu", query])


def version() -> str:
    """Versão do es.exe."""
    return _run(["-version"]).strip()
