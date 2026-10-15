# -*- coding: utf-8 -*-
"""es.py - Wrapper es.exe"""
import subprocess, json, os

ES = r"C:\ACERVO\bin\es.exe"
INST = "1.5a"


def count(q):
    try:
        r = subprocess.run([ES, "-instance", INST, "-get-result-count", q],
                           capture_output=True, text=True, timeout=60)
        return int(r.stdout.strip().split()[0] or 0)
    except Exception:
        return 0


def size(q):
    try:
        r = subprocess.run([ES, "-instance", INST, "-get-total-size", q],
                           capture_output=True, text=True, timeout=60)
        return int(r.stdout.strip().split()[0] or 0)
    except Exception:
        return 0


def search(q, n=100):
    try:
        r = subprocess.run([ES, "-instance", INST, "-json", "-n", str(n), q],
                           capture_output=True, text=True, encoding="utf-8", timeout=180)
        return json.loads(r.stdout) if r.stdout.strip() else []
    except Exception:
        return []


def top(q, n=20):
    try:
        r = subprocess.run([ES, "-instance", INST, "-n", str(n), "-size", "-dm",
                            "-sort", "size-descending", q],
                           capture_output=True, text=True, encoding="utf-8", timeout=180)
        return [l for l in r.stdout.splitlines() if l.strip()]
    except Exception:
        return []


def efu(q, path):
    try:
        r = subprocess.run([ES, "-instance", INST, "-efu", q],
                           capture_output=True, text=True, encoding="utf-8", timeout=180)
        with open(path, "w", encoding="utf-8") as f:
            f.write(r.stdout)
        return True
    except Exception:
        return False
