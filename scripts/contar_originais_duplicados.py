import csv
from pathlib import Path

csv_path = Path(r"C:\ACERVO\logs\csv_max_confidence\cruzamento_ultra_confianca_v8.csv")
print("[INFO] A calcular contagens exatas de Originais vs Duplicados (Score == 100)...")

totais = {}
originais_globais = set()
duplicados_globais = set()

with open(csv_path, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if int(row.get("score_confianca") or 0) < 100:
            continue
        tipo = row.get("dup_tipo") or row.get("orig_tipo") or "outro"
        orig = (row.get("orig_caminho") or "") + "\\" + (row.get("orig_nome") or "")
        dup  = (row.get("dup_caminho") or "") + "\\" + (row.get("dup_nome") or "")
        
        if tipo not in totais:
            totais[tipo] = {"orig": set(), "dup": set(), "bytes": 0}
        
        totais[tipo]["orig"].add(orig)
        totais[tipo]["dup"].add(dup)
        totais[tipo]["bytes"] += int(row.get("tamanho_bytes") or 0)
        
        originais_globais.add(orig)
        duplicados_globais.add(dup)

print("=" * 70)
print(f"{'TIPO':12} | {'ORIGINAIS':12} | {'DUPLICADOS':12} | {'ESPACO RECUPERAVEL':18}")
print("-" * 70)

total_gb = 0
for t, d in sorted(totais.items(), key=lambda x: len(x[1]["dup"]), reverse=True):
    bytes_totais = d["bytes"]
    if bytes_totais >= 1024**3:
        txt_tam = f"{bytes_totais / (1024**3):.2f} GB"
    else:
        txt_tam = f"{bytes_totais / (1024**2):.2f} MB"
    total_gb += bytes_totais / (1024**3)
    print(f"{t:12} | {len(d['orig']):12} | {len(d['dup']):12} | {txt_tam:18}")

print("=" * 70)
print(f"TOTAL GLOBAL: {len(originais_globais)} ORIGINAIS  vs  {len(duplicados_globais)} DUPLICADOS")
print(f"ESPACO GLOBAL RECUPERAVEL: {total_gb:.2f} GB")
print("=" * 70)
