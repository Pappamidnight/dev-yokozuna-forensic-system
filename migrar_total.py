import os
import hashlib
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

DESKTOP = Path(r"C:\Users\Yokozuna\Desktop")
PESSOAL = DESKTOP / "Pessoal"
STORAGE = Path(r"C:\ACERVO\storage")
DB = Path(r"C:\ACERVO\db\acervo.db")

# Extensões pessoais
EXT_PESSOAIS = {'.jpg','.jpeg','.png','.gif','.bmp','.heic','.webp',
                '.mp4','.mov','.avi','.mkv','.mp3','.flac','.wav','.m4a',
                '.txt','.rtf','.odt','.epub'}

# Ignorar pastas
IGNORAR = {'Pessoal', '$RECYCLE.BIN', 'System Volume Information'}

conn = sqlite3.connect(str(DB))
cur = conn.cursor()

total = 0
importados = 0
duplicados = 0
erros = 0
pessoais_mantidos = 0

# Listar tudo no Desktop
print("A migrar Desktop...")
print()

for root, dirs, files in os.walk(DESKTOP):
    # Ignorar pastas pessoais e sistema
    dirs[:] = [d for d in dirs if d not in IGNORAR]
    
    root_path = Path(root)
    
    # Se está dentro de Pessoal, manter
    if "Pessoal" in root_path.parts:
        pessoais_mantidos += len(files)
        continue
    
    for nome in files:
        f = root_path / nome
        total += 1
        
        try:
            # Ler
            dados = f.read_bytes()
            tamanho = len(dados)
            
            if tamanho == 0:
                continue
            
            # Hash
            hash_sha = hashlib.sha256(dados).hexdigest()
            hash_b3 = hashlib.blake2b(dados, digest_size=32).hexdigest()
            
            # Verificar duplicado
            cur.execute("SELECT id FROM ficheiros WHERE hash_sha256 = ?", (hash_sha,))
            if cur.fetchone():
                duplicados += 1
                continue
            
            # Copiar para storage
            subdir = hash_sha[:2]
            destino = STORAGE / "files" / subdir / hash_sha
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(dados)
            
            # Inserir DB
            s3_key = f"files/{subdir}/{hash_sha}"
            cur.execute("""
                INSERT INTO ficheiros (hash_sha256, hash_blake3, nome, s3_key, tamanho)
                VALUES (?, ?, ?, ?, ?)
            """, (hash_sha, hash_b3, f.name, s3_key, tamanho))
            
            importados += 1
            
            if total % 500 == 0:
                conn.commit()
                print(f"  {total} processados | {importados} importados | {duplicados} duplicados")
        
        except Exception as e:
            erros += 1
            if erros < 10:
                print(f"  ERRO: {f.name} — {e}")

conn.commit()

cur.execute("SELECT COUNT(*) FROM ficheiros")
total_db = cur.fetchone()[0]

print()
print("=" * 70)
print("  MIGRAÇÃO CONCLUÍDA")
print("=" * 70)
print(f"  Total processados:   {total}")
print(f"  Importados:          {importados}")
print(f"  Duplicados:          {duplicados}")
print(f"  Erros:               {erros}")
print(f"  Pessoais mantidos:   {pessoais_mantidos}")
print(f"  Total na DB:         {total_db}")
print("=" * 70)

conn.close()
