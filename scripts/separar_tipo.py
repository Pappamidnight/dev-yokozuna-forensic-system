#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
separar_tipo.py (Versao V8)
Processamento Atomico e Bloqueio Automatico de Progressao.
1 CSV = 1 Tipo = 1 Relatorio JSON = 1 Validacao = 1 Decisao.
Se estado == 'FALHA' -> STOP Imediato (sys.exit(1)).
"""

import csv
import sys
import json
import time
from pathlib import Path
from collections import defaultdict
from datetime import datetime

ROOT = Path(r"C:\ACERVO\logs\csv")
OUT_BASE = Path(r"C:\ACERVO\logs\deduplicado")
OUT_BASE.mkdir(parents=True, exist_ok=True)

CABECALHOS_OBRIGATORIOS = ["Nome", "Caminho", "Tamanho", "DataMod"]

PRIORIDADE = [
    "ACERVO_CONSOLIDADO",
    "VAULT",
    "Dossiers_Master",
    "01_WORK",
    "Dev",
    "LEGACY_COOKBOOK",
    "LEGACY_ARQUIVO_HISTORICO"
]

def rank(path):
    p = (path or "").upper()
    for i, v in enumerate(PRIORIDADE):
        if v.upper() in p:
            return i
    return 999

def formatar_duracao(segundos):
    m, s = divmod(int(segundos), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def processar_tipo(tipo):
    data_inicio = datetime.now()
    t0 = time.time()

    # Localizar ficheiro de entrada
    csvs = list(ROOT.glob(f"duplicados_{tipo}_*.csv")) or list(ROOT.glob(f"duplicados_{tipo}.csv"))
    if not csvs:
        print(f"[ERRO] Nenhum CSV encontrado para o tipo '{tipo}' em {ROOT}")
        sys.exit(1)

    csvfile = sorted(csvs)[-1]
    pasta_out = OUT_BASE / tipo
    pasta_out.mkdir(parents=True, exist_ok=True)

    orig_path = pasta_out / f"originais_{tipo}.csv"
    dup_path = pasta_out / f"duplicados_{tipo}.csv"
    resumo_path = pasta_out / f"resumo_{tipo}.json"

    print("=" * 70)
    print(f"  ACERVO V8 - EXECUCAO ATOMICA: [{tipo.upper()}]")
    print(f"  Ficheiro de Entrada: {csvfile.name}")
    print("=" * 70)

    grupos = defaultdict(list)
    total_candidatos = 0
    erros_resiliencia = 0
    validacao_csv = False

    # Leitura e parsing estrito
    with open(csvfile, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        
        # Validar cabecalhos obrigatorios
        if all(col in fieldnames for col in CABECALHOS_OBRIGATORIOS):
            validacao_csv = True

        for row in reader:
            total_candidatos += 1
            nome = (row.get("Nome") or "").strip()
            tam = (row.get("Tamanho") or "").strip()
            caminho = (row.get("Caminho") or "").strip()

            if not nome or not caminho:
                erros_resiliencia += 1
                continue

            grupos[(nome, tam)].append(row)

    originais_eleitos = 0
    duplicados_marcados = 0

    # Escrita dos ficheiros segregados
    with open(orig_path, "w", newline="", encoding="utf-8") as fo, \
         open(dup_path, "w", newline="", encoding="utf-8") as fd:

        w_orig = csv.DictWriter(fo, fieldnames=CABECALHOS_OBRIGATORIOS)
        w_orig.writeheader()

        w_dup = csv.DictWriter(fd, fieldnames=CABECALHOS_OBRIGATORIOS)
        w_dup.writeheader()

        for grupo in grupos.values():
            # Ordenar por prioridade de precedencia
            grupo.sort(key=lambda r: rank(r.get("Caminho", "")))

            # O primeiro e obrigatoriamente eleito original
            w_orig.writerow({k: grupo[0].get(k, "") for k in CABECALHOS_OBRIGATORIOS})
            originais_eleitos += 1

            # Os restantes sao classificados como duplicados
            for dup in grupo[1:]:
                w_dup.writerow({k: dup.get(k, "") for k in CABECALHOS_OBRIGATORIOS})
                duplicados_marcados += 1

    t1 = time.time()
    data_fim = datetime.now()
    duracao_segundos = round(t1 - t0, 3)

    # Calculo das regras matematicas estritas
    ficheiros_processados = originais_eleitos + duplicados_marcados + erros_resiliencia
    diferenca = total_candidatos - ficheiros_processados
    grupos_totais = len(grupos)

    validacao_contagem = (diferenca == 0)
    validacao_grupos = (grupos_totais == originais_eleitos)

    # Regras de estado
    if (diferenca == 0 and 
        originais_eleitos > 0 and 
        duplicados_marcados > 0 and 
        validacao_csv and 
        validacao_grupos):
        estado = "OK"
    else:
        estado = "FALHA"

    resumo = {
        "tipo": tipo,
        "data_inicio": data_inicio.isoformat(),
        "data_fim": data_fim.isoformat(),
        "duracao_segundos": duracao_segundos,
        "duracao_humana": formatar_duracao(duracao_segundos),
        "ficheiro_entrada": csvfile.name,
        "total_candidatos": total_candidatos,
        "grupos_totais": grupos_totais,
        "originais_eleitos": originais_eleitos,
        "duplicados_marcados": duplicados_marcados,
        "erros_resiliencia": erros_resiliencia,
        "diferenca": diferenca,
        "validacao_contagem": validacao_contagem,
        "validacao_grupos": validacao_grupos,
        "validacao_csv": validacao_csv,
        "ficheiros_processados": ficheiros_processados,
        "estado": estado
    }

    with open(resumo_path, "w", encoding="utf-8") as f:
        json.dump(resumo, f, indent=2, ensure_ascii=False)

    print(f"  Total Candidatos:      {total_candidatos}")
    print(f"  Grupos Totais:         {grupos_totais}")
    print(f"  Originais Eleitos:     {originais_eleitos}")
    print(f"  Duplicados Marcados:   {duplicados_marcados}")
    print(f"  Erros Resiliencia:     {erros_resiliencia}")
    print(f"  Diferenca:             {diferenca}")
    print(f"  Ficheiros Processados: {ficheiros_processados}")
    print(f"  Validacao CSV:         {validacao_csv}")
    print(f"  Validacao Grupos:      {validacao_grupos}")
    print(f"  Validacao Contagem:    {validacao_contagem}")
    print(f"  Duracao:               {duracao_segundos}s ({resumo['duracao_humana']})")
    print(f"  Estado Final:          {estado}")
    print("-" * 70)

    # Bloqueio obrigatorio V8
    if resumo["estado"] == "FALHA":
        print("[BLOQUEADO - FALHA NA VALIDACAO]")
        print("A execucao foi interrompida imediatamente. Nenhum tipo seguinte pode ser executado.")
        sys.exit(1)

    print("[OK - VALIDACAO SUPERADA COM SUCESSO]")
    print(f"Relatorio gravado em: {resumo_path}")
    print("=" * 70)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python separar_tipo.py <tipo>")
        sys.exit(1)
    processar_tipo(sys.argv[1].lower())
