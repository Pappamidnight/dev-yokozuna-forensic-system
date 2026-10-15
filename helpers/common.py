import os
import sys
import json
import hashlib
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Any, Optional

HTTP_EVERYTHING_URL = "http://127.0.0.1:8080/"

def everything_http_search(query: str, limit: int = 100, sort: str = "date_modified", ascending: int = 0) -> List[Dict[str, Any]]:
    """Pesquisa arquivos no Everything 1.5 via API REST HTTP (Porta 8080) com fallback resiliente para varredura local."""
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
    url = f"{HTTP_EVERYTHING_URL}?{urllib.parse.urlencode(params)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AGY-Forensic-Helper/8.0"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = []
            for item in data.get("results", []):
                p_dir = item.get("path", "")
                name = item.get("name", "")
                caminho = str(Path(p_dir) / name)
                results.append({
                    "caminho": caminho,
                    "nome": name,
                    "tamanho": item.get("size", 0),
                    "data_modificacao": item.get("date_modified", "")
                })
            return results
    except Exception:
        # Fallback resiliente: pesquisa local direta na pasta do Acervo
        results = []
        termos = [t.strip(' "\'<>') for t in query.split() if len(t.strip(' "\'<>')) >= 3 and not t.startswith("ext:")]
        base = Path(r"C:\ACERVO")
        for termo in termos[:2]:
            for p in base.glob(f"**/*{termo}*"):
                if p.is_file():
                    try:
                        results.append({
                            "caminho": str(p),
                            "nome": p.name,
                            "tamanho": p.stat().st_size,
                            "data_modificacao": ""
                        })
                    except OSError:
                        continue
                if len(results) >= limit:
                    break
        return results

def everything_http_count(query: str) -> int:
    """Retorna a contagem exata de ficheiros para uma query Everything."""
    params = {"search": query, "json": "1", "count": "1"}
    url = f"{HTTP_EVERYTHING_URL}?{urllib.parse.urlencode(params)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AGY-Forensic-Helper/8.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return int(data.get("totalResults", 0))
    except Exception:
        return 0

def calcular_sha256_custodia(caminho: Path) -> Optional[str]:
    """Calcula hash SHA-256 com protecao resiliente P-03 (try...except OSError)."""
    try:
        h = hashlib.sha256()
        with open(caminho, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None

def extrair_texto_ficheiro(caminho: Path) -> str:
    """Extrai texto de ficheiro (Markdown, TXT, JSON, CSV) com encoding UTF-8 explícito."""
    try:
        return caminho.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""

def executar_comando_wsl(comando: str, distro: str = "Ubuntu-26.04", password: str = "y") -> Dict[str, Any]:
    """Executa utilitario forense no WSL2 com suporte a elevacao."""
    cmd_completo = f"wsl -d {distro} -- bash -c \"echo '{password}' | sudo -S {comando}\""
    try:
        res = subprocess.run(cmd_completo, shell=True, capture_output=True, text=True, timeout=30)
        return {
            "codigo": res.returncode,
            "stdout": res.stdout.strip(),
            "stderr": res.stderr.strip()
        }
    except Exception as e:
        return {"codigo": -1, "stdout": "", "stderr": str(e)}
