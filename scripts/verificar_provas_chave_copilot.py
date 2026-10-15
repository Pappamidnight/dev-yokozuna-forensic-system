import hashlib
from pathlib import Path

base = Path(r"C:\Users\Yokozuna\OneDrive\Microsoft Copilot Chat Files\Copilot Notebook Uploads")
target_files = [
    "reclamaçaograciosa 2022.jpeg",
    "varela AMECA RECENTE.jpeg",
    "01_PROC_15547-26.0T8LSB.pdf",
    "02_PROC_3719-25.0T8LSB.pdf",
    "03_PROC_20203-22.6T8LSB.pdf",
    "04_PROC_10153-24.7T8LSB.pdf",
    "05_PROC_10153-24.7T8LSB-A.pdf",
    "06_PROC_23142-22.7T8LSB.pdf",
    "2021 - 2025.08.08 20_42.pdf",
    "fatura 82k.jpeg"
]

print("=== INSPEÇÃO DAS 10 PROVAS CHAVE DO COPILOT UPLOADS ===")
for name in target_files:
    fpath = base / name
    try:
        if fpath.exists():
            with open(fpath, "rb") as fp:
                content = fp.read()
                sz = len(content)
                h = hashlib.sha256(content).hexdigest()
                print(f"OK: {name} | {sz:,} bytes | SHA-256: {h}")
        else:
            print(f"NÃO ENCONTRADO: {name}")
    except Exception as e:
        print(f"ERRO em {name}: {e}")
