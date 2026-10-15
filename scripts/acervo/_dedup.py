# -*- coding: utf-8 -*-
r"""
_dedup.py - Deduplicacao por varios criterios
==============================================
- Nome
- Nome + tamanho
- Tamanho
- Hash SHA-256 (leitura real)
- Duracao (audio/video)
"""
import os
import hashlib
from collections import defaultdict


def chave_nome(r):    return r["nome"].lower()
def chave_tamanho(r): return r["tamanho"]
def chave_nome_tam(r): return (r["nome"].lower(), r["tamanho"])
def chave_stem_tam_ext(r):
    return ((r.get("stem") or os.path.splitext(r["nome"])[0]).lower(),
            r["tamanho"],
            (r.get("ext") or "").lower())


def hash_ficheiro(caminho, bloco=65536):
    h = hashlib.sha256()
    try:
        with open(caminho, "rb") as f:
            h.update(f.read(bloco))
            try:
                f.seek(-bloco, 2)
                h.update(f.read(bloco))
            except OSError:
                pass
        return h.hexdigest()
    except (OSError, PermissionError):
        return None


def segregar(items, chave_fn=chave_stem_tam_ext):
    """Separa originais de duplicados por chave."""
    grupos = defaultdict(list)
    for r in items:
        grupos[chave_fn(r)].append(r)

    originais = []
    duplicados = []
    for chave, grupo in grupos.items():
        if len(grupo) == 1:
            originais.append(grupo[0])
            continue
        grupo.sort(key=lambda x: (
            x.get("rank", 3),
            x.get("prof", 0),
            x.get("caminho", ""),
            x.get("nome", "")
        ))
        o = grupo[0]
        o["grau"] = "ORIGINAL"
        o["score"] = 100
        originais.append(o)
        for d in grupo[1:]:
            d["grau"] = "DUPLICADO"
            d["score"] = 85
            duplicados.append(d)
    return originais, duplicados, len(grupos)


def dedup_por_hash(items, progress_cb=None):
    """
    Dedup por hash SHA-256. So calcula hash para ficheiros com
    mesmo tamanho (evita ler tudo). Muito mais lento que nome.
    """
    por_tamanho = defaultdict(list)
    for r in items:
        por_tamanho[r["tamanho"]].append(r)

    # So grupos com >1 elemento interessam
    grupos_hash = defaultdict(list)
    total_calc = sum(len(g) for g in por_tamanho.values() if len(g) > 1)
    contador = 0

    for tam, grupo in por_tamanho.items():
        if len(grupo) <= 1:
            continue
        for r in grupo:
            h = hash_ficheiro(r["caminho"])
            if h:
                r["hash"] = h
                grupos_hash[h].append(r)
            contador += 1
            if progress_cb:
                progress_cb(contador, total_calc)

    originais = []
    duplicados = []
    for h, grupo in grupos_hash.items():
        if len(grupo) == 1:
            originais.append(grupo[0])
            continue
        grupo.sort(key=lambda x: (x.get("rank", 3), x.get("caminho", "")))
        o = grupo[0]
        o["grau"] = "ORIGINAL"
        o["score"] = 100
        originais.append(o)
        for d in grupo[1:]:
            d["grau"] = "DUPLICADO"
            d["score"] = 100
            duplicados.append(d)

    return originais, duplicados, len(grupos_hash)
