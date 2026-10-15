# -*- coding: utf-8 -*-
"""
V9 FINAL - Melhor versao
- 6 tipos: imagem, pdf, video, csv, excel, md
- Protege ficheiros do sistema
- Renomeia: DATA_ORDEM_CONTEXTO.ext
- Ordem ideal: data -> contexto -> ordem
"""
import os
import sys
import csv
import json
import time
import re
from collections import defaultdict
from datetime import datetime

# ============================================================
# TIPOS PRIORITARIOS
# ============================================================
TIPOS = {
    "imagem":  [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif", ".svg", ".heic", ".raw"],
    "pdf":     [".pdf"],
    "video":   [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
    "csv":     [".csv"],
    "excel":   [".xls", ".xlsx", ".xlsm", ".xlsb"],
    "md":      [".md", ".markdown"],
}

# ============================================================
# PROTECAO DE FICHEIROS DO SISTEMA
# ============================================================
SISTEMA_PATHS = [
    "\\windows\\",
    "\\program files\\",
    "\\program files (x86)\\",
    "\\programdata\\",
    "\\$recycle.bin",
    "\\system volume information",
    "\\windows.old\\",
    "\\$windows.~bt\\",
    "\\$windows.~ws\\",
    "\\recovery\\",
    "\\boot\\",
    "\\efi\\",
    "\\perflogs\\",
    "\\msocache\\",
    "\\intel\\",
    "\\amd\\",
    "\\nvidia\\",
    "\\drivers\\",
    "\\system32\\",
    "\\syswow64\\",
    "\\winsxs\\",
    "\\servicing\\",
    "\\assembly\\",
    "\\microsoft.net\\",
    "\\windowsapps\\",
]

def eh_sistema(caminho):
    c = caminho.lower()
    for p in SISTEMA_PATHS:
        if p in c:
            return True
    return False

def humano(b):
    for u in ["B","KB","MB","GB","TB"]:
        if b < 1024:
            return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} PB"

# ============================================================
# CARREGAR APENAS 1 TIPO
# ============================================================
def carregar_tipo(tipo_nome, extensoes):
    p = os.path.join(r"C:\ACERVO\logs\pipeline_v5", "TODOS_NORMALIZADOS.csv")
    if not os.path.isfile(p):
        return []
    
    regs = []
    with open(p, "r", encoding="utf-8", errors="replace", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                tam = int(row.get("tamanho", 0))
            except ValueError:
                continue
            if tam <= 0:
                continue
            ext = row.get("ext", "").lower()
            if ext not in extensoes:
                continue
            regs.append({
                "origem": row.get("origem", ""),
                "nome": row.get("nome", ""),
                "caminho": row.get("caminho", ""),
                "tamanho": tam,
                "stem": row.get("stem", ""),
                "ext": ext,
                "data_mod": row.get("data_mod", ""),
                "rank": int(row.get("rank", 3)),
                "prof": int(row.get("prof", 0)),
            })
    return regs

# ============================================================
# CONTEXTO DO CAMINHO
# ============================================================
def extrair_contexto(caminho):
    """Extrai contexto do caminho (pasta pai, drive, etc)."""
    partes = caminho.replace("/", "\\").split("\\")
    if len(partes) >= 2:
        return partes[-2]  # pasta imediata
    return ""

# ============================================================
# ORDENAR POR DATA
# ============================================================
def data_para_num(d):
    """Converte data para numero (menor = mais antigo)."""
    if not d:
        return 99999999999
    formatos = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y",
    ]
    for fmt in formatos:
        try:
            dt = datetime.strptime(d.strip(), fmt)
            return int(dt.timestamp())
        except ValueError:
            continue
    return 99999999999

# ============================================================
# RENOMEAR POR EXTENSAO
# ============================================================
def gerar_nome_final(r, ordem, contexto):
    """
    Formato: DATA_ORDEM_CONTEXTO.ext
    - DATA: YYYYMMDD da data de modificacao
    - ORDEM: 0001, 0002... (mais antigo = 0001)
    - CONTEXTO: pasta pai (higienizada)
    """
    # Extrair data
    data_num = data_para_num(r["data_mod"])
    if data_num < 99999999999:
        dt = datetime.fromtimestamp(data_num)
        data_str = dt.strftime("%Y%m%d")
    else:
        data_str = "00000000"
    
    # Contexto higienizado
    ctx = re.sub(r"[^\w\-]", "_", contexto)[:30]
    if not ctx:
        ctx = "root"
    
    # Nome final
    ext = r["ext"]
    nome_final = f"{data_str}_{ordem:04d}_{ctx}{ext}"
    return nome_final

# ============================================================
# PROCESSAR 1 TIPO
# ============================================================
def processar_tipo(tipo_nome, extensoes):
    t0 = time.time()
    print("=" * 78)
    print(f"  V9 FINAL - {tipo_nome.upper()}")
    print("=" * 78)
    print()

    # 1. Carregar
    print(f"[1/6] A carregar {tipo_nome}...")
    t1 = time.time()
    regs = carregar_tipo(tipo_nome, extensoes)
    print(f"  Registos: {len(regs):,} em {time.time()-t1:.2f}s")
    print()

    if not regs:
        print(f"[ERRO] Nenhum registo para {tipo_nome}!")
        return None

    # 2. Protecao de sistema
    print("[2/6] A proteger ficheiros do sistema...")
    t2 = time.time()
    protegidos = 0
    validos = []
    for r in regs:
        if eh_sistema(r["caminho"]):
            protegidos += 1
            continue
        validos.append(r)
    print(f"  Registos:    {len(regs):,}")
    print(f"  Protegidos:  {protegidos:>10,} (sistema)")
    print(f"  Validos:     {len(validos):>10,}")
    print(f"  Tempo: {time.time()-t2:.2f}s")
    print()

    # 3. Validar existencia
    print("[3/6] A validar existencia...")
    t3 = time.time()
    lixo = 0
    inexistente = 0
    finais = []
    for r in validos:
        if os.path.isfile(r["caminho"]):
            finais.append(r)
        else:
            inexistente += 1
    print(f"  Existem:     {len(finais):>10,}")
    print(f"  Inexistentes: {inexistente:>10,}")
    print(f"  Tempo: {time.time()-t3:.2f}s")
    print()

    # 4. Segregar
    print("[4/6] A segregar originais/duplicados...")
    t4 = time.time()
    grupos = defaultdict(list)
    for r in finais:
        chave = (r["stem"], r["tamanho"], r["ext"])
        grupos[chave].append(r)

    originais = []
    duplicados = []
    for chave, grupo in grupos.items():
        if len(grupo) == 1:
            originais.append(grupo[0])
            continue
        # Ordenar por: data (mais antigo primeiro) -> contexto -> rank
        grupo.sort(key=lambda x: (
            data_para_num(x["data_mod"]),   # mais antigo primeiro
            x["rank"],                       # custódia
            extrair_contexto(x["caminho"]),  # contexto
            x["caminho"],                    # desempate
        ))
        originais.append(grupo[0])
        for d in grupo[1:]:
            d["grau"] = "DUPLICADO"
            d["score"] = 85
            duplicados.append(d)

    print(f"  Grupos:     {len(grupos):>10,}")
    print(f"  Originais:  {len(originais):>10,}")
    print(f"  Duplicados: {len(duplicados):>10,}")
    print(f"  Tempo: {time.time()-t4:.2f}s")
    print()

    # 5. Renomear
    print("[5/6] A renomear por extensao...")
    t5 = time.time()
    for i, r in enumerate(originais, 1):
        ctx = extrair_contexto(r["caminho"])
        r["nome_final"] = gerar_nome_final(r, i, ctx)
    for i, r in enumerate(duplicados, 1):
        ctx = extrair_contexto(r["caminho"])
        r["nome_final"] = gerar_nome_final(r, i, ctx)
    print(f"  Originais renomeados: {len(originais):,}")
    print(f"  Duplicados renomeados: {len(duplicados):,}")
    print(f"  Tempo: {time.time()-t5:.2f}s")
    print()

    # 6. Gravar
    print("[6/6] A gravar resultados...")
    t6 = time.time()
    DEST = r"C:\ACERVO\logs\v9"
    SANDBOX = r"C:\ACERVO\SANDBOX\v9"
    os.makedirs(DEST, exist_ok=True)
    os.makedirs(os.path.join(SANDBOX, tipo_nome), exist_ok=True)

    campos = ["nome_final","nome","caminho","tamanho","stem","ext","data_mod","rank","grau","score"]

    orig_path = os.path.join(DEST, f"originais_{tipo_nome}.csv")
    with open(orig_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for r in originais:
            w.writerow({k: r.get(k, "") for k in campos})
    print(f"  [OK] {orig_path} ({len(originais):,})")

    dup_path = os.path.join(DEST, f"duplicados_{tipo_nome}.csv")
    with open(dup_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for r in duplicados:
            w.writerow({k: r.get(k, "") for k in campos})
    print(f"  [OK] {dup_path} ({len(duplicados):,})")

    sbx_path = os.path.join(SANDBOX, tipo_nome, f"duplicados_{tipo_nome}.csv")
    with open(sbx_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for r in duplicados:
            w.writerow({k: r.get(k, "") for k in campos})
    print(f"  [OK] {sbx_path}")

    espaco = sum(r["tamanho"] for r in duplicados)
    man = {
        "tipo": tipo_nome,
        "data": datetime.now().isoformat(),
        "modo": "DRYRUN",
        "total_entrada": len(regs),
        "protegidos_sistema": protegidos,
        "validos": len(validos),
        "existem": len(finais),
        "inexistentes": inexistente,
        "originais": len(originais),
        "duplicados": len(duplicados),
        "espaco_recuperavel_bytes": espaco,
        "espaco_recuperavel_gb": round(espaco / 1024 / 1024 / 1024, 2),
        "ficheiros_alterados": 0,
    }
    man_path = os.path.join(DEST, f"manifesto_{tipo_nome}.json")
    with open(man_path, "w", encoding="utf-8") as f:
        json.dump(man, f, indent=2, ensure_ascii=False)
    print(f"  [OK] {man_path}")
    print(f"  Tempo: {time.time()-t6:.2f}s")
    print()

    print("=" * 78)
    print(f"  RESUMO [{tipo_nome.upper()}]")
    print("=" * 78)
    print(f"  Entrada:            {len(regs):>10,}")
    print(f"  Protegidos sistema: {protegidos:>10,}")
    print(f"  Existem:            {len(finais):>10,}")
    print(f"  Originais:          {len(originais):>10,}")
    print(f"  Duplicados:         {len(duplicados):>10,}")
    print(f"  Espaco recuperavel: {humano(espaco)}")
    print(f"  Tempo total:        {time.time()-t0:.2f}s")
    print("=" * 78)

    return man

def main():
    if len(sys.argv) < 2:
        print("Uso: python pipeline_v9_final.py <tipo>")
        print(f"Tipos: {', '.join(TIPOS.keys())}")
        sys.exit(1)

    tipo_alvo = sys.argv[1].lower()
    if tipo_alvo not in TIPOS:
        print(f"[ERRO] Tipo invalido: {tipo_alvo}")
        print(f"Tipos: {', '.join(TIPOS.keys())}")
        sys.exit(1)

    processar_tipo(tipo_alvo, TIPOS[tipo_alvo])

if __name__ == "__main__":
    main()
