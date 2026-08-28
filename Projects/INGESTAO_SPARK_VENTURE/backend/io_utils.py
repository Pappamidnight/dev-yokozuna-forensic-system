from __future__ import annotations

import os
import hashlib
import json
from pathlib import Path
from typing import Iterable, Any


def make_long_path(path_str: str) -> str:
    abs_str = os.path.abspath(path_str)
    if abs_str.startswith("\\\\?\\"):
        return abs_str
    if abs_str.startswith("\\\\"):
        return "\\\\?\\UNC\\" + abs_str[2:]
    return "\\\\?\\" + abs_str


def sha256_file(filepath: Path | str, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    lp = make_long_path(str(filepath))
    try:
        with open(lp, "rb") as handle:
            while chunk := handle.read(chunk_size):
                digest.update(chunk)
        return digest.hexdigest()
    except Exception:
        return "0" * 64


def read_text_lossy(filepath: Path | str, max_chars: int = 2_000_000) -> str:
    lp = make_long_path(str(filepath))
    try:
        with open(lp, "rb") as handle:
            data = handle.read(max_chars)
        for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue
        return data.decode("utf-8", errors="replace")
    except Exception:
        return ""


def write_jsonl(path: Path, rows: Iterable[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            if hasattr(row, "model_dump"):
                payload = row.model_dump(mode="json")
            else:
                payload = row
            handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = obj.model_dump(mode="json") if hasattr(obj, "model_dump") else obj
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
