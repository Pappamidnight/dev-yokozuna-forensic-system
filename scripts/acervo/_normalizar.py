# -*- coding: utf-8 -*-
r"""
_normalizar.py - Normalizacao de nomes de ficheiros
====================================================
Operacoes:
- lowercase / uppercase
- remover acentos
- substituir espacos por underscore
- colapsar multiplos espacos
- remover caracteres invalidos
- normalizar separadores
"""
import os
import re
import unicodedata

INVALIDOS_WIN = r'[<>:"/\\|?*\x00-\x1f]'


def remover_acentos(texto):
    if not texto:
        return texto
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def limpar_nome(nome, lower=True, sem_acentos=True, espaco="_",
                colapsar=True, remover_invalidos=True):
    base, ext = os.path.splitext(nome)
    if sem_acentos:
        base = remover_acentos(base)
    if lower:
        base = base.lower()
    if espaco:
        base = base.replace(" ", espaco)
        base = base.replace("-", espaco)
    if colapsar:
        base = re.sub(re.escape(espaco) + r"+", espaco, base) if espaco else base
        base = re.sub(r"_+", "_", base)
        base = base.strip("_")
    if remover_invalidos:
        base = re.sub(INVALIDOS_WIN, "_", base)
        base = re.sub(r"__+", "_", base)
    return base + ext.lower()


def normalizar_item(item, **kwargs):
    item = dict(item)
    if "nome" in item:
        item["nome"] = limpar_nome(item["nome"], **kwargs)
    return item


def normalizar_lote(items, **kwargs):
    return [normalizar_item(i, **kwargs) for i in items]
