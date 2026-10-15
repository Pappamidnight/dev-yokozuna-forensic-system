# -*- coding: utf-8 -*-
r"""
_rename.py - Renomeacao em massa (dry-run por defeito)
=======================================================
Padroes suportados:
  {n}     -> numero sequencial
  {nome}  -> nome base original
  {ext}   -> extensao
  {ano}   -> ano do ficheiro (mtime)
  {mes}   -> mes (2 digitos)
  {dia}   -> dia (2 digitos)
  {hora}  -> hora (2 digitos)
  {min}   -> minuto (2 digitos)
  {seg}   -> segundo (2 digitos)
"""
import os
import re
import shutil
from datetime import datetime


def gerar_novo_nome(padrao, item, indice=0):
    caminho = item.get("caminho", "")
    nome = item.get("nome", "")
    stem, ext = os.path.splitext(nome)
    dt = item.get("dm")
    if not dt and os.path.isfile(caminho):
        try:
            dt = datetime.fromtimestamp(os.path.getmtime(caminho))
        except OSError:
            dt = None
    if not dt:
        dt = datetime.now()

    novo = padrao
    novo = novo.replace("{n}", f"{indice:04d}")
    novo = novo.replace("{nome}", stem)
    novo = novo.replace("{ext}", ext.lstrip("."))
    novo = novo.replace("{ano}", f"{dt.year:04d}")
    novo = novo.replace("{mes}", f"{dt.month:02d}")
    novo = novo.replace("{dia}", f"{dt.day:02d}")
    novo = novo.replace("{hora}", f"{dt.hour:02d}")
    novo = novo.replace("{min}", f"{dt.minute:02d}")
    novo = novo.replace("{seg}", f"{dt.second:02d}")

    # Se o padrao nao inclui extensao, adiciona
    if not os.path.splitext(novo)[1]:
        novo += ext
    return novo


def aplicar_regex_nome(nome, padrao, substituicao):
    return re.sub(padrao, substituicao, nome, flags=re.IGNORECASE)


def renomear_lote(items, padrao=None, regex_de=None, regex_para=None,
                  dry_run=True, progress_cb=None):
    """
    items: lista de dicts com 'caminho'
    padrao: template (ex: "{ano}-{mes}-{dia}_{nome}")
    regex_de + regex_para: substituicao direta por regex
    dry_run: se True, nao renomeia
    """
    renomeados = []
    falhas = []
    for i, item in enumerate(items, 1):
        caminho = item.get("caminho")
        if not caminho or not os.path.isfile(caminho):
            falhas.append((caminho, "inexistente"))
            continue

        pasta = os.path.dirname(caminho)
        nome_antigo = os.path.basename(caminho)

        if regex_de and regex_para:
            nome_novo = aplicar_regex_nome(nome_antigo, regex_de, regex_para)
        elif padrao:
            nome_novo = gerar_novo_nome(padrao, item, i)
        else:
            continue

        if nome_novo == nome_antigo:
            if progress_cb: progress_cb(i, len(items))
            continue

        novo_caminho = os.path.join(pasta, nome_novo)

        # Evitar overwrite
        if os.path.exists(novo_caminho) and not dry_run:
            base, ext = os.path.splitext(novo_caminho)
            novo_caminho = f"{base}_{i:04d}{ext}"

        if dry_run:
            renomeados.append({"antigo": caminho, "novo": novo_caminho,
                               "dry_run": True})
        else:
            try:
                shutil.move(caminho, novo_caminho)
                renomeados.append({"antigo": caminho, "novo": novo_caminho})
            except (OSError, PermissionError, shutil.Error) as e:
                falhas.append((caminho, str(e)))

        if progress_cb:
            progress_cb(i, len(items))

    return renomeados, falhas
