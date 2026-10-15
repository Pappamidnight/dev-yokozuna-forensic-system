import csv, json, sys, os, time, hashlib
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed

CSV_FILE     = r"C:\ACERVO\logs\todos.csv"
MANIFEST_DIR = Path(r"C:\ACERVO\manifests")
STORAGE      = Path(r"C:\ACERVO\storage")
QUARENTENA   = Path(r"C:\ACERVO\quarentena")

MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
STORAGE.mkdir(parents=True, exist_ok=True)
QUARENTENA.mkdir(parents=True, exist_ok=True)

def sha256(path, chunk=1024*1024):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for c in iter(lambda: f.read(chunk), b""):
                h.update(c)
        return h.hexdigest()
    except (OSError, PermissionError):
        return None

def processar_grupo(args):
    """Grupo = ficheiros com mesmo tamanho. Retorna (originais, duplicados, erros)."""
    size, items = args
    originais = []
    duplicados = []
    erros = 0
    
    hashes = defaultdict(list)
    
    for item in items:
        # Construir caminho Windows
        path = os.path.join(item["Caminho"], item["Nome"])
        
        h = sha256(path)
        if not h:
            erros += 1
            continue
        
        hashes[h].append({
            "nome": item["Nome"],
            "caminho": path,
            "tamanho": int(item["Tamanho"]),
            "data_mod": item["DataMod"]
        })
    
    for h, ficheiros in hashes.items():
        if len(ficheiros) < 2:
            continue
        
        ficheiros.sort(key=lambda x: x["data_mod"])
        originais.append((h, ficheiros[0]))
        for d in ficheiros[1:]:
            duplicados.append((h, d, ficheiros[0]))
    
    return (originais, duplicados, erros)

def main():
    print("  Ler CSV...")
    with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    
    total_rows = len(rows)
    print(f"  Registos CSV: {total_rows}")
    
    # Agrupar por tamanho
    print("  Agrupar por tamanho...")
    grupos = defaultdict(list)
    for r in rows:
        try:
            size = int(r["Tamanho"])
        except:
            continue
        grupos[size].append(r)
    
    # Filtrar grupos com >1
    grupos_dup = [(s, v) for s, v in grupos.items() if len(v) > 1]
    print(f"  Grupos: {len(grupos)} | Grupos com >1: {len(grupos_dup)}")
    
    # SHA-256 apenas nos grupos com >1
    print("  Calcular SHA-256 (paralelo)...")
    inicio = time.time()
    
    originais_total = []
    duplicados_total = []
    erros_total = 0
    concluidos = 0
    
    with ProcessPoolExecutor() as ex:
        futures = {ex.submit(processar_grupo, g): g for g in grupos_dup}
        for fut in as_completed(futures):
            try:
                o, d, e = fut.result()
                originais_total.extend(o)
                duplicados_total.extend(d)
                erros_total += e
            except Exception:
                erros_total += 1
            
            concluidos += 1
            if concluidos % 500 == 0:
                print(f"    {concluidos}/{len(grupos_dup)}")
    
    duracao = time.time() - inicio
    
    print(f"  Originais: {len(originais_total)}")
    print(f"  Duplicados: {len(duplicados_total)}")
    print(f"  Erros: {erros_total}")
    print(f"  Duracao: {duracao:.2f}s")
    
    # Manifest
    print("  Gravar manifest...")
    manifest = {
        "total_csv": total_rows,
        "grupos": len(grupos),
        "grupos_dup": len(grupos_dup),
        "originais": len(originais_total),
        "duplicados": len(duplicados_total),
        "erros": erros_total,
        "duracao_segundos": round(duracao, 2),
        "registos_originais": [
            {"hash": h, "nome": o["nome"], "caminho": o["caminho"], "tamanho": o["tamanho"]}
            for h, o in originais_total
        ],
        "registos_duplicados": [
            {"hash": h, "nome": d["nome"], "caminho": d["caminho"], "tamanho": d["tamanho"], "original": o["caminho"]}
            for h, d, o in duplicados_total
        ]
    }
    with open(MANIFEST_DIR / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"  Manifest: {MANIFEST_DIR / 'manifest.json'}")
    
    # Output para PowerShell
    print(f"MANIFEST|{len(originais_total)}|{len(duplicados_total)}|{erros_total}|{duracao:.2f}")

if __name__ == "__main__":
    main()
