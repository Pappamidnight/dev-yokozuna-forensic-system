# -*- coding: utf-8 -*-
"""http_client.py - Cliente HTTP Server do Everything"""
import os
import json
import urllib.request
import urllib.parse

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

HTTP_BASE = CONFIG["http_server"]


def search(query: str, limit: int = 100, sort: str = "size",
           ascending: int = 0) -> dict:
    """Pesquisa via HTTP Server."""
    params = {
        "search": query,
        "json": "1",
        "count": str(limit),
        "sort": sort,
        "ascending": str(ascending),
        "path_column": "1",
        "size_column": "1",
        "date_modified_column": "1",
    }
    url = HTTP_BASE + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def count(query: str) -> int:
    """Contagem via HTTP."""
    params = {"search": query, "json": "1", "count": "1"}
    url = HTTP_BASE + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))
            return data.get("totalResults", 0)
    except Exception:
        return 0
