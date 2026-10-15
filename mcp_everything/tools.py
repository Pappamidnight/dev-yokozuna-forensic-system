# -*- coding: utf-8 -*-
"""tools.py - Ferramentas expostas ao LLM"""
import os
import json
import time
from datetime import datetime

import es_client
from sdk_client import EverythingSDK


# Instância global do SDK
_sdk = None


def get_sdk():
    global _sdk
    if _sdk is None:
        _sdk = EverythingSDK()
    return _sdk


# ============================================================
# TOOLS
# ============================================================

def everything_search(query: str, limit: int = 100, source: str = "es") -> str:
    """
    Pesquisa ficheiros no Everything.
    
    Args:
        query: Sintaxe de pesquisa do Everything (ex: "ext:pdf size:>10mb")
        limit: Número máximo de resultados (default: 100)
        source: "es" (CLI), "sdk" (DLL), ou "http"
    
    Returns:
        JSON com os resultados.
    """
    limit = min(int(limit), 10000)
    if source == "sdk":
        sdk = get_sdk()
        res = sdk.search(query, limit)
    elif source == "http":
        import http_client
        res = http_client.search(query, limit)
    else:
        res = es_client.search(query, limit, json_output=True)

    return json.dumps({
        "query": query,
        "limit": limit,
        "source": source,
        "count": len(res) if isinstance(res, list) else 0,
        "results": res,
    }, ensure_ascii=False, default=str)


def everything_count(query: str) -> str:
    """
    Conta quantos ficheiros correspondem à query.
    
    Args:
        query: Sintaxe do Everything.
    
    Returns:
        JSON com a contagem.
    """
    n = es_client.count(query)
    return json.dumps({"query": query, "count": n})


def everything_size(query: str) -> str:
    """
    Tamanho total (bytes) dos ficheiros que correspondem à query.
    
    Args:
        query: Sintaxe do Everything.
    
    Returns:
        JSON com bytes, MB, GB.
    """
    b = es_client.size(query)
    return json.dumps({
        "query": query,
        "bytes": b,
        "mb": round(b / 1024 / 1024, 2),
        "gb": round(b / 1024 / 1024 / 1024, 2),
    })


def everything_top(query: str, n: int = 20) -> str:
    """
    Top N ficheiros maiores que correspondem à query.
    
    Args:
        query: Sintaxe do Everything.
        n: Número de resultados (default: 20).
    
    Returns:
        Lista de ficheiros por tamanho.
    """
    res = es_client.top(query, n)
    return json.dumps({
        "query": query,
        "n": n,
        "results": res,
    }, ensure_ascii=False)


def everything_dupes(query: str, limit: int = 100) -> str:
    """
    Encontra duplicados (dupe:) com filtro.
    
    Args:
        query: Base da query (ex: "ext:pdf").
        limit: Máximo de resultados.
    
    Returns:
        JSON com duplicados.
    """
    full = f"{query} dupe:name;size"
    res = es_client.search(full, limit)
    return json.dumps({
        "query": full,
        "count": len(res),
        "results": res,
    }, ensure_ascii=False, default=str)


def everything_ghosts() -> str:
    """
    Deteta ghost entries (ficheiros no índice mas não no disco).
    
    Returns:
        JSON com o número de ghosts.
    """
    n = es_client.count('!EXISTSONDISK($filename:)')
    return json.dumps({
        "query": "!EXISTSONDISK($filename:)",
        "ghosts": n,
    })


def everything_efu(query: str, output_path: str) -> str:
    """
    Exporta resultado como EFU (Everything File List).
    
    Args:
        query: Sintaxe do Everything.
        output_path: Caminho do ficheiro .efu.
    
    Returns:
        Confirmação.
    """
    try:
        conteudo = es_client.efu(query)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(conteudo)
        return json.dumps({
            "query": query,
            "output": output_path,
            "ok": True,
        })
    except Exception as e:
        return json.dumps({"ok": False, "error": str(e)})


def everything_version() -> str:
    """Versão do es.exe e do SDK."""
    sdk = get_sdk()
    return json.dumps({
        "es_exe": es_client.version(),
        "sdk_disponivel": sdk.disponivel,
    })


def filesystem_scan(path: str, depth: int = 1) -> str:
    """
    Scan rápido de uma pasta (contagem + tamanho).
    
    Args:
        path: Caminho da pasta.
        depth: Profundidade (default: 1).
    
    Returns:
        JSON com estatísticas.
    """
    if not os.path.isdir(path):
        return json.dumps({"error": f"Nao e pasta: {path}"})

    q = f'path:"{path}"'
    n = es_client.count(q)
    b = es_client.size(q)
    return json.dumps({
        "path": path,
        "files": n,
        "bytes": b,
        "gb": round(b / 1024 / 1024 / 1024, 2),
    })


# ============================================================
# REGISTO
# ============================================================
TOOLS = [
    everything_search,
    everything_count,
    everything_size,
    everything_top,
    everything_dupes,
    everything_ghosts,
    everything_efu,
    everything_version,
    filesystem_scan,
]
