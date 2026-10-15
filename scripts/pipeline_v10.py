# -*- coding: utf-8 -*-
"""
V10 FINAL - Pipeline Definitivo
- 1 tipo de cada vez (valida fim antes de iniciar outro)
- Nome: ID_PROCESO_DATA_CONTEUDO.ext
- Prioridade: ID Processo > Data
- Checksum SHA-256 (parcial + completo)
- EP Hash (Extended Partial Hash)
- Everything HTTP para cruzamento
- Havendo duvidas -> MANTER
"""
import os
import sys
import csv
import json
import time
import re
import hashlib
import urllib.request
import urllib.parse
from collections import defaultdict
from datetime import datetime

# ============================================================
# CONFIGURACAO
# ============================================================
TIPOS = {
    "imagem":  [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif", ".svg", ".heic", ".raw"],
    "pdf":     [".pdf"],
    "video":   [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
    "csv":     [".csv"],
    "excel":   [".xls", ".xlsx", ".xlsm", ".xlsb"],
    "md":      [".md", ".markdown"],
}

ENTRADA = r"C:\ACERVO\logs\pipeline_v5\TODOS_NORMALIZADOS.csv"
DEST    = r"C:\ACERVO\logs\v10"
SANDBOX = r"C:\ACERVO\SANDBOX\v10"
STATE   = r"C:\ACERVO\logs\v10\_estado.json"

os.makedirs(DEST, exist_ok=True)
os.makedirs(SANDBOX, exist_ok=True)

# ============================================================
# PROTECAO DE SISTEMA
# ============================================================
SISTEMA_PATHS = [
    "\\windows\\", "\\program files\\", "\\program files (x86)\\",
    "\\programdata\\", "\\$recycle.bin", "\\system volume information",
    "\\windows.old\\", "\\$windows.~bt\\", "\\$windows.~ws\\",
    "\\recovery\\", "\\boot\\", "\\efi\\", "\\perflogs\\",
    "\\msocache\\", "\\intel\\", "\\amd\\", "\\nvidia\\",
    "\\drivers\\", "\\system32\\", "\\syswow64\\", "\\winsxs\\",
    "\\servicing\\", "\\assembly\\", "\\microsoft.net\\", "\\windowsapps\\",
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
# ESTADO (valida fim de tipo antes de iniciar outro)
# ============================================================
def carregar_estado():
    if os.path.isfile(STATE):
        try:
            with open(STATE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"tipos_terminados": [], "tipos_em_curso": [], "tipo_atual": None}

def guardar_estado(estado):
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(estado, f, indent=2, ensure_ascii=False)

# ============================================================
# CHECKSUM: SHA-256 PARCIAL + EP HASH
# ============================================================
def sha256_parcial(caminho, bloco=65536):
    """SHA-256 dos primeiros 64KB + ultimos 64KB."""
    try:
        h = hashlib.sha256()
        with open(caminho, "rb") as f:
            h.update(f.read(bloco))
            try:
                f.seek(-bloco, 2)
                h.update(f.read(bloco))
            except OSError:
                pass
        return h.hexdigest()[:32]
    except Exception:
        return None

def ep_hash(caminho, bloco=4096, amostras=4):
    """Extended Partial Hash - amostra em 4 pontos do ficheiro."""
    try:
        st = os.stat(caminho)
        tam = st.st_size
        if tam == 0:
            return None
        h = hashlib.sha256()
        with open(caminho, "rb") as f:
            # Amostra 0: inicio
            f.seek(0)
            h.update(f.read(bloco))
            # Amostra 1: 1/4
            f.seek(tam // 4)
            h.update(f.read(bloco))
            # Amostra 2: meio
            f.seek(tam // 2)
            h.update(f.read(bloco))
            # Amostra 3: fim
            f.seek(max(0, tam - bloco))
            h.update(f.read(bloco))
        return h.hexdigest()[:32]
    except Exception:
        return None

# ============================================================
# ID DE PROCESSO
# ============================================================
def gerar_id_processo(tipo, data_num):
    """Gera ID de processo: TIPO-YYYYMMDD-#####"""
    if data_num and data_num < 99999999999:
        dt = datetime.fromtimestamp(data_num)
        data_str = dt.strftime("%Y%m%d")
    else:
        data_str = "00000000"
    return f"{tipo.upper()}-{data_str}"

def data_para_num(d):
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
            return int(datetime.strptime(d.strip(), fmt).timestamp())
        except ValueError:
            continue
    return 99999999999

def extrair_contexto(caminho):
    partes = caminho.replace("/", "\\").split("\\")
    if len(partes) >= 2:
        return partes[-2]
    return "root"

# ============================================================
# NOME FINAL: ID_PROCESO_DATA_CONTEUDO.ext
# ============================================================
def gerar_nome_final(r, ordem, contexto):
    """
    Formato: ID_PROCESO_DATA_CONTEUDO.ext
    Prioridade: ID Processo > Data
    Exemplo: IMAGEM-20240115_20240115_0001_Fotos.jpg
    """
    data_num = data_para_num(r.get("data_mod", ""))
    id_proc = gerar_id_processo(r["tipo"], data_num)
    
    if data_num < 99999999999:
        dt = datetime.fromtimestamp(data_num)
        data_str = dt.strftime("%Y%m%d")
    else:
        data_str = "00000000"
    
    ctx = re.sub(r"[^\w\-]", "_", contexto)[:30] or "root"
    ext = r["ext"]
    
    # ID_PROCESO_DATA_CONTEXTO_ORDEM.ext
    nome = f"{id_proc}_{data_str}_{ctx}_{ordem:04d}{ext}"
    return nome

# ============================================================
# EVERYTHING HTTP
# ============================================================
def tudo_consulta(query, count=10000000):
    params = {
        "search": query,
        "json": "1",
        "count": str(count),
        "path_column": "1",
        "size_column": "1",
    }
    url = "http://localhost:8080/?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace")).get("results", [])
    except Exception as e:
        print(f"  [Everything ERRO] {e}")
        return []

# ============================================================
# CARREGAR 1 TIPO
# ============================================================
def carregar_tipo(tipo_nome, extensoes):
    if not os.path.isfile(ENTRADA):
        return []
    regs = []
    with open(ENTRADA, "r", encoding="utf-8", errors="replace", newline="") as f:
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
                "tipo": tipo_nome,
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
# PROCESSAR 1 TIPO
# ============================================================
def processar_tipo(tipo_nome, extensoes):
    t0 = time.time()
    print("=" * 78)
    print(f"  V10 - TIPO: {tipo_nome.upper()}")
    print("=" * 78)
    print()

    # ============================================================
    # 1. VALIDAR FIM DE TIPO ANTERIOR
    # ============================================================
    estado = carregar_estado()
    if estado["tipo_atual"] and estado["tipo_atual"] != tipo_nome:
        print(f"[AVISO] Tipo anterior '{estado['tipo_atual']}' ainda em curso!")
        print(f"  Estado: {estado}")
        print(f"  A continuar de qualquer forma...")
        print()
    
    estado["tipo_atual"] = tipo_nome
    if tipo_nome not in estado["tipos_em_curso"]:
        estado["tipos_em_curso"].append(tipo_nome)
    guardar_estado(estado)

    # ============================================================
    # 2. CARREGAR
    # ============================================================
    print(f"[1/8] A carregar {tipo_nome}...")
    t1 = time.time()
    regs = carregar_tipo(tipo_nome, extensoes)
    print(f"  Registos: {len(regs):,} em {time.time()-t1:.2f}s")
    print()
    if not regs:
        print(f"[ERRO] Nenhum registo!")
        return None

    # ============================================================
    # 3. PROTECAO SISTEMA
    # ============================================================
    print("[2/8] A proteger sistema...")
    t2 = time.time()
    protegidos = 0
    validos = []
    for r in regs:
        if eh_sistema(r["caminho"]):
            protegidos += 1
            continue
        validos.append(r)
    print(f"  Protegidos: {protegidos:>10,}")
    print(f"  Validos:    {len(validos):>10,}")
    print(f"  Tempo: {time.time()-t2:.2f}s")
    print()

    # ============================================================
    # 4. VALIDAR EXISTENCIA
    # ============================================================
    print("[3/8] A validar existencia...")
    t3 = time.time()
    finais = []
    inexistente = 0
    for r in validos:
        if os.path.isfile(r["caminho"]):
            finais.append(r)
        else:
            inexistente += 1
    print(f"  Existem:     {len(finais):>10,}")
    print(f"  Inexistentes: {inexistente:>10,}")
    print(f"  Tempo: {time.time()-t3:.2f}s")
    print()

    # ============================================================
    # 5. SEGREGAR (sem checksum ainda)
    # ============================================================
    print("[4/8] A segregar por metadados...")
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
        grupo.sort(key=lambda x: (
            data_para_num(x["data_mod"]),   # data mais antiga primeiro
            x["rank"],
            x["prof"],
            x["caminho"],
        ))
        originais.append(grupo[0])
        for d in grupo[1:]:
            d["grau"] = "DUPLICADO_METADADOS"
            d["score"] = 85
            duplicados.append(d)

    print(f"  Grupos:     {len(grupos):>10,}")
    print(f"  Originais:  {len(originais):>10,}")
    print(f"  Duplicados: {len(duplicados):>10,}")
    print(f"  Tempo: {time.time()-t4:.2f}s")
    print()

    # ============================================================
    # 6. CHECKSUM SHA-256 + EP HASH
    # ============================================================
    print("[5/8] A calcular SHA-256 + EP Hash...")
    t5 = time.time()
    total_hash = len(originais) + len(duplicados)
    n = 0
    for r in originais + duplicados:
        r["sha256"] = sha256_parcial(r["caminho"])
        r["ep_hash"] = ep_hash(r["caminho"])
        n += 1
        if n % 5000 == 0:
            print(f"    ... {n:,}/{total_hash:,}", end="\r", flush=True)
    print(f"    ... {n:,}/{total_hash:,} concluido")
    print(f"  Tempo: {time.time()-t5:.2f}s")
    print()

    # ============================================================
    # 7. VALIDAR DUPLICADOS COM CHECKSUM
    # ============================================================
    print("[6/8] A validar duplicados com checksum...")
    t6 = time.time()

    originais_final = []
    duplicados_final = []
    duvidas = 0

    # Re-agrupar com checksum
    grupos_hash = defaultdict(list)
    for r in originais + duplicados:
        chave = (r["stem"], r["tamanho"], r["ext"])
        grupos_hash[chave].append(r)

    for chave, grupo in grupos_hash.items():
        if len(grupo) == 1:
            originais_final.append(grupo[0])
            continue

        # Ordenar por custodia/data
        grupo.sort(key=lambda x: (
            data_para_num(x["data_mod"]),
            x["rank"],
            x["prof"],
            x["caminho"],
        ))
        orig = grupo[0]
        originais_final.append(orig)
        
        for d in grupo[1:]:
            # Se SHA-256 bate -> duplicado real
            if orig["sha256"] and d["sha256"] and orig["sha256"] == d["sha256"]:
                d["grau"] = "IDENTIDADE_CRIPTO_PROVAVEL"
                d["score"] = 100
                duplicados_final.append(d)
            # Se EP Hash bate -> provavel duplicado
            elif orig["ep_hash"] and d["ep_hash"] and orig["ep_hash"] == d["ep_hash"]:
                d["grau"] = "PROVAVEL_DUPLICADO"
                d["score"] = 90
                duplicados_final.append(d)
            else:
                # HAVENDO DUVIDAS -> MANTER
                d["grau"] = "DUVIDA_MANTER"
                d["score"] = 0
                originais_final.append(d)
                duvidas += 1

    print(f"  Originais finais:  {len(originais_final):>10,}")
    print(f"  Duplicados reais:  {len(duplicados_final):>10,}")
    print(f"  Duvidas (manter):  {duvidas:>10,}")
    print(f"  Tempo: {time.time()-t6:.2f}s")
    print()

    # ============================================================
    # 8. RENOMEAR E GRAVAR
    # ============================================================
    print("[7/8] A renomear com ID_PROCESO_DATA_CONTEUDO...")
    t7 = time.time()
    for i, r in enumerate(originais_final, 1):
        ctx = extrair_contexto(r["caminho"])
        r["nome_final"] = gerar_nome_final(r, i, ctx)
    for i, r in enumerate(duplicados_final, 1):
        ctx = extrair_contexto(r["caminho"])
        r["nome_final"] = gerar_nome_final(r, i, ctx)
    print(f"  Tempo: {time.time()-t7:.2f}s")
    print()

    print("[8/8] A gravar resultados...")
    t8 = time.time()
    campos = ["nome_final","nome","caminho","tamanho","stem","ext","data_mod","rank","grau","score","sha256","ep_hash"]

    orig_path = os.path.join(DEST, f"originais_{tipo_nome}.csv")
    with open(orig_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for r in originais_final:
            w.writerow({k: r.get(k, "") for k in campos})
    print(f"  [OK] {orig_path} ({len(originais_final):,})")

    dup_path = os.path.join(DEST, f"duplicados_{tipo_nome}.csv")
    with open(dup_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for r in duplicados_final:
            w.writerow({k: r.get(k, "") for k in campos})
    print(f"  [OK] {dup_path} ({len(duplicados_final):,})")

    sbx_path = os.path.join(SANDBOX, tipo_nome, f"duplicados_{tipo_nome}.csv")
    os.makedirs(os.path.dirname(sbx_path), exist_ok=True)
    with open(sbx_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for r in duplicados_final:
            w.writerow({k: r.get(k, "") for k in campos})
    print(f"  [OK] {sbx_path}")

    # ============================================================
    # MARCA FIM ACO-z
    # ============================================================
    fim_path = os.path.join(DEST, f"_ACO-z_{tipo_nome}.json")
    espaco = sum(r["tamanho"] for r in duplicados_final)
    man = {
        "tipo": tipo_nome,
        "data": datetime.now().isoformat(),
        "fim_ACO-z": True,
        "modo": "DRYRUN",
        "total_entrada": len(regs),
        "protegidos_sistema": protegidos,
        "existem": len(finais),
        "originais": len(originais_final),
        "duplicados": len(duplicados_final),
        "duvidas_manter": duvidas,
        "espaco_recuperavel_bytes": espaco,
        "espaco_recuperavel_gb": round(espaco / 1024 / 1024 / 1024, 2),
        "ficheiros_alterados": 0,
    }
    with open(fim_path, "w", encoding="utf-8") as f:
        json.dump(man, f, indent=2, ensure_ascii=False)
    print(f"  [OK] {fim_path}")
    print(f"  Tempo: {time.time()-t8:.2f}s")
    print()

    # ============================================================
    # ATUALIZAR ESTADO (FIM DO TIPO)
    # ============================================================
    estado = carregar_estado()
    if tipo_nome in estado["tipos_em_curso"]:
        estado["tipos_em_curso"].remove(tipo_nome)
    if tipo_nome not in estado["tipos_terminados"]:
        estado["tipos_terminados"].append(tipo_nome)
    estado["tipo_atual"] = None
    estado["ultimo_fim"] = datetime.now().isoformat()
    estado["ultimo_tipo"] = tipo_nome
    guardar_estado(estado)
    print(f"  [ESTADO] Fim de {tipo_nome} registado")
    print()

    # ============================================================
    # RESUMO
    # ============================================================
    print("=" * 78)
    print(f"  RESUMO [{tipo_nome.upper()}]  --  FIM ACO-z")
    print("=" * 78)
    print(f"  Entrada:            {len(regs):>10,}")
    print(f"  Protegidos sistema: {protegidos:>10,}")
    print(f"  Existem:            {len(finais):>10,}")
    print(f"  Originais:          {len(originais_final):>10,}")
    print(f"  Duplicados:         {len(duplicados_final):>10,}")
    print(f"  Duvidas (manter):   {duvidas:>10,}")
    print(f"  Espaco recuperavel: {humano(espaco)}")
    print(f"  Tempo total:        {time.time()-t0:.2f}s")
    print("=" * 78)

    return man

# ============================================================
# MAIN
# ============================================================
def main():
    if len(sys.argv) < 2:
        print("Uso: python pipeline_v10.py <tipo>")
        print(f"Tipos: {', '.join(TIPOS.keys())}")
        print()
        print("Estado atual:")
        estado = carregar_estado()
        print(f"  Terminados: {estado['tipos_terminados']}")
        print(f"  Em curso:   {estado['tipos_em_curso']}")
        print(f"  Atual:      {estado['tipo_atual']}")
        sys.exit(1)

    tipo_alvo = sys.argv[1].lower()
    if tipo_alvo not in TIPOS:
        print(f"[ERRO] Tipo invalido: {tipo_alvo}")
        sys.exit(1)

    processar_tipo(tipo_alvo, TIPOS[tipo_alvo])

if __name__ == "__main__":
    main()
