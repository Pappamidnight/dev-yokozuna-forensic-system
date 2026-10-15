import csv
import json
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

CSV_DIR = Path(r"C:\ACERVO\logs\csv")
OUT_DIR = Path(r"C:\ACERVO\data\normalizado")
OUT_DIR.mkdir(parents=True, exist_ok=True)

CLASSIF = {
    "pdf":      ("FORENSE",      "ALTO",    "ALTO"),
    "word":     ("FORENSE",      "ALTO",    "ALTO"),
    "excel":    ("FORENSE",      "ALTO",    "ALTO"),
    "database": ("FORENSE",      "CRITICO", "ALTO"),
    "audio":    ("FORENSE",      "ALTO",    "ALTO"),
    "video":    ("FORENSE",      "ALTO",    "ALTO"),
    "imagem":   ("FORENSE",      "MEDIO",   "MEDIO"),
    "texto":    ("DOCUMENTO",    "MEDIO",   "MEDIO"),
    "csv":      ("DADOS",        "MEDIO",   "MEDIO"),
    "yaml":     ("CONFIG",       "BAIXO",   "BAIXO"),
    "json":     ("DADOS",        "BAIXO",   "BAIXO"),
    "markdown": ("DOCUMENTACAO", "BAIXO",   "BAIXO"),
}

def tipo_de(nome):
    p = nome.split("_")
    return p[1] if len(p) >= 2 else "desconhecido"

def processar(csv_path):
    csv_path = Path(csv_path)
    tipo = tipo_de(csv_path.name)
    cat, val, sens = CLASSIF.get(tipo, ("DESCONHECIDO", "NULO", "NULO"))
    
    regs = []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            try:
                nome_fich = (row.get("Nome") or "").strip()
                dir_caminho = (row.get("Caminho") or "").strip()
                caminho_completo = str(Path(dir_caminho) / nome_fich) if dir_caminho and nome_fich else (dir_caminho or nome_fich)
                regs.append({
                    "nome": nome_fich,
                    "caminho": dir_caminho,
                    "caminho_completo": caminho_completo,
                    "tamanho_bytes": int((row.get("Tamanho") or "0").strip() or 0),
                    "data_mod": (row.get("DataMod") or "").strip()
                })
            except (ValueError, AttributeError):
                continue
    
    out = OUT_DIR / f"normalizado_{tipo}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump({
            "tipo": tipo,
            "categoria": cat,
            "valor_forense": val,
            "sensibilidade": sens,
            "total": len(regs),
            "registos": regs
        }, f, indent=2, ensure_ascii=False)
    
    return (tipo, len(regs), cat, val, sens)

def main():
    csvs = sorted(CSV_DIR.glob("duplicados_*.csv"))
    if not csvs:
        print("ERRO: sem CSVs")
        sys.exit(1)
    
    total = 0
    inicio = time.time()
    resultados = []
    
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(processar, c): c for c in csvs}
        for fut in as_completed(futures):
            r = fut.result()
            total += r[1]
            resultados.append(r)
    
    duracao = time.time() - inicio
    resultados.sort()
    
    resumo = {
        "total_tipos": len(resultados),
        "total_registos": total,
        "duracao_segundos": round(duracao, 2),
        "tipos": {t: {"total": n, "categoria": c, "valor": v, "sensibilidade": s}
                  for t, n, c, v, s in resultados}
    }
    with open(OUT_DIR / "resumo.json", "w", encoding="utf-8") as f:
        json.dump(resumo, f, indent=2, ensure_ascii=False)
    
    for tipo, n, cat, val, sens in resultados:
        print(f"{tipo}|{n}|{cat}|{val}|{sens}")
    print(f"RESUMO|{len(resultados)}|{total}|{duracao:.2f}")

if __name__ == "__main__":
    main()
